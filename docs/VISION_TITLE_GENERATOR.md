# 🎥 Vision-Based Title Generator

## Overview

The **Vision Title Generator** uses OpenAI's GPT-4o mini with vision capabilities to analyze actual video frames and generate accurate, engaging YouTube titles based on what's really happening in the video.

## Why Vision-Based?

### ❌ Comment-Based Generator Problems
- Comments might be irrelevant or off-topic
- Descriptions might be generic ("Follow @user")
- Can't verify if title matches video content
- Limited context about visual content

### ✅ Vision-Based Advantages
- **Sees the actual video** - Analyzes real frames
- **Accurate descriptions** - Based on visual content
- **Context-aware** - Understands what's happening
- **Verifiable** - Title matches what viewers will see

## Quick Start

### 1. Setup

Install dependencies:
```bash
pip install -r requirements_vision.txt
```

Add your OpenAI API key to `.env`:
```bash
echo 'OPENAI_API_KEY="sk-your-key-here"' > .env
```

### 2. Generate Title for Single Video

```bash
python src/utils/vision_title_generator.py "videos/remix_0001.mp4"
```

**Output:**
```
🎬 Analyzing video: remix_0001.mp4
📹 Video info: 10.5s, 315 frames, 30.0 fps
  ✓ Extracted frame 0/315 (0.0s)
  ✓ Extracted frame 78/315 (2.6s)
  ✓ Extracted frame 157/315 (5.2s)
  ✓ Extracted frame 236/315 (7.9s)
✅ Extracted 4 frames

🤖 Generating title with GPT-4o mini vision...

============================================================
GENERATED TITLE:
============================================================
Gorilla Breaks Through Glass Wall and Escapes 🦍 #SoraAI
============================================================
```

### 3. Batch Generate Titles

```bash
python src/utils/vision_title_generator.py "videos/remix-batch-3/" \
  --num-frames 4 \
  --hashtag \
  -o titles.json
```

## How It Works

### 1. Frame Extraction
The system extracts evenly-spaced frames from your video:
```
[Frame 1]    [Frame 2]    [Frame 3]    [Frame 4]
   0s           3.3s         6.7s         10s
```

### 2. Vision Analysis
GPT-4o mini analyzes each frame to understand:
- **Subjects** - What's in the scene (gorilla, robot, person)
- **Actions** - What's happening (break, escape, dance)
- **Environment** - Where it takes place (zoo, city, space)
- **Emotions** - The mood and reactions

### 3. Title Generation
Combines visual analysis with optional metadata to create:
- **Descriptive** - Accurate to video content
- **Engaging** - Uses power words and hooks
- **SEO-optimized** - Includes relevant keywords
- **Branded** - Adds emojis and hashtags

## Customizing the System Prompt

The system prompt is at the **top of the file** for easy editing!

Open `src/utils/vision_title_generator.py` and edit:

```python
# ============================================================================
# SYSTEM PROMPT - EDIT THIS TO CUSTOMIZE TITLE GENERATION STYLE
# ============================================================================

TITLE_GENERATION_PROMPT = """You are an expert YouTube title writer...

Your custom instructions here...

Examples of GOOD titles:
- "Your example 1"
- "Your example 2"
"""
```

### Customize Style Prompts

You can also customize style-specific instructions:

```python
STYLE_PROMPTS = {
    'engaging': """
    Your custom engaging style instructions...
    """,
    
    'viral': """
    Your custom viral style instructions...
    """,
    
    # Add your own styles:
    'my_custom_style': """
    Your custom style here...
    """
}
```

## Options

### Frame Count

Control how many frames to analyze:

```bash
# More frames = better context, higher cost
--num-frames 6

# Fewer frames = faster, lower cost
--num-frames 2

# Default: 4 frames (good balance)
```

**Cost consideration:**
- 2 frames: ~$0.001 per video
- 4 frames: ~$0.002 per video  
- 6 frames: ~$0.003 per video

### Title Style

Choose from 5 built-in styles:

```bash
# Engaging (default) - Catchy and intriguing
--style engaging

# Descriptive - Clear and accurate
--style descriptive

# Viral - Optimized for maximum clicks
--style viral

# Clickbait - Curiosity-driven (use responsibly!)
--style clickbait

# Professional - Business/educational tone
--style professional
```

### Emoji and Hashtags

```bash
# Disable emojis
--no-emoji

# Disable hashtags
--no-hashtag

# Both disabled
--no-emoji --no-hashtag
```

### Output

```bash
# Save to custom file
-o my_titles.json

# Default: vision_titles.json in video directory
```

## Examples

### Example 1: Quick Single Video

```bash
python src/utils/vision_title_generator.py "videos/gorilla.mp4"
```

**Result:** `Gorilla Smashes Through Glass and Escapes Zoo 🦍 #SoraAI`

### Example 2: Batch with Viral Style

```bash
python src/utils/vision_title_generator.py "videos/batch/" \
  --style viral \
  --num-frames 3 \
  --hashtag \
  -o viral_titles.json
```

**Results:**
- `You Won't Believe What This Gorilla Does Next 🦍 #SoraAI`
- `Robot Dog Backflip That Broke the Internet 🤖 #SoraAI`
- `This AI Video Will Blow Your Mind 🤯 #SoraAI`

### Example 3: Professional, No Emojis

```bash
python src/utils/vision_title_generator.py "videos/demo.mp4" \
  --style professional \
  --no-emoji \
  --no-hashtag
```

**Result:** `Computer Vision Analysis: Gorilla Breaking Through Glass Barrier`

