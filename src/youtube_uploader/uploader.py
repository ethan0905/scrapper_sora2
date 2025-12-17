#!/usr/bin/env python3
"""
YouTube Video Uploader

This module monitors a source folder for videos and automatically uploads them to YouTube.
Once uploaded, videos are moved to a destination folder.

Features:
- Monitors source folder for new videos
- Uploads videos to YouTube with customizable metadata
- Moves successfully uploaded videos to destination folder
- Handles errors and retries
- Progress tracking and logging

Requirements:
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client

Install with:
    pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import sys
import time
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
except ImportError:
    print("❌ Error: Required Google API libraries not installed!")
    print("Please install with:")
    print("   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


# YouTube API settings
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


class YouTubeUploader:
    """Handles automated YouTube video uploads"""
    
    def __init__(self, source_folder: str, destination_folder: str, 
                 credentials_file: str = "youtube_credentials.json",
                 token_file: str = "youtube_token.json",
                 default_title: str = "Sora Video",
                 default_description: str = "Video created with Sora AI",
                 default_category: str = "22",  # People & Blogs
                 default_privacy: str = "private"):
        """
        Initialize YouTube Uploader
        
        Args:
            source_folder: Folder to monitor for videos
            destination_folder: Folder to move uploaded videos
            credentials_file: Path to YouTube API credentials JSON
            token_file: Path to save/load OAuth token
            default_title: Default title for videos
            default_description: Default description
            default_category: YouTube category ID (22 = People & Blogs)
            default_privacy: Privacy status (public, private, unlisted)
        """
        self.source_folder = Path(source_folder)
        self.destination_folder = Path(destination_folder)
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        
        self.default_title = default_title
        self.default_description = default_description
        self.default_category = default_category
        self.default_privacy = default_privacy
        
        # Validate that source is a folder (not a file)
        if self.source_folder.exists() and self.source_folder.is_file():
            raise ValueError(
                f"❌ Error: Source must be a FOLDER, not a file!\n"
                f"You provided: {source_folder}\n"
                f"Please provide the folder containing videos, not a video file.\n"
                f"Example: --source videos/remix-batch-3/url-18"
            )
        
        # Create folders if they don't exist
        self.source_folder.mkdir(parents=True, exist_ok=True)
        self.destination_folder.mkdir(parents=True, exist_ok=True)
        
        # Upload tracking
        self.upload_log_file = self.destination_folder / ".upload_log.json"
        self.uploaded_videos = self._load_upload_log()
        
        self.youtube = None
    
    def _load_upload_log(self) -> Dict:
        """Load upload log to track which videos have been uploaded"""
        if self.upload_log_file.exists():
            try:
                with open(self.upload_log_file, 'r') as f:
                    return json.load(f)
            except:
                return {"uploads": []}
        return {"uploads": []}
    
    def _save_upload_log(self, video_path: str, video_id: str, video_url: str):
        """Save upload record to log"""
        self.uploaded_videos["uploads"].append({
            "file": str(video_path),
            "video_id": video_id,
            "video_url": video_url,
            "uploaded_at": datetime.now().isoformat()
        })
        
        with open(self.upload_log_file, 'w') as f:
            json.dump(self.uploaded_videos, f, indent=2)
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API
        
        Returns:
            bool: True if authentication successful
        """
        creds = None
        
        # Load existing token
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            except Exception as e:
                print(f"⚠️  Error loading token: {e}")
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing authentication token...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not self.credentials_file.exists():
                    print(f"❌ Error: Credentials file not found: {self.credentials_file}")
                    print("\nTo use this feature:")
                    print("1. Go to: https://console.cloud.google.com/")
                    print("2. Create a project and enable YouTube Data API v3")
                    print("3. Create OAuth 2.0 credentials (Desktop app)")
                    print("4. Download credentials as 'youtube_credentials.json'")
                    return False
                
                print("🔐 Starting authentication flow...")
                print("A browser window will open for authorization.")
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"❌ Authentication failed: {e}")
                    return False
            
            # Save credentials
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            print("✅ Authentication successful!")
        
        # Build YouTube service
        try:
            self.youtube = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
            return True
        except Exception as e:
            print(f"❌ Error building YouTube service: {e}")
            return False
    
    def upload_video(self, video_path: Path, title: Optional[str] = None,
                     description: Optional[str] = None,
                     category: Optional[str] = None,
                     privacy: Optional[str] = None) -> Optional[str]:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title (uses default if None)
            description: Video description (uses default if None)
            category: YouTube category ID (uses default if None)
            privacy: Privacy status (uses default if None)
        
        Returns:
            str: YouTube video ID if successful, None otherwise
        """
        if not self.youtube:
            print("❌ Not authenticated! Call authenticate() first.")
            return None
        
        # Use defaults if not provided
        title = title or f"{self.default_title} - {video_path.stem}"
        description = description or self.default_description
        category = category or self.default_category
        privacy = privacy or self.default_privacy
        
        print(f"📤 Uploading: {video_path.name}")
        print(f"   Title: {title}")
        print(f"   Privacy: {privacy}")
        
        # Prepare request body
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            str(video_path),
            chunksize=1024*1024,  # 1MB chunks
            resumable=True
        )
        
        try:
            # Execute upload request
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"   Progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"   ✅ Upload successful!")
            print(f"   📺 Video ID: {video_id}")
            print(f"   🔗 URL: {video_url}")
            
            return video_id
        
        except HttpError as e:
            print(f"   ❌ Upload failed: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return None
    
    def get_video_files(self) -> List[Path]:
        """Get list of video files in source folder"""
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm']
        videos = []
        
        for ext in video_extensions:
            videos.extend(self.source_folder.glob(f'*{ext}'))
            videos.extend(self.source_folder.glob(f'*{ext.upper()}'))
        
        return sorted(videos)
    
    def process_folder(self, watch_mode: bool = False, interval: int = 60):
        """
        Process all videos in source folder
        
        Args:
            watch_mode: If True, continuously monitor folder
            interval: Check interval in seconds (for watch mode)
        """
        print("="*70)
        print("📺 YOUTUBE AUTO-UPLOADER")
        print("="*70)
        print(f"Source: {self.source_folder}")
        print(f"Destination: {self.destination_folder}")
        print(f"Watch mode: {'Enabled' if watch_mode else 'Disabled'}")
        print()
        
        # Authenticate
        if not self.authenticate():
            return
        
        processed_files = set()
        
        while True:
            videos = self.get_video_files()
            new_videos = [v for v in videos if str(v) not in processed_files]
            
            if new_videos:
                print(f"\n📹 Found {len(new_videos)} video(s) to upload")
                
                for video_path in new_videos:
                    print(f"\n{'='*70}")
                    
                    # Check if already uploaded
                    if any(str(video_path) == upload['file'] for upload in self.uploaded_videos['uploads']):
                        print(f"⏭️  Skipping (already uploaded): {video_path.name}")
                        processed_files.add(str(video_path))
                        continue
                    
                    # Upload video
                    video_id = self.upload_video(video_path)
                    
                    if video_id:
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        # Log upload
                        self._save_upload_log(str(video_path), video_id, video_url)
                        
                        # Move to destination folder
                        dest_path = self.destination_folder / video_path.name
                        try:
                            shutil.move(str(video_path), str(dest_path))
                            print(f"   📁 Moved to: {dest_path}")
                        except Exception as e:
                            print(f"   ⚠️  Could not move file: {e}")
                    
                    processed_files.add(str(video_path))
                    
                    # Small delay between uploads
                    if len(new_videos) > 1:
                        time.sleep(2)
            
            if not watch_mode:
                break
            
            # Wait before checking again
            print(f"\n⏳ Waiting {interval}s before next check...")
            time.sleep(interval)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="YouTube Auto-Uploader - Automatically upload videos from folder A to folder B",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload all videos once
  python -m src.youtube_uploader.uploader --source videos/to-upload --dest videos/uploaded
  
  # Watch mode - continuously monitor for new videos
  python -m src.youtube_uploader.uploader --source videos/to-upload --dest videos/uploaded --watch
  
  # Custom settings
  python -m src.youtube_uploader.uploader --source videos/to-upload --dest videos/uploaded --privacy unlisted --watch

Setup Instructions:
  1. Go to https://console.cloud.google.com/
  2. Create a project and enable YouTube Data API v3
  3. Create OAuth 2.0 credentials (Desktop app)
  4. Download credentials as 'youtube_credentials.json'
  5. Place credentials file in the same directory as this script
        """
    )
    
    parser.add_argument("--source", required=True, help="Source folder (or single video file) to upload")
    parser.add_argument("--dest", required=True, help="Destination folder for uploaded videos")
    parser.add_argument("--credentials", default="youtube_credentials.json", help="Path to credentials JSON")
    parser.add_argument("--watch", action="store_true", help="Watch mode - continuously monitor folder")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    parser.add_argument("--title", default="Sora Video", help="Default title for videos")
    parser.add_argument("--description", default="Video created with Sora AI", help="Default description")
    parser.add_argument("--privacy", default="public", choices=['public', 'private', 'unlisted'], 
                        help="Privacy status (default: public)")
    
    args = parser.parse_args()
    
    # Check if source is a single file
    source_path = Path(args.source)
    
    if source_path.is_file():
        # Single file mode
        print("="*70)
        print("📺 YOUTUBE UPLOADER - Single File Mode")
        print("="*70)
        print(f"File: {source_path}")
        print(f"Destination: {args.dest}")
        print()
        
        # Create temp folder for single file
        temp_source = source_path.parent / ".temp_upload"
        temp_source.mkdir(exist_ok=True)
        
        # Copy file to temp folder
        import shutil
        temp_file = temp_source / source_path.name
        if not temp_file.exists():
            shutil.copy(str(source_path), str(temp_file))
        
        # Create uploader with temp folder
        uploader = YouTubeUploader(
            source_folder=str(temp_source),
            destination_folder=args.dest,
            credentials_file=args.credentials,
            default_title=args.title,
            default_description=args.description,
            default_privacy=args.privacy
        )
        
        try:
            # Process the single file
            uploader.process_folder(watch_mode=False, interval=args.interval)
            
            # Cleanup temp folder
            shutil.rmtree(temp_source)
            print("\n✅ Upload complete!")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            shutil.rmtree(temp_source, ignore_errors=True)
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            shutil.rmtree(temp_source, ignore_errors=True)
    else:
        # Folder mode (original behavior)
        # Create uploader
        uploader = YouTubeUploader(
            source_folder=args.source,
            destination_folder=args.dest,
            credentials_file=args.credentials,
            default_title=args.title,
            default_description=args.description,
            default_privacy=args.privacy
        )
        
        try:
            # Process folder
            uploader.process_folder(watch_mode=args.watch, interval=args.interval)
            
            print("\n✅ All done!")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
