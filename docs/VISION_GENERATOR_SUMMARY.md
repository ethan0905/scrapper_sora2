# 🎉 Vision-Based Title Generator - Complete!

## What Was Built

A **GPT-4o mini vision-powered title generator** that actually watches your videos and creates accurate, engaging YouTube titles.

## ✨ Key Features

### 1. **Vision Analysis**
- Extracts frames from video at key moments
- Uses OpenAI GPT-4o mini vision API
- Analyzes actual visual content
- Much more accurate than comment-based approach

### 2. **Easy Customization**
- System prompt at **top of file** for easy editing
- 5 built-in styles: engaging, descriptive, viral, clickbait, professional
- Add your own custom styles
- Multi-language support

### 3. **Seamless Integration**
- Loads API key from `.env` file automatically
- Works with existing metadata for enhanced context
- Batch processing support
- JSON output for workflow integration

### 4. **Cost-Effective**
- ~$0.002 per video (4 frames)
- Configurable frame count (2-6 frames)
- Low-detail mode to save tokens
- Only pays for what you use

## 📁 Files Created

```
src/utils/
├── vision_title_generator.py    # Main vision generator (with editable prompt)
├── title_generator.py            # Comment-based generator (free)
└── smart_uploader.py             # Smart uploader (can use either)

docs/
├── VISION_TITLE_GENERATOR.md     # Complete documentation
├── CUSTOMIZE_VISION_PROMPT.md    # How to edit the prompt
├── TITLE_GENERATION.md           # Comment-based guide
└── TITLE_GENERATION_QUICK.md     # Quick reference

requirements_vision.txt            # Vision-specific dependencies
.env                               # API key storage (gitignored)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_vision.txt
```

### 2. Add API Key

Edit `.env` file (already exists):
```bash
OPENAI_API_KEY="sk-your-key-here"
```

### 3. Generate Title

```bash
# Single video
python src/utils/vision_title_generator.py "videos/remix_0001.mp4"

# Batch with style
python src/utils/vision_title_generator.py "videos/batch/" \
  --style viral \
  --hashtag \
  -o titles.json
```

## 🎨 Customize the Prompt

Open `src/utils/vision_title_generator.py` and find this section at the top:

```python
# ============================================================================
# SYSTEM PROMPT - EDIT THIS TO CUSTOMIZE TITLE GENERATION STYLE
# ============================================================================

TITLE_GENERATION_PROMPT = """You are an expert YouTube title writer...

[EDIT THIS SECTION]

Examples of GOOD titles:
- "Your example 1"
- "Your example 2"
```

**That's it!** No need to dig through code. The prompt is right at the top.

## 📊 Comparison

### Comment-Based Generator
```bash
python src/utils/title_generator.py "video_metadata.json"
```
- ✅ Free
- ✅ Fast
- ✅ No API needed
- ❌ Can be inaccurate
- ❌ Relies on comments

### Vision-Based Generator
```bash
python src/utils/vision_title_generator.py "video.mp4"
```
- ✅ Very accurate
- ✅ Analyzes actual video
- ✅ Context-aware
- ❌ Costs ~$0.002/video
- ❌ Requires API key

**Recommendation:** Use vision-based for important content, comment-based for large batches.

## 🎯 Use Cases

### Use Vision-Based When:
- You need accurate, high-quality titles
- Comments are generic or unhelpful
- Video content is complex
- You're uploading to main channel
- Quality > cost

### Use Comment-Based When:
- Processing hundreds of videos
- On a tight budget
- Comments are descriptive
- Testing/prototyping
- Speed > accuracy

## 💡 Pro Tips

### 1. Test Different Frame Counts
```bash
# Faster, cheaper (2 frames)
python src/utils/vision_title_generator.py video.mp4 --num-frames 2

# Better quality (6 frames)
python src/utils/vision_title_generator.py video.mp4 --num-frames 6
```

### 2. Compare Styles
```bash
# Try all styles
for style in engaging descriptive viral professional; do
  python src/utils/vision_title_generator.py video.mp4 --style $style
done
```

### 3. Combine Both Approaches
```bash
# Generate both types
python src/utils/title_generator.py "video_metadata.json"
python src/utils/vision_title_generator.py "video.mp4"

# Pick the best!
```

### 4. Edit the Prompt for Your Niche
```python
# For gaming content
TITLE_GENERATION_PROMPT = """Create gaming-focused titles with:
- Game name if visible
- Epic play/fail/moment
- Relevant gaming terms
Example: "Insane Clutch in Apex Legends - 1v3 Squad Wipe 🎮"
```

## 📈 Cost Breakdown

| Videos | Frames | Cost/Video | Total Cost |
|--------|--------|------------|------------|
| 10     | 2      | $0.001     | $0.01      |
| 10     | 4      | $0.002     | $0.02      |
| 100    | 4      | $0.002     | $0.20      |
| 1000   | 4      | $0.002     | $2.00      |

**Very affordable for the quality you get!**

## 🔧 Troubleshooting

### "OpenAI API key required"
- Add key to `.env` file: `OPENAI_API_KEY="sk-..."`
- Or export it: `export OPENAI_API_KEY="sk-..."`

### "Could not open video"
- Check file exists: `ls -lh video.mp4`
- Check format: `ffprobe video.mp4`
- Convert if needed: `ffmpeg -i input.webm output.mp4`

### Titles are generic
- Increase frames: `--num-frames 6`
- Change style: `--style descriptive`
- Edit the system prompt

### API rate limits
- Add delays between requests
- Reduce frame count
- Process in smaller batches

## 📚 Documentation

All documentation is in the `docs/` folder:

1. **[VISION_TITLE_GENERATOR.md](docs/VISION_TITLE_GENERATOR.md)**
   - Complete guide
   - All features explained
   - Cost estimates
   - Examples

2. **[CUSTOMIZE_VISION_PROMPT.md](docs/CUSTOMIZE_VISION_PROMPT.md)**
   - How to edit the prompt
   - Style customization
   - Example prompts
   - Testing tips

3. **[README.md](README.md)**
   - Main project overview
   - All features listed
   - Quick start guide

## 🎬 Example Workflow

```bash
# 1. Scrape videos
python main.py --batch urls.txt --max 10 --output videos/batch

# 2. Generate vision-based titles
python src/utils/vision_title_generator.py "videos/batch/" \
  --style engaging \
  --hashtag \
  --num-frames 4 \
  -o vision_titles.json

# 3. Review titles
cat vision_titles.json | jq '.'

# 4. Upload with smart uploader
python src/utils/smart_uploader.py "videos/batch/" --privacy public
```

## ✅ What's Next?

You now have TWO title generation methods:

1. **Comment-Based** (free, fast)
   - `title_generator.py`
   - Good for bulk processing

2. **Vision-Based** (accurate, paid)
   - `vision_title_generator.py`  
   - Good for quality content

Choose the right tool for your needs!

## 🎉 Summary

### What You Got:
✅ Vision-based title generator with GPT-4o mini  
✅ Easy-to-edit system prompt at top of file  
✅ 5 built-in styles + custom style support  
✅ Automatic .env API key loading  
✅ Batch processing  
✅ Complete documentation  
✅ Integration with existing tools  

### How to Use:
1. Add API key to `.env`
2. Run: `python src/utils/vision_title_generator.py video.mp4`
3. Edit prompt if needed (top of file)
4. Generate amazing titles! 🎬

---

**All code committed and pushed to GitHub!** 🚀

Questions? Check the docs or the code comments!
