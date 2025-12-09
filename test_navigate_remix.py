#!/usr/bin/env python3
"""
Test program to navigate through remix list systematically.

This program focuses on understanding the HTML structure and navigating
through remixes in a reliable way, especially after "Load more" clicks.

Strategy:
1. Find the remix container (parent element)
2. Get all remix buttons as a list
3. Navigate by index (remix[0], remix[1], etc.)
4. After "Load more", re-scan and continue from last index
"""

import sys
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver(use_existing=False, debug_port=9222):
    """Setup Selenium WebDriver"""
    chrome_options = Options()
    
    if use_existing:
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    else:
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    if use_existing:
        driver = webdriver.Chrome(options=chrome_options)
    else:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def get_page_html_structure(driver):
    """Get and analyze the HTML structure around remixes"""
    print("\n" + "="*70)
    print("🔍 ANALYZING HTML STRUCTURE")
    print("="*70)
    
    # Look for common container patterns
    container_selectors = [
        "div.flex.w-full.flex-col.gap-2.pt-2",
        "[class*='remix']",
        "[class*='related']",
        "div[class*='grid']",
        "div[class*='flex-col']",
    ]
    
    for selector in container_selectors:
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, selector)
            if containers:
                print(f"\n✅ Found {len(containers)} containers with: {selector}")
                
                # Analyze first container
                if containers:
                    container = containers[0]
                    print(f"   HTML: {container.get_attribute('outerHTML')[:200]}...")
                    
                    # Find buttons inside
                    buttons = container.find_elements(By.TAG_NAME, "button")
                    print(f"   Contains {len(buttons)} buttons")
                    
                    if buttons:
                        print(f"\n   First button classes: {buttons[0].get_attribute('class')}")
                        print(f"   First button HTML: {buttons[0].get_attribute('outerHTML')[:150]}...")
        except Exception as e:
            pass
    
    print("\n" + "="*70)

def find_remix_container(driver):
    """Find the main remix container element"""
    print("\n🔍 Looking for remix container...")
    
    # Try to find the container that holds all remix buttons
    possible_selectors = [
        "div.flex.w-full.flex-col.gap-2.pt-2 > div",  # Known structure
        "div[class*='remix']",
        "div.grid",
        "div.flex.flex-row",
    ]
    
    for selector in possible_selectors:
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, selector)
            if containers:
                # Check if container has remix buttons (small buttons with images)
                for container in containers:
                    buttons = container.find_elements(By.TAG_NAME, "button")
                    small_buttons = [b for b in buttons if "h-8" in (b.get_attribute("class") or "") and "w-6" in (b.get_attribute("class") or "")]
                    
                    if len(small_buttons) > 0:
                        print(f"✅ Found remix container with {len(small_buttons)} remix buttons")
                        print(f"   Selector: {selector}")
                        return container
        except Exception as e:
            pass
    
    print("⚠️  Could not find remix container")
    return None

def get_all_remix_buttons_indexed(driver):
    """
    Get all remix buttons as an indexed list.
    Returns: list of (index, button_element) tuples
    """
    print("\n📋 Scanning for remix buttons...")
    
    remix_buttons = []
    
    # Find all buttons on the page
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    
    for button in all_buttons:
        try:
            classes = button.get_attribute("class") or ""
            aria_label = button.get_attribute("aria-label") or ""
            
            # Skip non-remix buttons
            skip_keywords = ["close", "login", "sign", "share", "like", "follow", "menu", "play"]
            if any(kw in aria_label.lower() for kw in skip_keywords):
                continue
            
            # Check if it's a remix button (h-8 w-6 with image)
            if "h-8" in classes and "w-6" in classes and "shrink-0" in classes:
                imgs = button.find_elements(By.TAG_NAME, "img")
                if imgs and button.is_displayed() and button.is_enabled():
                    remix_buttons.append(button)
        except:
            continue
    
    print(f"✅ Found {len(remix_buttons)} remix buttons")
    
    # Return as indexed list
    return [(i, btn) for i, btn in enumerate(remix_buttons)]

