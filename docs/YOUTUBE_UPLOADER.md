# 📺 YouTube Auto-Uploader Guide

## Overview

The YouTube Auto-Uploader monitors a source folder for videos and automatically uploads them to YouTube. Once uploaded, videos are moved to a destination folder.

## Features

- ✅ **Automatic upload** - Drop videos in a folder and they're uploaded
- ✅ **Watch mode** - Continuously monitor for new videos
- ✅ **Organized** - Uploaded videos moved to separate folder
- ✅ **Upload tracking** - Never upload the same video twice
- ✅ **Customizable** - Set title, description, privacy per video
- ✅ **Progress display** - See upload progress in real-time

## Setup (One-time)

### 1. Install Dependencies

```bash
pip install -r requirements_youtube.txt
```

### 2. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**:
   - Click "Enable APIs and Services"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "Credentials" tab
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: **Desktop app**
   - Name it (e.g., "Sora Video Uploader")
   - Click "Create"
5. Download credentials:
   - Click the download button (⬇️) next to your OAuth client
   - Save as `youtube_credentials.json` in project root

### 3. First Run - Authorization

The first time you run the uploader:

```bash
python -m src.youtube_uploader.uploader \
    --source videos/to-upload \
    --dest videos/uploaded
```

It will:
1. Open your browser automatically
2. Ask you to log into your YouTube account
3. Request permission to upload videos
4. Save the authorization for future use

**Note:** You only need to do this once! The token is saved in `youtube_token.json`.

## Usage

### Basic Upload (One-time)

Upload all videos in a folder once:

```bash
python -m src.youtube_uploader.uploader \
    --source videos/to-upload \
    --dest videos/uploaded
```

### Watch Mode (Recommended)

Continuously monitor folder and upload new videos:

```bash
python -m src.youtube_uploader.uploader \
    --source videos/to-upload \
    --dest videos/uploaded \
    --watch
```

The uploader will:
- Check for new videos every 60 seconds
- Upload any new videos found
- Move uploaded videos to destination folder
- Keep running until you press Ctrl+C

### Custom Settings

```bash
python -m src.youtube_uploader.uploader \
    --source videos/to-upload \
    --dest videos/uploaded \
    --watch \
    --privacy unlisted \
    --title "My Sora Video" \
    --description "Created with Sora AI" \
    --interval 120
```

## Command Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--source DIR` | Folder to monitor for videos | Required | `--source videos/scraped` |
| `--dest DIR` | Destination for uploaded videos | Required | `--dest videos/uploaded` |
| `--watch` | Enable watch mode | Disabled | `--watch` |
| `--interval N` | Check interval in seconds | 60 | `--interval 120` |
| `--privacy` | Privacy status | `private` | `--privacy unlisted` |
| `--title` | Default video title | "Sora Video" | `--title "My Video"` |
| `--description` | Default description | "Video created..." | `--description "..."` |
| `--credentials` | Path to credentials JSON | `youtube_credentials.json` | `--credentials path/to/creds.json` |

### Privacy Options

- `public` - Anyone can find and watch
- `unlisted` - Anyone with link can watch (not searchable)
- `private` - Only you can watch

## Workflow Examples

### Example 1: Scrape + Upload Pipeline

```bash
# Terminal 1: Scrape videos
python main.py --batch urls.txt --max 50 --use-existing --output videos/scraped

# Terminal 2: Auto-upload (watch mode)
python -m src.youtube_uploader.uploader \
    --source videos/scraped/url-1 \
    --dest videos/uploaded \
    --watch \
    --privacy unlisted
```

### Example 2: Batch Upload Multiple Folders

```bash
# Upload from url-1
python -m src.youtube_uploader.uploader \
    --source videos/scraped/url-1 \
    --dest videos/uploaded/batch-1

# Upload from url-2
python -m src.youtube_uploader.uploader \
    --source videos/scraped/url-2 \
    --dest videos/uploaded/batch-2
```

### Example 3: Background Upload

```bash
# Run in background with nohup
nohup python -m src.youtube_uploader.uploader \
    --source videos/to-upload \
    --dest videos/uploaded \
    --watch \
    --privacy unlisted \
    > upload.log 2>&1 &

# Check progress
tail -f upload.log

# Stop background process
ps aux | grep uploader  # Find process ID
kill <PID>
```

