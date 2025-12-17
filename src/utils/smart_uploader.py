"""
YouTube Upload Helper with Smart Title Generation

Combines the title generator with the YouTube uploader for seamless
batch uploading with engaging, auto-generated titles.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.title_generator import TitleGenerator
from youtube_uploader.uploader import YouTubeUploader


class SmartUploader:
    """YouTube uploader with automatic title generation."""
    
    def __init__(
        self,
        credentials_file: str = "youtube_credentials.json",
        title_settings: Optional[Dict] = None
    ):
        """
        Initialize the smart uploader.
        
        Args:
            credentials_file: Path to YouTube API credentials
            title_settings: Settings for title generation
        """
        self.uploader = YouTubeUploader(credentials_file)
        self.title_generator = TitleGenerator()
        self.title_settings = title_settings or {
            'include_emoji': True,
            'include_hashtag': True,
            'max_length': 100
        }
    
    def upload_with_metadata(
        self,
        video_path: str,
        metadata_path: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy: str = "public",
        made_for_kids: bool = False
    ) -> Dict:
        """
        Upload a video with auto-generated title from metadata.
        
        Args:
            video_path: Path to video file
            metadata_path: Path to metadata JSON (auto-detected if None)
            title: Manual title (overrides auto-generation)
            description: Video description (uses metadata if None)
            privacy: Privacy setting (public/unlisted/private)
            made_for_kids: Whether video is made for kids
            
        Returns:
            Upload response dictionary
        """
        # Auto-detect metadata file if not provided
        if metadata_path is None:
            video_p = Path(video_path)
            metadata_path = video_p.parent / f"{video_p.stem}_metadata.json"
        
        metadata_p = Path(metadata_path)
        
        # Load metadata if available
        metadata = {}
        if metadata_p.exists():
            with open(metadata_p, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # Generate title if not provided
        if title is None:
            if metadata:
                title = self.title_generator.generate_title(
                    metadata,
                    **self.title_settings
                )
            else:
                title = f"Sora AI Generated Video {Path(video_path).stem}"
        
        # Generate description if not provided
        if description is None:
            description = self._generate_description(metadata)
        
        # Upload the video
        print(f"\n📤 Uploading: {Path(video_path).name}")
        print(f"   Title: {title}")
        print(f"   Privacy: {privacy}")
        
        response = self.uploader.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            privacy=privacy,
            made_for_kids=made_for_kids
        )
        
        return response
    
    def batch_upload_folder(
        self,
        folder_path: str,
        privacy: str = "public",
        made_for_kids: bool = False,
        skip_existing: bool = True
    ) -> List[Dict]:
        """
        Upload all videos in a folder with auto-generated titles.
        
        Args:
            folder_path: Path to folder containing videos
            privacy: Privacy setting for all videos
            made_for_kids: Whether videos are made for kids
            skip_existing: Skip videos that have been uploaded (checks log)
            
        Returns:
            List of upload responses
        """
        folder = Path(folder_path)
        
        # Find all video files
        video_files = []
        for ext in ['.mp4', '.mov', '.avi', '.mkv']:
            video_files.extend(folder.rglob(f'*{ext}'))
        
        # Filter out _start files and duplicates
        video_files = [
            v for v in video_files 
            if '_start' not in v.stem and 'all_remixes' not in v.stem
        ]
        
        if not video_files:
            print(f"❌ No video files found in {folder_path}")
            return []
        
        print(f"\n🎬 Found {len(video_files)} videos to upload")
        
        # Upload each video
        results = []
        uploaded_count = 0
        skipped_count = 0
        failed_count = 0
        
        for i, video_path in enumerate(video_files, 1):
            print(f"\n{'='*60}")
            print(f"Video {i}/{len(video_files)}")
            print(f"{'='*60}")
            
            try:
                # Check if already uploaded
                if skip_existing and self._is_uploaded(video_path):
                    print(f"⏭️  Skipping (already uploaded): {video_path.name}")
                    skipped_count += 1
                    continue
                
                # Upload with auto-generated title
                response = self.upload_with_metadata(
                    video_path=str(video_path),
                    privacy=privacy,
                    made_for_kids=made_for_kids
                )
                
                results.append({
                    'video_path': str(video_path),
                    'response': response,
                    'success': True
                })
                
                # Log the upload
                self._log_upload(video_path, response)
                uploaded_count += 1
                
                print(f"✅ Upload successful!")
                if 'id' in response:
                    print(f"   Video ID: {response['id']}")
                    print(f"   URL: https://www.youtube.com/watch?v={response['id']}")
                
            except Exception as e:
                print(f"❌ Upload failed: {e}")
                results.append({
                    'video_path': str(video_path),
                    'error': str(e),
                    'success': False
                })
                failed_count += 1
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 UPLOAD SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Uploaded: {uploaded_count}")
        print(f"⏭️  Skipped: {skipped_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📁 Total: {len(video_files)}")
        
        return results
    
    def _generate_description(self, metadata: Dict) -> str:
        """
        Generate a description from metadata.
        
        Args:
            metadata: Video metadata dictionary
            
        Returns:
            Generated description
        """
        parts = []
        
        # Add original description if available
        if metadata.get('description'):
            desc = metadata['description']
            if not desc.startswith('Follow @'):
                parts.append(desc)
        
        # Add creator info
        if metadata.get('creator'):
            parts.append(f"\nOriginal creator: {metadata['creator']}")
        
        # Add source URL
        if metadata.get('url'):
            parts.append(f"Source: {metadata['url']}")
        
        # Add default text
        parts.append("\nGenerated with Sora AI")
        parts.append("#SoraAI #AIVideo #GenerativeAI")
        
        return '\n'.join(parts)
    
    def _is_uploaded(self, video_path: Path) -> bool:
        """
        Check if a video has already been uploaded.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if already uploaded
        """
        log_file = video_path.parent / 'upload_log.json'
        
        if not log_file.exists():
            return False
        
        try:
            with open(log_file, 'r') as f:
                log = json.load(f)
                return str(video_path) in log
        except Exception:
            return False
    
    def _log_upload(self, video_path: Path, response: Dict):
        """
        Log an uploaded video.
        
        Args:
            video_path: Path to video file
            response: Upload response
        """
        log_file = video_path.parent / 'upload_log.json'
        
        # Load existing log
        log = {}
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    log = json.load(f)
            except Exception:
                pass
        
        # Add this upload
        log[str(video_path)] = {
            'video_id': response.get('id'),
            'title': response.get('snippet', {}).get('title'),
            'uploaded_at': response.get('snippet', {}).get('publishedAt')
        }
        
        # Save log
        with open(log_file, 'w') as f:
            json.dump(log, f, indent=2)


def main():
    """CLI interface for smart uploading."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Upload Sora videos to YouTube with auto-generated titles'
    )
    parser.add_argument(
        'path',
        type=str,
        help='Path to video file or folder containing videos'
    )
    parser.add_argument(
        '-c', '--credentials',
        type=str,
        default='youtube_credentials.json',
        help='Path to YouTube API credentials file'
    )
    parser.add_argument(
        '-p', '--privacy',
        type=str,
        choices=['public', 'unlisted', 'private'],
        default='public',
        help='Privacy setting (default: public)'
    )
    parser.add_argument(
        '--kids',
        action='store_true',
        help='Mark videos as made for kids'
    )
    parser.add_argument(
        '--no-emoji',
        action='store_true',
        help='Disable emoji in titles'
    )
    parser.add_argument(
        '--no-hashtag',
        action='store_true',
        help='Disable #SoraAI hashtag in titles'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Upload even if already in log'
    )
    
    args = parser.parse_args()
    
    # Create smart uploader
    title_settings = {
        'include_emoji': not args.no_emoji,
        'include_hashtag': not args.no_hashtag,
        'max_length': 100
    }
    
    uploader = SmartUploader(
        credentials_file=args.credentials,
        title_settings=title_settings
    )
    
    path = Path(args.path)
    
    if path.is_file():
        # Single file upload
        uploader.upload_with_metadata(
            video_path=str(path),
            privacy=args.privacy,
            made_for_kids=args.kids
        )
    elif path.is_dir():
        # Batch upload
        uploader.batch_upload_folder(
            folder_path=str(path),
            privacy=args.privacy,
            made_for_kids=args.kids,
            skip_existing=not args.force
        )
    else:
        print(f"❌ Error: {path} is not a valid file or directory")


if __name__ == '__main__':
    main()