def click_load_more_button(driver):
    """Click the 'Load more' button if it exists"""
    print("\n🔄 Looking for 'Load more' button...")
    
    # Try multiple strategies to find the load more button
    strategies = [
        # Strategy 1: By specific class
        ("button.h-\\[21px\\].w-4", "CSS selector (specific classes)"),
        # Strategy 2: By size attributes
        ("button[class*='w-4'][class*='shrink-0']", "CSS selector (w-4 shrink-0)"),
        # Strategy 3: Scan all buttons
        (None, "Scan all buttons"),
    ]
    
    for selector, description in strategies:
        try:
            if selector:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   Strategy: {description} - Found {len(buttons)} candidates")
            else:
                # Scan all buttons
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                buttons = []
                for btn in all_buttons:
                    classes = btn.get_attribute("class") or ""
                    # Load more is smaller than remix buttons
                    if "h-[21px]" in classes or ("w-4" in classes and "shrink-0" in classes and "h-8" not in classes):
                        buttons.append(btn)
                print(f"   Strategy: {description} - Found {len(buttons)} candidates")
            
            for button in buttons:
                try:
                    if not button.is_displayed() or not button.is_enabled():
                        continue
                    
                    # Additional validation - should have div child
                    divs = button.find_elements(By.TAG_NAME, "div")
                    if not divs:
                        continue
                    
                    classes = button.get_attribute("class") or ""
                    print(f"✅ Found 'Load more' button!")
                    print(f"   Classes: {classes[:100]}...")
                    
                    # Random delay before clicking
                    pre_delay = random.uniform(1.0, 2.5)
                    print(f"   Waiting {pre_delay:.1f}s before clicking...")
                    time.sleep(pre_delay)
                    
                    # Scroll to button with horizontal scroll
                    driver.execute_script("""
                        arguments[0].scrollIntoView({block: 'center', inline: 'end'});
                        window.scrollBy(50, 0);
                    """, button)
                    time.sleep(random.uniform(0.8, 1.5))
                    
                    # Click with JavaScript
                    print("   Clicking 'Load more'...")
                    driver.execute_script("arguments[0].click();", button)
                    
                    # Wait for loading (longer random delay)
                    load_delay = random.uniform(3.5, 5.0)
                    print(f"   Waiting {load_delay:.1f}s for new content to load...")
                    time.sleep(load_delay)
                    
                    print("✅ 'Load more' clicked successfully")
                    return True
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            continue
    
    print("⚠️  'Load more' button not found with any strategy")
    return False

