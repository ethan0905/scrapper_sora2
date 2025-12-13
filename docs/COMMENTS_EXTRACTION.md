# Comments Extraction Feature

## Overview
The scraper now extracts all comments associated with each remix, including detailed user information and engagement metrics.

## Extracted Comment Data

For each comment, the following fields are extracted:

### 1. **Username** (`username`)
- The display name or username of the comment author
- Extracted from profile link or image alt text
- Example: `"john_doe"` or `"John Doe"`

### 2. **User Profile URL** (`user_profile_url`)
- Full URL to the user's profile page
- Example: `"https://sora.chatgpt.com/profile/john_doe"`

### 3. **User Avatar URL** (`user_avatar_url`)
- Full URL to the user's profile picture/avatar
- Example: `"https://cdn.openai.com/sora/images/avatars/..."`

### 4. **Comment Text** (`comment_text`)
- The actual comment content
- Example: `"This is amazing! Great work!"`

### 5. **Likes Count** (`likes`)
- Number of likes on the comment
- Example: `42`

## JSON Output Structure

Each remix metadata file now includes a `comments` array:

```json
{
  "url": "https://sora.chatgpt.com/p/s_...",
  "scraped_at": "2025-12-10T...",
  "title": "...",
  "description": "...",
  "creator": "...",
  "likes": 270,
  "remixes": 88,
  "comments": [
    {
      "username": "user123",
      "user_profile_url": "https://sora.chatgpt.com/profile/user123",
      "user_avatar_url": "https://cdn.openai.com/...",
      "comment_text": "This is incredible!",
      "likes": 15
    },
    {
      "username": "creator_name",
      "user_profile_url": "https://sora.chatgpt.com/profile/creator_name",
      "user_avatar_url": "https://cdn.openai.com/...",
      "comment_text": "Love the creativity here 🎨",
      "likes": 8
    }
  ],
  "video_url": "...",
  "downloaded_file": "..."
}
```

## How It Works

### Comment Detection Strategy
1. **Primary Method**: Looks for comment-specific containers:
   - `div[class*="comment"]`
   - `li[class*="comment"]`
   - `article[class*="comment"]`
   - `div[role="article"]`

2. **Fallback Method**: Searches for elements containing profile links
   - Identifies potential comments by finding divs/articles with profile URLs

### Extraction Process

For each detected comment container:

1. **User Info Extraction**:
   - Finds `a[href*="/profile/"]` links
   - Extracts username from URL path
   - Gets avatar from `<img>` tag within the link
   - Uses `alt` text for display name if available

2. **Comment Text Extraction**:
   - Searches for text in `<p>`, `<div>`, `<span>` elements
   - Filters out UI text (like, reply, share buttons)
   - Selects the longest meaningful text as comment content

3. **Likes Extraction**:
   - Finds like buttons within the comment element
   - Extracts count from button spans
   - Supports formatted numbers with commas

## Features

✅ **Robust Detection**: Multiple selector strategies to find comments
✅ **Complete User Info**: Username, profile URL, and avatar
✅ **Engagement Metrics**: Comment likes count
✅ **Smart Filtering**: Excludes UI elements and button text
✅ **Error Handling**: Continues extraction even if individual comments fail

## Testing

Run the scraper to see comments in action:

```bash
python scraper.py --max 5 --slow
```

Check the output JSON files:
```bash
cat videos/remix-X/remix_XXXX_metadata.json | jq '.comments'
```

## Console Output

During scraping, you'll see:
```
💬 Extracting comments...
✅ Found 3 comment(s)
```

Or if no comments:
```
💬 Extracting comments...
ℹ️  No comments found
```

## Notes

- Comments array will be empty `[]` if no comments are found
- Each comment is validated to have at least a username and text
- Invalid or incomplete comments are skipped
- Works with both authenticated and public comment sections
