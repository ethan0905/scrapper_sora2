#!/bin/bash

# Automated YouTube Uploader - Service Manager
# This script helps you install, start, stop, and monitor the background service

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_SOURCE="$PROJECT_DIR/scripts/com.sora.youtube.uploader.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.sora.youtube.uploader.plist"
SERVICE_NAME="com.sora.youtube.uploader"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     🤖 Automated YouTube Uploader - Service Manager       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_service_status() {
    if launchctl list | grep -q "$SERVICE_NAME"; then
        return 0  # Running
    else
        return 1  # Not running
    fi
}

# Commands

cmd_install() {
    print_info "Installing automated uploader service..."
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$HOME/Library/LaunchAgents"
    
    # Copy plist file
    cp "$PLIST_SOURCE" "$PLIST_DEST"
    print_success "Copied service configuration"
    
    # Load the service
    launchctl load "$PLIST_DEST"
    print_success "Loaded service"
    
    # Start the service
    launchctl start "$SERVICE_NAME"
    print_success "Started service"
    
    echo ""
    print_success "Installation complete!"
    print_info "The uploader will now run automatically and start on boot"
    echo ""
    print_info "Next steps:"
    echo "  1. Add videos to: $PROJECT_DIR/single-upload/"
    echo "  2. Monitor logs: ./scripts/service.sh logs"
    echo "  3. Check status: ./scripts/service.sh status"
}

cmd_uninstall() {
    print_info "Uninstalling automated uploader service..."
    
    # Stop and unload the service
    if check_service_status; then
        launchctl stop "$SERVICE_NAME" 2>/dev/null || true
        launchctl unload "$PLIST_DEST" 2>/dev/null || true
        print_success "Stopped and unloaded service"
    fi
    
    # Remove plist file
    if [ -f "$PLIST_DEST" ]; then
        rm "$PLIST_DEST"
        print_success "Removed service configuration"
    fi
    
    echo ""
    print_success "Uninstallation complete!"
}

cmd_start() {
    if check_service_status; then
        print_warning "Service is already running"
        return
    fi
    
    print_info "Starting service..."
    launchctl load "$PLIST_DEST"
    launchctl start "$SERVICE_NAME"
    sleep 2
    
    if check_service_status; then
        print_success "Service started successfully"
    else
        print_error "Failed to start service"
        exit 1
    fi
}

cmd_stop() {
    if ! check_service_status; then
        print_warning "Service is not running"
        return
    fi
    
    print_info "Stopping service..."
    launchctl stop "$SERVICE_NAME"
    launchctl unload "$PLIST_DEST"
    sleep 2
    
    if ! check_service_status; then
        print_success "Service stopped successfully"
    else
        print_error "Failed to stop service"
        exit 1
    fi
}

cmd_restart() {
    print_info "Restarting service..."
    cmd_stop
    sleep 1
    cmd_start
    print_success "Service restarted"
}

