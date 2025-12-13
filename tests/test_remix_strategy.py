#!/usr/bin/env python3
"""
NEW STRATEGY for remix navigation based on user feedback:

1. Load ALL remixes first (click "Load more" until no more)
2. Extract URLs from all remix buttons
3. Visit each URL one by one

This avoids stale element issues completely!
"""

import sys
import time
import random
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver(use_existing=False, debug_port=9222):
    """Setup Selenium WebDriver"""
    chrome_options = Options()
    
    if use_existing:
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    else:
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    print("📥 Setting up ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("✅ Connected!")
    
    return driver

def load_all_remixes(driver, max_remixes=None):
    """Click 'Load more' button repeatedly until all remixes are loaded"""
    print("\n" + "="*70)
    print("🔄 LOADING REMIXES")
    print("="*70)
    
    if max_remixes:
        print(f"Target: {max_remixes} remixes")
    else:
        print("Target: ALL remixes")
    
    loaded_count = 0
    max_attempts = 50  # Safety limit
    
    for attempt in range(max_attempts):
        # Count current remix buttons
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        remix_buttons = [b for b in all_buttons 
                        if "h-8" in (b.get_attribute("class") or "") 
                        and "w-6" in (b.get_attribute("class") or "")
                        and "border-[1.5px]" not in (b.get_attribute("class") or "")]
        
        current_count = len(remix_buttons)
        print(f"\n[Attempt {attempt + 1}] Currently visible: {current_count} remixes")
        
        # Check if we've reached the target
        if max_remixes and current_count >= max_remixes:
            print(f"✅ Reached target of {max_remixes} remixes! Stopping.")
            break
        
        # Find the "Load more" button (last button with backdrop-blur)
        load_more_button = None
        for button in all_buttons:
            try:
                # Load more has specific size and backdrop-blur child
                classes = button.get_attribute("class") or ""
                if "w-4" in classes and "shrink-0" in classes:
                    # Check for backdrop-blur div child
                    divs = button.find_elements(By.TAG_NAME, "div")
                    for div in divs:
                        div_classes = div.get_attribute("class") or ""
                        if "backdrop-blur" in div_classes:
                            load_more_button = button
                            break
                if load_more_button:
                    break
            except:
                continue
        
        if not load_more_button:
            print("✅ No more 'Load more' button found - all remixes loaded!")
            break
        
        try:
            print("   🖱️  Clicking 'Load more'...")
            
            # Scroll to button (horizontal scroll)
            driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center', inline: 'end'});
            """, load_more_button)
            
            # Random delay
            delay = random.uniform(1.5, 3.0)
            print(f"   ⏳ Waiting {delay:.1f}s...")
            time.sleep(delay)
            
            # Click
            load_more_button.click()
            loaded_count += 1
            
            # Wait for new content to load
            time.sleep(random.uniform(2.0, 3.5))
            
        except Exception as e:
            print(f"   ⚠️  Could not click: {e}")
            break
    
    # Final count
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    remix_buttons = [b for b in all_buttons 
                    if "h-8" in (b.get_attribute("class") or "") 
                    and "w-6" in (b.get_attribute("class") or "")
                    and "border-[1.5px]" not in (b.get_attribute("class") or "")]
    
    print(f"\n✅ Finished loading! Total remixes: {len(remix_buttons)}")
    print(f"   Clicked 'Load more' {loaded_count} times")
    return len(remix_buttons)

def extract_remix_urls(driver):
    """Extract URLs from all remix buttons by clicking them briefly"""
    print("\n" + "="*70)
    print("📍 EXTRACTING REMIX URLS")
    print("="*70)
    
    start_url = driver.current_url
    urls = []
    
    # We need to click each button to get its URL
    # But we'll do it more carefully to avoid losing connection
    
    attempt = 0
    max_attempts = 100  # Safety limit
    
    while attempt < max_attempts:
        # Re-fetch buttons each time
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        remix_buttons = [b for b in all_buttons 
                        if "h-8" in (b.get_attribute("class") or "") 
                        and "w-6" in (b.get_attribute("class") or "")
                        and "border-[1.5px]" not in (b.get_attribute("class") or "")]
        
        print(f"\n[Attempt {attempt + 1}] Found {len(remix_buttons)} buttons, extracted {len(urls)} URLs so far")
        
        if attempt >= len(remix_buttons):
            print("✅ Processed all buttons!")
            break
        
        try:
            button = remix_buttons[attempt]
            
            # Scroll to button
            driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center', inline: 'center'});
            """, button)
            time.sleep(0.3)
            
            # Click
            print(f"   🖱️  Clicking button {attempt + 1}...")
            button.click()
            time.sleep(1.0)
            
            # Get URL
            new_url = driver.current_url
            if new_url != start_url and new_url not in urls:
                urls.append(new_url)
                print(f"   ✅ New URL: {new_url}")
            else:
                print(f"   ⚠️  Same URL or duplicate")
            
            # Go back
            driver.back()
            time.sleep(1.0)
            
            # Verify we're back
            if driver.current_url != start_url:
                print(f"   🔙 Not on start page, navigating back...")
                driver.get(start_url)
                time.sleep(1.5)
            
        except Exception as e:
            print(f"   ❌ Error on button {attempt + 1}: {e}")
            # Try to recover
            try:
                if driver.current_url != start_url:
                    driver.get(start_url)
                    time.sleep(1.5)
            except:
                print("   ⚠️  Could not recover, stopping extraction")
                break
        
        attempt += 1
    
    print(f"\n✅ Extracted {len(urls)} unique remix URLs")
    
    # Show URLs
    for i, url in enumerate(urls[:10]):
        print(f"   {i+1}. {url}")
    
    if len(urls) > 10:
        print(f"   ... and {len(urls) - 10} more")
    
    return urls