### Example 4: With Metadata Context

If you have metadata files (from the scraper), they'll be automatically used:

```bash
# Metadata file: remix_0001_metadata.json
# Video file: remix_0001.mp4

python src/utils/vision_title_generator.py "remix_0001.mp4"
```

The generator will:
1. ✅ Analyze video frames
2. ✅ Read metadata file
3. ✅ Combine visual + comment context
4. ✅ Generate enhanced title

## Integration with Smart Uploader

Use vision titles with the smart uploader:

```bash
# 1. Generate vision-based titles
python src/utils/vision_title_generator.py "videos/batch/" -o titles.json

# 2. Review and edit if needed
cat titles.json

# 3. Upload with smart uploader (it will use titles.json)
python src/utils/smart_uploader.py "videos/batch/" --privacy public
```

## Comparison: Comment-Based vs Vision-Based

### Example Video: Gorilla Breaking Glass

**Comment-Based Generator:**
```
Input: Comments say "GORILLA IS FREEEEEEE", "bro's still going"
Output: "Epic Gorilla Escape Caught on Camera 🦍"
```

**Vision-Based Generator:**
```
Input: Analyzed frames show gorilla + rope + glass + breaking action
Output: "Gorilla Breaks Through Glass Wall During Tug of War 🦍 #SoraAI"
```

**Vision is more specific and accurate!** ✨

## Cost Estimates

Based on OpenAI GPT-4o mini pricing:

| Frames | Cost per Video | 100 Videos | 1000 Videos |
|--------|----------------|------------|-------------|
| 2      | ~$0.001        | ~$0.10     | ~$1.00      |
| 4      | ~$0.002        | ~$0.20     | ~$2.00      |
| 6      | ~$0.003        | ~$0.30     | ~$3.00      |

💡 **Tip:** Start with 2-3 frames for testing, use 4-5 for production.

## Advanced Usage

### Custom Frame Selection

Currently uses uniform spacing. You can modify `extract_frames()` to:
- Detect scene changes
- Focus on action moments
- Sample first/middle/last frames

### Multi-Language Support

The vision model understands content in any language. For non-English titles:

```python
# Edit TITLE_GENERATION_PROMPT
TITLE_GENERATION_PROMPT = """...
Generate the title in Spanish/French/Japanese/etc.
"""
```

### Custom Model

Change the model in `generate_title()`:

```python
response = self.client.chat.completions.create(
    model="gpt-4o-mini",  # or "gpt-4o" for even better quality
    # ...
)
```

## Troubleshooting

### Error: "OpenAI API key required"

**Solution:** Add key to `.env` file:
```bash
echo 'OPENAI_API_KEY="sk-..."' > .env
```

Or export it:
```bash
export OPENAI_API_KEY="sk-..."
```

### Error: "Could not open video"

**Causes:**
- Video file doesn't exist
- Corrupted video file
- Unsupported format

**Solution:**
```bash
# Check file exists
ls -lh videos/your-video.mp4

# Check format
ffprobe videos/your-video.mp4

# Convert if needed
ffmpeg -i input.webm output.mp4
```

### Titles are too generic

**Solutions:**
1. Increase frame count: `--num-frames 6`
2. Change style: `--style descriptive`
3. Edit the system prompt for more specific instructions

### API Rate Limits

**Solution:** Add delays between requests:
```python
import time

for video in videos:
    title = generate_title(video)
    time.sleep(1)  # Wait 1 second between requests
```

### High API Costs

**Solutions:**
1. Reduce frame count: `--num-frames 2`
2. Resize frames smaller (edit code)
3. Use cached titles (save to JSON)

## Environment Variables

Create a `.env` file:

```bash
# Required
OPENAI_API_KEY="sk-your-key-here"

# Optional
OPENAI_ORG_ID="org-your-org-id"  # If using organization
```

## API Key Security

⚠️ **IMPORTANT:** Never commit your API key!

The `.env` file is already in `.gitignore`, but double-check:

```bash
# Verify .env is ignored
git status
# Should NOT show .env file

# If it does, remove it:
git rm --cached .env
```

## Next Steps

- **[Smart Uploader Guide](SMART_UPLOADER.md)** - Upload with auto-titles
- **[Title Generation Quick Reference](TITLE_GENERATION_QUICK.md)** - Compare methods
- **[YouTube Upload Guide](YOUTUBE_UPLOAD.md)** - Complete upload workflow

## FAQ

**Q: Which is better, comment-based or vision-based?**

A: Vision-based is more accurate but costs money. Use vision for:
- Important content that needs accurate titles
- Videos where comments are unreliable
- When you want guaranteed quality

Use comment-based for:
- Large batches on a budget
- Quick testing
- When metadata is high quality

**Q: Can I use both?**

A: Yes! Generate both and compare:
```bash
# Comment-based (free)
python src/utils/title_generator.py "video.mp4"

# Vision-based (paid)
python src/utils/vision_title_generator.py "video.mp4"

# Pick the best one!
```

**Q: How accurate is it?**

A: Very accurate! GPT-4o vision can:
- Identify objects and people
- Understand actions and motion
- Recognize scenes and environments
- Detect emotions and reactions

**Q: Can it handle long videos?**

A: Yes! It samples frames throughout the video:
- 10-second video: frames at 0s, 3s, 7s, 10s
- 60-second video: frames at 0s, 20s, 40s, 60s
- Captures beginning, middle, and end

---

**Made with 🎥 by AI for AI content creators**
