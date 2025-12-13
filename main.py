#!/usr/bin/env python3
"""
Sora Video Scraper - Main Entry Point

This is the main entry point for the Sora video scraper application.
It provides a unified interface for all scraping operations.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scraper.scraper import main as scraper_main


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="Sora Video Scraper - Download videos and metadata from Sora remixes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape first 10 remixes from a single URL
  python main.py https://sora.chatgpt.com/p/VIDEO_ID --max 10
  
  # Use existing Chrome session (recommended)
  python main.py https://sora.chatgpt.com/p/VIDEO_ID --use-existing --max 50
  
  # Metadata only (no video downloads)
  python main.py https://sora.chatgpt.com/p/VIDEO_ID --metadata-only --max 20
  
  # Slow mode - human-like delays to avoid detection (recommended for large batches)
  python main.py https://sora.chatgpt.com/p/VIDEO_ID --max 50 --slow --use-existing
  
  # Batch processing from file (process multiple URLs)
  python main.py --batch urls.txt --max 50 --slow --use-existing
  
  # Custom output directory
  python main.py --batch urls.txt --max 100 --output my-batch --slow --use-existing

For more information, see docs/README.md
        """
    )
    
    parser.add_argument("url", nargs="?", help="URL of the Sora video page with remixes")
    parser.add_argument("--batch", type=str, metavar="FILE", 
                        help="Path to text file containing URLs (one per line)")
    parser.add_argument("--max", type=int, default=None, metavar="N", 
                        help="Maximum number of remixes to scrape per URL")
    parser.add_argument("--use-existing", action="store_true", 
                        help="Connect to existing Chrome session (recommended)")
    parser.add_argument("--metadata-only", action="store_true", 
                        help="Only extract metadata, don't download videos")
    parser.add_argument("--output", type=str, default="videos", metavar="DIR", 
                        help="Output directory (default: videos)")
    parser.add_argument("--debug-port", type=int, default=9222, metavar="PORT", 
                        help="Chrome debugging port (default: 9222)")
    parser.add_argument("--slow", action="store_true", 
                        help="Enable slow mode with human-like delays (recommended)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.batch:
        parser.error("Either provide a URL or use --batch with a file path")
    
    if args.url and args.batch:
        parser.error("Cannot use both URL and --batch. Choose one.")
    
    # Call the scraper main function
    sys.argv = ['scraper.py']  # Reset argv for the scraper
    if args.url:
        sys.argv.append(args.url)
    if args.batch:
        sys.argv.extend(['--batch', args.batch])
    if args.max:
        sys.argv.extend(['--max', str(args.max)])
    if args.use_existing:
        sys.argv.append('--use-existing')
    if args.metadata_only:
        sys.argv.append('--metadata-only')
    if args.output:
        sys.argv.extend(['--output', args.output])
    if args.debug_port:
        sys.argv.extend(['--debug-port', str(args.debug_port)])
    if args.slow:
        sys.argv.append('--slow')
    
    scraper_main()


if __name__ == "__main__":
    main()
