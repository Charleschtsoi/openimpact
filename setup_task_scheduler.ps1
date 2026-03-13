# PowerShell script to set up Windows Task Scheduler for automated fact collection
# Run this script as Administrator

#Requires -RunAsAdministrator

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Task Scheduler Setup for Fact Collection" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-ColorOutput Red "Error: This script must be run as Administrator."
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Find Python executable
Write-Host "Finding Python executable..." -ForegroundColor Yellow

$pythonPaths = @(
    "python.exe",
    "python3.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    "$env:PROGRAMFILES\Python*\python.exe",
    "$env:PROGRAMFILES(X86)\Python*\python.exe"
)

$PythonPath = $null
foreach ($path in $pythonPaths) {
    if ($path -like "*\*") {
        # Wildcard path
        $found = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $PythonPath = $found.FullName
            break
        }
    } else {
        # Direct command
        $found = Get-Command $path -ErrorAction SilentlyContinue
        if ($found) {
            $PythonPath = $found.Source
            break
        }
    }
}

if (-not $PythonPath) {
    Write-ColorOutput Red "Error: Python not found."
    Write-Host "Please install Python 3 or provide the path manually." -ForegroundColor Yellow
    $manualPath = Read-Host "Enter Python executable path (or press Enter to exit)"
    if ($manualPath -and (Test-Path $manualPath)) {
        $PythonPath = $manualPath
    } else {
        exit 1
    }
}

Write-ColorOutput Green "✓ Found Python: $PythonPath"

# Verify Python version
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "  Version: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-ColorOutput Red "Warning: Could not verify Python version"
}

Write-Host ""

# Find script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptPath = Join-Path $ScriptDir "fetch_fact.py"
$ArchiveFile = Join-Path $ScriptDir "facts_archive.json"

Write-Host "Script directory: $ScriptDir" -ForegroundColor Gray
Write-Host "Script path: $ScriptPath" -ForegroundColor Gray
Write-Host ""

# Check if script exists
if (-not (Test-Path $ScriptPath)) {
    Write-ColorOutput Red "Error: fetch_fact.py not found at $ScriptPath"
    exit 1
}

Write-ColorOutput Green "✓ Script found"
Write-Host ""

# Test script
Write-Host "Testing script..." -ForegroundColor Yellow
try {
    $testResult = & $PythonPath $ScriptPath --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "✓ Script is executable"
    } else {
        Write-ColorOutput Red "✗ Error: Script test failed"
        exit 1
    }
} catch {
    Write-ColorOutput Red "✗ Error: Script test failed: $_"
    exit 1
}
Write-Host ""

# Get schedule preference
Write-Host "Select schedule frequency:" -ForegroundColor Cyan
Write-Host "1) Every 15 minutes"
Write-Host "2) Every 30 minutes"
Write-Host "3) Every hour"
Write-Host "4) Every 2 hours"
Write-Host "5) Every 6 hours"
Write-Host "6) Daily at midnight"
Write-Host "7) Daily at 9 AM"
Write-Host ""
$choice = Read-Host "Enter choice [1-7]"

$RepetitionInterval = $null
$RepetitionDuration = [TimeSpan]::FromDays(365)
$StartTime = Get-Date

switch ($choice) {
    "1" {
        $RepetitionInterval = [TimeSpan]::FromMinutes(15)
        $ScheduleDesc = "Every 15 minutes"
    }
    "2" {
        $RepetitionInterval = [TimeSpan]::FromMinutes(30)
        $ScheduleDesc = "Every 30 minutes"
    }
    "3" {
        $RepetitionInterval = [TimeSpan]::FromHours(1)
        $ScheduleDesc = "Every hour"
    }
    "4" {
        $RepetitionInterval = [TimeSpan]::FromHours(2)
        $ScheduleDesc = "Every 2 hours"
    }
    "5" {
        $RepetitionInterval = [TimeSpan]::FromHours(6)
        $ScheduleDesc = "Every 6 hours"
    }
    "6" {
        $StartTime = (Get-Date).Date.AddDays(1)  # Tomorrow at midnight
        $ScheduleDesc = "Daily at midnight"
    }
    "7" {
        $StartTime = (Get-Date).Date.AddHours(9)
        if ($StartTime -lt (Get-Date)) {
            $StartTime = $StartTime.AddDays(1)  # Tomorrow at 9 AM if already past 9 AM today
        }
        $ScheduleDesc = "Daily at 9 AM"
    }
    default {
        Write-ColorOutput Red "Invalid choice"
        exit 1
    }
}