def extract_video_url_from_page(driver):
    """Extract video URL from current page"""
    try:
        video_elements = driver.find_elements(By.TAG_NAME, "video")
        for video in video_elements:
            src = video.get_attribute("src")
            if src and src.startswith("http"):
                return src
        
        # Try source elements
        source_elements = driver.find_elements(By.TAG_NAME, "source")
        for source in source_elements:
            src = source.get_attribute("src")
            if src and src.startswith("http"):
                return src
    except Exception as e:
        print(f"      ⚠️  Error extracting video URL: {e}")
    return None

def download_video(video_url, output_path):
    """Download video from URL"""
    try:
        print(f"      📥 Downloading video...")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_size) * 100
                        print(f"      Progress: {percent:.1f}%", end='\r')
        
        print(f"\n      ✅ Video saved: {output_path}")
        return True
    except Exception as e:
        print(f"      ❌ Download failed: {e}")
        return False

def extract_metadata(driver, page_url):
    """Extract metadata from current page"""
    metadata = {
        "url": page_url,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": None,
        "description": None,
        "creator": None
    }
    
    try:
        # Try to extract title
        try:
            metadata["title"] = driver.title
        except:
            pass
        
        # Try to extract description/prompt
        try:
            description_elements = driver.find_elements(By.CSS_SELECTOR, "p, div[class*='description'], div[class*='prompt']")
            for elem in description_elements[:3]:  # Check first 3
                text = elem.text.strip()
                if text and len(text) > 10:
                    metadata["description"] = text
                    break
        except:
            pass
        
        # Try to extract creator
        try:
            creator_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='user'], a[href*='profile']")
            if creator_elements:
                metadata["creator"] = creator_elements[0].text.strip()
        except:
            pass
        
    except Exception as e:
        print(f"      ⚠️  Error extracting metadata: {e}")
    
    return metadata

