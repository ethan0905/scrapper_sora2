#!/bin/bash
# Quick test script for systematic remix navigation
# Uses existing Chrome by default!

echo "🧪 Testing Systematic Remix Navigation"
echo "========================================"
echo ""

# Check if URL provided
if [ -z "$1" ]; then
    echo "Usage: $0 <sora-video-url>"
    echo ""
    echo "Example:"
    echo "  $0 https://sora.com/p/video-id"
    echo ""
    echo "Note: Uses existing Chrome by default!"
    echo "To start new browser: $0 <url> --new"
    exit 1
fi

VIDEO_URL="$1"
shift  # Remove first argument, keep others

# Check for existing Chrome
CHROME_PID=$(ps aux | grep -i "chrome.*remote-debugging-port=9222" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$CHROME_PID" ]; then
    echo "❌ No Chrome with remote debugging found!"
    echo ""
    echo "Please start Chrome first:"
    echo "  open -a 'Google Chrome' --args --remote-debugging-port=9222"
    echo ""
    echo "Then:"
    echo "  1. Log in to Sora in that Chrome window"
    echo "  2. Navigate to the video page"
    echo "  3. Run this script again"
    echo ""
    exit 1
else
    echo "✅ Found Chrome (PID: $CHROME_PID)"
    echo ""
fi

echo "🚀 Running navigation test..."
echo ""

python3 test_navigate_remix.py "$VIDEO_URL" "$@"

echo ""
echo "✅ Test complete!"
