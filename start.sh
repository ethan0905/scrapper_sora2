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

# Run the interactive scraper
python3 interactive_scraper.py
