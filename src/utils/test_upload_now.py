#!/usr/bin/env python3
"""
Quick test script to upload the first video immediately
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auto_uploader import AutomatedUploader

print("=" * 60)
print("🧪 TESTING AUTOMATED UPLOADER")
print("=" * 60)
print()

# Create uploader
uploader = AutomatedUploader(
    source_folder="single-upload",
    upload_interval_hours=8,  # Normal 8-hour schedule
    credentials_file="youtube_credentials.json",
    privacy="unlisted",  # Use unlisted for testing
    use_vision_titles=True,
    log_file="logs/test_upload_log.txt"
)

print("✅ Uploader initialized")
print(f"📁 Source folder: {uploader.source_folder}")
print(f"🎬 Vision titles: {uploader.use_vision_titles}")
print()

# Get next video
video = uploader._get_next_video()
if not video:
    print("❌ No videos found in single-upload folder!")
    sys.exit(1)

print(f"📹 Found video: {video.name}")
print()

# Force upload by setting last_upload_time to None
uploader.state['last_upload_time'] = None
uploader._save_state()

print("⏰ Forcing immediate upload (bypassing schedule)...")
print()

# Upload the video
success = uploader._upload_video(video)

if success:
    print()
    print("=" * 60)
    print("✅ TEST PASSED! Video uploaded successfully!")
    print("=" * 60)
    print()
    print("📊 Upload State:")
    print(f"   Uploaded videos: {len(uploader.state['uploaded_videos'])}")
    print(f"   Last upload: {uploader.state['last_upload_time']}")
    print(f"   Failures: {uploader.state.get('consecutive_failures', 0)}")
    print()
    print("🎯 Next Steps:")
    print("   1. Check the uploaded/ folder for moved video")
    print("   2. Start the service: ./scripts/service.sh start")
    print("   3. Next video will upload in 8 hours")
else:
    print()
    print("=" * 60)
    print("❌ TEST FAILED! Upload did not succeed")
    print("=" * 60)
    print()
    print(f"   Error: {uploader.state.get('last_error', 'Unknown')}")
    print(f"   Failures: {uploader.state.get('consecutive_failures', 0)}")
    sys.exit(1)
