#!/bin/bash

# Automated YouTube Upload Scheduler - Startup Script
# This script runs the automated uploader in the background

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
VENV_PATH="$PROJECT_DIR/venv"
PYTHON="$VENV_PATH/bin/python"
UPLOAD_SCRIPT="$PROJECT_DIR/src/utils/auto_uploader.py"
LOG_FILE="$PROJECT_DIR/logs/upload_scheduler.log"

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(cat "$PROJECT_DIR/.env" | xargs)
fi

# Activate virtual environment and run
cd "$PROJECT_DIR"
source "$VENV_PATH/bin/activate"

echo "🚀 Starting automated YouTube uploader..."
echo "📁 Project: $PROJECT_DIR"
echo "📝 Log file: $LOG_FILE"
echo ""

# Run the uploader
$PYTHON "$UPLOAD_SCRIPT" \
    --folder "single-upload" \
    --interval 8 \
    --privacy public \
    --log "$LOG_FILE"
