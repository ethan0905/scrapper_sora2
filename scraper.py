#!/usr/bin/env python3
"""
Sora Remix Scraper - Main orchestrator (simplified version)

Clean approach:
1. Load all remixes using "Load more"
2. Loop through index 0, 1, 2, 3... until max_remixes
3. For each index:
   - Get fresh buttons
   - Click button[i]
   - Download video
   - Go back
   - Wait for page reload
   - Continue to next index
"""

import time
import random
import json
import pathlib
import argparse
from datetime import datetime

from browser_manager import BrowserManager
from remix_navigator import RemixNavigator
from video_downloader import VideoDownloader
from metadata_extractor import MetadataExtractor


class SoraRemixScraper:
    """Main scraper orchestrator"""
    
    def __init__(self, use_existing_chrome=False, debug_port=9222, output_dir="videos", slow_mode=False):
        self.browser_mgr = BrowserManager(use_existing_chrome, debug_port)
        self.driver = None
        self.navigator = None
        self.downloader = None
        self.metadata_extractor = None
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.slow_mode = slow_mode
        self.use_existing_chrome = use_existing_chrome
        self.debug_port = debug_port
        
        # Progress tracking
        self.progress_file = self.output_dir / ".batch_progress.json"
        self.checkpoint_file = self.output_dir / ".scrape_checkpoint.json"
        
        # Slow mode delays (in seconds)
        if slow_mode:
            self.delays = {
                'after_click': (3.0, 5.0),       # After clicking a button
                'before_download': (2.0, 4.0),   # Before starting download
                'after_download': (2.0, 3.0),    # After download completes
                'page_load': (4.0, 6.0),         # Waiting for page to load
                'between_remixes': (3.0, 5.0)    # Between processing remixes
            }
            print("🐢 SLOW MODE ENABLED - Human-like delays activated")
        else:
            self.delays = {
                'after_click': (1.0, 2.0),
                'before_download': (0.5, 1.0),
                'after_download': (1.0, 1.5),
                'page_load': (2.0, 3.0),
                'between_remixes': (1.0, 2.0)
            }
            print("🚀 NORMAL MODE - Standard delays")
    
    def setup(self):
        """Initialize all components"""
        self.driver = self.browser_mgr.setup()
        self.navigator = RemixNavigator(self.driver)
        self.downloader = VideoDownloader(self.driver)
        self.metadata_extractor = MetadataExtractor(self.driver)
    
    def _sleep(self, delay_type):
        """
        Sleep for a random duration based on delay type
        
        Args:
            delay_type: Type of delay ('after_click', 'before_download', etc.)
        """
        if delay_type in self.delays:
            min_delay, max_delay = self.delays[delay_type]
            delay = random.uniform(min_delay, max_delay)
            if self.slow_mode:
                time.sleep(delay)
            else:
                time.sleep(delay)
    
    def _is_session_error(self, exception):
        """Check if exception is a session/connection error"""
        error_keywords = [
            "invalid session id",
            "session deleted",
            "chrome not reachable",
            "connection refused",
            "disconnected",
            "target window already closed"
        ]
        error_msg = str(exception).lower()
        return any(keyword in error_msg for keyword in error_keywords)
    
    def _load_progress(self):
        """Load batch processing progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {"completed_urls": []}
        return {"completed_urls": []}
    
    def _save_progress(self, url):
        """Save completed URL to progress file"""
        try:
            progress = self._load_progress()
            if url not in progress["completed_urls"]:
                progress["completed_urls"].append(url)
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save progress: {e}")
    
    def _is_completed(self, url):
        """Check if URL has already been processed"""
        progress = self._load_progress()
        return url in progress["completed_urls"]
    
    def _load_checkpoint(self, url):
        """Load checkpoint for a specific URL"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoints = json.load(f)
                    return checkpoints.get(url, {"last_completed_index": -1})
            except:
                return {"last_completed_index": -1}
        return {"last_completed_index": -1}
    
    def _save_checkpoint(self, url, index):
        """Save checkpoint after processing a remix"""
        try:
            checkpoints = {}
            if self.checkpoint_file.exists():
                try:
                    with open(self.checkpoint_file, 'r') as f:
                        checkpoints = json.load(f)
                except:
                    pass
            
            checkpoints[url] = {
                "last_completed_index": index,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoints, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save checkpoint: {e}")
    
    def _clear_checkpoint(self, url):
        """Clear checkpoint for a URL after successful completion"""
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'r') as f:
                    checkpoints = json.load(f)
                
                if url in checkpoints:
                    del checkpoints[url]
                    
                with open(self.checkpoint_file, 'w') as f:
                    json.dump(checkpoints, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not clear checkpoint: {e}")
    
    def _recover_session(self):
        """Attempt to recover browser session if lost"""
        try:
            print("🔄 Browser session lost, attempting to reconnect...")
            
            # Close old session if it exists
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass
            
            # Reinitialize browser completely
            print("   🔧 Restarting Chrome browser...")
            self.browser_mgr = BrowserManager(self.use_existing_chrome, self.debug_port)
            self.driver = self.browser_mgr.setup()
            self.navigator = RemixNavigator(self.driver, slow_mode=self.slow_mode)
            self.downloader = VideoDownloader(self.driver)
            self.metadata_extractor = MetadataExtractor(self.driver)
            
            print("✅ Browser session recovered")
            return True
        
        except Exception as e:
            print(f"❌ Failed to recover session: {e}")
            return False
    
    def scrape_remixes(self, start_url, max_remixes=None, download_videos=True, retry_on_error=True):
        """
        Main scraping function - simplified approach with session recovery and checkpointing
        
        Args:
            start_url: URL of the page with remixes
            max_remixes: Maximum number of remixes to scrape
            download_videos: Whether to download videos or just metadata
            retry_on_error: Whether to retry on session errors
        """
        print("="*70)
        print("🎬 SORA REMIX SCRAPER")
        print("="*70)
        print(f"Start URL: {start_url}")
        print(f"Max remixes: {max_remixes if max_remixes else 'Unlimited'}")
        print(f"Download videos: {'Yes' if download_videos else 'No'}")
        print(f"Output directory: {self.output_dir}")
        
        # Check for checkpoint
        checkpoint = self._load_checkpoint(start_url)
        last_completed = checkpoint["last_completed_index"]
        
        if last_completed >= 0:
            print(f"📍 Found checkpoint: Last completed remix index = {last_completed}")
            print(f"🔄 Will resume from index {last_completed + 1}")
        print()
        
        # Navigate to start URL with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🌐 Navigating to start URL...")
                print(f"🔍 DEBUG: Start URL = {start_url}")
                self.driver.get(start_url)
                self._sleep('page_load')
                
                # Verify we're on the right page
                actual_url = self.driver.current_url
                print(f"🔍 DEBUG: Actual URL after navigation = {actual_url}")
                print("✅ Page loaded\n")
                break
            
            except Exception as e:
                if self._is_session_error(e) and retry_on_error and attempt < max_retries - 1:
                    print(f"⚠️  Session error on attempt {attempt + 1}/{max_retries}")
                    if self._recover_session():
                        print(f"🔄 Retrying navigation...")
                        continue
                raise
        
        # Step 1: Load all remixes
        total_loaded = self.navigator.load_all_remixes(target_count=max_remixes)
        
        if total_loaded == 0:
            print("❌ No remixes found!")
            return []
        
        # Step 2: Determine how many to process
        remixes_to_process = min(total_loaded, max_remixes) if max_remixes else total_loaded
        
        print("="*70)
        print("📍 SCRAPING REMIXES")
        print("="*70)
        print(f"Will process: {remixes_to_process} remixes\n")
        
        all_metadata = []
        successful_downloads = 0
        
        # Step 2.5: First, download the START page (if not already done)
        if last_completed < 0:  # Haven't processed start page yet
            print(f"[0/{remixes_to_process}] Processing START page...")
            print(f"🔍 DEBUG: Start page URL = {self.driver.current_url}")
            
            try:
                start_page_url = self.driver.current_url
                
                # Extract metadata
                print(f"   📊 Extracting metadata from start page...")
                metadata = self.metadata_extractor.extract_metadata(start_page_url)
                
                # Download video if requested
                if download_videos:
                    print(f"   🎥 Looking for video...")
                    video_url = self.downloader.extract_video_url()
                    
                    if video_url:
                        print(f"      ✅ Found video URL")
                        metadata["video_url"] = video_url
                        
                        video_filename = f"remix_0000_start.mp4"
                        video_path = self.output_dir / video_filename
                        
                        if self.downloader.download_video(video_url, video_path):
                            metadata["downloaded_file"] = str(video_path)
                            successful_downloads += 1
                    else:
                        print(f"      ⚠️  No video found")
                
                # Save metadata
                metadata_file = self.output_dir / f"remix_0000_start_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                print(f"   💾 Metadata saved: {metadata_file.name}")
                
                all_metadata.append(metadata)
                print()
                
            except Exception as e:
                print(f"   ❌ Error processing start page: {e}")
                print()
        else:
            print(f"⏭️  Skipping start page (already processed)")
            print()
        
        # Step 3: Loop through remixes with checkpoint support
        start_index = max(0, last_completed + 1)
        
        if start_index > 0:
            print(f"🔄 Resuming from remix index {start_index}")
            print()
        
        for i in range(start_index, remixes_to_process):
            print(f"[{i+1}/{remixes_to_process}] Processing remix {i}...")
            print(f"🔍 DEBUG: Current page URL = {self.driver.current_url}")
            
            remix_success = False
            max_remix_retries = 3
            
            for retry_attempt in range(max_remix_retries):
                try:
                    # Click the button at index i
                    print(f"   🖱️  Clicking remix thumbnail {i}...")
                    if not self.navigator.click_remix_button(i):
                        print(f"   ⚠️  Skipping remix {i}")
                        break
                    
                    self._sleep('after_click')
                    
                    current_url = self.driver.current_url
                    print(f"   ✅ Navigated to: {current_url}")
                    
                    # Extract metadata
                    print(f"   📊 Extracting metadata...")
                    metadata = self.metadata_extractor.extract_metadata(current_url)
                    
                    # Download video if requested
                    if download_videos:
                        self._sleep('before_download')
                        print(f"   🎥 Looking for video...")
                        video_url = self.downloader.extract_video_url()
                        
                        if video_url:
                            print(f"      ✅ Found video URL")
                            metadata["video_url"] = video_url
                            
                            # Download
                            video_filename = f"remix_{i+1:04d}.mp4"
                            video_path = self.output_dir / video_filename
                            
                            if self.downloader.download_video(video_url, video_path):
                                metadata["downloaded_file"] = str(video_path)
                                successful_downloads += 1
                                self._sleep('after_download')
                        else:
                            print(f"      ⚠️  No video found")
                    
                    # Save individual metadata
                    metadata_file = self.output_dir / f"remix_{i+1:04d}_metadata.json"
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    print(f"   💾 Metadata saved: {metadata_file.name}")
                    
                    all_metadata.append(metadata)
                    
                    # Save checkpoint after successful processing
                    self._save_checkpoint(start_url, i)
                    print(f"   💾 Checkpoint saved (index {i})")
                    
                    remix_success = True
                    print()
                    break  # Success, exit retry loop
                
                except Exception as e:
                    error_msg = str(e)
                    
                    # Check if it's a session error
                    if self._is_session_error(e) and retry_attempt < max_remix_retries - 1:
                        print(f"   ⚠️  Session error on retry {retry_attempt + 1}/{max_remix_retries}")
                        print(f"   🔄 Attempting to recover and continue...")
                        
                        if self._recover_session():
                            # Navigate back to start URL
                            try:
                                print(f"   🌐 Navigating back to: {start_url}")
                                self.driver.get(start_url)
                                self._sleep('page_load')
                                
                                # Reload remixes
                                print(f"   🔄 Reloading remixes...")
                                self.navigator.load_all_remixes(target_count=max_remixes)
                                
                                print(f"   🔄 Retrying remix {i}...")
                                continue
                            except Exception as nav_error:
                                print(f"   ❌ Failed to navigate back: {nav_error}")
                        else:
                            print(f"   ❌ Session recovery failed")
                    
                    # If not a session error or last retry, log and continue
                    if retry_attempt == max_remix_retries - 1:
                        if len(error_msg) > 200:
                            error_msg = error_msg[:200] + "..."
                        print(f"   ❌ Error after {max_remix_retries} attempts: {error_msg}")
                        print()
                        break
            
            # Continue to next remix even if this one failed
            if not remix_success:
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
        print(f"   Total processed: {len(all_metadata)}")
        print(f"   Successful downloads: {successful_downloads}")
        print(f"   Metadata file: {combined_file}")
        print()
        
        return all_metadata
    
    def close(self):
        """Close browser"""
        self.browser_mgr.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sora Remix Scraper - Download videos and metadata from Sora remixes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape first 10 remixes
  python scraper.py https://sora.chatgpt.com/p/VIDEO_ID --max 10
  
  # Use existing Chrome session
  python scraper.py https://sora.chatgpt.com/p/VIDEO_ID --use-existing --max 50
  
  # Metadata only
  python scraper.py https://sora.chatgpt.com/p/VIDEO_ID --metadata-only --max 20
  
  # Slow mode (more human-like, avoids detection)
  python scraper.py https://sora.chatgpt.com/p/VIDEO_ID --max 50 --slow --use-existing
  
  # Batch processing from file
  python scraper.py --batch urls.txt --max 50 --slow
  python scraper.py --batch urls.txt --max 100 --use-existing --slow
        """
    )
    
    parser.add_argument("url", nargs="?", help="URL of the Sora video page with remixes")
    parser.add_argument("--batch", type=str, metavar="FILE", help="Path to text file containing URLs (one per line)")
    parser.add_argument("--max", type=int, default=None, metavar="N", help="Maximum number of remixes to scrape per URL")
    parser.add_argument("--use-existing", action="store_true", help="Connect to existing Chrome session")
    parser.add_argument("--metadata-only", action="store_true", help="Only extract metadata, don't download videos")
    parser.add_argument("--output", type=str, default="videos", metavar="DIR", help="Output directory")
    parser.add_argument("--debug-port", type=int, default=9222, metavar="PORT", help="Chrome debugging port")
    parser.add_argument("--slow", action="store_true", help="Enable slow mode (longer delays, more human-like)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.batch:
        parser.error("Either provide a URL or use --batch with a file path")
    
    if args.url and args.batch:
        parser.error("Cannot use both URL and --batch. Choose one.")
    
    # Determine URLs to process
    urls_to_process = []
    
    if args.batch:
        # Read URLs from file
        try:
            batch_file = pathlib.Path(args.batch)
            if not batch_file.exists():
                print(f"❌ Error: Batch file not found: {args.batch}")
                return
            
            print(f"📄 Reading URLs from: {args.batch}")
            with open(batch_file, 'r') as f:
                urls_to_process = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            
            print(f"✅ Found {len(urls_to_process)} URL(s) to process\n")
            
            if len(urls_to_process) == 0:
                print("❌ Error: No valid URLs found in batch file")
                return
        
        except Exception as e:
            print(f"❌ Error reading batch file: {e}")
            return
    else:
        # Single URL mode
        urls_to_process = [args.url]
    
    # Create scraper
    scraper = SoraRemixScraper(
        use_existing_chrome=args.use_existing,
        debug_port=args.debug_port,
        output_dir=args.output,
        slow_mode=args.slow
    )
    
    try:
        # Setup (only once for all URLs)
        scraper.setup()
        
        # Process each URL
        total_urls = len(urls_to_process)
        
        # Load progress for batch mode
        if total_urls > 1:
            progress = scraper._load_progress()
            completed_count = len(progress["completed_urls"])
            if completed_count > 0:
                print(f"📊 Found {completed_count} already completed URL(s)")
                print(f"🔄 Will skip completed URLs and resume where left off\n")
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        
        for idx, url in enumerate(urls_to_process, 1):
            # Check if already completed (for batch mode)
            if total_urls > 1 and scraper._is_completed(url):
                skipped_count += 1
                print(f"\n⏭️  Skipping URL {idx}/{total_urls} (already completed)")
                print(f"URL: {url}")
                continue
            
            if total_urls > 1:
                print("\n" + "="*70)
                print(f"🎯 PROCESSING URL {idx}/{total_urls}")
                print("="*70)
                print(f"URL: {url}")
                print()
            
            try:
                # Run scraper on this URL with retry logic
                max_url_retries = 2
                url_success = False
                
                for url_attempt in range(max_url_retries):
                    try:
                        scraper.scrape_remixes(
                            start_url=url,
                            max_remixes=args.max,
                            download_videos=not args.metadata_only
                        )
                        url_success = True
                        break
                    
                    except Exception as scrape_error:
                        # Check if it's a session error
                        if "invalid session id" in str(scrape_error).lower() and url_attempt < max_url_retries - 1:
                            print(f"\n⚠️  Session error, attempting recovery...")
                            if scraper._recover_session():
                                print(f"🔄 Retrying URL {idx}/{total_urls}...")
                                time.sleep(2)
                                continue
                        # Re-raise if not recoverable or last attempt
                        raise
                
                if url_success:
                    processed_count += 1
                    
                    # Save progress (mark URL as completed)
                    if total_urls > 1:
                        scraper._save_progress(url)
                    
                    if total_urls > 1:
                        print(f"\n✅ Completed URL {idx}/{total_urls}")
                        
                        # Add delay between URLs if in slow mode and not the last URL
                        if args.slow and idx < total_urls:
                            wait_time = random.uniform(5.0, 8.0)
                            print(f"⏳ Waiting {wait_time:.1f}s before next URL...")
                            time.sleep(wait_time)
            
            except Exception as e:
                failed_count += 1
                error_msg = str(e)
                
                # Shorten error message if it's too long
                if len(error_msg) > 200:
                    error_msg = error_msg[:200] + "..."
                
                print(f"\n❌ Error processing URL {idx}/{total_urls}: {error_msg}")
                print("⚠️  Continuing to next URL...")
                import traceback
                traceback.print_exc()
                
                # Continue to next URL even if this one failed
                continue
        
        if total_urls > 1:
            print("\n" + "="*70)
            print(f"🎉 BATCH PROCESSING COMPLETE")
            print("="*70)
            print(f"Total URLs in batch: {total_urls}")
            print(f"✅ Successfully processed: {processed_count}")
            print(f"⏭️  Skipped (already done): {skipped_count}")
            print(f"❌ Failed: {failed_count}")
            print()
            
            if failed_count > 0:
                print("💡 Tip: Failed URLs were NOT marked as completed.")
                print("   Run the same command again to retry only the failed ones.")
                print()
    
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
