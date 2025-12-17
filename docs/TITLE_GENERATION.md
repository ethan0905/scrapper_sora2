# YouTube Title Generation Guide

This guide explains how to generate engaging, SEO-friendly titles for your Sora AI videos before uploading to YouTube.

## Overview

The title generator analyzes your video metadata (descriptions, comments, reactions) to create catchy, descriptive titles that:
- 📝 **Describe the content** - Uses AI to understand what's happening
- 🎯 **Grab attention** - Includes power words and emojis
- 🔍 **Optimize for search** - Includes relevant keywords
- ✨ **Stand out** - Makes viewers want to click

## Quick Start

### Generate Titles for a Single Video

```bash
python src/utils/title_generator.py "path/to/video/remix_0001_metadata.json"
```

**Example output:**
```
Generated Title:
Epic Gorilla Escape Caught on Camera 🦍
```

### Generate Titles for All Videos in a Folder

```bash
python src/utils/title_generator.py "videos/remix-batch-3/" -o titles.json
```

This will:
1. Find all `*_metadata.json` files in the folder
2. Generate a title for each video
3. Save the mapping to `titles.json`

### Upload with Auto-Generated Titles

Use the smart uploader to automatically generate titles during upload:

```bash
# Upload a single video
python src/utils/smart_uploader.py "videos/remix-batch-3/url-1/remix_0001.mp4"

# Upload an entire folder
python src/utils/smart_uploader.py "videos/remix-batch-3/" --privacy public
```

## Title Generation Options

### Add Emojis (Default: On)

Emojis make titles more eye-catching:

```bash
python src/utils/title_generator.py "metadata.json"
# Output: Epic Gorilla Escape 🦍
```

Disable emojis:
```bash
python src/utils/title_generator.py "metadata.json" --no-emoji
# Output: Epic Gorilla Escape
```

### Add Hashtags

Add `#SoraAI` hashtag to titles:

```bash
python src/utils/title_generator.py "metadata.json" --hashtag
# Output: Epic Gorilla Escape 🦍 #SoraAI
```

### Control Title Length

YouTube's title limit is 100 characters. The generator respects this by default:

```bash
python src/utils/title_generator.py "metadata.json" --max-length 80
```

## How Title Generation Works

### 1. Metadata Analysis

The generator analyzes your scraped metadata:

```json
{
  "description": "Follow @mr.computerslop for more slop",
  "comments": [
    {"comment_text": "GORILLA IS FREEEEEEE"},
    {"comment_text": "bro's still going after the glass broke"}
  ],
  "likes": 466,
  "creator": "mr.computerslop"
}
```

### 2. Context Extraction

It extracts key information:
- **Subjects**: gorilla, robot, person, etc.
- **Actions**: break, escape, dance, etc.
- **Objects**: glass, rope, car, etc.
- **Sentiment**: funny, epic, crazy, shocking

### 3. Title Construction

Based on context, it creates targeted titles:

**Scenario: Gorilla + Glass + Break**
```
→ "Gorilla Smashes Through Glass Wall 🦍"
```

**Scenario: Robot + Dance**
```
→ "Robot Busts Incredible Dance Moves 🤖"
```

**Scenario: Epic + Crazy reactions**
```
→ "Epic [Subject] Does Something Unbelievable ⚡"
```

## Title Examples

Here are real examples from scraped videos:

| Video Content | Generated Title |
|--------------|----------------|
| Gorilla breaks glass | `Gorilla Smashes Through Glass Wall 🦍` |
| Robot dancing | `Robot Busts Incredible Dance Moves 🤖` |
| Car chase | `Epic Car Chase Gone Wrong 🚗` |
| Funny animal | `Hilarious Animal Does the Unexpected 😂` |
| Generic video | `Amazing Sora AI Generated Video ✨` |

## Smart Uploader Integration

The smart uploader combines title generation with YouTube uploading:

### Upload Single Video with Auto-Title

