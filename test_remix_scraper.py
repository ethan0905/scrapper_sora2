#!/usr/bin/env python3
"""
Test script to verify the remix scraper finds and extracts all remix URLs.
"""

import sys
import time
from selenium.webdriver.common.by import By
from scraper_sora_advanced import SoraScraper

def test_remix_extraction(test_url, use_existing=False):
    """Test remix extraction on a sample Sora video page"""
    
    print("=" * 70)
    print("TEST: Extraction des Remixes Sora")
    print("=" * 70)
    print()
    
    # Initialize scraper - use existing Chrome if specified
    if use_existing:
        print("🔗 Mode: Utilisation de Chrome existant")
        scraper = SoraScraper(use_existing_chrome=True, debug_port=9222)
    else:
        print("🆕 Mode: Nouveau navigateur")
        scraper = SoraScraper(headless=False)
    
    try:
        print(f"🌐 URL de test: {test_url}")
        print()
        
        # Create the driver first!
        if use_existing:
            print("🔗 Connexion à Chrome existant...")
        else:
            print("🚀 Initialisation du navigateur...")
        scraper.create_driver()
        print()
        
        # Navigate to the video page
        print("🌐 Navigation vers la page vidéo...")
        scraper.driver.get(test_url)
        time.sleep(5)  # Wait for page to load
        print()
        
        print("📋 Extraction des remixes...")
        print()
        
        # Store initial URL for safety check
        initial_url = scraper.driver.current_url
        
        # Extract remix URLs
        remix_urls = scraper._find_remix_links(max_load_more_clicks=5)
        
        # Safety check: verify we're back on the original page
        final_url = scraper.driver.current_url
        if final_url != initial_url:
            print(f"⚠️  WARNING: Page finale différente de la page initiale!")
            print(f"   Initial: {initial_url}")
            print(f"   Final:   {final_url}")
        else:
            print(f"✅ Page d'origine restaurée correctement")
        print()
        
        print("=" * 70)
        print("RÉSULTATS")
        print("=" * 70)
        print(f"✅ {len(remix_urls)} remixes trouvés")
        print()
        
        if remix_urls:
            print("URLs des remixes:")
            for i, url in enumerate(remix_urls, 1):
                print(f"  {i}. {url}")
        else:
            print("⚠️  Aucun remix trouvé")
        
        print()
        print("=" * 70)
        
        # Test metadata extraction on first remix
        if remix_urls:
            print()
            print("TEST: Extraction des métadonnées du premier remix")
            print("=" * 70)
            
            first_remix = remix_urls[0]
            print(f"🌐 URL: {first_remix}")
            print()
            
            # Navigate to the first remix page
            scraper.driver.get(first_remix)
            time.sleep(3)
            
            # Find video element and get video URL
            try:
                video_element = scraper.driver.find_element(By.TAG_NAME, "video")
                video_url = video_element.get_attribute("src")
                print(f"  - URL fichier vidéo: {video_url[:60] if video_url else 'Non trouvée'}...")
            except:
                print(f"  - URL fichier vidéo: Non trouvée")
            
            # For now, skip detailed metadata extraction in test
            print(f"  - Page remix chargée avec succès")
            print()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close browser
        try:
            if scraper.driver:
                scraper.driver.quit()
        except:
            pass
    
    return len(remix_urls) > 0

if __name__ == "__main__":
    # Check for --existing flag
    use_existing = "--existing" in sys.argv or "-e" in sys.argv
    
    # Remove flags from args
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    
    # Replace with actual Sora video URL
    if len(args) > 0:
        test_url = args[0]
        print(f"Using provided URL: {test_url}")
        if use_existing:
            print(f"Mode: Chrome existant (port 9222)")
        print()
    else:
        print("Usage: python test_remix_scraper.py [--existing] <sora_video_url>")
        print()
        print("Options:")
        print("  --existing, -e    Use existing Chrome session (recommended)")
        print()
        print("Examples:")
        print("  # Use existing Chrome (recommended):")
        print("  python test_remix_scraper.py --existing https://sora.chatgpt.com/p/abcd1234")
        print()
        print("  # Open new browser:")
        print("  python test_remix_scraper.py https://sora.chatgpt.com/p/abcd1234")
        sys.exit(1)
    
    # Run the test
    success = test_remix_extraction(test_url, use_existing=use_existing)
    
    if success:
        print("✅ Test réussi!")
        sys.exit(0)
    else:
        print("❌ Test échoué")
        sys.exit(1)
