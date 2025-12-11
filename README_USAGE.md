# Sora Remix Scraper

A robust, production-ready scraper for downloading Sora remix videos and metadata.

## Features

✅ **Load all remixes** - Automatically clicks "Load more" until target count is reached  
✅ **Smart navigation** - Clicks each thumbnail to navigate to full video page  
✅ **Robust downloads** - Downloads videos and extracts metadata from each page  
✅ **Rich metadata** - Extracts description, likes, remixes count, creator profile  
✅ **Comments extraction** - Captures all comments with user info, text, and likes  
✅ **Flexible limits** - Support for custom limits (e.g., 10, 50, 100, 200 remixes)  
✅ **Error recovery** - Avoids stale element errors and handles Chrome disconnections  
✅ **Human-like behavior** - Random delays and scrolling to avoid detection  
✅ **Session support** - Can use existing Chrome session (if you're already logged in)  

## Installation

```bash
# Install required packages
pip install selenium webdriver-manager requests

# Or using requirements.txt
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage (Scrape All Remixes)

```bash
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID
```

This will:
- Launch a new Chrome browser
- Load ALL remixes by clicking "Load more" repeatedly
- Navigate to each remix and download video + metadata
- Save everything to the `videos/` directory

### 2. Limit Number of Remixes

```bash
# Scrape only first 50 remixes
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --max 50

# Scrape only first 10 remixes
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --max 10
```

### 3. Use Existing Chrome Session (Recommended if you need to be logged in)

**Step 1:** Launch Chrome with remote debugging:
```bash
open -a "Google Chrome" --args --remote-debugging-port=9222
```

**Step 2:** Manually log in to Sora in that Chrome window

**Step 3:** Run the scraper:
```bash
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --use-existing
```

### 4. Metadata Only (No Video Downloads)

```bash
# Just extract metadata, don't download videos
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --metadata-only
```

This is useful for:
- Quickly cataloging remixes
- Checking what's available before downloading
- Saving bandwidth

### 5. Custom Output Directory

```bash
# Save to custom directory
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --output my_videos
```

## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `url` | URL of Sora video page with remixes | `https://sora.chatgpt.com/p/VIDEO_ID` |
| `--max N` | Maximum number of remixes to scrape | `--max 50` |
| `--use-existing` | Connect to existing Chrome session | `--use-existing` |
| `--metadata-only` | Only extract metadata, don't download videos | `--metadata-only` |
| `--output DIR` | Output directory for videos and metadata | `--output my_videos` |
| `--debug-port PORT` | Chrome remote debugging port (default: 9222) | `--debug-port 9222` |

## Output Structure

After running the scraper, you'll get:

```
videos/
├── remix_0001.mp4              # First video
├── remix_0001_metadata.json    # Metadata for first video
├── remix_0002.mp4              # Second video
├── remix_0002_metadata.json    # Metadata for second video
├── ...
└── all_remixes_metadata.json   # Combined metadata for all remixes
```

### Metadata Format

Each `remix_XXXX_metadata.json` file contains:

```json
{
  "url": "https://sora.chatgpt.com/p/...",
  "scraped_at": "2024-01-15T10:30:45.123456",
  "title": "Page title",
  "description": "Remix description or prompt",
  "creator": "Creator name",
  "video_url": "https://...",
  "downloaded_file": "videos/remix_0001.mp4"
}
```

The `all_remixes_metadata.json` file contains:

```json
{
  "scraped_at": "2024-01-15T10:30:45.123456",
  "total_remixes": 50,
  "successful_downloads": 48,
  "remixes": [
    { /* remix 1 metadata */ },
    { /* remix 2 metadata */ },
    ...
  ]
}
```

## Common Use Cases

### Download First 100 Remixes
```bash
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --max 100
```

### Quick Metadata Scan
```bash
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --metadata-only --max 10
```

### Use Your Logged-In Session
```bash
# Terminal 1: Launch Chrome with debugging
open -a "Google Chrome" --args --remote-debugging-port=9222

# Terminal 2: Run scraper
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --use-existing --max 200
```

### Save to Specific Directory
```bash
python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --output sora_collection --max 50
```

## How It Works

1. **Setup**: Launches Chrome (or connects to existing session)

2. **Navigate**: Goes to the provided Sora video URL

3. **Load Remixes**: 
   - Finds all remix thumbnail buttons
   - Clicks "Load more" repeatedly until target count or no more remixes
   - Re-fetches buttons before each action to avoid stale elements

4. **Scrape Each Remix**:
   - Clicks each thumbnail button to navigate to full video page
   - Extracts metadata (title, description, creator)
   - Finds and downloads the video file
   - Saves metadata to JSON file
   - Navigates back to main page
   - Random delays between actions (human-like behavior)

5. **Save Results**:
   - Individual video files and metadata
   - Combined metadata file with statistics

## Troubleshooting

### "No remixes found"
- Make sure the URL is correct and has remixes
- Check if you need to be logged in (use `--use-existing`)

### "Could not click 'Load more'"
- The page might be loading slowly - wait a bit and try again
- Check if all remixes are already loaded

### Chrome disconnection errors
- Use `--use-existing` to connect to persistent Chrome session
- Close other Chrome instances that might conflict
- Reduce `--max` value to scrape fewer remixes per session

### Stale element errors
- The scraper already handles this by re-fetching elements
- If it persists, try using `--use-existing` for more stability

### Download failures
- Check your internet connection
- Some videos might have access restrictions
- Try with `--metadata-only` first to see what's available

## Tips for Best Results

1. **Start Small**: Test with `--max 10` before scraping hundreds of remixes

2. **Use Existing Chrome**: More stable for large batches (100+ remixes)
   ```bash
   open -a "Google Chrome" --args --remote-debugging-port=9222
   python sora_remix_scraper.py URL --use-existing --max 200
   ```

3. **Monitor Progress**: Watch the terminal output to see progress

4. **Check Metadata First**: Use `--metadata-only` to preview before downloading

5. **Organize Output**: Use `--output` to separate different scraping sessions

## Advanced Examples

### Scrape Multiple Videos
```bash
# Create separate directories for each video
python sora_remix_scraper.py URL1 --output video1_remixes --max 50
python sora_remix_scraper.py URL2 --output video2_remixes --max 50
```

### Batch Processing
```bash
# Create a script to scrape multiple videos
for url in $(cat video_urls.txt); do
    python sora_remix_scraper.py "$url" --max 100 --use-existing
    sleep 60  # Wait between videos
done
```

### Resume Scraping
If scraping was interrupted, you can continue by checking the last saved file number and adjusting your approach.

## Performance Notes

- **Speed**: ~3-5 seconds per remix (including download)
- **Bandwidth**: Videos are typically 2-10 MB each
- **Memory**: Chrome uses ~500 MB - 1 GB RAM
- **Stability**: Best for batches of 50-100 remixes per session

## Requirements

- Python 3.7+
- Chrome browser
- Internet connection
- ~1 GB free disk space per 100 videos

## Support

For issues or questions:
1. Check the terminal output for error messages
2. Try with `--max 5` to test with small batch
3. Review the "Troubleshooting" section above
4. Check that Chrome and ChromeDriver versions are compatible

## License

This tool is for educational and personal use only. Respect Sora's terms of service and rate limits.
