# Batch Processing Feature

## Overview
Process multiple Sora video URLs from a text file in one run. The scraper will process each URL sequentially, downloading videos and metadata for each.

## Usage

### Basic Batch Processing
```bash
python scraper.py --batch urls.txt --max 50
```

### With Slow Mode (Recommended)
```bash
python scraper.py --batch urls.txt --max 50 --slow
```

### Using Existing Chrome Session
```bash
python scraper.py --batch urls.txt --max 100 --use-existing --slow
```

### Metadata Only
```bash
python scraper.py --batch urls.txt --max 50 --metadata-only --slow
```

## Text File Format

Create a text file (e.g., `urls.txt`) with one URL per line:

```
https://sora.chatgpt.com/p/s_6938eb61aa188191b082c4d8616abefd
https://sora.chatgpt.com/p/s_6934e8bee4a88191a2d2da6cee9fbfd1
https://sora.chatgpt.com/p/s_6939043409248191b8219e5d511ae0fa
https://sora.chatgpt.com/p/s_69399e6368c881918c6c809a975e7339
https://sora.chatgpt.com/p/s_6939c9bded3c81918feddd5b663a7f37
```

### File Format Rules:
- ✅ One URL per line
- ✅ Empty lines are ignored
- ✅ Lines starting with `#` are treated as comments and ignored
- ✅ Leading/trailing whitespace is automatically trimmed

### Example with Comments:
```
# My favorite Sora videos to scrape
https://sora.chatgpt.com/p/s_6938eb61aa188191b082c4d8616abefd

# High priority
https://sora.chatgpt.com/p/s_6934e8bee4a88191a2d2da6cee9fbfd1
https://sora.chatgpt.com/p/s_6939043409248191b8219e5d511ae0fa

# Low priority
https://sora.chatgpt.com/p/s_69399e6368c881918c6c809a975e7339
```

## How It Works

1. **Reads URLs from file** - Loads all valid URLs, ignoring comments and empty lines
2. **Sets up browser once** - Opens Chrome/connects to existing session only once
3. **Processes each URL sequentially**:
   - Navigates to the URL
   - Loads remixes (up to `--max` limit)
   - Downloads videos and metadata
   - Shows progress: `URL 1/20`, `URL 2/20`, etc.
4. **Adds delays between URLs** - If `--slow` mode is enabled, waits 5-8 seconds between URLs
5. **Continues on errors** - If one URL fails, continues to the next one
6. **Closes browser** - Cleans up after all URLs are processed

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--batch FILE` | Path to text file with URLs | `--batch urls.txt` |
| `--max N` | Max remixes per URL | `--max 50` |
| `--slow` | Enable slow mode (recommended) | `--slow` |
| `--use-existing` | Use existing Chrome session | `--use-existing` |
| `--metadata-only` | Skip video downloads | `--metadata-only` |
| `--output DIR` | Output directory | `--output my_videos` |

## Examples

### Example 1: Quick Batch (Default Speed)
```bash
python scraper.py --batch urls.txt --max 20
```

### Example 2: Large Batch with Slow Mode
```bash
python scraper.py --batch urls.txt --max 100 --slow --use-existing
```

### Example 3: Metadata Only for Analysis
```bash
python scraper.py --batch urls.txt --max 50 --metadata-only
```

### Example 4: Custom Output Directory
```bash
python scraper.py --batch urls.txt --max 50 --output batch_output --slow
```

## Output Structure

Each URL gets its own subdirectory based on the video ID:

```
videos/
├── s_6938eb61aa188191b082c4d8616abefd/
│   ├── remix_0000.mp4
│   ├── remix_0000_metadata.json
│   ├── remix_0001.mp4
│   ├── remix_0001_metadata.json
│   └── ...
├── s_6934e8bee4a88191a2d2da6cee9fbfd1/
│   ├── remix_0000.mp4
│   ├── remix_0000_metadata.json
│   └── ...
└── ...
```

## Progress Output

When running in batch mode, you'll see:

```
📄 Reading URLs from: urls.txt
✅ Found 20 URL(s) to process

