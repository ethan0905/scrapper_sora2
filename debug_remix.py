#!/usr/bin/env python3
"""
Debug script to inspect the remix section structure
"""

import sys
from pathlib import Path

# Add selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def inspect_remix_section(video_url):
    """Inspect the HTML structure of a video page's remix section."""
    
    print("="*60)
    print("DEBUG: Inspecting Remix Section")
    print("="*60)
    print(f"Video URL: {video_url}\n")
    
    # Create Chrome driver
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Connected to Chrome\n")
        
        # Navigate to video
        print(f"🌐 Loading page...")
        driver.get(video_url)
        time.sleep(5)
        
        print("✅ Page loaded\n")
        
        # Try to find remix section with exact XPath
        print("="*60)
        print("TEST 1: Exact XPath")
        print("="*60)
        try:
            remix_container = driver.find_element(
                By.XPATH,
                "/html/body/main/div[3]/div/div/div[2]/div/div[1]/div[4]/div/div[2]"
            )
            print("✅ Found remix container with exact XPath!")
            print(f"   Tag: {remix_container.tag_name}")
            print(f"   Classes: {remix_container.get_attribute('class')}")
            
            # Count buttons
            buttons = remix_container.find_elements(By.TAG_NAME, "button")
            print(f"   Buttons found: {len(buttons)}")
            
            # Count images
            images = remix_container.find_elements(By.TAG_NAME, "img")
            print(f"   Images found: {len(images)}")
            
            # Get first few buttons
            for i, btn in enumerate(buttons[:5], 1):
                print(f"\n   Button {i}:")
                print(f"      Classes: {btn.get_attribute('class')}")
                imgs = btn.find_elements(By.TAG_NAME, "img")
                if imgs:
                    print(f"      Has image: Yes ({len(imgs)})")
                    print(f"      Image src: {imgs[0].get_attribute('src')[:80]}...")
            
        except Exception as e:
            print(f"❌ Failed to find with exact XPath: {e}")
        
        # Try CSS selector approach
        print("\n" + "="*60)
        print("TEST 2: CSS Selector (div.flex)")
        print("="*60)
        try:
            flex_divs = driver.find_elements(By.CSS_SELECTOR, "div.flex.w-fit")
            print(f"Found {len(flex_divs)} flex containers")
            
            for i, div in enumerate(flex_divs[:3], 1):
                buttons = div.find_elements(By.TAG_NAME, "button")
                print(f"\n   Flex div {i}: {len(buttons)} buttons")
                if buttons:
                    imgs = div.find_elements(By.TAG_NAME, "img")
                    print(f"      Images: {len(imgs)}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Look for all /p/ links
        print("\n" + "="*60)
        print("TEST 3: All /p/ links")
        print("="*60)
        try:
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
            print(f"Found {len(links)} links with /p/")
            
            for i, link in enumerate(links[:10], 1):
                href = link.get_attribute("href")
                print(f"   {i}. {href}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Save page HTML for manual inspection
        print("\n" + "="*60)
        print("Saving page HTML for manual inspection...")
        print("="*60)
        
        html = driver.page_source
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("✅ Saved to: debug_page.html")
        print("\n💡 You can search in this file for:")
        print("   - 'remix' (to find remix section)")
        print("   - 'Load' (to find Load more button)")
        print("   - '/p/s_' (to find video links)")
        
        print("\n" + "="*60)
        print("✅ Debug complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_remix.py <video_url>")
        print("\nExample:")
        print("  python debug_remix.py https://sora.chatgpt.com/p/s_6932520ddd548191b4ddede8695d361a")
        sys.exit(1)
    
    video_url = sys.argv[1]
    inspect_remix_section(video_url)
