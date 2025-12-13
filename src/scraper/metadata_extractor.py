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
            "comments": [],
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
            
            # Extract COMMENTS - NEW FEATURE
            try:
                print(f"      💬 Extracting comments...")
                comments = self.extract_comments()
                metadata["comments"] = comments
                if comments:
                    print(f"      ✅ Found {len(comments)} comment(s)")
                else:
                    print(f"      ℹ️  No comments found")
            except Exception as e:
                print(f"      ⚠️  Error extracting comments: {e}")
        
        except Exception as e:
            print(f"      ⚠️  Error extracting metadata: {e}")
        
        return metadata
    
    def extract_comments(self):
        """
        Extract all comments from the current page
        
        Returns:
            list: List of unique comment dictionaries with user info and content
        """
        comments = []
        seen_comments = set()  # Track unique comments to avoid duplicates
        
        try:
            # UI text patterns to filter out (not actual comments)
            ui_patterns = [
                'replies', 'reply', 'like', 'share', 'delete', 'edit', 'more',
                'remixes', 'remix', 'load more', 'show more', 'view replies',
                'comments', 'comment', 'cast', 'follow', 'following', 'unfollow',
                'subscribe', 'subscribed', 'report', 'block', 'mute', 'copy',
                'download', 'save', 'saved', 'bookmark', 'bookmarked'
            ]
            
            # Single-word UI terms that are never comments
            single_word_ui = {'cast', 'like', 'share', 'remix', 'follow', 'save', 'edit', 'delete', 'reply', 'more'}
            
            # Look for comment-specific containers first
            comment_selectors = [
                'div[class*="comment"]',
                'li[class*="comment"]', 
                'article[class*="comment"]',
                'div[role="article"]',
            ]
            
            comment_elements = []
            for selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        comment_elements = elements
                        print(f"      🔍 Found {len(elements)} potential comment containers using {selector}")
                        break
                except:
                    continue
            
            # If no specific containers found, look for elements with profile links
            if not comment_elements:
                print(f"      🔍 No comment containers found, trying alternate method...")
                try:
                    # Find all profile links first
                    all_profile_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/profile/"]')
                    
                    # Get the parent element of each profile link (likely the comment container)
                    for link in all_profile_links:
                        try:
                            # Go up 2-3 levels to find the comment container
                            parent = link.find_element(By.XPATH, './ancestor::*[contains(@class, "comment") or contains(@class, "message") or contains(@role, "article")]')
                            if parent and parent not in comment_elements:
                                comment_elements.append(parent)
                        except:
                            # Try just the immediate parent
                            try:
                                parent = link.find_element(By.XPATH, '..')
                                # Only add if it has some text content
                                if parent and parent.text.strip() and len(parent.text.strip()) > 10:
                                    comment_elements.append(parent)
                            except:
                                pass
                except:
                    pass
            
            print(f"      📊 Processing {len(comment_elements)} potential comment(s)...")
            
            # Extract data from each comment element
            for elem in comment_elements:
                try:
                    comment_data = {
                        "username": None,
                        "user_profile_url": None,
                        "user_avatar_url": None,
                        "comment_text": None,
                        "likes": 0
                    }
                    
                    # Extract user profile information
                    try:
                        profile_link = elem.find_element(By.CSS_SELECTOR, 'a[href*="/profile/"]')
                        href = profile_link.get_attribute("href")
                        
                        if href and "/profile/" in href:
                            # Get username from URL
                            username = href.split("/profile/")[-1].strip().rstrip('/')
                            comment_data["user_profile_url"] = href
                            
                            # Try to get user avatar
                            try:
                                img = profile_link.find_element(By.TAG_NAME, 'img')
                                avatar_url = img.get_attribute("src")
                                alt_text = img.get_attribute("alt")
                                
                                if avatar_url:
                                    comment_data["user_avatar_url"] = avatar_url
                                
                                # Prefer alt text as username
                                if alt_text and alt_text.strip() and alt_text.strip() != username:
                                    comment_data["username"] = alt_text.strip()
                                else:
                                    comment_data["username"] = username
                            except:
                                comment_data["username"] = username
                    except:
                        # No profile link found, skip this element
                        continue
                    
                    # Extract comment text - improved logic
                    try:
                        # Get all text from the element
                        all_text = elem.text.strip()
                        
                        if all_text:
                            # Split into lines and find the actual comment
                            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                            
                            # Filter out UI text and find the actual comment
                            for line in lines:
                                # Skip very short lines (less than 4 chars)
                                if len(line) < 4:
                                    continue
                                
                                # Skip if it's just the username
                                if line == comment_data["username"]:
                                    continue
                                
                                # Skip single-word UI terms (case-insensitive)
                                if line.lower() in single_word_ui:
                                    continue
                                
                                # Skip UI patterns in longer text
                                is_ui_text = False
                                line_lower = line.lower()
                                for pattern in ui_patterns:
                                    if pattern in line_lower and len(line) < 20:
                                        is_ui_text = True
                                        break
                                
                                if is_ui_text:
                                    continue
                                
                                # Skip if it's just a number (like count)
                                if line.replace(',', '').replace('.', '').isdigit():
                                    continue
                                
                                # Skip if it's a time indicator (e.g., "2h ago", "5m")
                                if any(time_unit in line_lower for time_unit in ['ago', 'min', 'hour', 'day', 'week', 'month', 'year']) and len(line) < 15:
                                    continue
                                
                                # This looks like actual comment text
                                comment_data["comment_text"] = line
                                break
                                comment_data["comment_text"] = line
                                break
                    except:
                        pass
                    
                    # Extract comment likes
                    try:
                        # Look for like button in this comment
                        like_buttons = elem.find_elements(By.CSS_SELECTOR, 'button')
                        
                        for button in like_buttons:
                            try:
                                # Check if it's a like button (has heart icon or aria-label)
                                aria_label = button.get_attribute('aria-label') or ''
                                if 'like' in aria_label.lower():
                                    # Try to find the like count
                                    spans = button.find_elements(By.TAG_NAME, 'span')
                                    for span in spans:
                                        text = span.text.strip()
                                        if text and text.replace(',', '').replace('.', '').isdigit():
                                            comment_data["likes"] = int(text.replace(',', ''))
                                            break
                                    if comment_data["likes"] > 0:
                                        break
                            except:
                                continue
                    except:
                        pass
                    
                    # Create a unique key for this comment to avoid duplicates
                    # Use username + comment_text (or just username if no text)
                    if comment_data["username"]:
                        comment_key = f"{comment_data['username']}:{comment_data['comment_text'] or ''}"
                        
                        # Strict validation before adding comment:
                        # 1. Must have actual comment text (not null)
                        # 2. Comment text must be different from username
                        # 3. Comment must be unique (not seen before)
                        # 4. Comment must be at least 5 characters long (filter out "cast", "like", etc.)
                        # 5. Comment cannot be a single word from UI terms
                        is_valid_comment = (
                            comment_key not in seen_comments and 
                            comment_data["comment_text"] and 
                            comment_data["comment_text"] != comment_data["username"] and
                            len(comment_data["comment_text"]) >= 5 and
                            comment_data["comment_text"].lower() not in single_word_ui
                        )
                        
                        if is_valid_comment:
                            seen_comments.add(comment_key)
                            comments.append(comment_data)
                
                except Exception as e:
                    # Skip this comment if there's an error
                    continue
        
        except Exception as e:
            print(f"      ⚠️  Error in comment extraction: {e}")
        
        return comments
