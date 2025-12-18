#!/bin/bash
# monitor.sh - Real-time scraper monitoring dashboard
# Usage: ./scripts/monitor.sh [refresh_seconds]

REFRESH_INTERVAL=${1:-5}  # Default 5 seconds
PROJECT_DIR="${HOME}/scrapper_sora2"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

while true; do
    clear
    echo "========================================"
    echo "🎬 SORA SCRAPER - LIVE MONITORING"
    echo "========================================"
    echo ""
    echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Check if scraper is running
    if pgrep -f "main.py.*--batch" > /dev/null; then
        echo -e "${GREEN}✅ Scraper Status: RUNNING${NC}"
        SCRAPER_PID=$(pgrep -f "main.py.*--batch")
        echo "   PID: $SCRAPER_PID"
        
        # CPU and Memory usage
        if [ ! -z "$SCRAPER_PID" ]; then
            PS_INFO=$(ps -p $SCRAPER_PID -o %cpu,%mem,etime,cmd --no-headers 2>/dev/null)
            if [ ! -z "$PS_INFO" ]; then
                CPU=$(echo $PS_INFO | awk '{print $1}')
                MEM=$(echo $PS_INFO | awk '{print $2}')
                TIME=$(echo $PS_INFO | awk '{print $3}')
                echo "   CPU: ${CPU}% | RAM: ${MEM}% | Runtime: $TIME"
            fi
        fi
    else
        echo -e "${RED}❌ Scraper Status: NOT RUNNING${NC}"
        echo "   Start with: screen -S scraper"
        echo "   cd ~/scrapper_sora2 && source venv/bin/activate"
        echo "   python main.py --batch batch_urls.txt --max 999 --slow --use-existing"
    fi
    
    echo ""
    echo "──────────────────────────────────────"
    
    # Chrome status
    if pgrep -f "chrome.*remote-debugging-port" > /dev/null; then
        echo -e "${GREEN}✅ Chrome: RUNNING${NC}"
        CHROME_PID=$(pgrep -f "chrome.*remote-debugging-port" | head -1)
        echo "   PID: $CHROME_PID"
        echo "   Debug port: 9222"
    else
        echo -e "${RED}❌ Chrome: NOT RUNNING${NC}"
        echo "   Start with: google-chrome --remote-debugging-port=9222 --user-data-dir=\"\$HOME/.chrome-profile\" &"
    fi
    
    echo ""
    echo "──────────────────────────────────────"
    
    # Videos downloaded
    VIDEO_COUNT=$(find "$PROJECT_DIR/videos_batch" -name "*.mp4" 2>/dev/null | wc -l)
    echo -e "${BLUE}📹 Videos Downloaded: $VIDEO_COUNT${NC}"
    
    # Latest video
    if [ -d "$PROJECT_DIR/videos_batch" ]; then
        LATEST=$(ls -t "$PROJECT_DIR/videos_batch"/*.mp4 2>/dev/null | head -1)
        if [ ! -z "$LATEST" ]; then
            LATEST_NAME=$(basename "$LATEST")
            LATEST_SIZE=$(du -h "$LATEST" | cut -f1)
            LATEST_TIME=$(stat -f "%Sm" -t "%H:%M:%S" "$LATEST" 2>/dev/null || stat -c "%y" "$LATEST" 2>/dev/null | cut -d' ' -f2 | cut -d. -f1)
            echo "   Latest: $LATEST_NAME ($LATEST_SIZE)"
            echo "   Time: $LATEST_TIME"
        fi
    fi
    
    echo ""
    echo "──────────────────────────────────────"
    
    # Disk usage
    if [ -d "$PROJECT_DIR" ]; then
        DISK_USAGE=$(du -sh "$PROJECT_DIR/videos_batch" 2>/dev/null | cut -f1)
        echo -e "${YELLOW}💾 Storage Used: $DISK_USAGE${NC}"
    fi
    
    # Total disk
    DISK_INFO=$(df -h "$PROJECT_DIR" 2>/dev/null | tail -1)
    if [ ! -z "$DISK_INFO" ]; then
        DISK_TOTAL=$(echo $DISK_INFO | awk '{print $2}')
        DISK_USED=$(echo $DISK_INFO | awk '{print $3}')
        DISK_AVAIL=$(echo $DISK_INFO | awk '{print $4}')
        DISK_PERCENT=$(echo $DISK_INFO | awk '{print $5}')
        echo "   Total: $DISK_USED / $DISK_TOTAL ($DISK_PERCENT full)"
        echo "   Available: $DISK_AVAIL"
    fi
    
    echo ""
    echo "──────────────────────────────────────"
    
    # System resources
    echo "🖥️  System Resources:"
    
    # Memory
    if command -v free &> /dev/null; then
        MEM_INFO=$(free -h | grep Mem)
        MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
        MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
        MEM_PERCENT=$(free | grep Mem | awk '{printf "%.0f", ($3/$2) * 100}')
        echo "   RAM: $MEM_USED / $MEM_TOTAL (${MEM_PERCENT}%)"
    fi
    
    # CPU Load
    if [ -f /proc/loadavg ]; then
        LOAD=$(cat /proc/loadavg | awk '{print $1, $2, $3}')
        echo "   Load: $LOAD (1m, 5m, 15m)"
    fi
    
    echo ""
    echo "──────────────────────────────────────"
    
    # Recent log entries
    echo "📋 Recent Activity (last 5 lines):"
    if [ -f "$PROJECT_DIR/logs/scraper.log" ]; then
        tail -5 "$PROJECT_DIR/logs/scraper.log" 2>/dev/null | while read line; do
            echo "   $line"
        done
    else
        echo "   No logs yet"
    fi
    
    echo ""
    echo "──────────────────────────────────────"
    echo "Press Ctrl+C to exit | Refresh: ${REFRESH_INTERVAL}s"
    echo "========================================"
    
    sleep $REFRESH_INTERVAL
done
