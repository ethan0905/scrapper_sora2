#!/bin/bash
# Quick validation script to test safety improvements

echo "🔍 Testing Sora Remix Scraper - Safety Validation"
echo "=================================================="
echo ""

# Check if URL provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <sora-video-url>"
    echo "   Example: $0 https://sora.com/p/video-id"
    exit 1
fi

VIDEO_URL="$1"

# Try to find existing Chrome process
CHROME_PID=$(ps aux | grep -i "chrome.*remote-debugging-port=9222" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$CHROME_PID" ]; then
    echo "⚠️  No Chrome with remote debugging found"
    echo "   Please start Chrome with: open -a 'Google Chrome' --args --remote-debugging-port=9222"
    echo ""
    echo "   Or run without --existing flag for new browser instance"
    exit 1
fi

echo "✅ Found Chrome process (PID: $CHROME_PID)"
echo "📍 Testing URL: $VIDEO_URL"
echo ""
echo "👀 Watch for:"
echo "   - Should NEVER navigate to login/auth pages"
echo "   - Should always return to original page after clicking remix"
echo "   - Should stop after max 3 navigation errors"
echo ""
echo "Press Enter to start test..."
read

echo ""
echo "🚀 Running test..."
echo ""

python3 test_remix_scraper.py "$VIDEO_URL" --existing

echo ""
echo "✅ Test complete!"
echo ""
echo "Review the output above for:"
echo "  ✓ Total remixes found"
echo "  ✓ Page origin restored correctly"
echo "  ✓ No navigation errors to login/auth pages"