## File Structure

After running the uploader:

```
project/
├── youtube_credentials.json      # Your API credentials (DO NOT COMMIT!)
├── youtube_token.json            # Authorization token (auto-generated)
│
├── videos/
│   ├── to-upload/                # Source folder
│   │   ├── video1.mp4           # Waiting to upload
│   │   └── video2.mp4
│   │
│   └── uploaded/                 # Destination folder
│       ├── .upload_log.json     # Upload history
│       ├── video1.mp4           # Already uploaded
│       └── video2.mp4
```

## Upload Log

The uploader maintains a log of all uploads in `.upload_log.json`:

```json
{
  "uploads": [
    {
      "file": "/path/to/video1.mp4",
      "video_id": "dQw4w9WgXcQ",
      "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "uploaded_at": "2025-12-14T00:00:00"
    }
  ]
}
```

This ensures:
- Videos are never uploaded twice
- You have a record of all uploads
- Easy to track which videos are on YouTube

## Troubleshooting

### "Credentials file not found"

**Solution:** Make sure `youtube_credentials.json` is in the project root.

### "Authentication failed"

**Solutions:**
1. Delete `youtube_token.json` and re-authenticate
2. Check that OAuth client is for "Desktop app" (not "Web app")
3. Make sure YouTube Data API v3 is enabled in Google Cloud Console

### "Upload failed: quota exceeded"

YouTube has daily upload quotas. **Solutions:**
- Wait 24 hours for quota to reset
- Request quota increase in Google Cloud Console
- Use multiple YouTube accounts with different credentials

### "Video already uploaded"

The uploader tracks uploaded videos to avoid duplicates. To re-upload:
1. Edit `.upload_log.json` and remove the entry
2. OR delete `.upload_log.json` to reset all history

## Best Practices

### 1. Use Watch Mode for Continuous Scraping

```bash
# Terminal 1: Scrape continuously
python main.py --batch urls.txt --slow --use-existing --output videos/scraped

# Terminal 2: Upload continuously
python -m src.youtube_uploader.uploader \
    --source videos/scraped \
    --dest videos/uploaded \
    --watch
```

### 2. Start with Private/Unlisted

Always start with `--privacy private` or `--privacy unlisted` to test before making videos public.

### 3. Organize by Batches

```bash
# Scrape batch 1
python main.py --batch batch1-urls.txt --output videos/batch1

# Upload batch 1
python -m src.youtube_uploader.uploader \
    --source videos/batch1 \
    --dest videos/uploaded/batch1 \
    --watch
```

### 4. Monitor the Logs

```bash
# Run with logging
python -m src.youtube_uploader.uploader \
    --source videos/to-upload \
    --dest videos/uploaded \
    --watch \
    2>&1 | tee upload.log
```

## Security Notes

⚠️ **IMPORTANT:**

1. **Never commit credentials** - `youtube_credentials.json` and `youtube_token.json` are in `.gitignore`
2. **Keep credentials private** - Anyone with these files can upload to your YouTube account
3. **Review uploads** - Always check your YouTube channel to verify uploads

## Quota Limits

YouTube API has these limits (as of 2025):

- **Upload quota:** ~6 uploads per day per project (10,000 quota units)
- **Total quota:** 10,000 units per day
- **Reset:** Daily at midnight Pacific Time

To increase quota:
1. Go to Google Cloud Console → APIs & Services → Quotas
2. Request quota increase
3. Explain your use case
4. Usually approved within 24-48 hours

## FAQ

**Q: Can I upload to multiple YouTube channels?**  
A: Yes! Use different credentials files:
```bash
--credentials channel1_creds.json  # For channel 1
--credentials channel2_creds.json  # For channel 2
```

**Q: Can I customize title/description per video?**  
A: Currently, all videos use the default title/description. You can modify the uploader code to read metadata from JSON files.

**Q: What video formats are supported?**  
A: All formats YouTube supports: MP4, MOV, AVI, MKV, FLV, WMV, WEBM

**Q: Can I schedule uploads?**  
A: Not directly, but you can use cron (Linux/Mac) or Task Scheduler (Windows) to run the uploader at specific times.

---

**Made with ❤️ for the Sora community**
