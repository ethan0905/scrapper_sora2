# 🎨 Watermark Removal - Quick Start Guide

## 📋 Overview
You have a simple, user-friendly watermark removal system ready to use!

## 🚀 Quick Start (Recommended)

### One-Command Solution
```bash
./quick_remove.sh 1
```
This will:
- Automatically set up the environment (first time only)
- Remove watermark from `video_001.mp4` using **high-quality mode** (E2FGVI_HQ)
- Save cleaned video to `videos_cleaned/video_001_cleaned.mp4`

**Note:** The script now uses the better quality removal mode by default for best results!

## 📹 Available Videos
You currently have these videos ready to process:
- video_001.mp4 → video_239.mp4 (and more!)

## 📝 Examples

### Process a single video (high quality mode):
```bash
./quick_remove.sh 5
```

### Process another video:
```bash
./quick_remove.sh 10
```

### List available videos:
```bash
ls -1 videos/video_*.mp4 | head -10
```

### View cleaned videos:
```bash
open videos_cleaned/
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

# High quality mode (default)
python remove_watermark.py 1

# Fast mode (if you need speed over quality)
python remove_watermark.py 1 fast
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

1. **High quality mode** is now the default for best results
2. **Output location**: All cleaned videos go to `videos_cleaned/`
3. **Processing time**: ~5-10 minutes per video (varies by video length)
4. **Be patient**: Quality takes time, but the results are time-consistent and flicker-free

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
