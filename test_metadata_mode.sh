#!/bin/bash

# Test script for metadata extraction mode
# This script demonstrates the new metadata mode functionality

echo "🧪 TEST METADATA MODE"
echo "===================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Basic metadata extraction (home page, 5 videos, single JSON)
echo -e "${BLUE}Test 1: Basic metadata extraction (5 videos from home)${NC}"
echo "Command: python scraper_sora_advanced.py --mode home --num-videos 5 --metadata-mode"
echo ""
read -p "Press ENTER to run this test, or Ctrl+C to skip..."
python scraper_sora_advanced.py --mode home --num-videos 5 --metadata-mode

if [ -f "metadata.json" ]; then
    echo -e "${GREEN}✅ Test 1 passed: metadata.json created${NC}"
    echo "Preview:"
    head -20 metadata.json
    echo "..."
    echo ""
else
    echo -e "${YELLOW}⚠️  Test 1: No metadata.json found${NC}"
fi

echo ""
echo "---"
echo ""

# Test 2: Metadata with separate files per video
echo -e "${BLUE}Test 2: Metadata extraction with separate files${NC}"
echo "Command: python scraper_sora_advanced.py --mode home --num-videos 3 --metadata-mode --metadata-per-file --output-dir test_metadata"
echo ""
read -p "Press ENTER to run this test, or Ctrl+C to skip..."
python scraper_sora_advanced.py --mode home --num-videos 3 --metadata-mode --metadata-per-file --output-dir test_metadata

if [ -d "test_metadata" ]; then
    echo -e "${GREEN}✅ Test 2 passed: test_metadata/ directory created${NC}"
    echo "Files created:"
    ls -lh test_metadata/
    echo ""
    echo "Sample JSON file:"
    head -30 test_metadata/*.json | head -30
    echo "..."
    echo ""
else
    echo -e "${YELLOW}⚠️  Test 2: No test_metadata/ directory found${NC}"
fi

echo ""
echo "---"
echo ""

# Test 3: Profile metadata extraction (requires URL input)
echo -e "${BLUE}Test 3: Profile metadata extraction${NC}"
echo "This test requires a valid Sora profile URL."
echo ""
read -p "Enter a Sora profile URL (or press ENTER to skip): " PROFILE_URL

if [ -n "$PROFILE_URL" ]; then
    echo "Command: python scraper_sora_advanced.py --mode profile --profile-url \"$PROFILE_URL\" --num-videos 5 --metadata-mode --metadata-output profile_metadata.json"
    echo ""
    read -p "Press ENTER to run this test, or Ctrl+C to skip..."
    python scraper_sora_advanced.py --mode profile --profile-url "$PROFILE_URL" --num-videos 5 --metadata-mode --metadata-output profile_metadata.json
    
    if [ -f "profile_metadata.json" ]; then
        echo -e "${GREEN}✅ Test 3 passed: profile_metadata.json created${NC}"
        echo "Preview:"
        head -30 profile_metadata.json
        echo "..."
        echo ""
    else
        echo -e "${YELLOW}⚠️  Test 3: No profile_metadata.json found${NC}"
    fi
else
    echo "Skipping Test 3"
fi

echo ""
echo "---"
echo ""

# Test 4: With existing Chrome session (if available)
echo -e "${BLUE}Test 4: Metadata with existing Chrome session${NC}"
echo "This test uses --use-existing-chrome flag."
echo ""
echo "⚠️  Make sure Chrome is running with remote debugging:"
echo "   ./launch_chrome.sh"
echo ""
read -p "Is Chrome running with remote debugging? (y/n): " CHROME_READY

if [ "$CHROME_READY" = "y" ] || [ "$CHROME_READY" = "Y" ]; then
    echo "Command: python scraper_sora_advanced.py --mode home --num-videos 3 --metadata-mode --use-existing-chrome --metadata-output chrome_session_metadata.json"
    echo ""
    read -p "Press ENTER to run this test, or Ctrl+C to skip..."
    python scraper_sora_advanced.py --mode home --num-videos 3 --metadata-mode --use-existing-chrome --metadata-output chrome_session_metadata.json
    
    if [ -f "chrome_session_metadata.json" ]; then
        echo -e "${GREEN}✅ Test 4 passed: chrome_session_metadata.json created${NC}"
        echo "Preview:"
        head -30 chrome_session_metadata.json
        echo "..."
        echo ""
    else
        echo -e "${YELLOW}⚠️  Test 4: No chrome_session_metadata.json found${NC}"
    fi
else
    echo "Skipping Test 4"
fi

echo ""
echo "---"
echo ""

# Summary
echo "🎉 TESTS COMPLETE"
echo "================"
echo ""
echo "Generated files:"
ls -lh *.json 2>/dev/null | grep -E "(metadata|chrome_session)" || echo "No JSON files found"
echo ""
ls -lh test_metadata/*.json 2>/dev/null || echo "No test_metadata files found"
echo ""
echo "✅ All tests completed!"
echo ""
echo "📖 Next steps:"
echo "   1. Review the generated JSON files"
echo "   2. Check METADATA_MODE.md for usage examples"
echo "   3. Try importing the data into your app"
echo ""
echo "💡 To extract metadata from a specific profile:"
echo "   python scraper_sora_advanced.py --mode profile --profile-url 'URL' --num-videos 20 --metadata-mode"
echo ""
