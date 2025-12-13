#!/usr/bin/env python3
"""
Test script for remix mode - targets 10+ remixes
"""

import subprocess
import sys

print("="*60)
print("TEST: REMIX MODE (Target: 10+ remixes)")
print("="*60)
print()
print("This test will:")
print("  1. Follow remix chain from a video")
print("  2. Use depth 1 but click 'Load more' multiple times (~10+ remixes)")
print("  3. Extract metadata + download videos")
print()
print("⚠️  Note: Make sure Chrome is open with:")
print("   ./launch_chrome.sh")
print()

video_url = input("Enter video URL to test (e.g., https://sora.chatgpt.com/p/s_xxx): ").strip()

if not video_url:
    print("❌ No URL provided")
    sys.exit(1)

print()
print("🚀 Running test...")
print()

cmd = [
    sys.executable,
    "scraper_sora_advanced.py",
    "--mode", "remix",
    "--video-url", video_url,
    "--max-depth", "1",  # Only depth 1, but load more clicks will get 10+
    "--metadata-mode",
    "--use-existing-chrome",
    "--slow"
]

print("Command:", " ".join(cmd))
print()

result = subprocess.run(cmd)

print()
print("="*60)
if result.returncode == 0:
    print("✅ Test completed successfully!")
    print()
    print("Check the results:")
    print("  - videos/ folder for downloaded videos")
    print("  - metadata.json for video information")
else:
    print(f"❌ Test failed with exit code: {result.returncode}")
print("="*60)
