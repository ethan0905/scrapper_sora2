#!/bin/bash
# Quick script to remove watermark from a video
# Usage: ./quick_remove.sh <video_number> [mode]
# Example: ./quick_remove.sh 1
# Example: ./quick_remove.sh 5 slow

echo "🎨 Sora Watermark Remover - High Quality Mode"
echo "=============================================="
echo ""

# Check if video number is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./quick_remove.sh <video_number>"
    echo ""
    echo "Examples:"
    echo "  ./quick_remove.sh 1        # Remove from video_001.mp4 (high quality mode)"
    echo "  ./quick_remove.sh 5        # Remove from video_005.mp4 (high quality mode)"
    echo ""
    echo "📹 Available videos:"
    ls -1 videos/video_*.mp4 2>/dev/null | head -10 || echo "  No videos found in videos/"
    exit 1
fi

# Check if environment is set up
if [ ! -d "sora-watermark-remover/.venv" ]; then
    echo "⚠️  Environment not set up yet."
    echo "Running setup first..."
    echo ""
    ./setup_watermark_remover.sh
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Please fix the errors and try again."
        exit 1
    fi
    echo ""
fi

# Activate environment and run
echo "🚀 Starting watermark removal..."
echo ""

cd sora-watermark-remover
source .venv/bin/activate
cd ..

python remove_watermark.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✨ All done! Check videos_cleaned/ folder for the result."
else
    echo ""
    echo "❌ Something went wrong. Check the error messages above."
fi

exit $exit_code
