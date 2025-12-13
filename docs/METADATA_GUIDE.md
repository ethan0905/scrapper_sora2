# Metadata Extraction - Complete Guide

## 📊 Metadata Fields

The scraper now extracts the following metadata for each remix:

```json
{
  "url": "https://sora.chatgpt.com/p/s_xxx",
  "scraped_at": "2025-12-10T20:30:45.123456",
  "title": "Sora",
  "description": "She's back to her old ways again… 🙄",
  "creator": "dark.lex",
  "creator_profile_url": "https://sora.chatgpt.com/profile/dark.lex",
  "creator_avatar_url": "https://videos.openai.com/az/vg-assets/...",
  "likes": 270,
  "remixes": 88,
  "video_url": "https://videos.openai.com/az/files/...",
  "downloaded_file": "videos/remix_0001.mp4"
}
```

## 🔍 How Each Field Is Extracted

### 1. Description
**Selector Priority:**
1. `div.inline.max-h-[30vh]` - Main description container
2. `div[class*="max-h-"][class*="overflow-y-auto"]` - Overflow containers
3. Fallback: Search for text elements, filter out UI text

**Example HTML:**
```html
<div class="inline max-h-[30vh] overflow-y-auto tablet:max-h-[50vh]">
  She's back to her old ways again… 🙄
</div>
```

**Result:**
```json
"description": "She's back to her old ways again… 🙄"
```

### 2. Likes Count
**How it works:**
1. Find all `button[class*="rounded-full"]`
2. Look for button containing heart SVG (path with `M9 3.991`)
3. Extract number from `span.truncate` inside button

**Example HTML:**
```html
<button class="inline-flex gap-1.5 items-center...rounded-full...">
  <svg>
    <path d="M9 3.991c4.878-4.83 13.24 4.14 0 11.384..."></path>
  </svg>
  <span class="cursor-pointer truncate">270</span>
</button>
```

**Result:**
```json
"likes": 270
```

### 3. Remixes Count
**How it works:**
1. Find all `button[class*="rounded-full"]`
2. Look for button containing circle SVG (remix icon)
3. Extract number from `span.truncate` inside button

**Example HTML:**
```html
<button class="inline-flex gap-1.5...rounded-full..." data-disabled="false">
  <svg>
    <circle cx="9" cy="9" r="6.75"></circle>
    <path d="M11.25 9a4.5 4.5 0 0 0-9 0M15.75 9a4.5 4.5 0 1 1-9 0"></path>
  </svg>
  <span class="truncate">88</span>
</button>
```

**Result:**
```json
"remixes": 88
```

### 4. Creator Profile
**How it works:**
1. Find `a[href*="/profile/"]`
2. Extract username from URL path
3. Get `img` tag for avatar URL
4. Use `alt` attribute as display name

**Example HTML:**
```html
<a class="inline-flex self-start" href="/profile/dark.lex">
  <img 
    src="https://videos.openai.com/az/vg-assets/..." 
    alt="dark.lex" 
    class="object-cover rounded-full h-10 w-10"
  >
</a>
```

**Result:**
```json
"creator": "dark.lex",
"creator_profile_url": "https://sora.chatgpt.com/profile/dark.lex",
"creator_avatar_url": "https://videos.openai.com/az/vg-assets/..."
```

## 🎯 Debug Output

When running the scraper, you'll see:

```
   📊 Extracting metadata...
      ✅ Description found: She's back to her old ways again…
      ✅ Likes found: 270
      ✅ Remixes found: 88
      ✅ Creator found: dark.lex
      ✅ Profile URL: https://sora.chatgpt.com/profile/dark.lex
   💾 Metadata saved: remix_0001_metadata.json
```

## 📁 Output Files

### Individual Metadata Files
Each remix gets its own JSON file:
```
videos/
├── remix_0001_metadata.json
├── remix_0002_metadata.json
└── ...
```

### Combined Metadata File
All metadata in one file:
```json
{
  "scraped_at": "2025-12-10T20:30:45.123456",
  "total_remixes": 50,
  "successful_downloads": 48,
  "remixes": [
    {
      "url": "...",
      "description": "...",
      "creator": "...",
      "likes": 270,
      "remixes": 88,
      ...
    },
    ...
  ]
}
```

## 🔧 Troubleshooting

### Description is null
- Page might use different HTML structure
- Try waiting longer for page to load (use `--slow`)
- Check debug output for errors

### Likes/Remixes are 0
- Button structure might have changed
- SVG signature might be different
- Check if buttons are visible on page

### Creator is null
- Profile link might not be present
- Different URL pattern (not `/profile/`)
- Check if logged in (some profiles require auth)

## 🚀 Best Practices

1. **Use slow mode for better extraction:**
   ```bash
   python3 scraper.py "URL" --max 50 --slow --use-existing
   ```

2. **Check first few results:**
   ```bash
   python3 scraper.py "URL" --max 3 --use-existing
   cat videos/remix_0001_metadata.json
   ```

3. **Monitor debug output:**
   - Watch for "✅ Description found"
   - Watch for "✅ Likes found"
   - Watch for "✅ Creator found"

4. **If extraction fails:**
   - Save page HTML for analysis
   - Check browser console for errors
   - Verify you're on the correct page type
