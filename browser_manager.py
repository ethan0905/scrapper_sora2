#!/usr/bin/env python3
"""
Browser Manager - Handles Chrome WebDriver setup and configuration
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BrowserManager:
    """Manages Chrome browser setup and lifecycle"""
    
    def __init__(self, use_existing=False, debug_port=9222):
        self.driver = None
        self.use_existing = use_existing
        self.debug_port = debug_port
    
    def setup(self):
        """Setup and return Chrome WebDriver"""
        chrome_options = Options()
        
        if self.use_existing:
            print("🔗 Connecting to existing Chrome session...")
            print(f"   Port: {self.debug_port}")
            print("\n💡 If Chrome is not running with remote debugging, launch:")
            print(f'   open -a "Google Chrome" --args --remote-debugging-port={self.debug_port}')
            print()
            
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
        else:
            print("🚀 Launching new Chrome session...")
            # Anti-detection settings
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        if not self.use_existing:
            # Hide automation markers
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Browser ready!\n")
        return self.driver
    
    def close(self):
        """Close the browser"""
        if self.driver and not self.use_existing:
            print("🔒 Closing browser...")
            self.driver.quit()
        elif self.driver and self.use_existing:
            print("✅ Keeping Chrome open (existing session)")
