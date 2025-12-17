# 📝 How to Customize the Vision Title Generator

## Quick Edit: System Prompt

The easiest way to customize title generation is to edit the system prompt at the **top of the vision_title_generator.py file**.

### Location

Open: `src/utils/vision_title_generator.py`

Look for this section at the top (around line 20):

```python
# ============================================================================
# SYSTEM PROMPT - EDIT THIS TO CUSTOMIZE TITLE GENERATION STYLE  
# ============================================================================

TITLE_GENERATION_PROMPT = """You are an expert YouTube title writer...
```

### What You Can Customize

1. **Overall Instructions**
   ```python
   TITLE_GENERATION_PROMPT = """You are a [YOUR ROLE].
   
   Your task is to [YOUR TASK].
   
   Guidelines:
   - Your guideline 1
   - Your guideline 2
   ```

2. **Good/Bad Examples**
   ```python
   Examples of GOOD titles:
   - "Your Example 1"
   - "Your Example 2"
   
   Examples of BAD titles:
   - "Bad example 1"
   - "Bad example 2"
   ```

3. **Style Variations**
   ```python
   STYLE_PROMPTS = {
       'engaging': """Your engaging style...""",
       'viral': """Your viral style...""",
       'my_style': """Your custom style..."""
   }
   ```

## Example Customizations

### Example 1: More Specific Instructions

```python
TITLE_GENERATION_PROMPT = """You are a YouTube title expert for AI-generated Sora videos.

Your task: Create titles that:
1. START with the main action or subject
2. Use specific visual details you see in the frames
3. Include emotional words (Amazing, Epic, Incredible, Wild)
4. Keep it under 80 characters
5. Make viewers curious but don't spoil the ending

Examples:
✅ "Gorilla Smashes Through Glass Wall in Epic Zoo Escape 🦍"
✅ "Robot Does Perfect Backflip Over Moving Ferrari 🤖"
❌ "Video of gorilla" (too vague)
❌ "GORILLA DOES UNBELIEVABLE THING!!!" (too clickbait)
"""
```

### Example 2: Professional Tone

```python
TITLE_GENERATION_PROMPT = """You are a professional content curator for educational AI demonstrations.

Create clear, informative titles that:
- Describe exactly what happens
- Use proper terminology
- Avoid sensationalism
- Focus on technical accuracy
- Be suitable for academic contexts

Examples:
✅ "Computer Vision Demo: Object Recognition in Dynamic Environment"
✅ "AI-Generated Animation: Simulated Physics Interaction"
❌ "You Won't BELIEVE This AI Video!!!"
❌ "Crazy AI Does Something Wild 🤯"
"""
```

### Example 3: Viral Short-Form Style

```python
TITLE_GENERATION_PROMPT = """You are a viral TikTok/Shorts title expert.

Create punchy, SHORT titles (under 60 chars) that:
- Start with a hook word (POV:, When, Wait for it, etc.)
- Use trending language
- Create curiosity
- Are perfect for scrolling users

Examples:
✅ "POV: The gorilla had enough 🦍"
✅ "Wait for it... 💀"
✅ "This robot said 'watch this' 🤖"
✅ "Bro really thought... 😭"
"""
```

### Example 4: Multi-Language (Spanish)

```python
TITLE_GENERATION_PROMPT = """Eres un experto en crear títulos para YouTube en español.

Tu tarea es analizar los videos y crear títulos atractivos en español que:
- Sean descriptivos y precisos
- Usen palabras emotivas
- Incluyan emojis relevantes
- Sean optimizados para SEO

Ejemplos BUENOS:
✅ "Gorila Rompe el Cristal y Escapa del Zoo 🦍"
✅ "Robot Hace Increíble Acrobacia en la Ciudad 🤖"

Ejemplos MALOS:
❌ "Video de gorila" (muy vago)
❌ "NO VAS A CREER ESTO!!!" (clickbait)
"""
```

## Style Presets

You can add custom style presets in the `STYLE_PROMPTS` dictionary:

```python
STYLE_PROMPTS = {
    'engaging': """...""",
    
    # Add your custom style
    'documentary': """
    Create documentary-style titles:
    - Serious, informative tone
    - No emojis or slang
    - Focus on the story
    - Use phrases like "The Story of", "Inside", "How"
    Example: "The Story of a Gorilla's Quest for Freedom"
    """,
    
    'comedy': """
    Create humorous, meme-style titles:
    - Use current memes and slang
    - Add comedic timing
    - Include relevant emojis
    - Make people laugh
    Example: "Gorilla Really Said 'I'm Outta Here' 💀"
    """,
}
```

Then use it with:
```bash
python src/utils/vision_title_generator.py video.mp4 --style documentary
```

## Testing Your Changes

After editing the prompt:

```bash
# Test on a single video
python src/utils/vision_title_generator.py "test-video.mp4"

# Compare different styles
python src/utils/vision_title_generator.py "test.mp4" --style engaging
python src/utils/vision_title_generator.py "test.mp4" --style descriptive
python src/utils/vision_title_generator.py "test.mp4" --style your_custom_style
```

## Advanced: Programmatic Prompt Injection

If you want to modify the prompt dynamically without editing the file:

```python
from src.utils.vision_title_generator import VisionTitleGenerator

# Create generator
generator = VisionTitleGenerator()

# Inject custom prompt
generator.TITLE_GENERATION_PROMPT = """Your custom prompt here..."""

# Generate title
title = generator.generate_title("video.mp4")
```

## Tips for Great Prompts

### ✅ DO:
- Be specific about what you want
- Provide clear examples
- Define what to avoid
- Test with real videos
- Iterate based on results

### ❌ DON'T:
- Make the prompt too long (increases cost)
- Be vague or ambiguous
- Contradict yourself
- Forget to test changes

## Quick Reference Card

Save this near your workspace:

```
📝 PROMPT LOCATION:
src/utils/vision_title_generator.py (lines 20-60)

🔧 CHANGE THIS:
TITLE_GENERATION_PROMPT = """..."""

🎨 ADD STYLES:
STYLE_PROMPTS = { 'my_style': """...""" }

🧪 TEST:
python src/utils/vision_title_generator.py video.mp4

💰 COST:
~$0.002 per video (4 frames)
```

---

Need help? Check the [full documentation](VISION_TITLE_GENERATOR.md).
