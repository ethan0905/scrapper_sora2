#!/usr/bin/env python3
"""
Debug script to inspect the actual HTML structure of a Sora video page
and find the correct selectors for the remix section.
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def debug_page_structure(url):
    """Inspect the page and print information about remix elements"""
    
    print("=" * 70)
    print("DEBUG: Inspection de la structure de page Sora")
    print("=" * 70)
    print(f"🌐 URL: {url}")
    print()
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to page
        print("🌐 Chargement de la page...")
        driver.get(url)
        time.sleep(5)
        
        # Scroll to ensure everything loads
        print("📜 Scroll pour charger le contenu...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(3)
        
        print()
        print("=" * 70)
        print("ANALYSE DES ÉLÉMENTS")
        print("=" * 70)
        print()
        
        # 1. Check for overflow-x-auto divs
        print("1️⃣  Recherche de divs avec overflow-x-auto...")
        overflow_divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='overflow-x-auto']")
        print(f"   Trouvés: {len(overflow_divs)} éléments")
        
        for i, div in enumerate(overflow_divs[:5], 1):
            classes = div.get_attribute("class")
            print(f"   #{i}: {classes}")
            
            # Count buttons inside
            buttons = div.find_elements(By.TAG_NAME, "button")
            print(f"        -> {len(buttons)} boutons à l'intérieur")
        
        print()
        
        # 2. Check for flex containers with gap-2
        print("2️⃣  Recherche de containers flex avec gap-2...")
        flex_divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='gap-2']")
        print(f"   Trouvés: {len(flex_divs)} éléments")
        
        for i, div in enumerate(flex_divs[:5], 1):
            classes = div.get_attribute("class")
            print(f"   #{i}: {classes[:100]}...")
        
        print()
        
        # 3. Check for buttons with images
        print("3️⃣  Recherche de boutons avec images...")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"   Total de boutons sur la page: {len(all_buttons)}")
        
        buttons_with_img = []
        for button in all_buttons:
            imgs = button.find_elements(By.TAG_NAME, "img")
            if imgs:
                buttons_with_img.append(button)
        
        print(f"   Boutons avec images: {len(buttons_with_img)}")
        
        print()
        
        # 4. Look for buttons with overlay divs
        print("4️⃣  Recherche de boutons avec overlay...")
        buttons_with_overlay = []
        for button in all_buttons[:50]:  # Check first 50
            overlays = button.find_elements(By.CSS_SELECTOR, "div[class*='absolute']")
            if overlays:
                buttons_with_overlay.append(button)
        
        print(f"   Boutons avec div absolute: {len(buttons_with_overlay)}")
        
        print()
        
        # 5. Save HTML for manual inspection
        print("5️⃣  Sauvegarde du HTML...")
        html = driver.page_source
        with open("/Users/ethan/Desktop/scrapper_sora2/debug_page_structure.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   ✅ HTML sauvegardé: debug_page_structure.html")
        
        print()
        
        # 6. Try to find remix-related text
        print("6️⃣  Recherche de texte lié aux remixes...")
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        remix_keywords = ["remix", "load more", "show more", "voir plus"]
        for keyword in remix_keywords:
            if keyword in body_text:
                print(f"   ✅ Trouvé: '{keyword}'")
            else:
                print(f"   ❌ Non trouvé: '{keyword}'")
        
        print()
        print("=" * 70)
        print("✅ Inspection terminée")
        print("=" * 70)
        print()
        print("💡 Consultez le fichier debug_page_structure.html pour plus de détails")
        print("   Vous pouvez l'ouvrir avec Chrome et inspecter les éléments")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n⏸️  Appuyez sur ENTRÉE pour fermer le navigateur...")
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Usage: python debug_page_inspector.py <sora_video_url>")
        print()
        print("Example:")
        print("  python debug_page_inspector.py https://sora.chatgpt.com/p/abcd1234")
        sys.exit(1)
    
    debug_page_structure(url)
