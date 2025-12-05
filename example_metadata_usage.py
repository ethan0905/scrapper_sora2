"""
Example: How to use extracted metadata in a TikTok-like app

This script demonstrates different ways to load and use the metadata
extracted by the scraper for building a TikTok-like video feed app.
"""

import json
from pathlib import Path
from datetime import datetime


def load_single_json(filename='metadata.json'):
    """Load metadata from a single JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Loaded {data['total_videos']} videos from {filename}")
    print(f"   Scraped at: {data['scraped_at']}")
    print(f"   Source: {data['source']}\n")
    
    return data['videos']


def load_multiple_json(directory='metadata'):
    """Load metadata from multiple JSON files."""
    metadata_dir = Path(directory)
    videos = []
    
    for json_file in metadata_dir.glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            video = json.load(f)
            videos.append(video)
    
    print(f"📊 Loaded {len(videos)} videos from {directory}/\n")
    return videos


def display_video_feed(videos, limit=10):
    """Display videos in a feed-like format (like TikTok)."""
    print("="*60)
    print("📱 VIDEO FEED")
    print("="*60 + "\n")
    
    for i, video in enumerate(videos[:limit], 1):
        creator = video['creator']
        content = video['content']
        engagement = video['engagement']
        
        # Display creator info
        print(f"👤 @{creator['username']}")
        if creator['verified']:
            print("   ✓ Verified")
        
        # Display description
        desc = content['description'] or content['prompt'] or "No description"
        print(f"📝 {desc[:100]}{'...' if len(desc) > 100 else ''}")
        
        # Display engagement
        print(f"❤️  {engagement['likes']} likes")
        print(f"💬 {engagement['comments_count']} comments")
        print(f"👀 {engagement['views']} views")
        
        # Display video info
        print(f"🎬 Video: {video['video_url'][:50]}...")
        
        print("\n" + "-"*60 + "\n")


def get_top_videos_by_likes(videos, top_n=10):
    """Get top N videos sorted by likes."""
    sorted_videos = sorted(videos, key=lambda v: v['engagement']['likes'], reverse=True)
    return sorted_videos[:top_n]


def get_videos_by_creator(videos, username):
    """Get all videos from a specific creator."""
    return [v for v in videos if v['creator']['username'] == username]


def get_popular_creators(videos, min_likes=100):
    """Get list of popular creators with their stats."""
    creator_stats = {}
    
    for video in videos:
        username = video['creator']['username']
        if not username:
            continue
            
        if username not in creator_stats:
            creator_stats[username] = {
                'username': username,
                'display_name': video['creator']['display_name'],
                'verified': video['creator']['verified'],
                'video_count': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_views': 0
            }
        
        creator_stats[username]['video_count'] += 1
        creator_stats[username]['total_likes'] += video['engagement']['likes']
        creator_stats[username]['total_comments'] += video['engagement']['comments_count']
        creator_stats[username]['total_views'] += video['engagement']['views']
    
    # Filter by minimum likes
    popular = [stats for stats in creator_stats.values() if stats['total_likes'] >= min_likes]
    
    # Sort by total likes
    popular.sort(key=lambda x: x['total_likes'], reverse=True)
    
    return popular


def extract_all_comments(videos):
    """Extract all comments from all videos."""
    all_comments = []
    
    for video in videos:
        video_id = video['video_id']
        creator = video['creator']['username']
        
        for comment in video['comments']:
            all_comments.append({
                'video_id': video_id,
                'video_creator': creator,
                'comment_author': comment['author'],
                'comment_text': comment['text'],
                'comment_likes': comment['likes']
            })
    
    return all_comments


def generate_search_index(videos):
    """Generate a simple search index for videos."""
    search_index = []
    
    for video in videos:
        # Combine searchable text
        searchable_text = ' '.join(filter(None, [
            video['creator']['username'],
            video['creator']['display_name'],
            video['content']['description'],
            video['content']['prompt'],
            video['content']['title']
        ])).lower()
        
        search_index.append({
            'video_id': video['video_id'],
            'searchable_text': searchable_text,
            'video': video
        })
    
    return search_index


def search_videos(search_index, query):
    """Search videos by query."""
    query = query.lower()
    results = [
        item['video'] 
        for item in search_index 
        if query in item['searchable_text']
    ]
    return results


def export_to_csv(videos, filename='videos_export.csv'):
    """Export basic video info to CSV for analysis."""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'video_id', 'creator_username', 'description', 
            'likes', 'comments', 'views', 'video_url'
        ])
        
        # Data
        for video in videos:
            writer.writerow([
                video['video_id'],
                video['creator']['username'],
                video['content']['description'] or video['content']['prompt'],
                video['engagement']['likes'],
                video['engagement']['comments_count'],
                video['engagement']['views'],
                video['video_url']
            ])
    
    print(f"✅ Exported to {filename}")


def main():
    """Main example."""
    print("🎬 SORA METADATA USAGE EXAMPLES\n")
    
    # Example 1: Load from single JSON
    print("📖 Example 1: Loading from metadata.json")
    try:
        videos = load_single_json('metadata.json')
    except FileNotFoundError:
        print("⚠️  metadata.json not found. Trying metadata/ directory...\n")
        
        # Example 2: Load from multiple files
        print("📖 Example 2: Loading from metadata/ directory")
        try:
            videos = load_multiple_json('metadata')
        except:
            print("❌ No metadata found. Please run the scraper first:\n")
            print("   python scraper_sora_advanced.py --mode home --num-videos 5 --metadata-mode\n")
            return
    
    if not videos:
        print("❌ No videos found in metadata")
        return
    
    # Example 3: Display video feed
    print("\n📖 Example 3: Display video feed")
    display_video_feed(videos, limit=5)
    
    # Example 4: Get top videos
    print("\n📖 Example 4: Top videos by likes")
    top_videos = get_top_videos_by_likes(videos, top_n=5)
    print(f"🏆 Top {len(top_videos)} videos:")
    for i, video in enumerate(top_videos, 1):
        creator = video['creator']['username'] or 'Unknown'
        likes = video['engagement']['likes']
        desc = (video['content']['description'] or video['content']['prompt'] or 'No description')[:50]
        print(f"   {i}. @{creator} - {likes} likes - {desc}...")
    
    # Example 5: Get popular creators
    print("\n📖 Example 5: Popular creators")
    creators = get_popular_creators(videos, min_likes=0)
    print(f"👥 Found {len(creators)} creators:")
    for i, creator in enumerate(creators[:5], 1):
        print(f"   {i}. @{creator['username']} - {creator['video_count']} videos - {creator['total_likes']} total likes")
    
    # Example 6: Extract comments
    print("\n📖 Example 6: Extract all comments")
    comments = extract_all_comments(videos)
    print(f"💬 Found {len(comments)} comments across all videos")
    if comments:
        print("   Sample comments:")
        for comment in comments[:3]:
            print(f"   - @{comment['comment_author']}: {comment['comment_text'][:50]}...")
    
    # Example 7: Search
    print("\n📖 Example 7: Search functionality")
    search_index = generate_search_index(videos)
    print("🔍 Search index created")
    
    # Try a search
    search_query = "sunset"
    results = search_videos(search_index, search_query)
    print(f"   Searching for '{search_query}': {len(results)} results")
    
    # Example 8: Export to CSV
    print("\n📖 Example 8: Export to CSV")
    export_to_csv(videos, 'videos_export.csv')
    
    print("\n" + "="*60)
    print("✅ EXAMPLES COMPLETED")
    print("="*60)
    print("\n💡 You can now use this data in your TikTok-like app!")
    print("\n🚀 Next steps:")
    print("   1. Import to your database (MongoDB, PostgreSQL, etc.)")
    print("   2. Build your video feed UI")
    print("   3. Implement search and filters")
    print("   4. Add user interactions (likes, comments, etc.)")


if __name__ == "__main__":
    main()
