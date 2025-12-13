#!/usr/bin/env python3
"""
Simple test to click one remix button and see if it works
"""

import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_click_remix():
    """Test clicking a single remix button."""
    
    video_url = "https://sora.chatgpt.com/p/s_6932520ddd548191b4ddede8695d361a"
    
    print("="*60)
    print("TEST: Click Single Remix Button")
    print("="*60)
    print(f"Video: {video_url}\n")
    
    # Connect to existing Chrome
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Connected to Chrome\n")
        
        # Navigate
        print("🌐 Loading page...")
        driver.get(video_url)
        time.sleep(5)
        
        # Find remix container
        print("🔍 Finding remix section...")
        remix_container = driver.find_element(
            By.XPATH,
            "/html/body/main/div[3]/div/div/div[2]/div/div[1]/div[4]/div/div[2]"
        )
        print("✅ Found remix section\n")
        
        # Find buttons
        buttons = remix_container.find_elements(By.TAG_NAME, "button")
        print(f"📊 Found {len(buttons)} buttons\n")
        
        if len(buttons) > 0:
            print("🖱️  Attempting to click first button...")
            button = buttons[0]
            
            # Store current URL
            current_url = driver.current_url
            print(f"   Current URL: {current_url}")
            
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Try clicking with JavaScript
            print("   Clicking...")
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)
            
            # Check new URL
            new_url = driver.current_url
            print(f"   New URL: {new_url}")
            
            if new_url != current_url:
                print(f"\n✅ SUCCESS! Navigation worked!")
                print(f"   Remix URL: {new_url}")
                
                # Try to go back
                print("\n   Going back...")
                driver.back()
                time.sleep(2)
                
                final_url = driver.current_url
                print(f"   Back to: {final_url}")
                
                if final_url == current_url:
                    print("   ✅ Back navigation works!")
                else:
                    print("   ⚠️  Back navigation might have issues")
            else:
                print(f"\n❌ FAILED: URL didn't change")
                print("   Button might not be clickable or page structure changed")
                
        else:
            print("❌ No buttons found")
        
        print("\n" + "="*60)
        print("Test complete")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_click_remix()
