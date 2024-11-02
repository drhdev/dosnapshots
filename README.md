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

### API Token Scope

Ensure that your API token has the correct scope with sufficient permissions to create, list, and delete snapshots. Instructions on how to set up personal access tokens with the required permissions can be found in the DigitalOcean documentation: [Create Personal Access Token](https://docs.digitalocean.com/reference/api/create-personal-access-token/).

### Retention Policy

- **RETAIN_LAST_SNAPSHOTS**: Number of recent snapshots to retain.
- **DELETE_RETRIES**: Number of retries when attempting to delete a snapshot.

### Log File

- Logs are stored in the same directory as the script, with detailed logging of every operation.

### Path to `doctl`

- The full path to the `doctl` binary should be configured correctly, usually `/usr/local/bin/doctl` if installed manually.
- To manually install `doctl`, use these commands:
- Download to a temporary directory:
  ```bash
  sudo curl -sL https://github.com/digitalocean/doctl/releases/download/v1.117.0/doctl-1.117.0-linux-amd64.tar.gz -o /tmp/doctl.tar.gz
  ```
- Extract the binary from the tar.gz archive
  ```bash
  sudo tar -xzf /tmp/doctl.tar.gz -C /usr/local/bin doctl
  ```
- Make the binary executable
  ```bash
  sudo chmod +x /usr/local/bin/doctl
  ```
- After running the command, check the version:
  ```bash
  doctl version
  ```
- To find out where `doctl` is installed on your system, you can use the following command in the terminal:
  ```bash
  which doctl
  ```

This command will display the path to the `doctl` executable if it is available in your system's PATH.

## Usage Instructions

### Clone the Repository

Clone the `dosnapshots` repository to your home directory:

```bash
mkdir -p /home/user/python
cd /home/user/python
git clone https://github.com/drhdev/dosnapshots.git
cd dosnapshots
```

### Setup a Virtual Environment

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the `/home/user/python/dosnapshots` directory with your DigitalOcean configuration:

```plaintext
# .env file
DROPLET_ID=your_droplet_id
DROPLET_NAME=your_droplet_name
DO_API_TOKEN=your_api_token
```

### Test the Script Manually on the Command Line

Activate the virtual environment and run the script:

```bash
source /home/user/python/dosnapshots/venv/bin/activate
python /home/user/python/dosnapshots/dosnapshots.py
```

### Check Logs

Logs are stored in the same directory as the script. You can view them with:

```bash
cat /home/user/python/dosnapshots/dosnapshots.log
```

### Set Up a Cron Job

Edit your crontab to schedule the script to run at a specific time (e.g., daily at 2 AM):

```bash
crontab -e
```

Add the following line:

```bash
0 2 * * * /bin/bash -c 'source /home/user/python/dosnapshots/venv/bin/activate && python /home/user/python/dosnapshots/dosnapshots.py' > /home/user/python/dosnapshots/dosnapshots.log 2>&1
```

By following these steps and configurations, `dosnapshots.py` helps maintain a systematic backup strategy for your DigitalOcean Droplets, ensuring data is securely and efficiently managed.
