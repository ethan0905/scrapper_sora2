# Metadata Extraction Fix - December 10, 2025

## Issues Fixed

### 1. Description Extraction (Previously showing `null`)
**Problem:** CSS selector was too specific and escaped incorrectly
**Solution:** 
- Updated to use `div.inline[class*="max-h-"]` for better matching
- Added multiple fallback selectors
- Improved filtering to avoid button text
- Now properly extracts from: `<div class="inline max-h-[30vh] overflow-y-auto tablet:max-h-[50vh]">She's back to her old ways again… 🙄</div>`

### 2. Likes Count Extraction (Previously showing `0`)
**Problem:** Heart SVG detection was not robust enough
**Solution:**
- Enhanced SVG path detection for heart icon (`M9 3.991`)
- Improved span extraction with multiple selectors
- Added support for formatted numbers (with commas)
- Now properly extracts from: `<span class="cursor-pointer truncate">270</span>` inside heart button

### 3. Remixes Count Extraction (Previously showing `0`)
**Problem:** Circle SVG detection needed more specific validation
**Solution:**
- Added circle attribute validation (cx="9", cy="9")
- Enhanced span extraction logic
- Added support for formatted numbers
- Now properly extracts from: `<span class="truncate">88</span>` inside remix button

### 4. Creator Profile Extraction (Previously showing `null`)
**Problem:** Selector was too generic, not matching the specific element structure
**Solution:**
- Added multiple specific selectors: `a.inline-flex.self-start[href*="/profile/"]`
- Improved username extraction from URL
- Better handling of alt text vs username
- Added avatar URL extraction
- Now properly extracts from: `<a class="inline-flex self-start" href="/profile/dark.lex"><img src="..." alt="dark.lex" class="object-cover rounded-full h-10 w-10"></a>`

## Updated Selectors

### Description
```css
div.inline[class*="max-h-"]
div.inline[class*="overflow-y-auto"]
div[class*="max-h-"][class*="overflow-y-auto"]
div.inline
```

### Likes
- Button: `button[class*="rounded-full"]`
- SVG Path: `d` attribute contains `M9 3.991`
- Count: `span.truncate` or `span[class*="truncate"]`

### Remixes
- Button: `button[class*="rounded-full"]`
- SVG Circle: `cx="9"` and `cy="9"`
- Count: `span.truncate` or `span[class*="truncate"]`

### Creator Profile
```css
a.inline-flex.self-start[href*="/profile/"]
a[class*="inline-flex"][class*="self-start"][href*="/profile/"]
a.inline-flex[href*="/profile/"]
a[href*="/profile/"]
```

## Testing

To test the fixes, run:
```bash
python scraper.py --max 5 --slow
```

Check the output JSON files in `videos/` directory for:
- ✅ `description`: Non-null with actual text
- ✅ `likes`: Actual number (not 0)
- ✅ `remixes`: Actual number (not 0)
- ✅ `creator`: Username or display name
- ✅ `creator_profile_url`: Full URL to profile
- ✅ `creator_avatar_url`: Full URL to avatar image

## Example Output

```json
{
  "url": "https://sora.com/video/...",
  "scraped_at": "2025-12-10T...",
  "title": "...",
  "description": "She's back to her old ways again… 🙄",
  "creator": "dark.lex",
  "creator_profile_url": "https://sora.com/profile/dark.lex",
  "creator_avatar_url": "https://videos.openai.com/...",
  "likes": 270,
  "remixes": 88,
  "video_url": "https://...",
  "downloaded_file": "video.mp4"
}
```

## Files Modified
- `metadata_extractor.py` - All extraction logic improved with better selectors and error handling
