# 🎨 Watermark Removal - Quick Start Guide

## 📋 Overview
You have a simple, user-friendly watermark removal system ready to use!

## 🚀 Quick Start (Recommended)

### One-Command Solution

**Process a single video by number:**
```bash
./quick_remove.sh 1
```

**Process a specific video file:**
```bash
./quick_remove.sh videos/my_video.mp4
```

**Process an entire folder:**
```bash
./quick_remove.sh videos/
```

This will:
- Automatically set up the environment (first time only)
- Remove watermark(s) using the **best mode for your system**
- Save cleaned video(s) to `videos_cleaned/`

**📱 Mac Users (Important!):**
- **Default mode: LAMA (fast)** - GPU accelerated, works great on Apple Silicon
- **E2FGVI_HQ mode NOT recommended** - Doesn't support Mac GPU, runs on CPU (extremely slow)
- Stick with the default fast mode for best performance on Mac!

**💻 Linux/Windows Users:**
- **Default mode: E2FGVI_HQ (high quality)** - Time-consistent, no flicker
- Can use fast mode for quicker processing if needed

## 📹 Available Videos
You currently have these videos ready to process:
- video_001.mp4 → video_239.mp4 (and more!)

## 📝 Examples

### Process a single video by number:
```bash
./quick_remove.sh 5
```

### Process a specific video file:
```bash
./quick_remove.sh videos/video_023.mp4
./quick_remove.sh /path/to/any/video.mp4
```

### Process an entire folder:
```bash
# Process all videos in the videos folder
./quick_remove.sh videos/

# Process videos in a custom folder
./quick_remove.sh /path/to/my/videos/
```

### Use fast mode (optional):
```bash
# Single video with fast mode
./quick_remove.sh 1 fast

# Entire folder with fast mode
./quick_remove.sh videos/ fast
```

### List available videos:
```bash
ls -1 videos/video_*.mp4 | head -10
```

### View cleaned videos:
```bash
open videos_cleaned/
```

## 🔄 Batch Processing

Process multiple videos at once by pointing to a folder:

### Process all downloaded videos:
```bash
./quick_remove.sh videos/
```

**Output:**
- Shows progress for each video (e.g., `[1/10] Processing: video_001.mp4`)
- Displays summary at the end (successful vs failed)
- All cleaned videos saved to `videos_cleaned/`

### Process videos from a custom folder:
```bash
./quick_remove.sh /path/to/my/videos/
```

### Supported video formats:
- `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
- Works with both lowercase and uppercase extensions

**Example output:**
```
📁 Found 10 video(s) to process
============================================================

[1/10] Processing: video_001.mp4
------------------------------------------------------------
🎬 Processing: video_001.mp4
✨ Mode: E2FGVI_HQ (High Quality, time-consistent)
...
✅ SUCCESS! Watermark removed!
------------------------------------------------------------

[2/10] Processing: video_002.mp4
...

📊 BATCH PROCESSING COMPLETE
============================================================
✅ Successful: 10/10
❌ Failed: 0/10
💾 Output location: videos_cleaned/
```

## ⚙️ Advanced Usage

### Manual Setup (if needed):
```bash
./setup_watermark_remover.sh
```

### Using Python directly:
```bash
cd sora-watermark-remover
source .venv/bin/activate
cd ..

# Process by video number
python remove_watermark.py 1

# Process specific video file
python remove_watermark.py videos/my_video.mp4

# Process entire folder
python remove_watermark.py videos/

# Fast mode (if you need speed over quality)
python remove_watermark.py videos/ fast
```

## 📂 Directory Structure
```
scrapper_sora2/
├── videos/              # Your downloaded videos
├── videos_cleaned/      # Processed videos (created automatically)
├── quick_remove.sh      # One-command wrapper
├── remove_watermark.py  # Main watermark removal script
└── setup_watermark_remover.sh  # Environment setup script
```

## 🔧 Troubleshooting

### ❌ Processing is extremely slow or fails (Mac users)

**Problem:** E2FGVI_HQ mode doesn't support Apple Silicon GPU (MPS).

**Solution:** Use fast mode instead!
```bash
# Single video
./quick_remove.sh 1 fast

# Entire folder
./quick_remove.sh videos/ fast
```

The fast mode (LAMA) works great on Mac and is GPU-accelerated!

### ⚠️ Warning: "E2FGVI_HQ doesn't support MPS, using CPU"

This is expected on Mac. The script will automatically use fast mode by default on macOS.
If you force high-quality mode on Mac, it will be **very slow** (CPU only).

### If setup fails:
```bash
# Install uv package manager first
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Then run setup again
./setup_watermark_remover.sh
```

### If you get "permission denied":
```bash
chmod +x quick_remove.sh setup_watermark_remover.sh
```

### To check if video exists:
```bash
ls -la videos/video_001.mp4
```

## 💡 Tips

1. **Mac users**: Fast mode (LAMA) is default and recommended - GPU accelerated!
2. **Linux/Windows users**: High quality mode (E2FGVI_HQ) is default
3. **Batch processing** - Process entire folders with one command
4. **Flexible input** - Use video numbers, file paths, or folder paths
5. **Output location**: All cleaned videos go to `videos_cleaned/`
6. **Processing time**: 
   - Fast mode: ~1-2 minutes per video
   - High quality mode: ~5-10 minutes per video (varies by video length)
7. **Supported formats**: MP4, MOV, AVI, MKV, WEBM

## 🎯 Next Steps

1. Run a test on video 1:
   ```bash
   ./quick_remove.sh 1
   ```

2. View the result:
   ```bash
   open videos_cleaned/video_001_cleaned.mp4
   ```

3. If satisfied, process more videos!

---

**Need help?** Check the terminal output for detailed status and error messages.