def navigate_remix_by_index(driver, index, button, store_url):
    """
    Navigate to a specific remix by index.
    Returns: (success, new_url)
    """
    try:
        print(f"\n   [{index}] Navigating to remix...")
        
        # Random delay before interaction (anti-detection)
        pre_delay = random.uniform(0.8, 2.5)
        print(f"        Waiting {pre_delay:.1f}s before click...")
        time.sleep(pre_delay)
        
        # Scroll button into view with slight randomization
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", button)
        time.sleep(random.uniform(0.5, 1.2))
        
        # Get button info for debugging
        try:
            img = button.find_element(By.TAG_NAME, "img")
            img_src = img.get_attribute("src")
            print(f"        Button image: {img_src[:50]}...")
        except:
            pass
        
        # Click with JavaScript
        driver.execute_script("arguments[0].click();", button)
        
        # Random delay after click (2-4 seconds for page load)
        post_delay = random.uniform(2.5, 4.0)
        print(f"        Waiting {post_delay:.1f}s for page load...")
        time.sleep(post_delay)
        
        # Get new URL
        new_url = driver.current_url
        
        # Validate navigation
        is_valid = (
            new_url != store_url and
            "/p/" in new_url and
            "login" not in new_url.lower() and
            "auth" not in new_url.lower()
        )
        
        if is_valid:
            print(f"        ✅ Success: {new_url.split('/')[-1][:40]}...")
            
            # Random delay before going back
            back_delay = random.uniform(1.0, 2.0)
            print(f"        Waiting {back_delay:.1f}s before going back...")
            time.sleep(back_delay)
            
            # Go back
            driver.back()
            
            # Wait for page to load
            after_back_delay = random.uniform(2.5, 4.0)
            print(f"        Waiting {after_back_delay:.1f}s after going back...")
            time.sleep(after_back_delay)
            
            # Verify we're back on the right page
            if driver.current_url != store_url:
                print(f"        ⚠️  Not on original page, navigating...")
                driver.get(store_url)
                time.sleep(random.uniform(2.0, 3.0))
            
            # Re-scroll to remix section
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(random.uniform(0.8, 1.5))
            
            return True, new_url
        else:
            print(f"        ⚠️  Invalid URL: {new_url}")
            if new_url != store_url:
                driver.back()
                time.sleep(1)
            return False, None
            
    except Exception as e:
        print(f"        ❌ Error: {str(e)[:50]}")
        try:
            if driver.current_url != store_url:
                driver.back()
                time.sleep(1)
        except:
            pass
        return False, None

def test_systematic_navigation(driver, start_url, max_load_more=5):
    """
    Test systematic navigation through remixes using index-based approach.
    
    Strategy:
    1. Keep track of which index we're at (processed_count)
    2. Before each click, re-fetch ALL buttons to avoid stale elements
    3. Click button at current index
    4. Go back to original page
    5. Increment index and repeat
    6. After "Load more", continue with next index
    
    This ensures strictly forward navigation: 0→1→2→3... with no backtracking
    """
    
    print("\n" + "="*70)
    print("🧪 TEST: SYSTEMATIC REMIX NAVIGATION (STRICTLY FORWARD)")
    print("="*70)
    
    # Navigate to start URL
    print(f"\n📍 Navigating to: {start_url}")
    driver.get(start_url)
    time.sleep(3)
    
    # Store original URL
    store_url = driver.current_url
    print(f"✅ Page loaded: {store_url}")
    
    # Scroll to remix section
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(2)
    
    # Optional: Analyze HTML structure first
    print("\n" + "="*70)
    print("Would you like to analyze HTML structure first? (y/n)")
    print("="*70)
    # get_page_html_structure(driver)  # Uncomment to analyze
    
    # Track results
    all_remix_urls = []
    seen_urls = set()
    current_index = 0  # Current position in the remix list
    load_more_clicks = 0
    
    # Main loop
    while load_more_clicks <= max_load_more:
        print(f"\n{'='*70}")
        print(f"🔄 PROCESSING INDEX {current_index} (Load more clicks: {load_more_clicks})")
        print("="*70)
        
        # Make sure we're on the right page
        if driver.current_url != store_url:
            print("⚠️  Wrong page, navigating back...")
            driver.get(store_url)
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
        
        # Re-fetch ALL remix buttons (fresh elements)
        indexed_buttons = get_all_remix_buttons_indexed(driver)
        total_buttons = len(indexed_buttons)
        
        if not indexed_buttons:
            print("⚠️  No remix buttons found")
            break
        
        print(f"\n📊 Status:")
        print(f"   Total buttons available: {total_buttons}")
        print(f"   Current index: {current_index}")
        print(f"   Unique remixes found so far: {len(all_remix_urls)}")
        
        # Check if we need to load more
        if current_index >= total_buttons:
            if load_more_clicks < max_load_more:
                print(f"\n🔄 Reached end of list (index {current_index} >= {total_buttons} buttons)")
                print(f"   Attempting to load more remixes...")
                
                if click_load_more_button(driver):
                    load_more_clicks += 1
                    print(f"✅ Load more clicked ({load_more_clicks}/{max_load_more})")
                    
                    # Wait for new content
                    load_wait = random.uniform(4.0, 6.0)
                    print(f"   Waiting {load_wait:.1f}s for new content...")
                    time.sleep(load_wait)
                    
                    # Verify page
                    if driver.current_url != store_url:
                        print("   ⚠️  Page changed, navigating back...")
                        driver.get(store_url)
                        time.sleep(random.uniform(2.0, 3.0))
                    
                    # Scroll to remix section
                    scroll_position = random.randint(45, 55)
                    driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_position/100});")
                    time.sleep(random.uniform(1.5, 2.5))
                    
                    # Continue to next iteration to re-fetch buttons
                    continue
                else:
                    print("ℹ️  No 'Load more' button found, stopping")
                    break
            else:
                print(f"\n✅ Reached maximum load more clicks ({max_load_more})")
                break
        
        # Get the button at current index (with fresh element reference)
        if current_index < len(indexed_buttons):
            idx, button = indexed_buttons[current_index]
            
            # Navigate to this remix
            print(f"\n🎯 Navigating to remix at index {current_index}...")
            success, remix_url = navigate_remix_by_index(driver, current_index, button, store_url)
            
            if success and remix_url:
                if remix_url not in seen_urls:
                    seen_urls.add(remix_url)
                    all_remix_urls.append(remix_url)
                    print(f"        ✅ New remix found! Total: {len(all_remix_urls)}")
                else:
                    print(f"        ⚠️  Duplicate URL (already seen)")
            
            # Move to next index (strictly forward)
            current_index += 1
        else:
            print(f"⚠️  Index {current_index} out of range (only {len(indexed_buttons)} buttons)")
            break
    
    # Final results
    print("\n" + "="*70)
    print("🎉 NAVIGATION TEST COMPLETE")
    print("="*70)
    print(f"\n📊 Results:")
    print(f"   Total unique remixes found: {len(all_remix_urls)}")
    print(f"   Final index reached: {current_index}")
    print(f"   Load more clicks: {load_more_clicks}")
    print(f"\n📋 Remix URLs:")
    for i, url in enumerate(all_remix_urls, 1):
        print(f"   {i}. {url}")
    
    return all_remix_urls

