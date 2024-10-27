#!/usr/bin/env python3
# dosnapshots.py
# Version: 1.3
# Author: drhdev
# License: GPL v3
#
# Description:
# This script manages snapshots for a specified DigitalOcean droplet, including creation, retention, and deletion.

import subprocess
import logging
from logging.handlers import RotatingFileHandler
import datetime
import os
import sys
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# User Configuration Variables
DROPLET_ID = os.getenv("DROPLET_ID")
DROPLET_NAME = os.getenv("DROPLET_NAME")
DO_API_TOKEN = os.getenv("DO_API_TOKEN")

# Detect the path of the doctl command-line tool
def get_doctl_path():
    try:
        # Run 'which doctl' to find all doctl paths
        doctl_paths = subprocess.run("which -a doctl", shell=True, check=True, stdout=subprocess.PIPE).stdout.decode().strip().split('\n')
        
        # If multiple paths, sort by modification time and select the latest
        if len(doctl_paths) > 1:
            doctl_paths = sorted(doctl_paths, key=lambda path: os.path.getmtime(path), reverse=True)
        
        return doctl_paths[0] if doctl_paths else None
    except subprocess.CalledProcessError:
        return None

DOCTL_PATH = get_doctl_path() or "/usr/local/bin/doctl"  # Fallback to a default path if detection fails

# Check if doctl path was detected
if not DOCTL_PATH or not os.path.exists(DOCTL_PATH):
    print("Error: doctl command not found. Please ensure it is installed and accessible.")
    sys.exit(1)

RETAIN_LAST_SNAPSHOTS = 0  # Default to retain the last 1 snapshot
DELETE_RETRIES = 3  # Number of retries for deletion

