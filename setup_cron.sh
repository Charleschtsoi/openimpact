#!/bin/bash
#
# Helper script to set up cron job for automated fact collection
# This script will help you configure a cron job to run fetch_fact.py periodically
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Cron Job Setup for Fact Collection"
echo "=========================================="
echo ""

# Find Python executable
echo "Finding Python executable..."
if command -v python3 &> /dev/null; then
    PYTHON_PATH=$(which python3)
    echo -e "${GREEN}✓ Found Python3: $PYTHON_PATH${NC}"
elif command -v python &> /dev/null; then
    PYTHON_PATH=$(which python)
    echo -e "${GREEN}✓ Found Python: $PYTHON_PATH${NC}"
else
    echo -e "${RED}✗ Error: Python not found. Please install Python 3.${NC}"
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON_PATH --version 2>&1)
echo "  Version: $PYTHON_VERSION"
echo ""

# Find script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/fetch_fact.py"
ARCHIVE_FILE="$SCRIPT_DIR/facts_archive.json"
LOG_FILE="$SCRIPT_DIR/facts.log"

echo "Script directory: $SCRIPT_DIR"
echo "Script path: $SCRIPT_PATH"
echo ""

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}✗ Error: fetch_fact.py not found at $SCRIPT_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Script found${NC}"
echo ""

# Test script
echo "Testing script..."
if $PYTHON_PATH "$SCRIPT_PATH" --help &> /dev/null; then
    echo -e "${GREEN}✓ Script is executable${NC}"
else
    echo -e "${RED}✗ Error: Script test failed${NC}"
    exit 1
fi
echo ""

# Get schedule preference
echo "Select schedule frequency:"
echo "1) Every 15 minutes"
echo "2) Every 30 minutes"
echo "3) Every hour"
echo "4) Every 2 hours"
echo "5) Daily at midnight"
echo "6) Daily at 9 AM"
echo "7) Custom (you'll enter cron syntax)"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        CRON_SCHEDULE="*/15 * * * *"
        SCHEDULE_DESC="Every 15 minutes"
        ;;
    2)
        CRON_SCHEDULE="*/30 * * * *"
        SCHEDULE_DESC="Every 30 minutes"
        ;;
    3)
        CRON_SCHEDULE="0 * * * *"
        SCHEDULE_DESC="Every hour"
        ;;
    4)
        CRON_SCHEDULE="0 */2 * * *"
        SCHEDULE_DESC="Every 2 hours"
        ;;
    5)
        CRON_SCHEDULE="0 0 * * *"
        SCHEDULE_DESC="Daily at midnight"
        ;;
    6)
        CRON_SCHEDULE="0 9 * * *"
        SCHEDULE_DESC="Daily at 9 AM"
        ;;
    7)
        echo ""
        echo "Enter custom cron schedule (format: minute hour day month weekday)"
        echo "Examples:"
        echo "  '0 * * * *'     - Every hour"
        echo "  '*/30 * * * *'  - Every 30 minutes"
        echo "  '0 9 * * *'      - Daily at 9 AM"
        read -p "Cron schedule: " CRON_SCHEDULE
        SCHEDULE_DESC="Custom: $CRON_SCHEDULE"
        ;;
    *)
        echo -e "${RED}✗ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "Selected schedule: $SCHEDULE_DESC"
echo "Cron expression: $CRON_SCHEDULE"
echo ""

# Build cron command
CRON_COMMAND="$CRON_SCHEDULE $PYTHON_PATH \"$SCRIPT_PATH\" --archive-file \"$ARCHIVE_FILE\" --quiet >> \"$LOG_FILE\" 2>&1"

echo "Cron command that will be added:"
echo "$CRON_COMMAND"
echo ""

# Confirm
read -p "Add this cron job? [y/N]: " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Add to crontab
echo ""
echo "Adding to crontab..."

# Backup current crontab
CRONTAB_BACKUP="$SCRIPT_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$CRONTAB_BACKUP" 2>/dev/null || true
echo "Backup saved to: $CRONTAB_BACKUP"

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

echo -e "${GREEN}✓ Cron job added successfully!${NC}"
echo ""

# Verify
echo "Verifying crontab..."
echo ""
echo "Current crontab entries:"
crontab -l | grep -E "(fetch_fact|FACT)" || echo "  (No matching entries found)"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "The cron job will run: $SCHEDULE_DESC"
echo ""
echo "Useful commands:"
echo "  View crontab:        crontab -l"
echo "  Edit crontab:        crontab -e"
echo "  Remove cron job:     crontab -e (then delete the line)"
echo "  Check log file:      tail -f $LOG_FILE"
echo "  Check archive count: $PYTHON_PATH $SCRIPT_PATH --count"
echo "  View archive:       $PYTHON_PATH $SCRIPT_PATH --show-archive"
echo ""
echo "Note: Cron jobs run in a minimal environment."
echo "If you encounter issues, check the log file: $LOG_FILE"
echo ""
