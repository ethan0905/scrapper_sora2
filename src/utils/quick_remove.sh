#!/bin/bash
# Quick script to remove watermark from video(s)
# Usage: 
#   ./quick_remove.sh <video_number>     # Process video_001.mp4
#   ./quick_remove.sh <path/to/video>    # Process specific video
#   ./quick_remove.sh <path/to/folder>   # Process all videos in folder

echo "🎨 Sora Watermark Remover"
echo "========================="
echo ""

# Check if input is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./quick_remove.sh <input> [mode]"
    echo ""
    echo "Input Options:"
    echo "  <number>           - Video number (e.g., 1 for video_001.mp4)"
    echo "  <path/to/video>    - Path to a specific video file"
    echo "  <path/to/folder>   - Path to a folder of videos"
    echo ""
    echo "Examples:"
    echo "  ./quick_remove.sh 1                    # Process video_001.mp4"
    echo "  ./quick_remove.sh videos/my_video.mp4  # Process specific video"
    echo "  ./quick_remove.sh videos/              # Process entire folder"
    echo ""
    echo "Mode (optional):"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  Default: fast (LAMA) - GPU accelerated, recommended for Mac"
        echo "  hq: High quality - CPU only on Mac, VERY SLOW"
    else
        echo "  Default: hq (high quality)"
        echo "  fast: Faster processing"
    fi
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
