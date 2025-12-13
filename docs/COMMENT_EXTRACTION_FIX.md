# Comment Extraction Fix - December 10, 2025

## Issues Found in Initial Implementation

Looking at the metadata file, the comment extraction had several problems:

### ❌ Problems Identified:

1. **Duplicate Comments**
   - Same comment appearing 4-6 times
   - Example: "Har milk hits hard! 😅" appeared 6 times for user `artexmg`

2. **UI Text Captured as Comments**
   - "6 replies" being saved as comment text
   - "Remixes" being saved as comment text
   - Button labels mistaken for comments

3. **Username as Comment Text**
   - Some comments had `comment_text: "username"` instead of actual text
   - Example: `"comment_text": "onursakarya1982"`

4. **Null Comment Text**
   - Many comments with `comment_text: null` but still saved

## ✅ Fixes Implemented

### 1. **Deduplication**
```python
seen_comments = set()
comment_key = f"{username}:{comment_text}"
```
- Tracks unique comments using username + text combination
- Prevents the same comment from being added multiple times

### 2. **Improved UI Text Filtering**
```python
ui_patterns = [
    'replies', 'reply', 'like', 'share', 'delete', 'edit', 'more',
    'remixes', 'remix', 'load more', 'show more', 'view replies',
    'comments', 'comment'
]
```
- Filters out common UI button text
- Skips short text that matches UI patterns

### 3. **Better Text Extraction**
```python
# Skip if it's just the username
if line == comment_data["username"]:
    continue

# Skip if it's just a number
if line.replace(',', '').replace('.', '').isdigit():
    continue
```
- Excludes username-only text
- Excludes numeric-only text (counts, etc.)
- Only accepts actual comment content

### 4. **Stricter Validation**
```python
if (comment_key not in seen_comments and 
    comment_data["comment_text"] and 
    comment_data["comment_text"] != comment_data["username"]):
```
- Only saves comments that have actual text
- Rejects null or username-only comments
- Ensures unique comments only

### 5. **Better Debug Logging**
```python
print(f"      🔍 Found {len(elements)} potential comment containers")
print(f"      📊 Processing {len(comment_elements)} potential comment(s)...")
```
- Shows how many containers were found
- Helps debug extraction issues

## Expected Output Now

### Before (remix_0005_metadata.json):
```json
{
  "comments": [
    {"username": "artexmg", "comment_text": "6 replies", "likes": 0},
    {"username": "artexmg", "comment_text": "6 replies", "likes": 0},
    {"username": "artexmg", "comment_text": "Har milk hits hard! 😅", "likes": 0},
    {"username": "artexmg", "comment_text": "Har milk hits hard! 😅", "likes": 0},
    {"username": "artexmg", "comment_text": "Har milk hits hard! 😅", "likes": 0},
    {"username": "artexmg", "comment_text": null, "likes": 0},
    {"username": "onursakarya1982", "comment_text": "onursakarya1982", "likes": 0},
    // ... 50+ duplicates and junk
  ]
}
```

### After (Expected):
```json
{
  "comments": [
    {
      "username": "artexmg",
      "user_profile_url": "https://sora.chatgpt.com/profile/artexmg",
      "user_avatar_url": "https://videos.openai.com/...",
      "comment_text": "Har milk hits hard! 😅",
      "likes": 0
    },
    {
      "username": "onursakarya1982",
      "user_profile_url": "https://sora.chatgpt.com/profile/onursakarya1982",
      "user_avatar_url": "https://videos.openai.com/...",
      "comment_text": "🥛 it up 😆",
      "likes": 0
    },
    {
      "username": "achaucer",
      "user_profile_url": "https://sora.chatgpt.com/profile/achaucer",
      "user_avatar_url": "https://videos.openai.com/...",
      "comment_text": "Of all the beverages, milk has to be the funniest. What's funnier than milk? 🥛",
      "likes": 0
    },
    {
      "username": "ahmed.alakedy",
      "user_profile_url": "https://sora.chatgpt.com/profile/ahmed.alakedy",
      "user_avatar_url": "https://videos.openai.com/...",
      "comment_text": "Lol 😂 this is amazing 👌",
      "likes": 0
    },
    {
      "username": "tannermanor",
      "user_profile_url": "https://sora.chatgpt.com/profile/tannermanor",
      "user_avatar_url": "https://videos.openai.com/...",
      "comment_text": "Big calcium fans here",
      "likes": 0
    },
    {
      "username": "lebellysora",
      "user_profile_url": "https://sora.chatgpt.com/profile/lebellysora",
      "user_avatar_url": "https://videos.openai.com/...",
      "comment_text": "Love it!",
      "likes": 0
    }
  ]
}
```

## Testing

Run the scraper again to test the improvements:

```bash
python scraper.py --max 5 --slow
```

Then check the comments:
```bash
# View comments in a clean format
cat videos/remix-X/remix_XXXX_metadata.json | jq '.comments'

# Count comments
cat videos/remix-X/remix_XXXX_metadata.json | jq '.comments | length'

# Check for duplicates (should be 0)
cat videos/remix-X/remix_XXXX_metadata.json | jq '[.comments[].comment_text] | group_by(.) | map(select(length > 1))'
```

## What Changed

### File Modified
- `metadata_extractor.py` - Completely rewrote `extract_comments()` method

### Key Improvements
1. ✅ Deduplication using set tracking
2. ✅ Comprehensive UI text filtering
3. ✅ Username exclusion from comment text
4. ✅ Null/empty comment rejection
5. ✅ Better debug logging
6. ✅ Stricter validation before saving

## Notes

- Comments without actual text (null or just username) are now excluded
- Duplicates are automatically removed
- UI text like "X replies", "Remixes", etc. is filtered out
- Only meaningful, unique comments are saved
