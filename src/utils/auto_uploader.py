"""
Automated YouTube Upload Scheduler

Monitors a folder and automatically uploads videos at scheduled intervals.
Generates titles using vision AI and manages upload queue.
"""

import json
import time
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.vision_title_generator import VisionTitleGenerator
from youtube_uploader.uploader import YouTubeUploader


class AutomatedUploader:
    """Automatically uploads videos at scheduled intervals."""
    
    def __init__(
        self,
        source_folder: str = "single-upload",
        upload_interval_hours: int = 8,
        credentials_file: str = "youtube_credentials.json",
        privacy: str = "public",
        use_vision_titles: bool = True,
        log_file: Optional[str] = None
    ):
        """
        Initialize the automated uploader.
        
        Args:
            source_folder: Folder to monitor for videos
            upload_interval_hours: Hours between uploads
            credentials_file: YouTube API credentials
            privacy: Video privacy (public/unlisted/private)
            use_vision_titles: Use vision AI for titles (vs metadata)
            log_file: Path to log file
        """
        self.source_folder = Path(source_folder)
        self.upload_interval = timedelta(hours=upload_interval_hours)
        self.privacy = privacy
        self.use_vision_titles = use_vision_titles
        
        # Create source folder if it doesn't exist
        self.source_folder.mkdir(parents=True, exist_ok=True)
        
        # Create logs folder if it doesn't exist
        logs_folder = Path("logs")
        logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_file = log_file or logs_folder / "upload_scheduler.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # State file to track schedule
        self.state_file = self.source_folder / ".upload_state.json"
        self.state = self._load_state()
        
        # Initialize uploaders
        self.youtube = YouTubeUploader(credentials_file)
        
        if use_vision_titles:
            try:
                self.vision_generator = VisionTitleGenerator()
                self.logger.info("✅ Vision title generator initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Vision generator failed: {e}")
                self.logger.info("📝 Falling back to basic titles")
                self.use_vision_titles = False
        
        self.logger.info(f"🚀 Automated uploader initialized")
        self.logger.info(f"📁 Source folder: {self.source_folder}")
        self.logger.info(f"⏰ Upload interval: {upload_interval_hours} hours")
        self.logger.info(f"🎬 Vision titles: {'Enabled' if use_vision_titles else 'Disabled'}")
    
    def _load_state(self) -> Dict:
        """Load the scheduler state."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'last_upload_time': None,
            'uploaded_videos': [],
            'queue': [],
            'consecutive_failures': 0,
            'last_error': None
        }
    
    def _save_state(self):
        """Save the scheduler state."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _get_next_video(self) -> Optional[Path]:
        """
        Get the next video to upload.
        
        Returns:
            Path to next video or None if no videos available
        """
        # Find all video files
        video_files = []
        for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
            video_files.extend(self.source_folder.glob(f'*{ext}'))
        
        # Filter out already uploaded videos
        uploaded = set(self.state['uploaded_videos'])
        available = [v for v in video_files if str(v) not in uploaded]
        
        if not available:
            return None
        
        # Sort by name and get first
        available.sort()
        return available[0]
    
    def _generate_title_and_description(
        self,
        video_path: Path
    ) -> tuple[str, str]:
        """
        Generate title and description for video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (title, description)
        """
        if self.use_vision_titles:
            try:
                self.logger.info("🎥 Analyzing video with AI vision...")
                title = self.vision_generator.generate_title_from_file(
                    str(video_path),
                    style='engaging',
                    include_emoji=True,
                    include_hashtag=True
                )
                self.logger.info(f"✅ Generated title: {title}")
            except Exception as e:
                self.logger.error(f"❌ Vision generation failed: {e}")
                title = f"Sora AI Video - {video_path.stem}"
        else:
            # Try to load metadata
            metadata_path = video_path.parent / f"{video_path.stem}_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    desc = metadata.get('description', '')
                    if desc and not desc.startswith('Follow @'):
                        title = desc[:100]
                    else:
                        title = f"Sora AI Video - {video_path.stem}"
            else:
                title = f"Sora AI Video - {video_path.stem}"
        
        # Generate description
        description = self._generate_description(video_path)
        
        return title, description
    
    def _generate_description(self, video_path: Path) -> str:
        """Generate video description."""
        parts = [
            "AI-generated video created with Sora.",
            "",
            "Follow for more AI content!",
            "",
            "#SoraAI #AIVideo #GenerativeAI #OpenAI #ArtificialIntelligence"
        ]
        
        # Try to add metadata context
        metadata_path = video_path.parent / f"{video_path.stem}_metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    if metadata.get('creator'):
                        parts.insert(2, f"Original creator: {metadata['creator']}")
                    if metadata.get('url'):
                        parts.insert(3, f"Source: {metadata['url']}")
            except Exception:
                pass
        
        return '\n'.join(parts)
    
    def _upload_video(self, video_path: Path) -> bool:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"📤 Preparing to upload: {video_path.name}")
            
            # Generate title and description
            title, description = self._generate_title_and_description(video_path)
            
            # Upload to YouTube
            self.logger.info(f"⬆️  Uploading to YouTube...")
            self.logger.info(f"   Title: {title}")
            self.logger.info(f"   Privacy: {self.privacy}")
            
            response = self.youtube.upload_video(
                video_path=str(video_path),
                title=title,
                description=description,
                privacy=self.privacy,
                made_for_kids=False
            )
            
            video_id = response.get('id')
            if video_id:
                self.logger.info(f"✅ Upload successful!")
                self.logger.info(f"   Video ID: {video_id}")
                self.logger.info(f"   URL: https://www.youtube.com/watch?v={video_id}")
                
                # Update state - RESET failure counter on success
                self.state['uploaded_videos'].append(str(video_path))
                self.state['last_upload_time'] = datetime.now().isoformat()
                self.state['consecutive_failures'] = 0
                self.state['last_error'] = None
                self._save_state()
                
                # Move to uploaded folder
                uploaded_folder = self.source_folder / "uploaded"
                uploaded_folder.mkdir(exist_ok=True)
                new_path = uploaded_folder / video_path.name
                video_path.rename(new_path)
                self.logger.info(f"📦 Moved to: {new_path}")
                
                # Move metadata if exists
                metadata_path = self.source_folder / f"{video_path.stem}_metadata.json"
                if metadata_path.exists():
                    metadata_path.rename(uploaded_folder / metadata_path.name)
                
                return True
            else:
                error_msg = "No video ID in response"
                self.logger.error(f"❌ Upload failed: {error_msg}")
                self.state['consecutive_failures'] = self.state.get('consecutive_failures', 0) + 1
                self.state['last_error'] = error_msg
                self._save_state()
                return False
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ Upload failed: {error_msg}", exc_info=True)
            self.state['consecutive_failures'] = self.state.get('consecutive_failures', 0) + 1
            self.state['last_error'] = error_msg
            self._save_state()
            return False
    
    def _should_upload_now(self) -> bool:
        """Check if it's time to upload."""
        if not self.state['last_upload_time']:
            return True
        
        last_upload = datetime.fromisoformat(self.state['last_upload_time'])
        next_upload = last_upload + self.upload_interval
        
        return datetime.now() >= next_upload
    
    def _time_until_next_upload(self) -> Optional[timedelta]:
        """Calculate time until next upload."""
        if not self.state['last_upload_time']:
            return timedelta(0)
        
        last_upload = datetime.fromisoformat(self.state['last_upload_time'])
        next_upload = last_upload + self.upload_interval
        remaining = next_upload - datetime.now()
        
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def run(self, max_consecutive_failures: int = 10):
        """
        Run the automated uploader loop.
        
        Args:
            max_consecutive_failures: Stop after this many consecutive failures (default: 10)
        """
        self.logger.info("🚀 Starting automated uploader...")
        self.logger.info(f"   Max consecutive failures: {max_consecutive_failures}")
        self.logger.info("   Press Ctrl+C to stop")
        
        try:
            while True:
                # Check failure threshold
                failures = self.state.get('consecutive_failures', 0)
                if failures >= max_consecutive_failures:
                    self.logger.critical(f"\n{'='*60}")
                    self.logger.critical(f"🛑 CRITICAL: Too many consecutive failures!")
                    self.logger.critical(f"{'='*60}")
                    self.logger.critical(f"   Failed attempts: {failures}")
                    self.logger.critical(f"   Last error: {self.state.get('last_error', 'Unknown')}")
                    self.logger.critical(f"   Stopping uploader for safety.")
                    self.logger.critical(f"\n   To restart:")
                    self.logger.critical(f"   1. Fix the issue")
                    self.logger.critical(f"   2. Reset failures: rm {self.state_file}")
                    self.logger.critical(f"   3. Restart service: ./scripts/service.sh restart")
                    self.logger.critical(f"{'='*60}\n")
                    # Exit with error code
                    sys.exit(1)
                
                # Check if we should upload
                if self._should_upload_now():
                    # Get next video
                    video = self._get_next_video()
                    
                    if video:
                        self.logger.info(f"\n{'='*60}")
                        self.logger.info(f"⏰ Upload time! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        self.logger.info(f"{'='*60}\n")
                        
                        success = self._upload_video(video)
                        
                        if success:
                            self.logger.info(f"\n✅ Upload complete!")
                            next_time = datetime.now() + self.upload_interval
                            self.logger.info(f"⏰ Next upload: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            failures = self.state.get('consecutive_failures', 0)
                            self.logger.error(f"\n❌ Upload failed!")
                            self.logger.error(f"   Consecutive failures: {failures}/{max_consecutive_failures}")
                            self.logger.error(f"   Last error: {self.state.get('last_error', 'Unknown')}")
                            if failures >= max_consecutive_failures - 3:
                                self.logger.warning(f"   ⚠️  Warning: Approaching failure limit!")
                            self.logger.error(f"   Will retry next cycle")
                    else:
                        self.logger.warning(f"\n⚠️  No videos available to upload")
                        self.logger.info(f"   Add videos to: {self.source_folder}")
                        self.logger.info(f"   Checking again in 1 hour...")
                        time.sleep(3600)  # Check again in 1 hour
                        continue
                else:
                    # Wait until next upload time
                    remaining = self._time_until_next_upload()
                    hours = remaining.total_seconds() / 3600
                    
                    self.logger.info(f"⏳ Waiting for next upload...")
                    self.logger.info(f"   Time remaining: {hours:.1f} hours")
                    
                    # Check for new videos every 5 minutes
                    check_interval = 300  # 5 minutes
                    time.sleep(check_interval)
                    
        except KeyboardInterrupt:
            self.logger.info("\n\n🛑 Stopping automated uploader...")
            self.logger.info("   Goodbye! 👋")


def main():
    """CLI interface for automated uploader."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated YouTube upload scheduler'
    )
    parser.add_argument(
        '--folder',
        type=str,
        default='single-upload',
        help='Folder to monitor for videos (default: single-upload)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=8,
        help='Hours between uploads (default: 8)'
    )
    parser.add_argument(
        '--privacy',
        type=str,
        choices=['public', 'unlisted', 'private'],
        default='public',
        help='Video privacy setting (default: public)'
    )
    parser.add_argument(
        '--credentials',
        type=str,
        default='youtube_credentials.json',
        help='YouTube API credentials file'
    )
    parser.add_argument(
        '--no-vision',
        action='store_true',
        help='Disable vision-based title generation'
    )
    parser.add_argument(
        '--log',
        type=str,
        help='Path to log file'
    )
    parser.add_argument(
        '--max-failures',
        type=int,
        default=10,
        help='Stop after this many consecutive upload failures (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Create and run uploader
    uploader = AutomatedUploader(
        source_folder=args.folder,
        upload_interval_hours=args.interval,
        credentials_file=args.credentials,
        privacy=args.privacy,
        use_vision_titles=not args.no_vision,
        log_file=args.log
    )
    
    uploader.run(max_consecutive_failures=args.max_failures)


if __name__ == '__main__':
    main()
