#!/usr/bin/env python3
"""
Test script for remix mode with limited depth
"""

import subprocess
import sys

print("="*60)
print("TEST: REMIX MODE (Max 5 remixes)")
print("="*60)
print()
print("This test will:")
print("  1. Follow remix chain from a video")
print("  2. Limit to max depth of 2 (to find ~5 remixes)")
print("  3. Extract metadata + download videos")
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
    "--max-depth", "2",  # Limit depth to find ~5 remixes
    "--metadata-mode",
    "--use-existing-chrome",
    "--slow"
]

result = subprocess.run(cmd)

print()
print("="*60)
print(f"Test completed with exit code: {result.returncode}")
print("="*60)
