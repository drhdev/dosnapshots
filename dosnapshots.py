import subprocess
import logging
import datetime
from dateutil.relativedelta import relativedelta

# ============================ #
# User Configuration Variables  #
# ============================ #

# DigitalOcean Droplet ID
DROPLET_ID = "your_droplet_id"

# Name of the droplet (used as a prefix for snapshot names)
DROPLET_NAME = "your_droplet_name"

# DigitalOcean API Token
DO_API_TOKEN = "your_api_token"

# Full path to the doctl binary
DOCTL_PATH = "/snap/bin/doctl"

# Retention policies:
# - KEEP_LAST_DAYS: Number of daily snapshots to keep. Example: if set to 3, keeps the last 3 daily snapshots.
# - KEEP_WEEKLY: Number of weekly snapshots to keep. Example: if set to 4, keeps 4 weekly snapshots (one per week).
# - KEEP_MONTHLY: Number of monthly snapshots to keep. Example: if set to 6, keeps 6 monthly snapshots (one per month).
KEEP_LAST_DAYS = 3
KEEP_WEEKLY = 4
KEEP_MONTHLY = 6

# Log file path
LOG_FILE_PATH = "/var/log/dosnapshots.log"

# Masked token for logging
MASKED_TOKEN = DO_API_TOKEN[:6] + '...' + DO_API_TOKEN[-6:]

# ============================ #
#       End of Config          #
# ============================ #

# Set up logging
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, format='%(asctime)s %(message)s')

# Function to run shell commands
def run_command(command):
    masked_command = command.replace(DO_API_TOKEN, MASKED_TOKEN)
    logging.info(f"Starting command: {masked_command}")
    try:
        env = {"DO_API_TOKEN": DO_API_TOKEN}
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout = result.stdout.decode().strip()
        stderr = result.stderr.decode().strip()
        logging.info(f"Command '{masked_command}' executed successfully.")
        logging.info(f"Return code: {result.returncode}")
        logging.info(f"Output: {stdout}")
        if stderr:
            logging.warning(f"Error output: {stderr}")
        return stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command '{masked_command}'")
        logging.error(f"Return code: {e.returncode}")
        logging.error(f"Output: {e.stdout.decode().strip()}")
        logging.error(f"Error output: {e.stderr.decode().strip()}")
        return None

# Function to create a snapshot
def create_snapshot(droplet_id, name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    snapshot_name = f"{name}-{timestamp}"
    command = f"{DOCTL_PATH} compute droplet-action snapshot {droplet_id} --snapshot-name {snapshot_name} --wait --access-token {DO_API_TOKEN}"
    if run_command(command):
        logging.info(f"Snapshot '{snapshot_name}' created for droplet {droplet_id}.")
    else:
        logging.error(f"Failed to create snapshot '{snapshot_name}' for droplet {droplet_id}.")

# Function to delete old snapshots
def delete_old_snapshots(droplet_id, keep_last_days=3, keep_weekly=4, keep_monthly=6):
    command = f"{DOCTL_PATH} compute snapshot list --resource droplet --format ID,Name,CreatedAt,ResourceID --no-header --access-token {DO_API_TOKEN}"
    snapshots = run_command(command)
    if snapshots:
        snapshots = [line.split() for line in snapshots.split('\n') if line.split()[-1] == str(droplet_id)]
        snapshots = [{"id": s[0], "name": s[1], "created_at": datetime.datetime.fromisoformat(s[2].split('+')[0])} for s in snapshots]

        now = datetime.datetime.now()

        to_keep = []
        for snap in snapshots:
            age = now - snap["created_at"]
            if age <= datetime.timedelta(days=keep_last_days):
                to_keep.append(snap)
            elif age <= datetime.timedelta(days=keep_weekly*7):
                to_keep.append(snap)
            elif age <= relativedelta(months=+keep_monthly):
                to_keep.append(snap)

        to_delete = [snap for snap in snapshots if snap not in to_keep]

        for snap in to_delete:
            command = f"{DOCTL_PATH} compute snapshot delete {snap['id']} --force --access-token {DO_API_TOKEN}"
            if run_command(command):
                logging.info(f"Deleted old snapshot '{snap['name']}'.")
            else:
                logging.error(f"Failed to delete snapshot '{snap['name']}'.")

if __name__ == "__main__":
    if not DROPLET_ID or not DROPLET_NAME or not DO_API_TOKEN:
        logging.error("DROPLET_ID, DROPLET_NAME, and DO_API_TOKEN must be set.")
        exit(1)

    create_snapshot(DROPLET_ID, DROPLET_NAME)
    delete_old_snapshots(DROPLET_ID, KEEP_LAST_DAYS, KEEP_WEEKLY, KEEP_MONTHLY)
