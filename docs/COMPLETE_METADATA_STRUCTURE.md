# Complete Metadata Structure

## Full JSON Output Example

```json
{
  "url": "https://sora.chatgpt.com/p/s_69392fb980788191a36a4c402c226505",
  "scraped_at": "2025-12-10T22:18:14.872761",
  "title": "Sora",
  
  "description": "She's back to her old ways again… 🙄",
  
  "creator": "dark.lex",
  "creator_profile_url": "https://sora.chatgpt.com/profile/dark.lex",
  "creator_avatar_url": "https://videos.openai.com/az/vg-assets/project-y%2Fprofile%2F...",
  
  "likes": 270,
  "remixes": 88,
  
  "comments": [
    {
      "username": "user123",
      "user_profile_url": "https://sora.chatgpt.com/profile/user123",
      "user_avatar_url": "https://cdn.openai.com/sora/images/user123_avatar.jpg",
      "comment_text": "This is absolutely incredible! 🎨",
      "likes": 42
    },
    {
      "username": "creator_name",
      "user_profile_url": "https://sora.chatgpt.com/profile/creator_name",
      "user_avatar_url": "https://cdn.openai.com/sora/images/creator_avatar.jpg",
      "comment_text": "Love the creativity here!",
      "likes": 15
    },
    {
      "username": "fan_account",
      "user_profile_url": "https://sora.chatgpt.com/profile/fan_account",
      "user_avatar_url": "https://cdn.openai.com/sora/images/fan_avatar.jpg",
      "comment_text": "Can't wait to see more from this creator",
      "likes": 8
    }
  ],
  
  "video_url": "https://videos.openai.com/az/files/00000000-29a8-7280-9848-0b48ff100c31%2Fraw?...",
  "downloaded_file": "videos/remix_0028.mp4"
}
```

## Data Fields Breakdown

### Video Information
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `url` | string | Page URL of the remix | `"https://sora.chatgpt.com/p/s_..."` |
| `scraped_at` | string | ISO timestamp when scraped | `"2025-12-10T22:18:14.872761"` |
| `title` | string | Page title | `"Sora"` |
| `video_url` | string | Direct video file URL | `"https://videos.openai.com/..."` |
| `downloaded_file` | string | Local path to saved video | `"videos/remix_0028.mp4"` |

### Content Metadata
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `description` | string | Video description text | `"She's back to her old ways..."` |
| `likes` | number | Number of likes on video | `270` |
| `remixes` | number | Number of remixes created | `88` |

### Creator Information
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `creator` | string | Creator's username/display name | `"dark.lex"` |
| `creator_profile_url` | string | URL to creator's profile | `"https://sora.chatgpt.com/profile/dark.lex"` |
| `creator_avatar_url` | string | URL to creator's avatar image | `"https://videos.openai.com/..."` |

### Comments (Array)
Each comment contains:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `username` | string | Commenter's username | `"user123"` |
| `user_profile_url` | string | URL to commenter's profile | `"https://sora.chatgpt.com/profile/user123"` |
| `user_avatar_url` | string | URL to commenter's avatar | `"https://cdn.openai.com/..."` |
| `comment_text` | string | The comment content | `"This is amazing! 🎨"` |
| `likes` | number | Likes on this comment | `42` |

## Data Quality

### ✅ Extracted (Always)
- URL
- Scraped timestamp
- Video URL
- Downloaded file path

### ✅ Extracted (When Available)
- Title
- Description
- Creator info (name, profile, avatar)
- Likes count
- Remixes count
- Comments (all available)

### ℹ️ Default Values (When Not Available)
- `description`: `null`
- `creator`: `null`
- `likes`: `0`
- `remixes`: `0`
- `comments`: `[]` (empty array)

## Use Cases

### 1. Analyze Engagement
```python
import json

with open('videos/remix_0028_metadata.json') as f:
    data = json.load(f)
    
print(f"Video has {data['likes']} likes and {len(data['comments'])} comments")
print(f"Average comment engagement: {sum(c['likes'] for c in data['comments']) / len(data['comments'])}")
```

### 2. Extract All Comments
```python
import json

with open('videos/remix_0028_metadata.json') as f:
    data = json.load(f)
    
for comment in data['comments']:
    print(f"{comment['username']}: {comment['comment_text']} ({comment['likes']} likes)")
```

### 3. Find Top Creators
```python
import json
from collections import Counter

creators = []
for metadata_file in glob.glob('videos/**/metadata.json'):
    with open(metadata_file) as f:
        data = json.load(f)
        creators.append(data['creator'])

top_creators = Counter(creators).most_common(10)
print("Top 10 creators:", top_creators)
```

## File Structure

```
videos/
├── remix_0001.mp4
├── remix_0001_metadata.json
├── remix_0002.mp4
├── remix_0002_metadata.json
└── ...
```

Each remix has:
- Video file (`.mp4`)
- Metadata file (`_metadata.json`)
