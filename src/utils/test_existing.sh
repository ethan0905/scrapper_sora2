#!/bin/bash
# Quick command to test with existing Chrome

echo "🔗 Testing with existing Chrome session..."
echo ""
echo "Make sure you have Chrome running with remote debugging:"
echo "  ./launch_chrome"
echo ""

python3 test_remix_scraper.py --existing https://sora.chatgpt.com/p/s_6932520ddd548191b4ddede8695d361a