cmd_status() {
    echo ""
    print_header
    
    # Check if service is installed
    if [ ! -f "$PLIST_DEST" ]; then
        print_warning "Service is NOT installed"
        echo ""
        print_info "To install: ./scripts/service.sh install"
        return
    fi
    
    print_success "Service is installed"
    
    # Check if service is running
    if check_service_status; then
        print_success "Service is RUNNING"
        
        # Get PID
        PID=$(launchctl list | grep "$SERVICE_NAME" | awk '{print $1}')
        if [ "$PID" != "-" ]; then
            echo "   PID: $PID"
        fi
    else
        print_error "Service is NOT running"
        echo ""
        print_info "To start: ./scripts/service.sh start"
        return
    fi
    
    # Check for videos
    VIDEO_COUNT=$(find "$PROJECT_DIR/single-upload" -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" -o -name "*.webm" \) | wc -l | tr -d ' ')
    echo ""
    echo "📹 Videos in queue: $VIDEO_COUNT"
    
    # Check upload state
    if [ -f "$PROJECT_DIR/single-upload/.upload_state.json" ]; then
        UPLOADED_COUNT=$(grep -o '"uploaded_videos"' "$PROJECT_DIR/single-upload/.upload_state.json" -A 1000 | grep -o '".mp4"' | wc -l | tr -d ' ')
        echo "✅ Videos uploaded: $UPLOADED_COUNT"
        
        # Get last upload time
        LAST_UPLOAD=$(grep -o '"last_upload_time": "[^"]*"' "$PROJECT_DIR/single-upload/.upload_state.json" | cut -d'"' -f4)
        if [ ! -z "$LAST_UPLOAD" ]; then
            echo "⏰ Last upload: $LAST_UPLOAD"
        else
            echo "⏰ Last upload: Never"
        fi
        
        # Check for consecutive failures
        FAILURES=$(grep -o '"consecutive_failures": [0-9]*' "$PROJECT_DIR/single-upload/.upload_state.json" | grep -o '[0-9]*$' || echo "0")
        if [ "$FAILURES" -gt 0 ]; then
            if [ "$FAILURES" -ge 10 ]; then
                echo ""
                print_error "🛑 CRITICAL: Service stopped due to too many failures!"
                echo "   Consecutive failures: $FAILURES/10"
                LAST_ERROR=$(grep -o '"last_error": "[^"]*"' "$PROJECT_DIR/single-upload/.upload_state.json" | cut -d'"' -f4)
                if [ ! -z "$LAST_ERROR" ]; then
                    echo "   Last error: $LAST_ERROR"
                fi
                echo ""
                print_info "To fix:"
                echo "   1. Check logs: ./scripts/service.sh errors"
                echo "   2. Fix the issue (check YouTube quota, credentials, etc.)"
                echo "   3. Reset failures: ./scripts/service.sh reset-failures"
                echo "   4. Restart service: ./scripts/service.sh restart"
            elif [ "$FAILURES" -ge 7 ]; then
                echo ""
                print_warning "⚠️  Warning: Multiple consecutive failures detected!"
                echo "   Consecutive failures: $FAILURES/10"
                LAST_ERROR=$(grep -o '"last_error": "[^"]*"' "$PROJECT_DIR/single-upload/.upload_state.json" | cut -d'"' -f4)
                if [ ! -z "$LAST_ERROR" ]; then
                    echo "   Last error: $LAST_ERROR"
                fi
                echo "   Check logs: ./scripts/service.sh errors"
            else
                echo "⚠️  Consecutive failures: $FAILURES"
            fi
        fi
    fi
    
    # Check log file
    echo ""
    if [ -f "$PROJECT_DIR/single-upload/upload_scheduler.log" ]; then
        LOG_SIZE=$(ls -lh "$PROJECT_DIR/single-upload/upload_scheduler.log" | awk '{print $5}')
        echo "📋 Log file size: $LOG_SIZE"
        echo ""
        print_info "Recent log entries:"
        echo ""
        tail -n 10 "$PROJECT_DIR/single-upload/upload_scheduler.log" | sed 's/^/   /'
    fi
}

cmd_logs() {
    LOG_FILE="$PROJECT_DIR/single-upload/upload_scheduler.log"
    
    if [ ! -f "$LOG_FILE" ]; then
        print_error "Log file not found: $LOG_FILE"
        exit 1
    fi
    
    print_info "Showing live logs (Ctrl+C to exit)..."
    echo ""
    tail -f "$LOG_FILE"
}

cmd_errors() {
    ERROR_LOG="$PROJECT_DIR/single-upload/uploader_stderr.log"
    
    if [ ! -f "$ERROR_LOG" ]; then
        print_warning "No error log found (service may not have started yet)"
        exit 0
    fi
    
    if [ ! -s "$ERROR_LOG" ]; then
        print_success "No errors! 🎉"
        exit 0
    fi
    
    print_warning "Recent errors:"
    echo ""
    tail -n 50 "$ERROR_LOG"
}

cmd_reset_failures() {
    STATE_FILE="$PROJECT_DIR/single-upload/.upload_state.json"
    
    if [ ! -f "$STATE_FILE" ]; then
        print_warning "No state file found - nothing to reset"
        exit 0
    fi
    
    # Check current failures
    FAILURES=$(grep -o '"consecutive_failures": [0-9]*' "$STATE_FILE" | grep -o '[0-9]*$' || echo "0")
    
    if [ "$FAILURES" -eq 0 ]; then
        print_success "No failures to reset (count is already 0)"
        exit 0
    fi
    
    print_info "Current consecutive failures: $FAILURES"
    echo ""
    print_warning "This will reset the failure counter to 0."
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cancelled"
        exit 0
    fi
    
    # Reset failures in state file
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
state_file = '$STATE_FILE'
try:
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    state['consecutive_failures'] = 0
    state['last_error'] = None
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
except Exception as e:
    print(f'Error: {e}')
    exit(1)
"
        print_success "Failure counter reset successfully"
    else
        # Fallback: use sed
        sed -i '' 's/"consecutive_failures": [0-9]*/"consecutive_failures": 0/' "$STATE_FILE"
        sed -i '' 's/"last_error": "[^"]*"/"last_error": null/' "$STATE_FILE"
        print_success "Failure counter reset successfully"
    fi
    
    echo ""
    print_info "You can now restart the service:"
    echo "  ./scripts/service.sh restart"
}

cmd_help() {
    print_header
    
    echo "Usage: ./scripts/service.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install          Install and start the background service"
    echo "  uninstall        Stop and remove the background service"
    echo "  start            Start the service"
    echo "  stop             Stop the service"
    echo "  restart          Restart the service"
    echo "  status           Show service status and recent activity"
    echo "  logs             Show live logs (Ctrl+C to exit)"
    echo "  errors           Show error log"
    echo "  reset-failures   Reset consecutive failure counter"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/service.sh install   # Set up for the first time"
    echo "  ./scripts/service.sh status    # Check if it's running"
    echo "  ./scripts/service.sh logs      # Watch uploads in real-time"
    echo ""
    echo "Files:"
    echo "  Videos:      $PROJECT_DIR/single-upload/"
    echo "  Logs:        $PROJECT_DIR/single-upload/upload_scheduler.log"
    echo "  State:       $PROJECT_DIR/single-upload/.upload_state.json"
    echo "  Config:      $PLIST_DEST"
}

# Main script
main() {
    case "${1:-}" in
        install)
            print_header
            cmd_install
            ;;
        uninstall)
            print_header
            cmd_uninstall
            ;;
        start)
            print_header
            cmd_start
            ;;
        stop)
            print_header
            cmd_stop
            ;;
        restart)
            print_header
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        logs)
            cmd_logs
            ;;
        errors)
            cmd_errors
            ;;
        reset-failures)
            print_header
            cmd_reset_failures
            ;;
        help|--help|-h|"")
            cmd_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
