# Comment Extraction - Additional UI Filter Fix

## Issue Found
In `remix_0002_metadata.json`, two fake comments were captured:

```json
{
  "username": "dailydoseofaislop",
  "comment_text": "cast",  // ❌ This is a UI button, not a comment!
  "likes": 0
},
{
  "username": "happyremixing",
  "comment_text": "cast",  // ❌ This is a UI button, not a comment!
  "likes": 0
}
```

The actual page only had **ONE** real comment from `tornado_7`, but the scraper was picking up the "Cast" button text as comments.

## Root Cause
The word "cast" is likely a UI button (like Chrome's "Cast" feature or a platform-specific action button). The extractor was treating any text near a profile link as a potential comment, even single-word UI elements.

## Fixes Applied

### 1. **Expanded UI Pattern List**
```python
ui_patterns = [
    'replies', 'reply', 'like', 'share', 'delete', 'edit', 'more',
    'remixes', 'remix', 'load more', 'show more', 'view replies',
    'comments', 'comment', 'cast', 'follow', 'following', 'unfollow',
    'subscribe', 'subscribed', 'report', 'block', 'mute', 'copy',
    'download', 'save', 'saved', 'bookmark', 'bookmarked'
]
```

### 2. **Single-Word UI Blacklist**
```python
single_word_ui = {
    'cast', 'like', 'share', 'remix', 'follow', 'save', 
    'edit', 'delete', 'reply', 'more'
}
```
Any single word that matches this set is **immediately rejected**.

### 3. **Minimum Length Requirement**
```python
len(comment_data["comment_text"]) >= 5
```
Comments must be **at least 5 characters long** to be saved. This filters out:
- ❌ "cast" (4 chars)
- ❌ "like" (4 chars)
- ❌ "save" (4 chars)
- ✅ "Love it!" (8 chars) ✓
- ✅ "Great video" (11 chars) ✓

### 4. **Time Indicator Filter**
```python
if any(time_unit in line_lower for time_unit in 
    ['ago', 'min', 'hour', 'day', 'week', 'month', 'year']) and len(line) < 15:
    continue
```
Filters out timestamps like "2h ago", "5 min ago", etc.

### 5. **Stricter Validation Logic**
```python
is_valid_comment = (
    comment_key not in seen_comments and          # Not a duplicate
    comment_data["comment_text"] and              # Has text
    comment_data["comment_text"] != username and  # Not just username
    len(comment_data["comment_text"]) >= 5 and    # At least 5 chars
    comment_text.lower() not in single_word_ui    # Not a UI term
)
```

## Expected Results

### Before (3 comments, 2 fake):
```json
"comments": [
  {"username": "dailydoseofaislop", "comment_text": "cast"},  // ❌ FAKE
  {"username": "happyremixing", "comment_text": "cast"},      // ❌ FAKE
  {"username": "tornado_7", "comment_text": "Your videos are awesome, you're doing great, please make a video with my character!"}  // ✅ REAL
]
```

### After (1 comment, all real):
```json
"comments": [
  {
    "username": "tornado_7",
    "user_profile_url": "https://sora.chatgpt.com/profile/tornado_7",
    "user_avatar_url": "https://videos.openai.com/...",
    "comment_text": "Your videos are awesome, you're doing great, please make a video with my character!",
    "likes": 0
  }
]
```

## What's Filtered Out Now

### ❌ Single-Word UI Terms (rejected immediately):
- cast
- like
- share
- remix
- follow
- save
- edit
- delete
- reply
- more

### ❌ Short Text (< 5 characters):
- "ok" (2 chars)
- "lol" (3 chars)
- "cast" (4 chars)
- "nice" (4 chars)

### ❌ Time Indicators:
- "2h ago"
- "5 min ago"
- "1 day ago"

### ✅ Valid Comments (accepted):
- "Love it!" (8 chars)
- "This is amazing! 🎨" (18 chars)
- "Great work" (10 chars)
- Any text >= 5 characters that's not a UI term

## Testing

Run the scraper again:
```bash
python scraper.py --max 5 --slow
```

Verify clean output:
```bash
# Check comments
cat videos/remix-X/remix_XXXX_metadata.json | jq '.comments'

# Should only show real comments, no "cast", "like", etc.
cat videos/remix-X/remix_XXXX_metadata.json | jq '.comments[].comment_text'
```

## Files Modified
- `metadata_extractor.py` - Enhanced filtering with:
  - Expanded UI pattern list
  - Single-word UI blacklist
  - Minimum length requirement (5 chars)
  - Time indicator filter
  - Stricter validation logic

## Summary
The scraper now filters out **all** single-word UI terms and requires comments to be at least 5 characters long, ensuring only real, meaningful comments are saved.