# Set up logging
base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where the script is located
log_filename = os.path.join(base_dir, 'dosnapshots.log')
logger = logging.getLogger('dosnapshots.py')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(log_filename, maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Check for verbose flag
verbose = '-v' in sys.argv
if verbose:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

MASKED_TOKEN = DO_API_TOKEN[:6] + '...' + DO_API_TOKEN[-6:]

def setup_environment():
    """
    Checks for required environment variables and sets up the necessary directories.
    """
    if not DROPLET_ID or not DROPLET_NAME or not DO_API_TOKEN:
        error_exit("DROPLET_ID, DROPLET_NAME, and DO_API_TOKEN must be set in the environment.")

def error_exit(message):
    """
    Logs the error message and exits the script.
    """
    logger.error(message)
    sys.exit(1)

def run_command(command):
    """
    Executes a shell command securely and logs the output.
    """
    masked_command = command.replace(DO_API_TOKEN, MASKED_TOKEN)
    logger.info(f"Running command: {masked_command}")
    try:
        env = {
            "DO_API_TOKEN": DO_API_TOKEN,
            "HOME": os.path.expanduser("~"),  # Set HOME to the current user's home directory
            "XDG_CONFIG_HOME": os.path.expanduser("~/.config")  # Optionally set XDG_CONFIG_HOME
        }
        result = subprocess.run(command.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout = result.stdout.decode().strip()
        stderr = result.stderr.decode().strip()
        logger.info(f"Command executed successfully with output: {stdout}")
        if stderr:
            logger.warning(f"Command executed with errors: {stderr}")
        return stdout
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.decode().strip() if e.stdout else ""
        stderr = e.stderr.decode().strip() if e.stderr else ""
        logger.error(f"Command failed with error: {stderr}")
        logger.debug(f"Command failed with output: {stdout}")
        logger.debug(f"Full command that failed: {masked_command}")
        return None

def get_snapshots(droplet_id):
    """
    Retrieves snapshots associated with the specified droplet.
    """
    command = f"{DOCTL_PATH} compute snapshot list --resource droplet --format ID,Name,CreatedAt --no-header --access-token {DO_API_TOKEN}"
    snapshots_output = run_command(command)
    snapshots = []

    if snapshots_output:
        for line in snapshots_output.splitlines():
            parts = line.split(maxsplit=2)
            if len(parts) == 3 and (droplet_id in parts[1] or DROPLET_NAME in parts[1]):
                snapshot_id, snapshot_name, created_at_str = parts
                created_at = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00')).astimezone(datetime.timezone.utc)
                snapshots.append({"id": snapshot_id, "name": snapshot_name, "created_at": created_at})
                logger.debug(f"Snapshot found: {snapshot_name} (ID: {snapshot_id}) created at {created_at}")
    else:
        logger.error("No snapshots retrieved or an error occurred during retrieval.")

    return snapshots

def identify_snapshots_to_delete(snapshots):
    """
    Identifies which snapshots should be deleted based on the retention policy.
    """
    snapshots.sort(key=lambda x: x['created_at'], reverse=True)
    to_delete = snapshots[RETAIN_LAST_SNAPSHOTS:]
    logger.info(f"Snapshots identified for deletion: {[snap['name'] for snap in to_delete]}")
    return to_delete

def create_snapshot(droplet_id, name):
    """
    Creates a new snapshot for the specified droplet.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    snapshot_name = f"{name}-{timestamp}"
    command = f"{DOCTL_PATH} compute droplet-action snapshot {droplet_id} --snapshot-name {snapshot_name} --wait --access-token {DO_API_TOKEN}"
    if run_command(command):
        logger.info(f"New snapshot created: {snapshot_name}")
        return snapshot_name, timestamp
    else:
        logger.error(f"Failed to create a new snapshot for droplet {droplet_id}")
        return None, None

def delete_snapshots(snapshots):
    """
    Deletes the specified snapshots, with retry logic for robustness.
    """
    for snap in snapshots:
        for attempt in range(DELETE_RETRIES):
            command = f"{DOCTL_PATH} compute snapshot delete {snap['id']} --force --access-token {DO_API_TOKEN}"
            result = run_command(command)
            if result is not None:
                if "404" in result:
                    logger.warning(f"Snapshot not found (likely already deleted): {snap['name']}. Treating as successful deletion.")
                    break
                else:
                    logger.info(f"Snapshot deleted: {snap['name']}")
                    break
            else:
                logger.error(f"Attempt {attempt + 1} failed to delete snapshot: {snap['name']}")
                if attempt < DELETE_RETRIES - 1:
                    time.sleep(5)  # Wait before retrying
                else:
                    logger.error(f"Failed to delete snapshot after {DELETE_RETRIES} attempts: {snap['name']}")

def write_final_status(snapshot_name, timestamp, total_snapshots, status):
    """
    Writes the final status of the script to the log for monitoring purposes.
    Format: FINAL_STATUS | STATUS | HOSTNAME | TIMESTAMP | SNAPSHOT_NAME | TOTAL_SNAPSHOTS
    """
    hostname = os.uname().nodename
    final_status_message = f"FINAL_STATUS | {status.upper()} | {hostname} | {timestamp} | {snapshot_name} | {total_snapshots} snapshots exist"
    logger.info(final_status_message)

def main():
    """
    Main function that manages the DigitalOcean snapshots.
    """
    logger.info("Starting snapshot management process...")
    
    # Set up environment and check necessary variables
    setup_environment()

    # Retrieve existing snapshots
    snapshots = get_snapshots(DROPLET_ID)
    
    # Identify snapshots to delete
    to_delete = identify_snapshots_to_delete(snapshots)
    
    # Create a new snapshot
    snapshot_name, snapshot_time = create_snapshot(DROPLET_ID, DROPLET_NAME)
    
    # Delete old snapshots
    delete_snapshots(to_delete)
    
    # Write final status to the log
    if snapshot_name and snapshot_time:
        write_final_status(snapshot_name, snapshot_time, len(snapshots), "success")
    else:
        write_final_status("none", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(snapshots), "failure")
    
    logger.info("Snapshot management process completed.")

if __name__ == "__main__":
    main()

