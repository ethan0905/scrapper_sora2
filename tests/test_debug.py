#!/usr/bin/env python3
"""
Debug Test - Just test button finding and clicking with detailed logs
"""

import sys
import time
from browser_manager import BrowserManager
from remix_navigator import RemixNavigator

if len(sys.argv) < 2:
    print("Usage: python3 test_debug.py <URL> [--use-existing]")
    sys.exit(1)

url = sys.argv[1]
use_existing = "--use-existing" in sys.argv

print("="*70)
print("🧪 DEBUG TEST - Button Finding & Clicking")
print("="*70)
print(f"URL: {url}")
print(f"Mode: {'Existing Chrome' if use_existing else 'New Chrome'}")
print()

# Setup
browser_mgr = BrowserManager(use_existing=use_existing)
driver = browser_mgr.setup()
navigator = RemixNavigator(driver)

try:
    # Navigate
    print(f"🌐 Navigating to URL...")
    print(f"🔍 DEBUG: Target URL = {url}")
    driver.get(url)
    time.sleep(3.0)
    print(f"🔍 DEBUG: Actual URL = {driver.current_url}")
    print()
    
    # Load some remixes
    print("🔄 Loading remixes (target: 10)...")
    total = navigator.load_all_remixes(target_count=10)
    print(f"✅ Loaded {total} remixes\n")
    
    # Download start page first
    print(f"="*70)
    print(f"[0] Processing START page (before clicking anything)")
    print(f"="*70)
    print(f"Current URL: {driver.current_url}")
    print(f"(Here you would download the video from this page)")
    print()
    
    # Try clicking first 3 buttons (NO GOING BACK!)
    for i in range(min(3, total)):
        print(f"="*70)
        print(f"[{i+1}] Testing button {i} - FORWARD ONLY (no going back!)")
        print(f"="*70)
        
        if navigator.click_remix_button(i):
            print(f"✅ Click successful!")
            print(f"   Current URL: {driver.current_url}")
            print(f"   (Here you would download the video)")
            print(f"   (Then move to next button without going back)")
        else:
            print(f"❌ Click failed!")
        
        print()
        time.sleep(1.0)
    
    print("="*70)
    print("✅ DEBUG TEST COMPLETED")
    print("="*70)

except KeyboardInterrupt:
    print("\n⚠️  Interrupted")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if not use_existing:
        browser_mgr.close()
