#!/usr/bin/env python3
"""
Simple script to extract remixes using your existing Chrome session.
This will connect to your already-open Chrome browser.
"""

import sys
import time

# Add the parent directory to path to import the scraper
sys.path.insert(0, '/Users/ethan/Desktop/scrapper_sora2')

from scraper_sora_advanced import SoraScraper

def test_with_existing_chrome(video_url):
    """Test remix extraction using existing Chrome session"""
    
    print("=" * 70)
    print("TEST: Extraction des Remixes (Chrome Existant)")
    print("=" * 70)
    print()
    print(f"🌐 URL: {video_url}")
    print()
    print("💡 Assurez-vous que Chrome est ouvert avec remote debugging:")
    print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
    print("     --remote-debugging-port=9222 \\")
    print("     --user-data-dir=\"$HOME/chrome-selenium-profile\"")
    print()
    input("Appuyez sur ENTRÉE quand Chrome est prêt...")
    print()
    
    # Initialize scraper with existing Chrome
    scraper = SoraScraper(use_existing_chrome=True, debug_port=9222)
    
    try:
        # Connect to existing Chrome
        print("🔗 Connexion à Chrome...")
        scraper.create_driver()
        print()
        
        # Navigate to video page
        print("🌐 Navigation vers la page vidéo...")
        scraper.driver.get(video_url)
        time.sleep(5)
        print()
        
        # Extract remixes
        print("📋 Extraction des remixes...")
        print()
        remix_urls = scraper._find_remix_links(max_load_more_clicks=5)
        
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
        
        return len(remix_urls) > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Don't close the browser - leave it open
        print()
        print("✅ Test terminé (navigateur laissé ouvert)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    else:
        video_url = "https://sora.chatgpt.com/p/s_6932520ddd548191b4ddede8695d361a"
    
    success = test_with_existing_chrome(video_url)
    
    if success:
        print("✅ Test réussi!")
        sys.exit(0)
    else:
        print("❌ Test échoué - vérifiez les sélecteurs CSS")
        sys.exit(1)