======================================================================
🎯 PROCESSING URL 1/20
======================================================================
URL: https://sora.chatgpt.com/p/s_6938eb61aa188191b082c4d8616abefd

🌐 Navigating to start URL...
✅ Page loaded

... (normal scraping output) ...

✅ Completed URL 1/20
⏳ Waiting 6.3s before next URL...

======================================================================
🎯 PROCESSING URL 2/20
======================================================================
URL: https://sora.chatgpt.com/p/s_6934e8bee4a88191a2d2da6cee9fbfd1

... (continues for all URLs) ...

======================================================================
🎉 BATCH PROCESSING COMPLETE
======================================================================
Processed 20 URL(s)
```

## Error Handling

- **If one URL fails**: The scraper logs the error and continues to the next URL
- **If the batch file is not found**: Shows error and exits
- **If the file has no valid URLs**: Shows error and exits
- **On Ctrl+C**: Stops gracefully and closes the browser

### Example Error Output:
```
❌ Error processing URL 5/20: Connection timeout
⚠️  Continuing to next URL...

======================================================================
🎯 PROCESSING URL 6/20
======================================================================
```

## Tips for Large Batches

1. **Always use `--slow` mode** - Prevents detection and rate limiting
   ```bash
   python scraper.py --batch urls.txt --max 50 --slow
   ```

2. **Use existing Chrome session** - Stays logged in across all URLs
   ```bash
   python scraper.py --batch urls.txt --max 50 --use-existing --slow
   ```

3. **Start with small batches** - Test with 5-10 URLs first
   ```bash
   python scraper.py --batch test_urls.txt --max 10 --slow
   ```

4. **Monitor progress** - The scraper shows which URL it's currently processing

5. **Use comments in your URL file** - Organize URLs with comments
   ```
   # High priority videos
   https://sora.chatgpt.com/p/s_123...
   
   # Medium priority
   https://sora.chatgpt.com/p/s_456...
   ```

## Comparison: Single vs Batch Mode

### Single URL Mode
```bash
python scraper.py https://sora.chatgpt.com/p/VIDEO_ID --max 50
```
- Process one URL
- No file needed
- Good for quick tests

### Batch Mode
```bash
python scraper.py --batch urls.txt --max 50
```
- Process multiple URLs from a file
- One browser session for all URLs
- Efficient for large-scale scraping
- Progress tracking across URLs

## Creating Your URL File

You can use the file you already have:
```bash
# Use your existing file
python scraper.py --batch videos/remix-to-scrape/to-scrape.txt --max 50 --slow
```

Or create a new one:
```bash
# Create a new URL file
cat > my_urls.txt << EOF
https://sora.chatgpt.com/p/s_6938eb61aa188191b082c4d8616abefd
https://sora.chatgpt.com/p/s_6934e8bee4a88191a2d2da6cee9fbfd1
https://sora.chatgpt.com/p/s_6939043409248191b8219e5d511ae0fa
EOF

# Run the scraper
python scraper.py --batch my_urls.txt --max 50 --slow
```

## Advanced Usage

### Resume Failed URLs
If some URLs fail, create a new file with just those URLs and re-run:

```bash
# Create file with failed URLs
cat > failed_urls.txt << EOF
https://sora.chatgpt.com/p/s_FAILED_1
https://sora.chatgpt.com/p/s_FAILED_2
EOF

# Re-run just the failed ones
python scraper.py --batch failed_urls.txt --max 50 --slow --use-existing
```

### Process Different Batches
Organize URLs into different files:

```bash
# High priority batch
python scraper.py --batch high_priority.txt --max 100 --slow

# Low priority batch (metadata only)
python scraper.py --batch low_priority.txt --max 50 --metadata-only
```
