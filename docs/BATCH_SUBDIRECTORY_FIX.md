# Batch Subdirectory Fix

## Problem
When running batch mode with multiple URLs, each URL's data was overwriting the previous URL's data because everything was being saved to the same output directory.

## Solution
Modified the scraper to create separate subdirectories for each URL in batch mode:

- **URL 1** → saved to `output_dir/url-1/`
- **URL 2** → saved to `output_dir/url-2/`
- **URL 3** → saved to `output_dir/url-3/`
- etc.

## Changes Made

### 1. Separate Output Directories
Each URL now gets its own subdirectory:
```
remix-batch-2/
├── .batch_progress.json          ← Tracks completed URLs (shared)
├── url-1/                         ← First URL's data
│   ├── .scrape_checkpoint.json
│   ├── remix_0000_start.mp4
│   ├── remix_0000_start_metadata.json
│   ├── remix_0001.mp4
│   ├── remix_0001_metadata.json
│   └── all_remixes_metadata.json
├── url-2/                         ← Second URL's data
│   ├── .scrape_checkpoint.json
│   ├── remix_0000_start.mp4
│   └── ...
└── url-3/                         ← Third URL's data
    └── ...
```

### 2. Progress Tracking
- **Batch progress** (`.batch_progress.json`) - stays at the **base output directory** to track which URLs are completed
- **Checkpoint files** (`.scrape_checkpoint.json`) - stored in **each URL's subdirectory** to track remix progress per URL

### 3. Benefits
✅ **No data loss** - Each URL's data is isolated in its own folder  
✅ **Clear organization** - Easy to see which folder belongs to which URL  
✅ **Resume capability** - Can still resume if interrupted  
✅ **Progress tracking** - Still tracks completed URLs to avoid re-scraping  

## Usage

Same command as before - subdirectories are created automatically:

```bash
# Batch mode - each URL goes to url-1, url-2, url-3, etc.
python scraper.py --batch urls.txt --max 50 --slow --use-existing --output remix-batch-2
```

## Example Output

If you have 3 URLs in your batch file:
```
https://sora.chatgpt.com/p/VIDEO_ID_1
https://sora.chatgpt.com/p/VIDEO_ID_2
https://sora.chatgpt.com/p/VIDEO_ID_3
```

You'll get:
```
remix-batch-2/
├── url-1/  ← 50 remixes from VIDEO_ID_1
├── url-2/  ← 50 remixes from VIDEO_ID_2
└── url-3/  ← 50 remixes from VIDEO_ID_3
```

## Implementation Details

The scraper dynamically updates its output directory for each URL:

```python
# For each URL in batch mode
url_output_dir = base_output_dir / f"url-{idx}"
scraper.output_dir = url_output_dir
scraper.checkpoint_file = url_output_dir / ".scrape_checkpoint.json"
scraper.progress_file = base_progress_file  # Shared across all URLs
```

This ensures:
1. Videos and metadata go to the URL-specific folder
2. Checkpoints are URL-specific (can resume individual URLs)
3. Progress tracking is global (tracks which URLs are done)

---

**Date**: December 12, 2025  
**Status**: ✅ Fixed and tested
