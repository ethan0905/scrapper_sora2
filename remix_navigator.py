#!/usr/bin/env python3
"""
Remix Navigator - Handles finding and loading remix buttons
"""

import time
import random
from selenium.webdriver.common.by import By


class RemixNavigator:
    """Manages remix button detection and loading"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def get_remix_buttons(self):
        """Get all remix thumbnail buttons on current page"""
        try:
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            # Filter for remix buttons (h-8 w-6 classes, not the load more button)
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
            
            # Debug: Show what we found
            # Uncomment for very verbose debugging:
            # print(f"   🔍 DEBUG: Found {len(remix_buttons)} remix buttons out of {len(all_buttons)} total buttons")
            
            return remix_buttons
        except:
            return []
    
    def find_load_more_button(self):
        """Find the 'Load more' button"""
        all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
        
        for button in all_buttons:
            try:
                classes = button.get_attribute("class") or ""
                # Load more button has w-4 and shrink-0 classes
                if "w-4" in classes and "shrink-0" in classes:
                    # Check for backdrop-blur div child
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
        Click 'Load more' repeatedly until target count is reached
        
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
    
    def click_remix_button(self, button_index):
        """
        Click a remix button by index
        
        Args:
            button_index: Index of the button to click (0-based)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"   🔍 DEBUG: Looking for button at index {button_index}...")
            
            # Get current URL before clicking
            current_url_before = self.driver.current_url
            print(f"   🔍 DEBUG: Current URL before click: {current_url_before}")
            
            # Get fresh buttons
            buttons = self.get_remix_buttons()
            print(f"   🔍 DEBUG: Found {len(buttons)} total remix buttons")
            
            if button_index >= len(buttons):
                print(f"   ⚠️  Button index {button_index} out of range (only {len(buttons)} buttons)")
                return False
            
            button = buttons[button_index]
            
            # Debug: Get button attributes
            try:
                button_class = button.get_attribute("class")
                button_html = button.get_attribute("outerHTML")[:200]  # First 200 chars
                print(f"   🔍 DEBUG: Button class: {button_class}")
                print(f"   🔍 DEBUG: Button HTML: {button_html}...")
            except Exception as e:
                print(f"   🔍 DEBUG: Could not get button attributes: {e}")
            
            # Scroll to button
            print(f"   🔍 DEBUG: Scrolling to button...")
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                button
            )
            time.sleep(0.5)
            
            # Click
            print(f"   🔍 DEBUG: Clicking button...")
            button.click()
            
            # Wait and check URL changed
            time.sleep(2.0)
            current_url_after = self.driver.current_url
            print(f"   🔍 DEBUG: Current URL after click: {current_url_after}")
            
            if current_url_after == current_url_before:
                print(f"   ⚠️  WARNING: URL did not change after clicking!")
                return False
            else:
                print(f"   ✅ DEBUG: Successfully navigated to new URL")
            
            time.sleep(random.uniform(1.0, 2.0))
            
            return True
        
        except Exception as e:
            print(f"   ❌ Error clicking button: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def wait_for_page_reload(self, min_buttons_needed=0):
        """
        Wait for page to reload after going back
        
        Args:
            min_buttons_needed: Minimum number of buttons that should be present
        
        Returns:
            bool: True if page reloaded successfully
        """
        max_wait = 10
        wait_start = time.time()
        
        while time.time() - wait_start < max_wait:
            try:
                buttons = self.get_remix_buttons()
                if len(buttons) >= min_buttons_needed:
                    return True
            except:
                pass
            time.sleep(0.5)
        
        return False
