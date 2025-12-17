# 🎬 YouTube Title Generation - Quick Reference

## TL;DR

Generate engaging, catchy YouTube titles automatically from your scraped Sora video metadata!

## Three Ways to Use

### 1. Just Generate Titles 📝

```bash
# Single video
python src/utils/title_generator.py "videos/remix_0001_metadata.json"

# Entire folder
python src/utils/title_generator.py "videos/remix-batch-3/" --hashtag -o titles.json
```

**Example Output:**
```
Epic Gorilla Escape Caught on Camera 🦍 #SoraAI
Robot Busts Incredible Dance Moves 🤖 #SoraAI  
Gorilla Smashes Through Glass Wall 🦍 #SoraAI
```

### 2. Smart Upload (Auto-Title + Upload) 🚀

```bash
# Single video
python src/utils/smart_uploader.py "videos/remix_0001.mp4" --privacy public

# Batch upload
python src/utils/smart_uploader.py "videos/remix-batch-3/" --privacy public
```

**What it does:**
- ✅ Reads metadata
- ✅ Generates catchy title
- ✅ Creates description
- ✅ Uploads to YouTube
- ✅ Logs everything
- ✅ Skips duplicates

### 3. Review Then Upload 📊

```bash
# 1. Generate titles
python src/utils/title_generator.py "videos/batch/" -o titles.json

# 2. Review and edit titles.json
nano videos/batch/titles.json

# 3. Upload
python src/utils/smart_uploader.py "videos/batch/" --privacy public
```

## Title Generation Magic ✨

The AI analyzes:
- 💬 **Comments** - "GORILLA IS FREEEEEEE"
- 📝 **Descriptions** - Original video description
- 😀 **Reactions** - Funny, epic, crazy, shocking
- 🎯 **Context** - Subjects, actions, objects

Then creates:
- **Descriptive** - Tells what happens
- **Catchy** - Uses power words
- **Visual** - Adds relevant emojis
- **SEO-friendly** - Includes keywords

## How Titles Are Generated

### Example: Gorilla Video

**Input Metadata:**
```json
{
  "description": "Follow @mr.computerslop",
  "comments": [
    {"comment_text": "GORILLA IS FREEEEEEE"},
    {"comment_text": "bro's still going after the glass broke"}
  ]
}
```

**Analysis:**
- Subject: gorilla 🦍
- Action: break, escape
- Object: glass
- Sentiment: epic

**Generated Title:**
```
Epic Gorilla Escape Caught on Camera 🦍
```

## Options Reference

### Title Generator

```bash
--hashtag          # Add #SoraAI hashtag
--no-emoji         # Disable emojis
--max-length 80    # Set max title length
-o titles.json     # Save to file
```

### Smart Uploader

```bash
--privacy public|unlisted|private   # Set privacy
--kids                              # Mark as for kids
--no-emoji                          # No emojis in titles
--no-hashtag                        # No hashtags
--force                             # Re-upload existing
-c credentials.json                 # Custom credentials
```

## Title Examples from Real Videos

| Video Scenario | Generated Title |
|----------------|----------------|
| Gorilla breaks glass | `Gorilla Smashes Through Glass Wall 🦍` |
| Gorilla on rope swing | `Gorilla Rope Swing Goes Wrong 🦍` |
| Robot dancing | `Robot Busts Incredible Dance Moves 🤖` |
| Funny animal | `Hilarious Animal Does the Unexpected 😂` |
| Car chase | `Epic Car Chase Gone Wrong 🚗` |
| Generic/no context | `Amazing Sora AI Generated Video ✨` |

## Common Workflows

### Workflow 1: Quick Upload

```bash
# Scrape → Upload (auto-titles)
python main.py https://sora.chatgpt.com/... --max 5
python src/utils/smart_uploader.py "videos/" --privacy public
```

### Workflow 2: Batch with Review

```bash
# Scrape batch
python main.py --batch urls.txt --max 10 --output videos/batch1

# Generate titles
python src/utils/title_generator.py "videos/batch1/" -o titles.json

# Review titles
cat titles.json | jq '.'

# Upload
python src/utils/smart_uploader.py "videos/batch1/" --privacy unlisted
```

### Workflow 3: Custom Titles

```bash
# Generate base titles
python src/utils/title_generator.py "videos/" -o titles.json

# Edit in your favorite editor
code titles.json  # or nano, vim, etc.

# Manual upload with custom titles
python -m src.youtube_uploader.uploader \
  --source videos/ \
  --title "Your Custom Title"
```

## Tips for Best Results

### ✅ Better Titles

1. **Good metadata = good titles**
   - Scrape with `--slow` for complete metadata
   - More comments = better context
   
2. **Review before uploading**
   - Generate titles first
   - Edit if needed
   - Then upload

3. **Use hashtags for discoverability**
   - Add `--hashtag` flag
   - Helps with YouTube SEO

### ❌ Common Issues

1. **Generic titles** - Metadata has no comments/context
   - Solution: Scrape videos with active comment sections
   
2. **Repetitive titles** - All videos from same creator
   - Solution: Mix content from different creators
   
3. **Non-English descriptions** - Titles stay in original language
   - This is intentional for international content

## Advanced: Custom Title Rules

Edit `src/utils/title_generator.py` to add your own scenarios:

```python
# Around line 180
def _generate_from_comments(self, context: Dict) -> str:
    # Add custom scenario
    if 'YOUR_SUBJECT' in context['subjects']:
        if 'YOUR_ACTION' in context['actions']:
            return "Your Custom Title Format"
    
    # ... existing code
```

## Troubleshooting

**Q: Titles are too long**
```bash
# Set shorter max length
python src/utils/title_generator.py "video.json" --max-length 80
```

**Q: Don't want emojis**
```bash
python src/utils/title_generator.py "video.json" --no-emoji
```

**Q: Want to use titles.json with old uploader**
```bash
# Load titles from JSON manually
import json
with open('titles.json') as f:
    titles = json.load(f)
    
# Then use in your upload script
```

**Q: Can't find metadata file**
```bash
# Metadata is auto-created during scraping
# Must exist in same folder as video:
# remix_0001.mp4 → remix_0001_metadata.json
```

## Full Documentation

For complete details, see: [docs/TITLE_GENERATION.md](../docs/TITLE_GENERATION.md)

---

**Need Help?** 
- Check the [main README](../README.md)
- Review [title generator code](../src/utils/title_generator.py)
- See [smart uploader code](../src/utils/smart_uploader.py)
