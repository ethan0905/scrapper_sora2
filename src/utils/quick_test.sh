#!/bin/bash
# Quick start script for testing the Sora remix scraper

echo "========================================"
echo "Sora Remix Scraper - Quick Test"
echo "========================================"
echo ""

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./quick_test.sh <sora_video_url>"
    echo ""
    echo "Example:"
    echo "  ./quick_test.sh https://sora.com/p/abcd1234"
    echo ""
    exit 1
fi

VIDEO_URL="$1"

echo "🌐 Video URL: $VIDEO_URL"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import selenium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Selenium not installed. Installing..."
    pip3 install selenium
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Requests not installed. Installing..."
    pip3 install requests
fi

echo ""
echo "🚀 Starting scraper test..."
echo ""

# Check if Chrome is running with remote debugging
if lsof -i :9222 > /dev/null 2>&1; then
    echo "✅ Chrome with remote debugging detected (port 9222)"
    echo "   Using existing Chrome session..."
    echo ""
    # Run with existing Chrome
    python3 test_remix_scraper.py --existing "$VIDEO_URL"
else
    echo "⚠️  No Chrome with remote debugging detected"
    echo "   Opening new browser..."
    echo ""
    # Run with new browser
    python3 test_remix_scraper.py "$VIDEO_URL"
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Test completed successfully!"
else
    echo ""
    echo "❌ Test failed. Check the output above for errors."
    exit 1
fi
