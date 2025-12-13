#!/usr/bin/env python3
"""
Video Downloader - Handles video extraction and downloading
"""

import requests
from selenium.webdriver.common.by import By


class VideoDownloader:
    """Manages video URL extraction and downloading"""
    
    def __init__(self, driver):
        self.driver = driver
    
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
