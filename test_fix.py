#!/usr/bin/env python3
"""
Quick test of the fix - checks if we can extract remix links
"""

import subprocess
import sys

print("="*60)
print("TEST: Remix Link Extraction Fix")
print("="*60)
print()
print("This will test the video:")
print("  https://sora.chatgpt.com/p/s_6932520ddd548191b4ddede8695d361a")
print()
print("Expected: Should find at least 2-3 remix videos")
print()
print("⚠️  Note: Make sure Chrome is open with:")
print("   ./launch_chrome.sh")
print()

input("Press ENTER to start the test...")

cmd = [
    sys.executable,
    "scraper_sora_advanced.py",
    "--mode", "remix",
    "--video-url", "https://sora.chatgpt.com/p/s_6932520ddd548191b4ddede8695d361a",
    "--max-depth", "0",  # Just check the starting video's remixes
    "--use-existing-chrome"
]

print("Command:", " ".join(cmd))
print()

result = subprocess.run(cmd)

print()
print("="*60)
if result.returncode == 0:
    print("✅ Test completed! Check the output above to verify:")
    print("   - At least 2-3 remix URLs were found")
    print("   - The URLs look like: https://sora.chatgpt.com/p/s_...")
else:
    print(f"❌ Test failed with exit code: {result.returncode}")
print("="*60)