Write-Host ""
Write-Host "Selected schedule: $ScheduleDesc" -ForegroundColor Green
Write-Host ""

# Get task name
$TaskName = Read-Host "Enter task name [default: FetchFactsAutomatically]"
if ([string]::IsNullOrWhiteSpace($TaskName)) {
    $TaskName = "FetchFactsAutomatically"
}

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host ""
    Write-ColorOutput Yellow "Warning: Task '$TaskName' already exists."
    $overwrite = Read-Host "Overwrite existing task? [y/N]"
    if ($overwrite -notmatch "^[Yy]$") {
        Write-Host "Cancelled."
        exit 0
    }
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-ColorOutput Green "✓ Removed existing task"
    Write-Host ""
}

# Build action arguments
$Arguments = "`"$ScriptPath`" --archive-file `"$ArchiveFile`" --quiet"

Write-Host "Task configuration:" -ForegroundColor Cyan
Write-Host "  Task Name: $TaskName"
Write-Host "  Python: $PythonPath"
Write-Host "  Arguments: $Arguments"
Write-Host "  Working Directory: $ScriptDir"
Write-Host "  Schedule: $ScheduleDesc"
Write-Host ""

# Confirm
$confirm = Read-Host "Create this scheduled task? [y/N]"
if ($confirm -notmatch "^[Yy]$") {
    Write-Host "Cancelled."
    exit 0
}

# Create action
Write-Host ""
Write-Host "Creating scheduled task..." -ForegroundColor Yellow

try {
    $Action = New-ScheduledTaskAction `
        -Execute $PythonPath `
        -Argument $Arguments `
        -WorkingDirectory $ScriptDir

    # Create trigger
    if ($RepetitionInterval) {
        $Trigger = New-ScheduledTaskTrigger `
            -Once `
            -At $StartTime `
            -RepetitionInterval $RepetitionInterval `
            -RepetitionDuration $RepetitionDuration
    } else {
        $Trigger = New-ScheduledTaskTrigger `
            -Daily `
            -At $StartTime
    }

    # Create settings
    $Settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable

    # Register task
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description "Automatically fetch and save useless facts from API" `
        -User $env:USERNAME `
        -RunLevel Limited | Out-Null

    Write-ColorOutput Green "✓ Scheduled task created successfully!"
    Write-Host ""

    # Verify
    Write-Host "Verifying task..." -ForegroundColor Yellow
    $createdTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($createdTask) {
        Write-ColorOutput Green "✓ Task verified"
        Write-Host ""
        Write-Host "Task details:" -ForegroundColor Cyan
        Write-Host "  Name: $($createdTask.TaskName)"
        Write-Host "  State: $($createdTask.State)"
        Write-Host "  Next Run Time: $((Get-ScheduledTaskInfo -TaskName $TaskName).NextRunTime)"
    }

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Setup Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Cyan
    Write-Host "  View task:        Get-ScheduledTask -TaskName $TaskName"
    Write-Host "  View task info:   Get-ScheduledTaskInfo -TaskName $TaskName"
    Write-Host "  Run task now:     Start-ScheduledTask -TaskName $TaskName"
    Write-Host "  Disable task:     Disable-ScheduledTask -TaskName $TaskName"
    Write-Host "  Enable task:      Enable-ScheduledTask -TaskName $TaskName"
    Write-Host "  Delete task:      Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
    Write-Host "  Check archive:    & '$PythonPath' '$ScriptPath' --count"
    Write-Host "  View archive:     & '$PythonPath' '$ScriptPath' --show-archive"
    Write-Host ""
    Write-Host "You can also manage the task in Task Scheduler GUI:" -ForegroundColor Yellow
    Write-Host "  Press Win+R, type 'taskschd.msc', press Enter"
    Write-Host ""

} catch {
    Write-ColorOutput Red "Error creating scheduled task: $_"
    exit 1
}
