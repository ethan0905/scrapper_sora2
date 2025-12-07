#!/bin/bash

# Check if dependencies are installed

echo "🔍 Checking dependencies..."
echo ""

if python -c "import selenium" 2>/dev/null; then
    echo "✅ selenium - installed"
else
    echo "❌ selenium - MISSING"
    MISSING=1
fi

if python -c "import requests" 2>/dev/null; then
    echo "✅ requests - installed"
else
    echo "❌ requests - MISSING"
    MISSING=1
fi

if python -c "import bs4" 2>/dev/null; then
    echo "✅ beautifulsoup4 - installed"
else
    echo "❌ beautifulsoup4 - MISSING"
    MISSING=1
fi

if python -c "import tqdm" 2>/dev/null; then
    echo "✅ tqdm - installed"
else
    echo "❌ tqdm - MISSING"
    MISSING=1
fi

if python -c "import webdriver_manager" 2>/dev/null; then
    echo "✅ webdriver-manager - installed"
else
    echo "❌ webdriver-manager - MISSING"
    MISSING=1
fi

echo ""

if [ -n "$MISSING" ]; then
    echo "❌ Some dependencies are missing!"
    echo ""
    echo "To install them, run:"
    echo "  pip install -r requirements_selenium.txt"
    echo ""
    exit 1
else
    echo "✅ All dependencies installed!"
    echo "✅ Ready to scrape!"
    echo ""
    exit 0
fi
