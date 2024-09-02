# dosnapshots

`dosnapshots.py` is a Python script designed to manage DigitalOcean snapshots for a specified Droplet. The script automates the creation and deletion of snapshots based on a configurable retention policy, ensuring an efficient and organized backup system.

## Key Features

### Snapshot Creation

- The script creates a snapshot of the specified DigitalOcean Droplet using the `doctl` command-line tool.
- Snapshots are named with the droplet name followed by a timestamp for easy identification.
  
### Snapshot Retention

- The script enforces a retention policy that retains a specified number of recent snapshots.
- Older snapshots that do not fit within the retention policy are automatically deleted.

### Detailed Logging

- Logs detailed information about each command executed, including success messages and any errors encountered.
- Ensures sensitive information, such as the DigitalOcean API token, is masked in the logs.
- Final status messages provide a summary of each run, including the hostname, timestamp, snapshot name, and the total number of snapshots retained.

## Configuration

The script is highly configurable through environment variables set in the `.env` file:

- **DROPLET_ID**: The unique identifier of the DigitalOcean Droplet to manage.
- **DROPLET_NAME**: A prefix for snapshot names to easily identify them.
- **DO_API_TOKEN**: The DigitalOcean API token used for authentication with the `doctl` tool.

### Retention Policy

- **RETAIN_LAST_SNAPSHOTS**: Number of recent snapshots to retain.
- **DELETE_RETRIES**: Number of retries when attempting to delete a snapshot.

### Log File

- Logs are stored in the same directory as the script, with detailed logging of every operation.

### Path to `doctl`

- The full path to the `doctl` binary should be configured correctly. If installed manually, the path is usually `/usr/local/bin/doctl`. 
- If installed via Snap, the path might be `/snap/bin/doctl`.
- To manually install `doctl`, use the command:
  ```bash
  curl -sL https://github.com/digitalocean/doctl/releases/latest/download/doctl-$(uname -s)-$(uname -m) -o /usr/local/bin/doctl && chmod +x /usr/local/bin/doctl
  ```

## Usage Instructions

### Install `doctl`

```bash
sudo apt update
sudo apt install snapd
sudo snap install doctl
doctl version
which doctl
```

### Create and Configure the Project Directory

```bash
sudo mkdir -p /var/python/dosnapshots
sudo chown $USER:$USER /var/python/dosnapshots
cd /var/python/dosnapshots
```

### Setup a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Copy the Script

Place the `dosnapshots.py` script in `/var/python/dosnapshots`.

### Test the Script Manually on the Command Line

```bash
source /var/python/dosnapshots/venv/bin/activate
python /var/python/dosnapshots/dosnapshots.py
```

### Check Logs

```bash
cat /var/python/dosnapshots/dosnapshots.log
```

### Set Up a Cron Job

```bash
crontab -e
```

Add the following line to run the script daily at 2 AM:

```bash
0 2 * * * /bin/bash -c 'source /var/python/dosnapshots/venv/bin/activate && python /var/python/dosnapshots/dosnapshots.py'
```

By following these steps and configurations, `dosnapshots.py` helps maintain a systematic backup strategy for your DigitalOcean Droplets, ensuring data is securely and efficiently managed.

