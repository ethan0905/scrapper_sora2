#!/usr/bin/env python3
"""
Metadata Extractor - Handles metadata extraction from pages
"""

from datetime import datetime
from selenium.webdriver.common.by import By


class MetadataExtractor:
    """Extracts metadata from Sora remix pages"""
    
    def __init__(self, driver):
        self.driver = driver
    
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