```bash
python src/utils/smart_uploader.py "videos/remix_0001.mp4" \
  --privacy public \
  --credentials youtube_credentials.json
```

**What happens:**
1. ✅ Loads `remix_0001_metadata.json`
2. ✅ Generates engaging title from metadata
3. ✅ Creates description from video info
4. ✅ Uploads to YouTube with auto-generated content

### Batch Upload with Auto-Titles

```bash
python src/utils/smart_uploader.py "videos/remix-batch-3/" \
  --privacy public
```

**Features:**
- 📊 Progress tracking
- ⏭️ Skips already uploaded videos
- 📝 Logs all uploads
- 🔄 Automatic retry on failure
- 📈 Summary statistics

### Smart Uploader Options

```bash
# Privacy settings
--privacy public|unlisted|private

# Made for kids
--kids

# Disable emojis in titles
--no-emoji

# Disable hashtags
--no-hashtag

# Force re-upload
--force

# Custom credentials
--credentials path/to/credentials.json
```

## Advanced Usage

### Custom Title Templates

Edit `src/utils/title_generator.py` to add custom scenarios:

```python
def _generate_from_comments(self, context: Dict) -> str:
    # Add your custom scenario
    if 'dragon' in context['subjects']:
        if 'fly' in context['actions']:
            return "Dragon Takes Flight in Epic Scene"
    
    # ... rest of the logic
```

### Batch Processing

Process multiple batches at once:

```bash
# Generate titles for all batches
for batch in videos/remix-batch-*/; do
    python src/utils/title_generator.py "$batch" -o "${batch}/titles.json"
done
```

### Integration with Your Workflow

1. **Scrape videos** → metadata JSON files created
2. **Generate titles** → review and edit if needed
3. **Upload videos** → auto-applies titles

```bash
# 1. Scrape
python main.py batch --input urls.txt

# 2. Generate titles
python src/utils/title_generator.py "videos/remix-batch-1/" -o titles.json

# 3. Edit titles.json if needed (optional)
nano videos/remix-batch-1/titles.json

# 4. Upload with auto-titles
python src/utils/smart_uploader.py "videos/remix-batch-1/" --privacy public
```

## Tips for Best Titles

### ✅ DO:
- Use descriptive, specific titles
- Include power words (epic, amazing, incredible)
- Add relevant emojis for visual appeal
- Keep under 100 characters
- Include keywords for SEO
- Make it intriguing

### ❌ DON'T:
- Use clickbait or misleading titles
- Include "Follow @..." in titles
- Make titles too generic
- Exceed 100 characters
- Use ALL CAPS
- Include special characters that break URLs

## Troubleshooting

### Title is too generic

**Problem:** Getting titles like "Sora AI Does Something Unbelievable"

**Solution:** Check if:
1. Metadata file exists and has comments
2. Description is descriptive (not just "Follow @...")
3. Comments contain contextual information

### Emoji not showing

**Problem:** Emojis appear as boxes or question marks

**Solution:** 
- Ensure your terminal supports UTF-8
- Try: `export LANG=en_US.UTF-8`

### Title too long

**Problem:** Title exceeds YouTube's 100-character limit

**Solution:**
- Use `--max-length` option
- The generator auto-truncates, but you can set a lower limit

### Can't find metadata

**Problem:** `FileNotFoundError: metadata file not found`

**Solution:**
- Ensure you scraped the video first
- Check the metadata file is named correctly: `remix_XXXX_metadata.json`
- Provide the metadata path explicitly

## Next Steps

- [YouTube Upload Guide](YOUTUBE_UPLOAD.md) - Learn how to upload videos
- [Batch Processing](BATCH_PROCESSING.md) - Process multiple videos efficiently
- [API Reference](API.md) - Detailed API documentation

## Support

For issues or questions:
1. Check this documentation
2. Review the [main README](../README.md)
3. Check the code comments in `src/utils/title_generator.py`
