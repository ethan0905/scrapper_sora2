#!/bin/bash

# Simple launcher for the interactive scraper

echo "🚀 Starting Sora Scraper - Interactive Mode"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python 3 first"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
if ! python3 -c "import selenium, requests, bs4, tqdm, webdriver_manager" 2>/dev/null; then
    echo ""
    echo "❌ Missing dependencies! Installing..."
    echo ""
    pip3 install -r requirements_selenium.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Failed to install dependencies"
        echo "   Please run manually: pip3 install -r requirements_selenium.txt"
        exit 1
    fi
    echo ""
    echo "✅ Dependencies installed!"
fi
echo "✅ All dependencies ready!"
echo ""

# Run the interactive scraper
python3 interactive_scraper.py
