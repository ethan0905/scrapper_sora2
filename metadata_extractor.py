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
            "creator_profile_url": None,
            "creator_avatar_url": None,
            "likes": 0,
            "remixes": 0,
            "video_url": None,
            "downloaded_file": None
        }
        
        try:
            # Extract page title
            try:
                metadata["title"] = self.driver.title
            except:
                pass
            
            # Extract description - FIXED SELECTOR
            try:
                # Look for the specific div with description
                # Example: <div class="inline max-h-[30vh] overflow-y-auto tablet:max-h-[50vh]">
                desc_selectors = [
                    'div.inline[class*="max-h-"]',  # Main description div
                    'div.inline[class*="overflow-y-auto"]',
                    'div[class*="max-h-"][class*="overflow-y-auto"]',
                    'div.inline',
                ]
                
                for selector in desc_selectors:
                    try:
                        desc_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for desc_elem in desc_elements:
                            text = desc_elem.text.strip()
                            # Look for meaningful description text (not just numbers or single words)
                            if text and len(text) > 5 and not text.isdigit():
                                # Make sure it's not a button or UI element
                                classes = desc_elem.get_attribute("class") or ""
                                if "button" not in classes.lower() and "btn" not in classes.lower():
                                    metadata["description"] = text
                                    print(f"      ✅ Description found: {text[:50]}...")
                                    break
                        if metadata["description"]:
                            break
                    except Exception as e:
                        continue
                
                # Fallback: look for text in div elements with overflow-y-auto
                if not metadata["description"]:
                    try:
                        divs = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="overflow-y-auto"]')
                        for div in divs:
                            text = div.text.strip()
                            if text and 5 < len(text) < 500 and not text.isdigit():
                                # Skip if it contains common UI patterns
                                skip_patterns = ['like', 'share', 'download', 'button', 'profile', 'login', 'sign up']
                                if not any(pattern in text.lower() for pattern in skip_patterns):
                                    metadata["description"] = text
                                    print(f"      ✅ Description found (fallback): {text[:50]}...")
                                    break
                    except:
                        pass
            except Exception as e:
                print(f"      ⚠️  Error extracting description: {e}")
            
            # Extract LIKES count - FIXED SELECTOR
            try:
                # Look for like button with heart SVG and span.truncate
                # Example: <button class="...rounded-full..."><svg>...</svg><span class="cursor-pointer truncate">270</span></button>
                like_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'button[class*="rounded-full"]'
                )
                
                for button in like_buttons:
                    try:
                        # Check if button contains heart SVG
                        svg_elements = button.find_elements(By.TAG_NAME, 'svg')
                        for svg in svg_elements:
                            try:
                                # Look for path with heart shape (d attribute contains "M9 3.991")
                                paths = svg.find_elements(By.TAG_NAME, 'path')
                                for path in paths:
                                    d_attr = path.get_attribute('d')
                                    
                                    # Heart SVG has specific path signature
                                    if d_attr and 'M9 3.991' in d_attr:
                                        # Found like button, now get the count from span.truncate
                                        spans = button.find_elements(By.CSS_SELECTOR, 'span.truncate, span[class*="truncate"]')
                                        for span in spans:
                                            text = span.text.strip()
                                            if text and text.replace(',', '').replace('.', '').isdigit():
                                                # Remove formatting and convert to int
                                                likes_count = text.replace(',', '').replace('.', '')
                                                metadata["likes"] = int(likes_count)
                                                print(f"      ✅ Likes found: {metadata['likes']}")
                                                break
                                        if metadata["likes"] > 0:
                                            break
                                if metadata["likes"] > 0:
                                    break
                            except:
                                continue
                        if metadata["likes"] > 0:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"      ⚠️  Error extracting likes: {e}")
            
            # Extract REMIXES count - FIXED SELECTOR
            try:
                # Look for remix button with circle SVG and span.truncate
                # Example: <button class="...rounded-full..." data-disabled="false"><svg><circle...></svg><span class="truncate">88</span></button>
                remix_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'button[class*="rounded-full"]'
                )
                
                for button in remix_buttons:
                    try:
                        # Check if button contains circle SVG (remix icon)
                        svg_elements = button.find_elements(By.TAG_NAME, 'svg')
                        for svg in svg_elements:
                            try:
                                circles = svg.find_elements(By.TAG_NAME, 'circle')
                                
                                # Remix button has circle elements (specifically cx="9" cy="9")
                                if circles and len(circles) > 0:
                                    # Verify it's the remix button by checking circle attributes
                                    is_remix_button = False
                                    for circle in circles:
                                        cx = circle.get_attribute('cx')
                                        cy = circle.get_attribute('cy')
                                        if (cx == '9' or cx == '9.0') and (cy == '9' or cy == '9.0'):
                                            is_remix_button = True
                                            break
                                    
                                    if is_remix_button:
                                        # Found remix button, now get the count from span.truncate
                                        spans = button.find_elements(By.CSS_SELECTOR, 'span.truncate, span[class*="truncate"]')
                                        for span in spans:
                                            text = span.text.strip()
                                            if text and text.replace(',', '').replace('.', '').isdigit():
                                                # Remove formatting and convert to int
                                                remixes_count = text.replace(',', '').replace('.', '')
                                                metadata["remixes"] = int(remixes_count)
                                                print(f"      ✅ Remixes found: {metadata['remixes']}")
                                                break
                                        if metadata["remixes"] > 0:
                                            break
                            except:
                                continue
                        if metadata["remixes"] > 0:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"      ⚠️  Error extracting remixes: {e}")
            
            # Extract creator/author - FIXED SELECTOR
            try:
                # Look for profile link with specific classes and image
                # Example: <a class="inline-flex self-start" href="/profile/dark.lex"><img src="..." alt="dark.lex" class="object-cover rounded-full h-10 w-10"></a>
                profile_link_selectors = [
                    'a.inline-flex.self-start[href*="/profile/"]',
                    'a[class*="inline-flex"][class*="self-start"][href*="/profile/"]',
                    'a.inline-flex[href*="/profile/"]',
                    'a[href*="/profile/"]'
                ]
                
                for selector in profile_link_selectors:
                    try:
                        profile_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for link in profile_links:
                            try:
                                href = link.get_attribute("href")
                                if href and "/profile/" in href:
                                    # Extract username from URL
                                    username = href.split("/profile/")[-1].strip().rstrip('/')
                                    
                                    if username:
                                        metadata["creator_profile_url"] = href
                                        
                                        # Try to get avatar image and alt text
                                        try:
                                            img = link.find_element(By.TAG_NAME, 'img')
                                            avatar_url = img.get_attribute("src")
                                            alt_text = img.get_attribute("alt")
                                            
                                            if avatar_url:
                                                metadata["creator_avatar_url"] = avatar_url
                                            
                                            # Prefer alt text as creator name, fallback to username from URL
                                            if alt_text and alt_text.strip():
                                                metadata["creator"] = alt_text.strip()
                                            else:
                                                metadata["creator"] = username
                                        except:
                                            # If no image, just use username from URL
                                            metadata["creator"] = username
                                        
                                        print(f"      ✅ Creator found: {metadata['creator']}")
                                        print(f"      ✅ Profile URL: {metadata['creator_profile_url']}")
                                        if metadata["creator_avatar_url"]:
                                            print(f"      ✅ Avatar URL: {metadata['creator_avatar_url'][:60]}...")
                                        break
                            except:
                                continue
                        
                        if metadata["creator"]:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"      ⚠️  Error extracting creator: {e}")
        
        except Exception as e:
            print(f"      ⚠️  Error extracting metadata: {e}")
        
        return metadata
