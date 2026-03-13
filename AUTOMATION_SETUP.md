# Automation Setup Guide

This guide explains how to set up automated fact collection using system-level schedulers. The script supports two modes:

- **One-shot mode**: Fetches one fact and exits (perfect for schedulers)
- **Automated mode**: Runs continuously in a loop (use `--auto` flag)

For system schedulers, we use **one-shot mode** so the scheduler runs the script periodically.

## Table of Contents

- [Linux/macOS: Cron Jobs](#linuxmacos-cron-jobs)
- [Windows: Task Scheduler](#windows-task-scheduler)
- [Testing Your Setup](#testing-your-setup)
- [Troubleshooting](#troubleshooting)

---

## Linux/macOS: Cron Jobs

### Prerequisites

1. Python 3 installed and accessible
2. Script path: Know the full path to `fetch_fact.py`
3. Python path: Know the full path to your Python executable

### Finding Your Python Path

```bash
# Find Python 3 executable
which python3

# Or if using a virtual environment
which python

# Example output: /usr/bin/python3 or /usr/local/bin/python3
```

### Finding Your Script Path

```bash
# Navigate to the script directory
cd /path/to/openimpactlab

# Get absolute path
pwd

# Full script path will be: /path/to/openimpactlab/fetch_fact.py
```

### Setting Up a Cron Job

1. **Open your crontab for editing:**
   ```bash
   crontab -e
   ```

2. **Add a cron entry.** Here are common examples:

   **Every hour:**
   ```bash
   0 * * * * /usr/bin/python3 /path/to/openimpactlab/fetch_fact.py --quiet >> /path/to/openimpactlab/facts.log 2>&1
   ```

   **Every 30 minutes:**
   ```bash
   */30 * * * * /usr/bin/python3 /path/to/openimpactlab/fetch_fact.py --quiet >> /path/to/openimpactlab/facts.log 2>&1
   ```

   **Every 15 minutes:**
   ```bash
   */15 * * * * /usr/bin/python3 /path/to/openimpactlab/fetch_fact.py --quiet >> /path/to/openimpactlab/facts.log 2>&1
   ```

   **Daily at 9 AM:**
   ```bash
   0 9 * * * /usr/bin/python3 /path/to/openimpactlab/fetch_fact.py --quiet >> /path/to/openimpactlab/facts.log 2>&1
   ```

   **Every day at midnight:**
   ```bash
   0 0 * * * /usr/bin/python3 /path/to/openimpactlab/fetch_fact.py --quiet >> /path/to/openimpactlab/facts.log 2>&1
   ```

3. **Save and exit** the editor (usually `:wq` in vim or `Ctrl+X` then `Y` in nano)

4. **Verify your cron job:**
   ```bash
   crontab -l
   ```

### Cron Syntax Explanation

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, where 0 and 7 = Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

Examples:
- `0 * * * *` = Every hour at minute 0
- `*/30 * * * *` = Every 30 minutes
- `0 9 * * *` = Every day at 9:00 AM
- `0 0 * * 0` = Every Sunday at midnight

### Using the Helper Script

For easier setup, use the provided helper script:

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

This script will:
- Find your Python path automatically
- Find your script path
- Test the script before adding to cron
- Help you choose a schedule
- Add the cron job for you

---

## Windows: Task Scheduler

### Method 1: Using GUI (Task Scheduler)

1. **Open Task Scheduler:**
   - Press `Win + R`, type `taskschd.msc`, press Enter
   - Or search for "Task Scheduler" in Start menu

2. **Create Basic Task:**
   - Click "Create Basic Task..." in the right panel
   - Name: "Fetch Facts Automatically"
   - Description: "Automatically fetch and save useless facts"

3. **Set Trigger:**
   - Choose frequency (Daily, Weekly, etc.)
   - Set time and recurrence

4. **Set Action:**
   - Action: "Start a program"
   - Program/script: Full path to Python executable
     - Example: `C:\Python39\python.exe`
     - Or: `C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe`
   - Add arguments: Full path to `fetch_fact.py` with `--quiet` flag
     - Example: `C:\path\to\openimpactlab\fetch_fact.py --quiet`
   - Start in: Directory containing `fetch_fact.py`
     - Example: `C:\path\to\openimpactlab`

5. **Finish:**
   - Review settings
   - Check "Open the Properties dialog..." if you want to configure more
   - Click Finish

### Method 2: Using PowerShell (Command Line)

Run PowerShell as Administrator and execute:

```powershell
# Set variables
$TaskName = "FetchFactsAutomatically"
$PythonPath = "C:\Python39\python.exe"  # Update with your Python path
$ScriptPath = "C:\path\to\openimpactlab\fetch_fact.py"  # Update with your script path
$WorkingDir = "C:\path\to\openimpactlab"  # Update with your directory

# Create scheduled task (runs every hour)
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`" --quiet" -WorkingDirectory $WorkingDir
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Automatically fetch and save useless facts"
```

### Method 3: Using schtasks Command

Open Command Prompt as Administrator:

```cmd
schtasks /create /tn "FetchFactsAutomatically" /tr "C:\Python39\python.exe C:\path\to\openimpactlab\fetch_fact.py --quiet" /sc hourly /st 00:00
```

### Using the Helper Script

Run PowerShell as Administrator and execute:

```powershell
.\setup_task_scheduler.ps1
```

This script will:
- Find your Python installation
- Find your script path
- Test the script
- Create the scheduled task interactively

---

## Testing Your Setup

### Test One-Shot Mode Manually

Before setting up automation, test that the script works:

```bash
# Linux/macOS
python3 fetch_fact.py --quiet

# Windows
python fetch_fact.py --quiet
```

Expected behavior:
- Script runs silently (with `--quiet`)
- Fetches one fact
- Saves to archive if unique
- Exits with code 0 (success)

### Test Cron Job (Linux/macOS)

1. **Add a test cron job that runs in 2 minutes:**
   ```bash
   crontab -e
   ```
   
   Add this line (replace paths):
   ```bash
   */2 * * * * /usr/bin/python3 /path/to/openimpactlab/fetch_fact.py --quiet >> /path/to/openimpactlab/test_cron.log 2>&1
   ```

2. **Wait 2 minutes, then check:**
   ```bash
   # Check log file
   cat /path/to/openimpactlab/test_cron.log
   
   # Check archive
   python3 fetch_fact.py --count
   ```

3. **Remove test cron job:**
   ```bash
   crontab -e
   # Remove the test line
   ```

### Test Task Scheduler (Windows)

1. **Create a test task** that runs in 1 minute
2. **Wait and check:**
   - Check Task Scheduler history (right-click task → History)
   - Check archive: `python fetch_fact.py --count`
3. **Delete test task** if successful

---

## Troubleshooting

### Cron Job Not Running

**Check cron logs:**
```bash
# macOS
grep CRON /var/log/system.log

# Linux (varies by distribution)
grep CRON /var/log/syslog
# or
journalctl -u cron
```

**Common issues:**

1. **Wrong Python path:**
   - Use `which python3` to find correct path
   - Use absolute path, not relative

2. **Wrong script path:**
   - Use absolute path to `fetch_fact.py`
   - Example: `/home/user/openimpactlab/fetch_fact.py`

3. **Permissions:**
   - Ensure script is executable: `chmod +x fetch_fact.py`
   - Or call with `python3` explicitly

4. **Environment variables:**
   - Cron runs with minimal environment
   - Use full paths for everything
   - If using virtual environment, activate it in the cron command:
     ```bash
     0 * * * * /path/to/venv/bin/python /path/to/fetch_fact.py --quiet
     ```

5. **Output redirection:**
   - Check log file for errors
   - Use `>> logfile.log 2>&1` to capture both stdout and stderr

### Task Scheduler Not Running

**Check task history:**
- Open Task Scheduler
- Find your task
- Click "History" tab
- Look for errors

**Common issues:**

1. **Python path incorrect:**
   - Use full path to `python.exe`
   - Example: `C:\Python39\python.exe`

2. **Script path with spaces:**
   - Wrap in quotes: `"C:\path with spaces\fetch_fact.py" --quiet`

3. **Working directory:**
   - Set "Start in" to the script's directory

4. **User permissions:**
   - Ensure task runs with appropriate user account
   - Check "Run whether user is logged on or not"

5. **Python not in PATH:**
   - Use full path to Python executable
   - Don't rely on PATH environment variable

### Script Runs But No Facts Added

1. **Check for duplicates:**
   - The script skips duplicates silently
   - Run without `--quiet` to see messages

2. **Check archive file:**
   ```bash
   python3 fetch_fact.py --count
   python3 fetch_fact.py --show-archive
   ```

3. **Check network connectivity:**
   - Script needs internet to fetch facts
   - API might be temporarily unavailable

4. **Check log file:**
   - Review log file for error messages
   - Look for network errors or API failures

### Archive File Not Found

The archive file (`facts_archive.json`) is created automatically on first save. If it's missing:

1. **Check current directory:**
   - Script creates archive in current working directory
   - For cron/Task Scheduler, use `--archive-file` with absolute path:
     ```bash
     python3 /path/to/fetch_fact.py --archive-file /path/to/facts_archive.json --quiet
     ```

2. **Permissions:**
   - Ensure script has write permissions in the directory
   - Check directory exists

---

## Best Practices

1. **Use absolute paths** for everything in cron/Task Scheduler
2. **Use `--quiet` flag** to reduce log noise
3. **Redirect output to log file** for debugging
4. **Test manually first** before setting up automation
5. **Start with frequent intervals** (every 15-30 min) for testing, then adjust
6. **Monitor archive growth** periodically:
   ```bash
   python3 fetch_fact.py --count
   ```

---

## Example: Complete Cron Setup

```bash
# 1. Find paths
PYTHON_PATH=$(which python3)
SCRIPT_DIR="/home/user/openimpactlab"
SCRIPT_PATH="$SCRIPT_DIR/fetch_fact.py"
ARCHIVE_FILE="$SCRIPT_DIR/facts_archive.json"
LOG_FILE="$SCRIPT_DIR/facts.log"

# 2. Test script manually
$PYTHON_PATH $SCRIPT_PATH --archive-file $ARCHIVE_FILE --quiet

# 3. Add to crontab (every hour)
crontab -e

# Add this line:
0 * * * * $PYTHON_PATH $SCRIPT_PATH --archive-file $ARCHIVE_FILE --quiet >> $LOG_FILE 2>&1
```

---

## Example: Complete Task Scheduler Setup (PowerShell)

```powershell
# Set variables
$TaskName = "FetchFactsAutomatically"
$PythonPath = "C:\Python39\python.exe"
$ScriptDir = "C:\Users\YourName\openimpactlab"
$ScriptPath = "$ScriptDir\fetch_fact.py"
$ArchiveFile = "$ScriptDir\facts_archive.json"

# Create action
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`" --archive-file `"$ArchiveFile`" --quiet" `
    -WorkingDirectory $ScriptDir

# Create trigger (every hour)
$Trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 365)

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Register task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Automatically fetch and save useless facts"
```

---

## Need Help?

- Check script help: `python3 fetch_fact.py --help`
- View archive: `python3 fetch_fact.py --show-archive`
- Check count: `python3 fetch_fact.py --count`
- Review log files for error messages
