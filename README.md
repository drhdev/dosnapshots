### Summary of `dosnapshots.py`

`dosnapshots.py` is a Python script designed to manage DigitalOcean snapshots for a specified Ubuntu Droplet. 

The script automates the creation and deletion of snapshots based on a configurable retention policy, ensuring that the user maintains an efficient and organized backup system.

#### Key Features

1. **Snapshot Creation**:
   - The script creates a snapshot of the specified DigitalOcean Droplet using the `doctl` command-line tool.
   - Snapshots are named with a specified prefix followed by a timestamp for easy identification.

2. **Snapshot Retention**:
   - The script enforces a retention policy that retains:
     - A specified number of recent daily snapshots.
     - A specified number of weekly snapshots.
     - A specified number of monthly snapshots.
   - Older snapshots that do not fit within the retention policy are automatically deleted.

3. **Detailed Logging**:
   - Logs detailed information about each command executed, including success messages and any errors encountered.
   - Ensures sensitive information, like the DigitalOcean API token, is masked in the logs.

#### Configuration

The script is highly configurable through variables set at the beginning:

- **Droplet ID**: The unique identifier of the DigitalOcean Droplet to manage.
- **Droplet Name**: A prefix for snapshot names to easily identify them.
- **API Token**: The DigitalOcean API token, used for authentication with the `doctl` tool.
- **Retention Policies**:
  - `KEEP_LAST_DAYS`: Number of daily snapshots to retain.
  - `KEEP_WEEKLY`: Number of weekly snapshots to retain.
  - `KEEP_MONTHLY`: Number of monthly snapshots to retain.
- **Log File Path**: The file path where logs are stored.
- **Path to `doctl`**: The full path to the `doctl` binary, ensuring it is correctly located and executed.

#### Usage Instructions

1. **Install `doctl`**:
   ```bash
   sudo apt update
   sudo apt install snapd
   sudo snap install doctl
   doctl version
   which doctl
   ```

2. **Create and Configure the Project Directory**:
   ```bash
   sudo mkdir -p /var/python/dosnapshots
   sudo chown $USER:$USER /var/python/dosnapshots
   cd /var/python/dosnapshots
   ```

3. **Setup a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install python-dateutil
   ```

4. **Copy the Script**:
   Place the `dosnapshots.py` script in `/var/python/dosnapshots`.

5. **Test the Script manually on the Command Line**:
   ```bash
   sudo /bin/bash -c 'source /var/python/dosnapshots/venv/bin/activate && python /var/python/dosnapshots/dosnapshots.py'
   ```

6. **Check Logs**:
   ```bash
   sudo cat /var/log/dosnapshots.log
   ```

7. **Set Up a Cron Job**:
   ```bash
   sudo crontab -e
   ```
   Add the following line:
   ```bash
   0 2 * * * /bin/bash -c 'source /var/python/dosnapshots/venv/bin/activate && python /var/python/dosnapshots/dosnapshots.py'
   ```

By following these steps and configurations, `dosnapshots.py` helps maintain a systematic backup strategy for your DigitalOcean Droplets, ensuring data is securely and efficiently managed.
