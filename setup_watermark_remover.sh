#!/bin/bash
# Setup script for Sora Watermark Remover

echo "🔧 Setting up Sora Watermark Remover..."
echo ""

# Check if we're in the right directory
if [ ! -d "sora-watermark-remover" ]; then
    echo "❌ Error: sora-watermark-remover directory not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Navigate to the watermark remover directory
cd sora-watermark-remover

echo "📦 Installing dependencies with uv..."
echo "This may take a few minutes..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  'uv' package manager not found."
    echo "Installing uv first..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Sync dependencies
uv sync

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "📝 Quick Start Guide:"
    echo "===================="
    echo ""
    echo "1. Activate the environment:"
    echo "   cd sora-watermark-remover && source .venv/bin/activate && cd .."
    echo ""
    echo "2. Remove watermark from a video:"
    echo "   python remove_watermark.py 1        # Process video_001.mp4 (fast mode)"
    echo "   python remove_watermark.py 5 slow   # Process video_005.mp4 (slow but better)"
    echo ""
    echo "3. View results:"
    echo "   open videos_cleaned/"
    echo ""
    echo "💡 Tip: The first run will download AI models (~200MB), please be patient!"
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi
