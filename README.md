# 🎬 Sora Video Scraper

A powerful Python tool to extract videos and metadata from Sora (ChatGPT). Extract complete video information for building TikTok-like apps, or download videos for archiving.

## ✨ Key Features

- 🎯 **Two scraping modes**: Homepage or user profile
- 📊 **Metadata extraction**: Get creator info, engagement stats, comments, and more (JSON format)
- 📥 **Video download**: Download actual MP4 files
- 🔄 **Virtual scrolling fix**: Collects ALL videos (not just visible ones)
- 🌐 **Chrome session reuse**: Stay logged in between runs (no repeated logins)
- �� **Slow mode**: Random delays to avoid detection
- 🖥️ **Interactive interface**: Beginner-friendly guided setup

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements_selenium.txt
```

### 2. Run interactive mode (Easiest!)

```bash
./start.sh
```

Just answer a few questions and the scraper does the rest!

### 3. Or use direct commands

```bash
# Test with 5 videos from homepage
python scraper_sora_advanced.py --mode home --num-videos 5 --metadata-mode

# Extract metadata from a user profile
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 20 \
  --metadata-mode
```

---

## 📋 Usage Modes

### 🌟 Interactive Mode (Recommended for beginners)

```bash
./start.sh
# Or: python interactive_scraper.py
```

The interactive interface will:
- ✅ Guide you through all options step-by-step
- ✅ Show relevant documentation links
- ✅ Build commands automatically
- ✅ Validate your inputs
- ✅ Run the scraper for you

### ⚡ Command Line Mode (For advanced users)

Full control with CLI flags:

```bash
python scraper_sora_advanced.py [OPTIONS]
```

**Common Options:**
- `--mode home|profile` - Scrape homepage or user profile
- `--profile-url URL` - User profile URL (required for profile mode)
- `--num-videos N` - Number of videos to scrape (default: 10)
- `--all` - Scrape ALL available videos
- `--metadata-mode` - Extract metadata instead of downloading videos
- `--metadata-per-file` - Create one JSON file per video
- `--metadata-output FILE` - Output filename (default: metadata.json)
- `--use-existing-chrome` - Connect to existing Chrome session
- `--slow` - Use slow mode with random delays (5-10s)
- `--delay N` - Delay between scrolls in seconds (default: 2.0)
- `--headless` - Run browser in headless mode
- `--output-dir DIR` - Output directory (default: videos)

**View all options:**
```bash
python scraper_sora_advanced.py --help
```

---

## 📊 Metadata Mode

Extract structured video information without downloading files - perfect for building apps!

### What you get for each video:

```json
{
  "video_id": "abc123",
  "creator": {
    "username": "johndoe",
    "avatar_url": "https://...",
    "profile_url": "https://...",
    "verified": true
  },
  "content": {
    "description": "Amazing sunset over ocean",
    "prompt": "Cinematic shot of golden hour...",
    "title": "Sunset Dreams"
  },
  "engagement": {
    "likes": 1250,
    "comments_count": 45,
    "shares": 89,
    "views": 5600,
    "remixes": 12
  },
  "media": {
    "video_url": "https://...",
    "thumbnail_url": "https://...",
    "duration": "00:05"
  },
  "comments": [
    {
      "author": "user123",
      "author_avatar": "https://...",
      "text": "Great work!",
      "likes": 23,
      "timestamp": "2 hours ago"
    }
  ],
  "metadata": {
    "created_at": "2025-12-05T10:30:00Z",
    "scraped_at": "2025-12-07T14:20:00Z",
    "post_url": "https://..."
  }
}
```

### Use cases:

- 🎬 **TikTok-like apps** - Import complete video data
- 📊 **Analytics dashboards** - Track engagement and trends
- 🔍 **Search engines** - Index descriptions and prompts
- 📈 **Trend analysis** - Monitor popularity over time
- 💾 **Data archiving** - Store info without huge video files

### Examples:

```bash
# Single JSON file with all videos
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 50 \
  --metadata-mode

# One JSON file per video in metadata/ directory
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --metadata-mode \
  --metadata-per-file
```

---

## 🌐 Using Existing Chrome Session

Avoid repeated logins by connecting to an existing Chrome instance:

### Setup (One time):

```bash
# 1. Launch Chrome with remote debugging
./launch_chrome.sh

# 2. Log in to Sora in that Chrome window

# 3. Keep Chrome open
```

### Use the session:

```bash
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --metadata-mode \
  --use-existing-chrome \
  --slow
```

**Benefits:**
- ✅ No repeated logins
- ✅ Faster startup
- ✅ Keep your session active
- ✅ Can run scraper multiple times

---

## 📥 Download Mode

Download actual video files instead of just metadata:

```bash
# Download 20 videos from profile
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 20 \
  --output-dir my_videos

# Download all videos (with slow mode)
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --slow \
  --use-existing-chrome
```

**Output:**
```
videos/
├── video_001.mp4
├── video_002.mp4
├── video_003.mp4
└── ...
```

---

## 🎯 Common Use Cases

### 1. Quick test (5 videos)
```bash
python scraper_sora_advanced.py --mode home --num-videos 5 --metadata-mode
```

### 2. Extract all metadata from a profile
```bash
./launch_chrome.sh  # First time only

python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --metadata-mode \
  --metadata-per-file \
  --use-existing-chrome \
  --slow
```

### 3. Download videos for archiving
```bash
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 50 \
  --use-existing-chrome \
  --slow
```

### 4. Build a video database
```bash
# Extract metadata
python scraper_sora_advanced.py \
  --mode home \
  --all \
  --metadata-mode \
  --metadata-output database.json

# Import to MongoDB
mongoimport --db myapp --collection videos --file database.json --jsonArray
```

---

## 🔧 Troubleshooting

### ❌ Only getting a few videos

The scraper now handles React virtual scrolling correctly. Make sure you're using:
- `--all` flag to scrape everything, OR
- Higher `--num-videos` count

### ❌ Chrome connection failed

If using `--use-existing-chrome`:
1. Make sure Chrome is running with `./launch_chrome.sh`
2. Check if port 9222 is in use: `lsof -ti:9222`
3. Close other Chrome instances

### ❌ "403 Forbidden" or login required

1. Use `--use-existing-chrome` and log in manually
2. Don't use `--headless` mode
3. Use `--slow` mode to avoid detection

### ❌ No videos found

1. Check your profile URL is correct
2. Ensure you're logged in
3. Try increasing `--delay` value
4. Use `--slow` mode

---

## 📁 Project Structure

```
scrapper_sora2/
├── scraper_sora_advanced.py   # Main scraper (use this!)
├── interactive_scraper.py      # Interactive interface
├── start.sh                    # Launch interactive mode
├── launch_chrome.sh            # Launch Chrome with debugging
├── requirements_selenium.txt   # Dependencies
├── README.md                   # This file
├── videos/                     # Downloaded videos (auto-created)
└── metadata/                   # Metadata JSON files (auto-created)
```

---

## 📊 Metadata vs Download Mode

| Feature | Metadata Mode | Download Mode |
|---------|---------------|---------------|
| **Output** | Structured JSON | MP4 video files |
| **Speed** | Fast (no downloads) | Slow (downloads videos) |
| **Storage** | Small (KBs) | Large (GBs) |
| **Data** | Creator, stats, comments | Video files only |
| **Best for** | App development, analytics | Video archiving |
| **Flag** | `--metadata-mode` | (default) |

---

## ⚠️ Best Practices

### Avoid detection:
- ✅ Use `--slow` mode for large scrapes
- ✅ Use `--use-existing-chrome` to reuse sessions
- ✅ Don't scrape too aggressively
- ✅ Respect rate limits

### Efficient scraping:
- ✅ Use `--metadata-mode` if you don't need video files
- ✅ Use `--metadata-per-file` for incremental processing
- ✅ Use `--all` to get everything in one run
- ✅ Keep Chrome session alive for multiple runs

### Data management:
- ✅ Use `--metadata-output` to name your datasets
- ✅ Use `--output-dir` to organize downloads
- ✅ Back up your metadata files
- ✅ Parse JSON with your favorite tools

---

## 🎓 Examples

### Beginner: Just testing
```bash
./start.sh
# Select: Home, 5 videos, Metadata mode
```

### Intermediate: Specific profile
```bash
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 30 \
  --metadata-mode
```

### Advanced: Complete extraction
```bash
# Step 1: Setup (one time)
./launch_chrome.sh
# Log in to Sora

# Step 2: Extract everything
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --metadata-mode \
  --metadata-per-file \
  --use-existing-chrome \
  --slow \
  --delay 3
```

---

## ⚖️ Legal & Ethics

- ✅ Use only for your own content or with permission
- ✅ Respect Sora's Terms of Service
- ✅ Don't redistribute scraped content
- ✅ Don't abuse the service (rate limiting)
- ❌ Don't use for commercial purposes without authorization

---

## 🆘 Getting Help

1. **Read this README** thoroughly
2. **Try interactive mode**: `./start.sh`
3. **Check command help**: `python scraper_sora_advanced.py --help`
4. **Test with small numbers** first (e.g., `--num-videos 5`)
5. **Use `--slow` mode** if having issues

---

## 🎉 What's New

### v2.0 - Metadata Mode & Interactive Interface
- ✨ Complete metadata extraction (creator, engagement, comments)
- 🎮 Interactive CLI for beginners
- 🔄 Virtual scrolling fix (collects ALL videos)
- 🌐 Chrome session reuse
- 🐢 Slow mode for stealth
- 📝 Comprehensive JSON output
- 🎯 One JSON per video option

---

**Happy scraping! 🎬✨**

**Quick start:** `./start.sh`