def visit_and_scrape_remixes(driver, remix_urls, max_remixes=None, output_dir="videos", metadata_mode=False):
    """Visit each remix URL and scrape it"""
    print("\n" + "="*70)
    print("🎬 VISITING AND SCRAPING REMIXES")
    print("="*70)
    
    # Create output directory
    import pathlib
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Limit number of remixes if specified
    if max_remixes and max_remixes < len(remix_urls):
        print(f"⚠️  Limiting to {max_remixes} remixes (out of {len(remix_urls)} available)")
        remix_urls = remix_urls[:max_remixes]
    
    all_metadata = []
    
    for i, url in enumerate(remix_urls):
        print(f"\n[{i+1}/{len(remix_urls)}] Visiting: {url}")
        
        try:
            # Random delay before navigation
            delay = random.uniform(2.0, 4.0)
            print(f"   ⏳ Waiting {delay:.1f}s...")
            time.sleep(delay)
            
            # Navigate to remix
            driver.get(url)
            time.sleep(random.uniform(2.0, 3.0))
            
            print("   ✅ Page loaded")
            
            # Extract metadata
            print("   📊 Extracting metadata...")
            metadata = extract_metadata(driver, url)
            all_metadata.append(metadata)
            
            if not metadata_mode:
                # Extract video URL
                print("   🎥 Looking for video...")
                video_url = extract_video_url_from_page(driver)
                
                if video_url:
                    print(f"      ✅ Found video URL")
                    metadata["video_url"] = video_url
                    
                    # Download video
                    video_filename = f"remix_{i+1:03d}.mp4"
                    video_path = output_path / video_filename
                    
                    if download_video(video_url, video_path):
                        metadata["downloaded_file"] = str(video_path)
                else:
                    print("      ⚠️  No video found on page")
            
            # Save individual metadata
            metadata_file = output_path / f"remix_{i+1:03d}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"   💾 Metadata saved: {metadata_file}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Save combined metadata
    combined_file = output_path / "all_remixes_metadata.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Combined metadata saved: {combined_file}")
    
    return all_metadata

def main():
    print("="*70)
    print("🧪 NEW REMIX STRATEGY TEST")
    print("="*70)
    print()
    print("Strategy:")
    print("1. Load ALL remixes (click 'Load more' repeatedly)")
    print("2. Extract URLs from all remix buttons")
    print("3. Visit each URL one by one to scrape")
    print()
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python test_remix_strategy.py <video-url> [--max N] [--use-existing]")
        print()
        print("Options:")
        print("  --max N          Limit to N remixes (e.g., --max 50)")
        print("  --use-existing   Connect to existing Chrome session")
        print()
        print("Example:")
        print("  python test_remix_strategy.py https://sora.chatgpt.com/p/video_id --max 50 --use-existing")
        sys.exit(1)
    
    start_url = sys.argv[1]
    use_existing = "--use-existing" in sys.argv
    
    # Parse --max argument
    max_remixes = None
    if "--max" in sys.argv:
        try:
            max_idx = sys.argv.index("--max")
            max_remixes = int(sys.argv[max_idx + 1])
        except (IndexError, ValueError):
            print("❌ Error: --max requires a number")
            sys.exit(1)
    
    print(f"🔧 Setup:")
    print(f"   URL: {start_url}")
    print(f"   Mode: {'Existing Chrome' if use_existing else 'New browser'}")
    print(f"   Max remixes: {max_remixes if max_remixes else 'Unlimited'}")
    print()
    
    if use_existing:
        print("🔗 Connecting to existing Chrome (port 9222)...")
        print("   Make sure Chrome is running with:")
        print("   open -a 'Google Chrome' --args --remote-debugging-port=9222")
        print()
    
    # Setup driver
    driver = setup_driver(use_existing=use_existing)
    
    try:
        # Navigate to start URL
        if not use_existing or driver.current_url != start_url:
            print(f"🌐 Navigating to: {start_url}")
            driver.get(start_url)
            time.sleep(3.0)
        
        # Step 1: Load remixes (up to max_remixes if specified)
        total_remixes = load_all_remixes(driver, max_remixes=max_remixes)
        
        if total_remixes == 0:
            print("\n❌ No remixes found!")
            return
        
        # Step 2: Extract URLs
        remix_urls = extract_remix_urls(driver)
        
        if len(remix_urls) == 0:
            print("\n❌ Could not extract any URLs!")
            return
        
        # Step 3: Visit and scrape each remix
        visit_and_scrape_remixes(driver, remix_urls, max_remixes=max_remixes, output_dir="videos", metadata_mode=False)
        
        actual_processed = min(len(remix_urls), max_remixes) if max_remixes else len(remix_urls)
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED!")
        print("="*70)
        print(f"📊 Total remixes processed: {actual_processed}")
        if max_remixes and len(remix_urls) > max_remixes:
            print(f"   ({len(remix_urls) - max_remixes} remixes skipped due to --max limit)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not use_existing:
            print("\n🔒 Closing browser...")
            driver.quit()
        else:
            print("\n✅ Keeping Chrome open (existing session)")

if __name__ == "__main__":
    main()
