#!/bin/bash
# Quick test of batch processing feature

echo "🧪 Testing Batch Processing Feature"
echo "===================================="
echo ""

# Check if scraper exists
if [ ! -f "scraper.py" ]; then
    echo "❌ Error: scraper.py not found"
    exit 1
fi

# Show help
echo "📖 Showing help for batch mode:"
python scraper.py --help | grep -A 5 "batch"
echo ""

# Check if test file exists
if [ -f "videos/remix-to-scrape/to-scrape.txt" ]; then
    echo "✅ Found existing URL file: videos/remix-to-scrape/to-scrape.txt"
    URL_COUNT=$(grep -c "^https://" videos/remix-to-scrape/to-scrape.txt)
    echo "   Contains $URL_COUNT URL(s)"
    echo ""
    echo "📝 To run batch processing on this file:"
    echo "   python scraper.py --batch videos/remix-to-scrape/to-scrape.txt --max 50 --slow"
    echo ""
else
    echo "📝 Creating sample URL file..."
    cat > sample_urls.txt << 'EOF'
# Sample URLs for testing batch processing
https://sora.chatgpt.com/p/s_6938eb61aa188191b082c4d8616abefd
https://sora.chatgpt.com/p/s_6934e8bee4a88191a2d2da6cee9fbfd1
https://sora.chatgpt.com/p/s_6939043409248191b8219e5d511ae0fa
EOF
    echo "✅ Created sample_urls.txt"
    echo ""
    echo "📝 To run batch processing:"
    echo "   python scraper.py --batch sample_urls.txt --max 10 --slow"
    echo ""
fi

echo "💡 BATCH PROCESSING EXAMPLES:"
echo "================================"
echo ""
echo "1. Basic batch (default speed):"
echo "   python scraper.py --batch urls.txt --max 20"
echo ""
echo "2. Batch with slow mode (recommended):"
echo "   python scraper.py --batch urls.txt --max 50 --slow"
echo ""
echo "3. Using existing Chrome session:"
echo "   python scraper.py --batch urls.txt --max 100 --use-existing --slow"
echo ""
echo "4. Metadata only:"
echo "   python scraper.py --batch urls.txt --max 50 --metadata-only"
echo ""
echo "📚 For full documentation, see:"
echo "   BATCH_PROCESSING.md"
echo ""
