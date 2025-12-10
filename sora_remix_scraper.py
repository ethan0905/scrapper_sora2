#!/usr/bin/env python3
"""
Sora Remix Scraper - Production Version

A robust scraper for Sora remixes that:
1. Loads all remix buttons (using "Load more" until target count)
2. Navigates to each remix by clicking on button with thumbnails
3. Downloads video and metadata from each page
4. Supports user-specified limits (--max N)
5. Avoids stale element errors and Chrome disconnections
"""

import sys
import time
import random
import json
import pathlib
import argparse
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class SoraRemixScraper:
    """Main scraper class for Sora remixes"""
    
    def __init__(self, use_existing_chrome=False, debug_port=9222, output_dir="videos"):
        self.driver = None
        self.use_existing_chrome = use_existing_chrome
        self.debug_port = debug_port
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        
        if self.use_existing_chrome:
            print("🔗 Connecting to existing Chrome session...")
            print(f"   Port: {self.debug_port}")
            print("\n💡 If Chrome is not running with remote debugging, launch:")
            print(f'   open -a "Google Chrome" --args --remote-debugging-port={self.debug_port}')
            print()
            
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
        else:
            print("🚀 Launching new Chrome session...")
            # Anti-detection settings
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        if not self.use_existing_chrome:
            # Hide automation markers
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Browser ready!\n")
        return self.driver
    
    def get_remix_buttons(self):
        """Get all remix thumbnail buttons on current page"""
        try:
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            # Filter for remix buttons (specific size classes, excluding "Load more" button)
            remix_buttons = []
            for b in all_buttons:
                try:
                    class_attr = b.get_attribute("class") or ""
                    if ("h-8" in class_attr 
                        and "w-6" in class_attr 
                        and "border-[1.5px]" not in class_attr):
                        remix_buttons.append(b)
                except:
                    # Skip stale elements
                    continue
            
            return remix_buttons
        except:
            return []
    
    def find_load_more_button(self):
        """Find the 'Load more' button"""
        all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
        
        for button in all_buttons:
            try:
                classes = button.get_attribute("class") or ""
                # Load more button has specific size classes
                if "w-4" in classes and "shrink-0" in classes:
                    # Check for backdrop-blur div child (signature of load more button)
                    divs = button.find_elements(By.TAG_NAME, "div")
                    for div in divs:
                        div_classes = div.get_attribute("class") or ""
                        if "backdrop-blur" in div_classes:
                            return button
            except:
                continue
        
        return None
    
    def load_all_remixes(self, target_count=None):
        """
        Click 'Load more' repeatedly until target count is reached or no more remixes
        
        Args:
            target_count: Maximum number of remixes to load (None = all)
        
        Returns:
            int: Number of remixes loaded
        """
        print("="*70)
        print("🔄 LOADING REMIXES")
        print("="*70)
        
        if target_count:
            print(f"Target: {target_count} remixes\n")
        else:
            print("Target: ALL remixes\n")
        
        load_more_clicks = 0
        max_attempts = 100  # Safety limit
        
        for attempt in range(max_attempts):
            # Count current remixes
            remix_buttons = self.get_remix_buttons()
            current_count = len(remix_buttons)
            
            print(f"[Attempt {attempt + 1}] Currently visible: {current_count} remixes")
            
            # Check if we've reached target
            if target_count and current_count >= target_count:
                print(f"✅ Reached target of {target_count} remixes!\n")
                break
            
            # Find and click "Load more"
            load_more_button = self.find_load_more_button()
            
            if not load_more_button:
                print("✅ No more 'Load more' button - all remixes loaded!\n")
                break
            
            try:
                # Scroll to button (horizontal scroll)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'end'});",
                    load_more_button
                )
                
                # Random human-like delay
                delay = random.uniform(1.5, 2.5)
                time.sleep(delay)
                
                # Click
                load_more_button.click()
                load_more_clicks += 1
                
                # Wait for new content
                time.sleep(random.uniform(2.0, 3.0))
                
            except Exception as e:
                print(f"⚠️  Could not click 'Load more': {e}\n")
                break
        
        # Final count
        final_buttons = self.get_remix_buttons()
        print(f"✅ Finished loading!")
        print(f"   Total remixes visible: {len(final_buttons)}")
        print(f"   'Load more' clicks: {load_more_clicks}\n")
        
        return len(final_buttons)
    
    def extract_video_url(self):
        """Extract video URL from current page"""
        try:
            # Try <video> tags first
            video_elements = self.driver.find_elements(By.TAG_NAME, "video")
            for video in video_elements:
                src = video.get_attribute("src")
                if src and src.startswith("http"):
                    return src
            
            # Try <source> tags
            source_elements = self.driver.find_elements(By.TAG_NAME, "source")
            for source in source_elements:
                src = source.get_attribute("src")
                if src and src.startswith("http"):
                    return src
        except Exception as e:
            print(f"      ⚠️  Error extracting video URL: {e}")
        
        return None
    
    def download_video(self, video_url, output_path):
        """
        Download video from URL
        
        Args:
            video_url: URL of the video
            output_path: Path to save the video
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"      📥 Downloading video...")
            response = requests.get(video_url, stream=True, timeout=60)
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
            
            print(f"\n      ✅ Video saved ({total_size / 1024 / 1024:.1f} MB)")
            return True
        
        except Exception as e:
            print(f"\n      ❌ Download failed: {e}")
            return False
    
    def extract_metadata(self, page_url):
        """
        Extract metadata from current page
        
        Args:
            page_url: URL of the current page
        
        Returns:
            dict: Metadata dictionary
        """
        metadata = {
            "url": page_url,
            "scraped_at": datetime.now().isoformat(),
            "title": None,
            "description": None,
            "creator": None,
            "video_url": None,
            "downloaded_file": None
        }
        
        try:
            # Extract page title
            try:
                metadata["title"] = self.driver.title
            except:
                pass
            
            # Extract description/prompt
            try:
                # Look for text elements that might contain the prompt
                text_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "p, div[class*='description'], div[class*='prompt'], div[class*='text']"
                )
                
                for elem in text_elements[:5]:  # Check first 5
                    text = elem.text.strip()
                    if text and len(text) > 20 and len(text) < 1000:
                        metadata["description"] = text
                        break
            except:
                pass
            
            # Extract creator/author
            try:
                creator_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "a[href*='user'], a[href*='profile'], span[class*='author'], span[class*='creator']"
                )
                
                if creator_elements:
                    creator_text = creator_elements[0].text.strip()
                    if creator_text:
                        metadata["creator"] = creator_text
            except:
                pass
        
        except Exception as e:
            print(f"      ⚠️  Error extracting metadata: {e}")
        
        return metadata
    
    def scrape_remixes(self, start_url, max_remixes=None, download_videos=True):
        """
        Main scraping function
        
        Args:
            start_url: URL of the page with remixes
            max_remixes: Maximum number of remixes to scrape (None = all)
            download_videos: Whether to download videos or just metadata
        
        Returns:
            list: List of metadata dictionaries
        """
        print("="*70)
        print("🎬 SORA REMIX SCRAPER")
        print("="*70)
        print(f"Start URL: {start_url}")
        print(f"Max remixes: {max_remixes if max_remixes else 'Unlimited'}")
        print(f"Download videos: {'Yes' if download_videos else 'No (metadata only)'}")
        print(f"Output directory: {self.output_dir}")
        print()
        
        # Navigate to start URL
        print(f"🌐 Navigating to start URL...")
        self.driver.get(start_url)
        time.sleep(3.0)
        print("✅ Page loaded\n")
        
        # Step 1: Load all remixes
        total_loaded = self.load_all_remixes(target_count=max_remixes)
        
        if total_loaded == 0:
            print("❌ No remixes found!")
            return []
        
        # Step 2: Scrape each remix
        print("="*70)
        print("📍 SCRAPING REMIXES")
        print("="*70)
        
        # Limit to max_remixes if specified
        remixes_to_process = min(total_loaded, max_remixes) if max_remixes else total_loaded
        print(f"Will process: {remixes_to_process} remixes\n")
        
        all_metadata = []
        successful_downloads = 0
        start_page_url = self.driver.current_url  # Remember the start page URL
        
        for i in range(remixes_to_process):
            print(f"[{i+1}/{remixes_to_process}] Processing remix...")
            
            try:
                # Re-fetch remix buttons (avoid stale elements)
                remix_buttons = self.get_remix_buttons()
                
                if i >= len(remix_buttons):
                    print(f"   ⚠️  Button index {i} out of range (only {len(remix_buttons)} buttons)")
                    print(f"   🔄 Trying to return to start page and reload...")
                    
                    # Try to get back to the start page
                    try:
                        self.driver.get(start_page_url)
                        time.sleep(3.0)
                        
                        # Re-check buttons
                        remix_buttons = self.get_remix_buttons()
                        if i >= len(remix_buttons):
                            print(f"   ❌ Still can't find button {i}, skipping...")
                            continue
                        else:
                            print(f"   ✅ Found {len(remix_buttons)} buttons after reload")
                    except:
                        print(f"   ❌ Failed to reload, skipping this remix")
                        continue
                
                button = remix_buttons[i]
                
                # Scroll to button
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                    button
                )
                time.sleep(0.5)
                
                # Click button to navigate to remix
                print(f"   🖱️  Clicking remix thumbnail...")
                button.click()
                
                # Wait for page load
                time.sleep(random.uniform(2.0, 3.0))
                
                current_url = self.driver.current_url
                print(f"   ✅ Navigated to: {current_url}")
                
                # Extract metadata
                print(f"   📊 Extracting metadata...")
                metadata = self.extract_metadata(current_url)
                
                # Extract and download video
                if download_videos:
                    print(f"   🎥 Looking for video...")
                    video_url = self.extract_video_url()
                    
                    if video_url:
                        print(f"      ✅ Found video URL")
                        metadata["video_url"] = video_url
                        
                        # Download video
                        video_filename = f"remix_{i+1:04d}.mp4"
                        video_path = self.output_dir / video_filename
                        
                        if self.download_video(video_url, video_path):
                            metadata["downloaded_file"] = str(video_path)
                            successful_downloads += 1
                    else:
                        print(f"      ⚠️  No video found")
                
                # Save individual metadata
                metadata_file = self.output_dir / f"remix_{i+1:04d}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                print(f"   💾 Metadata saved: {metadata_file.name}")
                
                all_metadata.append(metadata)
                
                # Navigate back to main page
                print(f"   🔙 Navigating back to main page...")
                self.driver.back()
                time.sleep(2.0)
                
                # Wait for remix buttons to reload
                print(f"   ⏳ Waiting for page to reload...")
                max_wait = 10
                wait_start = time.time()
                buttons_loaded = False
                
                while time.time() - wait_start < max_wait:
                    try:
                        # Check if buttons are back
                        test_buttons = self.get_remix_buttons()
                        if len(test_buttons) > i:  # Make sure we have enough buttons
                            buttons_loaded = True
                            print(f"   ✅ Found {len(test_buttons)} remix buttons")
                            break
                    except:
                        pass
                    time.sleep(0.5)
                
                if not buttons_loaded:
                    print(f"   ⚠️  Buttons didn't reload, trying to refresh page...")
                    self.driver.refresh()
                    time.sleep(3.0)
                
                # Random delay between remixes (human-like behavior)
                if i < remixes_to_process - 1:  # Don't delay after last one
                    delay = random.uniform(1.0, 2.0)
                    time.sleep(delay)
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error processing remix {i+1}: {e}")
                import traceback
                traceback.print_exc()
                
                # Try to recover by going back
                try:
                    print(f"   🔄 Attempting to recover...")
                    self.driver.back()
                    time.sleep(2.0)
                except:
                    print(f"   ⚠️  Recovery failed")
                
                print()
                continue
        
        # Save combined metadata
        combined_file = self.output_dir / "all_remixes_metadata.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scraped_at": datetime.now().isoformat(),
                "total_remixes": len(all_metadata),
                "successful_downloads": successful_downloads,
                "remixes": all_metadata
            }, f, indent=2, ensure_ascii=False)
        
        print("="*70)
        print("✅ SCRAPING COMPLETED!")
        print("="*70)
        print(f"📊 Statistics:")
        print(f"   Total remixes processed: {len(all_metadata)}")
        print(f"   Successful downloads: {successful_downloads}")
        print(f"   Metadata saved: {combined_file}")
        print()
        
        return all_metadata
    
    def close(self):
        """Close the browser"""
        if self.driver and not self.use_existing_chrome:
            print("🔒 Closing browser...")
            self.driver.quit()
        elif self.driver and self.use_existing_chrome:
            print("✅ Keeping Chrome open (existing session)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sora Remix Scraper - Download videos and metadata from Sora remixes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all remixes (new Chrome session)
  python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID
  
  # Scrape first 50 remixes
  python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --max 50
  
  # Use existing Chrome session (you must be logged in)
  python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --use-existing
  
  # Metadata only (no video download)
  python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --metadata-only
  
  # Custom output directory
  python sora_remix_scraper.py https://sora.chatgpt.com/p/VIDEO_ID --output my_videos
        """
    )
    
    parser.add_argument(
        "url",
        help="URL of the Sora video page with remixes"
    )
    
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of remixes to scrape (default: all)"
    )
    
    parser.add_argument(
        "--use-existing",
        action="store_true",
        help="Connect to existing Chrome session (requires Chrome running with --remote-debugging-port=9222)"
    )
    
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Only extract metadata, don't download videos"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="videos",
        metavar="DIR",
        help="Output directory for videos and metadata (default: videos)"
    )
    
    parser.add_argument(
        "--debug-port",
        type=int,
        default=9222,
        metavar="PORT",
        help="Chrome remote debugging port (default: 9222)"
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = SoraRemixScraper(
        use_existing_chrome=args.use_existing,
        debug_port=args.debug_port,
        output_dir=args.output
    )
    
    try:
        # Setup browser
        scraper.setup_driver()
        
        # Run scraper
        scraper.scrape_remixes(
            start_url=args.url,
            max_remixes=args.max,
            download_videos=not args.metadata_only
        )
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