def main():
    """Main test program"""
    
    print("="*70)
    print("🧪 REMIX NAVIGATION TEST")
    print("="*70)
    print()
    print("This program tests systematic navigation through remix lists,")
    print("especially after 'Load more' clicks.")
    print()
    
    # Get URL from command line or prompt
    if len(sys.argv) > 1:
        start_url = sys.argv[1]
    else:
        start_url = input("Enter Sora video URL: ").strip()
    
    if not start_url:
        print("❌ No URL provided")
        return
    
    # Check for --existing flag (or default to True)
    use_existing = "--new" not in sys.argv  # Use existing by default
    
    print()
    print("🔧 Setup:")
    print(f"   URL: {start_url}")
    print(f"   Mode: {'Existing Chrome' if use_existing else 'New Browser'}")
    print()
    
    if use_existing:
        print("🔗 Connecting to existing Chrome (port 9222)...")
        print("   Make sure Chrome is running with:")
        print("   open -a 'Google Chrome' --args --remote-debugging-port=9222")
        print()
    else:
        print("🚀 Starting new browser...")
    
    # Setup driver
    driver = setup_driver(use_existing=use_existing)
    
    try:
        # Run the test
        remix_urls = test_systematic_navigation(driver, start_url, max_load_more=5)
        
        print("\n✅ Test completed!")
        print(f"📊 Found {len(remix_urls)} unique remixes")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not use_existing:
            print("\n🔒 Closing browser...")
            driver.quit()
        else:
            print("\n✅ Keeping Chrome open (existing session)")

if __name__ == "__main__":
    main()
