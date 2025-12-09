import os
import time
import pathlib
import argparse
import json
import hashlib
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuration par défaut
DEST_DIR = pathlib.Path("videos")
DEST_DIR.mkdir(exist_ok=True)

# Extensions vidéo supportées
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.mkv', '.avi', '.flv')

# Configuration Selenium
HEADLESS = False  # False = voir le navigateur, True = mode invisible


class SoraScraper:
    """Classe principale pour scraper Sora avec différents modes."""
    
    def __init__(self, headless=False, use_existing_chrome=False, debug_port=9222):
        self.driver = None
        self.headless = headless
        self.use_existing_chrome = use_existing_chrome
        self.debug_port = debug_port
        
    def create_driver(self):
        """
        Crée un driver Selenium configuré pour Chrome.
        Peut soit créer une nouvelle instance, soit se connecter à une session existante.
        
        Returns:
            webdriver.Chrome: Le driver Selenium
        """
        chrome_options = Options()
        
        if self.use_existing_chrome:
            # Se connecter à une session Chrome existante
            print("� Connexion à votre session Chrome existante...")
            print(f"   Port de débogage: {self.debug_port}")
            print("\n💡 Si Chrome n'est pas ouvert avec remote debugging, lancez:")
            print(f'   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port={self.debug_port} --user-data-dir="$HOME/chrome-selenium-profile"')
            print()
            
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
            
            try:
                # Pas besoin de ChromeDriverManager pour une session existante
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Connecté à Chrome existant!\n")
                return self.driver
            except Exception as e:
                print(f"❌ Impossible de se connecter à Chrome: {e}")
                print("\n💡 Assurez-vous que Chrome est lancé avec --remote-debugging-port")
                print("   Lancez cette commande dans un terminal:")
                print(f'   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port={self.debug_port} --user-data-dir="$HOME/chrome-selenium-profile"')
                raise
        else:
            # Créer une nouvelle instance Chrome
            print("🚀 Création d'une nouvelle session Chrome...")
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Options pour éviter la détection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # User agent
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Créer le service et le driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Masquer l'automatisation
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Navigateur prêt\n")
            return self.driver
    
    def wait_for_login(self):
        """Attend que l'utilisateur se connecte si nécessaire."""
        current_url = self.driver.current_url.lower()
        
        # Vérifier si on est sur une page de connexion
        if any(keyword in current_url for keyword in ["login", "auth", "signin", "sign-in"]):
            print("\n" + "="*60)
            print("🔐 CONNEXION REQUISE")
            print("="*60)
            print("Le site nécessite une authentification.")
            print(f"URL actuelle: {self.driver.current_url}")
            print("\n👉 Veuillez vous connecter manuellement dans le navigateur.")
            print("👉 Naviguez vers la page souhaitée si nécessaire.")
            print("👉 Appuyez sur ENTRÉE une fois connecté et sur la bonne page...")
            input()
            print("\n✅ Reprise du scraping...")
            print(f"📍 URL après connexion: {self.driver.current_url}\n")
            time.sleep(2)  # Petit délai pour stabiliser
    
    def scroll_and_load(self, num_scrolls=5, delay=2, all_mode=False):
        """
        Fait défiler la page pour charger les vidéos lazy-loaded.
        
        IMPORTANT: Collecte les URLs PENDANT le scroll pour contourner le virtual scrolling.
        Sora utilise un système de virtualisation React qui ne garde que ~6 vidéos dans le DOM.
        
        Args:
            num_scrolls (int): Nombre de scrolls à effectuer
            delay (float): Délai entre chaque scroll en secondes
            all_mode (bool): Si True, continue jusqu'à la fin réelle du contenu
            
        Returns:
            set: Ensemble d'URLs de vidéos collectées pendant le scroll
        """
        if all_mode:
            print(f"📜 Scrolling en mode ALL (jusqu'à la fin du contenu, délai: {delay}s)...")
            max_no_change = 5  # Plus tolérant en mode ALL
        else:
            print(f"📜 Scrolling de la page (max {num_scrolls} fois, délai: {delay}s)...")
            max_no_change = 3  # Normal
        
        print("   🎯 Collection des URLs pendant le scroll (contournement du virtual scrolling)...")
        
        collected_urls = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        no_change_count = 0  # Compteur pour détecter la fin
        scroll_count = 0
        
        while True:
            scroll_count += 1
            
            # COLLECTER les URLs AVANT de scroller (vidéos dans le viewport actuel)
            try:
                video_elements = self.driver.find_elements(By.TAG_NAME, "video")
                for video in video_elements:
                    try:
                        src = video.get_attribute("src")
                        if src and src not in collected_urls:
                            collected_urls.add(src)
                    except:
                        pass
            except:
                pass
            
            # Vérifier si on a atteint la limite (sauf en mode ALL)
            if not all_mode and scroll_count > num_scrolls:
                print(f"   ℹ️  Limite de {num_scrolls} scrolls atteinte")
                break
            
            # Scroller jusqu'en bas
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)
            
            # Vérifier si la hauteur a changé (nouveau contenu chargé)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                no_change_count += 1
                print(f"   ⚠️ Pas de nouveau contenu (tentative {no_change_count}/{max_no_change}) - {len(collected_urls)} URLs collectées")
                
                # Si N scrolls consécutifs sans changement, on arrête
                if no_change_count >= max_no_change:
                    print(f"   ✅ Fin du contenu atteinte après {scroll_count} scrolls")
                    break
            else:
                no_change_count = 0  # Réinitialiser si du contenu est chargé
                last_height = new_height
                if all_mode:
                    print(f"   Scroll {scroll_count} effectué - Nouveau contenu chargé - {len(collected_urls)} URLs")
                else:
                    print(f"   Scroll {scroll_count}/{num_scrolls} effectué - Nouveau contenu chargé - {len(collected_urls)} URLs")
            
            # Sécurité : limite absolue même en mode ALL
            if scroll_count >= 500:
                print(f"   ⚠️ Limite de sécurité atteinte (500 scrolls)")
                break
        
        # DERNIÈRE collecte après le dernier scroll
        try:
            video_elements = self.driver.find_elements(By.TAG_NAME, "video")
            for video in video_elements:
                try:
                    src = video.get_attribute("src")
                    if src and src not in collected_urls:
                        collected_urls.add(src)
                except:
                    pass
        except:
            pass
        
        print(f"✅ Scrolling terminé - {len(collected_urls)} URLs collectées au total\n")
        return collected_urls
    
    def extract_video_elements(self, max_videos=None):
        """
        Extrait les éléments vidéo de la page.
        
        Args:
            max_videos (int): Nombre maximum de vidéos à extraire
            
        Returns:
            list: Liste d'éléments WebElement contenant des vidéos
        """
        print("🔍 Recherche d'éléments vidéo dans la page...")
        
        video_elements = []
        
        # Chercher différents sélecteurs possibles pour Sora
        selectors = [
            "video",
            "[data-video]",
            "[data-src*='.mp4']",
            "[data-src*='.webm']",
            "div[class*='video']",
            "article[class*='video']",
            "div[class*='post']",
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   Trouvé {len(elements)} éléments avec sélecteur: {selector}")
                    video_elements.extend(elements)
            except Exception as e:
                pass
        
        # Dédupliquer
        video_elements = list(set(video_elements))
        
        # Limiter au nombre demandé
        if max_videos and len(video_elements) > max_videos:
            video_elements = video_elements[:max_videos]
            print(f"   Limité à {max_videos} vidéos")
        
        print(f"✅ {len(video_elements)} éléments vidéo trouvés\n")
        return video_elements
    
    def extract_video_urls_from_elements(self, elements):
        """
        Extrait les URLs de vidéos depuis les éléments.
        
        Args:
            elements (list): Liste d'éléments WebElement
            
        Returns:
            set: Ensemble d'URLs de vidéos
        """
        print("🔗 Extraction des URLs depuis les éléments...")
        
        video_urls = set()
        
        for element in elements:
            try:
                # Essayer différents attributs
                for attr in ['src', 'data-src', 'data-video', 'href']:
                    try:
                        url = element.get_attribute(attr)
                        if url and any(ext in url.lower() for ext in VIDEO_EXTENSIONS):
                            video_urls.add(url)
                    except:
                        pass
                
                # Chercher dans les enfants
                try:
                    video_tag = element.find_element(By.TAG_NAME, "video")
                    src = video_tag.get_attribute("src")
                    if src:
                        video_urls.add(src)
                except:
                    pass
                
                try:
                    source_tag = element.find_element(By.TAG_NAME, "source")
                    src = source_tag.get_attribute("src")
                    if src:
                        video_urls.add(src)
                except:
                    pass
                    
            except Exception as e:
                pass
        
        print(f"✅ {len(video_urls)} URLs extraites\n")
        return video_urls
    
    def extract_all_video_urls(self, html, base_url):
        """
        Extrait toutes les URLs de vidéos depuis le HTML (méthode de backup).
        
        Args:
            html (str): Le contenu HTML
            base_url (str): L'URL de base
            
        Returns:
            set: Ensemble d'URLs de vidéos
        """
        soup = BeautifulSoup(html, 'html.parser')
        video_urls = set()
        
        # Balises <video>
        for video_tag in soup.find_all('video', src=True):
            url = urljoin(base_url, video_tag['src'])
            video_urls.add(url)
        
        # Balises <source>
        for source_tag in soup.find_all('source', src=True):
            url = urljoin(base_url, source_tag['src'])
            video_urls.add(url)
        
        # Liens vers vidéos
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(href.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                url = urljoin(base_url, href)
                video_urls.add(url)
        
        # Attributs data-*
        all_tags = soup.find_all(True)
        for tag in all_tags:
            for attr, value in tag.attrs.items():
                if isinstance(value, str) and any(ext in value.lower() for ext in VIDEO_EXTENSIONS):
                    url = urljoin(base_url, value)
                    if url.startswith('http'):
                        video_urls.add(url)
        
        return video_urls
    
    def scrape_homepage(self, num_videos=10, scroll_delay=2, all_mode=False):
        """
        Mode 1: Scrape la page d'accueil de Sora.
        
        Args:
            num_videos (int): Nombre de vidéos à scraper
            scroll_delay (float): Délai entre chaque scroll
            all_mode (bool): Si True, scrape jusqu'à la fin du contenu
            
        Returns:
            set: Ensemble d'URLs de vidéos
        """
        url = "https://sora.chatgpt.com/explore?feed=top"
        
        print("="*60)
        print("🏠 MODE 1: SCRAPING DE LA PAGE D'ACCUEIL")
        print("="*60)
        print(f"📍 URL: {url}")
        if all_mode:
            print(f"🎯 Mode: TOUTES les vidéos (♾️)")
        else:
            print(f"🎯 Nombre de vidéos: {num_videos}")
        print(f"⏱️  Délai entre scrolls: {scroll_delay}s\n")
        
        # Créer le driver si nécessaire
        if not self.driver:
            self.create_driver()
        
        # Charger la page
        print(f"🌐 Chargement de la page...")
        self.driver.get(url)
        time.sleep(5)  # Attente initiale
        
        # Vérifier si connexion nécessaire
        self.wait_for_login()
        
        # Calculer le nombre de scrolls nécessaires (environ 3-5 vidéos par scroll)
        if all_mode:
            num_scrolls = 500  # Grande valeur pour le mode ALL
        else:
            num_scrolls = max(5, (num_videos // 3) + 2)
        
        # Scroller ET collecter les vidéos (important pour le virtual scrolling!)
        video_urls = self.scroll_and_load(num_scrolls=num_scrolls, delay=scroll_delay, all_mode=all_mode)
        
        print(f"📊 URLs collectées pendant le scroll: {len(video_urls)}")
        
        # Fallback: extraire aussi les éléments restants dans le viewport final
        elements = self.extract_video_elements(max_videos=num_videos)
        fallback_urls = self.extract_video_urls_from_elements(elements)
        
        # Combiner les deux ensembles
        original_count = len(video_urls)
        video_urls.update(fallback_urls)
        
        if len(video_urls) > original_count:
            print(f"📊 URLs additionnelles trouvées dans le viewport final: {len(video_urls) - original_count}")
        
        print(f"✅ Total final: {len(video_urls)} URLs uniques\n")
        
        # Backup: parser le HTML (au cas où)
        if not video_urls:
            print("⚠️ Aucune URL trouvée, tentative avec BeautifulSoup...")
            html = self.driver.page_source
            video_urls = self.extract_all_video_urls(html, url)
        
        return video_urls
    
    def scrape_user_profile(self, profile_url, num_videos=10, scroll_delay=2, all_mode=False):
        """
        Mode 2: Scrape le profil d'un utilisateur spécifique.
        
        Args:
            profile_url (str): URL du profil utilisateur
            num_videos (int): Nombre de vidéos à scraper
            scroll_delay (float): Délai entre chaque scroll
            all_mode (bool): Si True, scrape jusqu'à la fin du contenu
            
        Returns:
            set: Ensemble d'URLs de vidéos
        """
        print("="*60)
        print("👤 MODE 2: SCRAPING D'UN PROFIL UTILISATEUR")
        print("="*60)
        print(f"📍 URL demandée: {profile_url}")
        if all_mode:
            print(f"🎯 Mode: TOUTES les vidéos (♾️)")
        else:
            print(f"🎯 Nombre de vidéos: {num_videos}")
        print(f"⏱️  Délai entre scrolls: {scroll_delay}s\n")
        
        # Créer le driver si nécessaire
        if not self.driver:
            self.create_driver()
        
        # Charger la page du profil
        print(f"🌐 Chargement du profil...")
        self.driver.get(profile_url)
        time.sleep(5)  # Attente initiale
        
        # Vérifier l'URL actuelle après chargement
        current_url = self.driver.current_url
        print(f"📍 URL actuelle: {current_url}")
        
        # Vérifier si on a été redirigé vers la page de connexion
        self.wait_for_login()
        
        # Re-vérifier l'URL après connexion potentielle
        current_url = self.driver.current_url
        print(f"📍 URL finale: {current_url}")
        
        # Détecter le type de page
        page_type = self._detect_page_type()
        print(f"🔍 Type de page détecté: {page_type}")
        
        # Vérifier qu'on est bien sur le profil demandé
        if profile_url not in current_url and not self._is_similar_url(profile_url, current_url):
            print("\n⚠️  ATTENTION: L'URL actuelle ne correspond pas à l'URL demandée!")
            print(f"   Demandée: {profile_url}")
            print(f"   Actuelle: {current_url}")
            
            # Si on est sur la homepage au lieu du profil, c'est un problème
            if page_type == "homepage":
                print("\n❌ ERREUR: Vous êtes sur la page d'accueil, pas sur le profil!")
                print("\n💡 Tentative de navigation vers le bon profil...")
                
                # Essayer de naviguer à nouveau
                self.driver.get(profile_url)
                time.sleep(5)
                
                current_url = self.driver.current_url
                page_type = self._detect_page_type()
                print(f"📍 Nouvelle URL: {current_url}")
                print(f"🔍 Type de page: {page_type}")
                
                if page_type != "profile":
                    print("\n❌ Impossible d'atteindre le profil demandé.")
                    print("   Le site vous a redirigé vers une autre page.")
                    print("\n💡 Conseils:")
                    print("   1. Vérifiez que l'URL du profil est correcte")
                    print("   2. Le profil existe-t-il vraiment ?")
                    print("   3. Êtes-vous connecté avec un compte valide ?")
                    print("   4. Le profil est-il privé ou bloqué ?")
                    print("\n⚠️  Continuation du scraping sur la page actuelle...")
        
        # Vérifier qu'on est sur un profil
        if page_type != "profile":
            print(f"\n⚠️  ATTENTION: Vous n'êtes pas sur une page de profil!")
            print(f"   Type de page: {page_type}")
            print(f"   URL: {current_url}")
            print("\n   Les résultats peuvent ne pas être ceux attendus.")
        
        # Attendre que la page se stabilise
        print("\n⏳ Attente du chargement complet de la page...")
        time.sleep(3)
        
        # Calculer le nombre de scrolls
        if all_mode:
            num_scrolls = 500  # Grande valeur pour le mode ALL
        else:
            num_scrolls = max(5, (num_videos // 3) + 2)
        
        # Scroller ET collecter les vidéos (important pour le virtual scrolling!)
        video_urls = self.scroll_and_load(num_scrolls=num_scrolls, delay=scroll_delay, all_mode=all_mode)
        
        print(f"📊 URLs collectées pendant le scroll: {len(video_urls)}")
        
        # Fallback: extraire aussi les éléments restants dans le viewport final
        elements = self.extract_video_elements(max_videos=num_videos)
        fallback_urls = self.extract_video_urls_from_elements(elements)
        
        # Combiner les deux ensembles
        original_count = len(video_urls)
        video_urls.update(fallback_urls)
        
        if len(video_urls) > original_count:
            print(f"📊 URLs additionnelles trouvées dans le viewport final: {len(video_urls) - original_count}")
        
        print(f"✅ Total final: {len(video_urls)} URLs uniques\n")
        
        # Backup: parser le HTML (au cas où)
        if not video_urls:
            print("⚠️ Aucune URL trouvée, tentative avec BeautifulSoup...")
            html = self.driver.page_source
            # Utiliser l'URL actuelle du navigateur, pas celle demandée
            video_urls = self.extract_all_video_urls(html, self.driver.current_url)
        
        return video_urls
    
    def scrape_remix_chain(self, video_url, max_depth=None, scroll_delay=2):
        """
        Scrape all remixes starting from a single video, following the remix chain.
        This allows scraping unlimited videos by following remix links.
        
        Args:
            video_url (str): Starting video URL (e.g., https://sora.chatgpt.com/video/abc123)
            max_depth (int): Maximum depth to follow (None = unlimited)
            scroll_delay (float): Delay between actions
            
        Returns:
            set: Set of video URLs found in the remix chain
        """
        print("="*60)
        print("🎨 MODE REMIX: Suivi de la chaîne de remixes")
        print("="*60)
        print(f"📍 Vidéo de départ: {video_url}")
        print(f"🔄 Profondeur max: {'Illimitée' if max_depth is None else max_depth}")
        print("="*60)
        print()
        
        # Create the driver if it doesn't exist
        if not self.driver:
            self.create_driver()
        
        all_video_urls = set()
        processed_urls = set()  # To avoid processing same video twice
        queue = [(video_url, 0)]  # (url, depth)
        
        while queue:
            current_url, depth = queue.pop(0)
            
            # Check depth limit
            if max_depth is not None and depth > max_depth:
                print(f"⚠️  Profondeur maximale atteinte ({max_depth})")
                continue
            
            # Skip if already processed
            if current_url in processed_urls:
                continue
            
            processed_urls.add(current_url)
            
            print(f"\n{'  ' * depth}[Profondeur {depth}] 🎬 Analyse: {current_url}")
            
            try:
                # Navigate to the video page
                self.driver.get(current_url)
                time.sleep(scroll_delay + 1)  # Extra time for page load
                
                # Add current video URL
                all_video_urls.add(current_url)
                
                # Wait for page to load completely
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check for login prompts and close them
                try:
                    # Look for and close any modals/overlays
                    close_buttons = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "button[aria-label*='Close'], button[aria-label*='close']"
                    )
                    for btn in close_buttons[:1]:  # Close first modal only
                        try:
                            if btn.is_displayed():
                                btn.click()
                                time.sleep(1)
                                print(f"{'  ' * depth}   ℹ️  Fermé une popup")
                        except:
                            pass
                except:
                    pass
                
                # Wait for dynamic content to load
                time.sleep(3)
                
                # Scroll down to ensure remix section is loaded
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                    time.sleep(1)
                except:
                    pass
                
                # Look for remix links/buttons
                remix_urls = self._find_remix_links(max_load_more_clicks=10)
                
                if remix_urls:
                    print(f"{'  ' * depth}   ✅ Trouvé {len(remix_urls)} remix(s)")
                    
                    # Add remix URLs to queue
                    for remix_url in remix_urls:
                        if remix_url and remix_url not in processed_urls:
                            queue.append((remix_url, depth + 1))
                            all_video_urls.add(remix_url)
                else:
                    print(f"{'  ' * depth}   ℹ️  Aucun remix trouvé (fin de chaîne)")
                
            except Exception as e:
                print(f"{'  ' * depth}   ❌ Erreur: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ Chaîne de remixes terminée!")
        print(f"📊 Total de vidéos trouvées: {len(all_video_urls)}")
        print(f"🔄 Vidéos analysées: {len(processed_urls)}")
        print(f"{'='*60}\n")
        
        return all_video_urls
    
    def _find_remix_links(self, max_load_more_clicks=10):
        """
        Find remix links on a video page by clicking remix thumbnails.
        
        Uses exact CSS selectors from the Sora page structure:
        - Remix container: div.flex.w-full.flex-col.gap-2.pt-2 > div
        - Remix buttons: button.h-8.w-6.shrink-0.overflow-hidden.rounded-md > img
        - Load more button: button.relative.h-[21px].w-4.shrink-0 > div
        
        Args:
            max_load_more_clicks (int): Maximum number of times to click "Load more"
            
        Returns:
            list: List of remix video URLs
        """
        
        remix_urls = []
        seen_urls = set()
        
        print("      🔍 Recherche des remixes dans la section dédiée...")
        
        # Store the original URL BEFORE any operations
        store_url = self.driver.current_url
        print(f"      📍 URL d'origine: {store_url}")
        
        # Scroll down to ensure remix section is visible
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(2)
        except:
            pass
        
        # Track which index we're at (strictly forward navigation)
        current_index = 0
        load_more_clicks = 0
        navigation_error_count = 0
        
        # Main loop: process remixes one by one, strictly forward
        while load_more_clicks <= max_load_more_clicks:
            try:
                # Close any login popups
                try:
                    close_buttons = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "button[aria-label*='Close'], button[aria-label*='close']"
                    )
                    for btn in close_buttons[:1]:
                        try:
                            if btn.is_displayed():
                                btn.click()
                                time.sleep(0.5)
                                print("      ⚠️  Fermé une popup")
                                break
                        except:
                            pass
                except:
                    pass
                
                # Make sure we're on the original page
                current = self.driver.current_url
                
                # Check for unexpected navigation (login, auth, etc.)
                if "login" in current.lower() or "auth" in current.lower() or "signin" in current.lower():
                    print(f"      ⚠️  Navigation vers une page inattendue: {current}")
                    navigation_error_count += 1
                    self.driver.get(store_url)
                    time.sleep(2)
                    if navigation_error_count > 3:
                        print(f"      ❌ Trop d'erreurs de navigation, abandon")
                        break
                    continue
                
                if "/p/" in current and current != store_url:
                    print(f"      🔙 Retour à la page d'origine...")
                    self.driver.get(store_url)
                    time.sleep(2)
                
                # RE-FETCH all buttons (fresh elements, no stale references)
                try:
                    all_small_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    
                    remix_buttons = []
                    load_more_button = None
                    
                    for button in all_small_buttons:
                        try:
                            classes = button.get_attribute("class") or ""
                            aria_label = button.get_attribute("aria-label") or ""
                            
                            # Skip buttons that are clearly not remix buttons
                            skip_keywords = ["close", "login", "sign", "share", "like", "follow", "menu"]
                            if any(kw in aria_label.lower() for kw in skip_keywords):
                                continue
                            if any(kw in classes.lower() for kw in ["modal", "dialog", "nav"]):
                                continue
                            
                            # Check if it's a remix button (h-8 w-6 with image)
                            if "h-8" in classes and "w-6" in classes and "shrink-0" in classes:
                                imgs = button.find_elements(By.TAG_NAME, "img")
                                if imgs and button.is_displayed() and button.is_enabled():
                                    remix_buttons.append(button)
                            
                            # Check if it's the load more button
                            elif "h-[21px]" in classes or ("w-4" in classes and "h-" in classes and len(classes) < 200):
                                divs = button.find_elements(By.TAG_NAME, "div")
                                if divs and not load_more_button and button.is_displayed():
                                    load_more_button = button
                        except:
                            continue
                    
                    total_buttons = len(remix_buttons)
                    
                    # Check if we need to load more
                    if current_index >= total_buttons:
                        if load_more_clicks < max_load_more_clicks:
                            if load_more_button:
                                print(f"      🔄 Index {current_index} >= {total_buttons} boutons, tentative load more ({load_more_clicks + 1}/{max_load_more_clicks})...")
                                
                                # Re-find load more button (avoid stale)
                                time.sleep(1)
                                all_buttons_refresh = self.driver.find_elements(By.TAG_NAME, "button")
                                load_more_refresh = None
                                
                                for btn in all_buttons_refresh:
                                    try:
                                        classes = btn.get_attribute("class") or ""
                                        if "h-[21px]" in classes or ("w-4" in classes and "h-" in classes and len(classes) < 200):
                                            divs = btn.find_elements(By.TAG_NAME, "div")
                                            if divs:
                                                load_more_refresh = btn
                                                break
                                    except:
                                        continue
                                
                                if load_more_refresh:
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'end'});", load_more_refresh)
                                    time.sleep(0.5)
                                    self.driver.execute_script("arguments[0].click();", load_more_refresh)
                                    time.sleep(3)
                                    load_more_clicks += 1
                                    print(f"      ✅ 'Load more' cliqué ({load_more_clicks}/{max_load_more_clicks})")
                                    
                                    # Scroll back to remix section
                                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                                    time.sleep(1)
                                    continue  # Re-fetch buttons
                            else:
                                print(f"      ℹ️  Plus de 'Load more', arrêt")
                                break
                        else:
                            print(f"      ✅ Maximum load more atteint ({max_load_more_clicks})")
                            break
                    
                    # Process button at current_index
                    if current_index < len(remix_buttons):
                        button = remix_buttons[current_index]
                        
                        # Safety check
                        if navigation_error_count > 3:
                            print(f"      ⚠️  Trop d'erreurs de navigation, arrêt")
                            break
                        
                        try:
                            # Safety check: ensure we're still on the correct page
                            if self.driver.current_url != store_url:
                                print(f"         ⚠️  Page changée avant le clic, retour à l'origine")
                                self.driver.get(store_url)
                                time.sleep(2)
                                continue
                            
                            # Scroll button into view
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", button)
                            time.sleep(0.5)
                            
                            # Click with JavaScript
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(2.5)
                            
                            # Get new URL
                            new_url = self.driver.current_url
                            
                            # Validate this is a proper video page
                            is_valid_remix = (
                                new_url != store_url and 
                                "/p/" in new_url and 
                                new_url not in seen_urls and
                                "login" not in new_url.lower() and
                                "auth" not in new_url.lower() and
                                "signin" not in new_url.lower()
                            )
                            
                            if is_valid_remix:
                                seen_urls.add(new_url)
                                remix_urls.append(new_url)
                                print(f"         ✓ Remix {current_index + 1} trouvé: {new_url.split('/')[-1][:30]}... (Total: {len(remix_urls)})")
                                
                                # Go back to original page
                                self.driver.back()
                                time.sleep(2.5)
                                
                                # Re-scroll to remix section
                                try:
                                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                                    time.sleep(0.5)
                                except:
                                    pass
                            else:
                                # Invalid URL, go back if needed
                                if new_url != store_url:
                                    if "login" in new_url.lower() or "auth" in new_url.lower():
                                        print(f"         ⚠️  Navigation inattendue vers: {new_url}")
                                        navigation_error_count += 1
                                    self.driver.back()
                                    time.sleep(1)
                                    
                        except Exception as e:
                            print(f"         ⚠️  Erreur clic remix {current_index + 1}: {str(e)[:50]}")
                            # Try to recover
                            try:
                                if self.driver.current_url != store_url:
                                    self.driver.back()
                                    time.sleep(1)
                            except:
                                try:
                                    self.driver.get(store_url)
                                    time.sleep(2)
                                except:
                                    pass
                        
                        # Move to next index (strictly forward!)
                        current_index += 1
                    else:
                        print(f"      ⚠️  Index {current_index} hors limites ({total_buttons} boutons)")
                        break
                    
                except Exception as e:
                    print(f"      ⚠️  Erreur lors de la recherche: {e}")
                    import traceback
                    traceback.print_exc()
                    break
                    
            except Exception as e:
                print(f"      ⚠️ Erreur lors de la recherche: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # Fallback: Look for any /p/ links in the page
        if not remix_urls:
            print("      🔄 Méthode de fallback: recherche de liens vidéo...")
            try:
                all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
                for link in all_links[:10]:  # Limit to first 10
                    try:
                        href = link.get_attribute("href")
                        if href and href not in seen_urls and href != self.driver.current_url:
                            seen_urls.add(href)
                            remix_urls.append(href)
                    except:
                        pass
            except:
                pass
        
        print(f"      ✅ Total: {len(remix_urls)} remixes trouvés")
        return remix_urls
    
    def extract_video_metadata(self, video_url):
        """
        Extrait les métadonnées complètes d'une vidéo Sora.
        Retourne un dictionnaire structuré pour import dans une app type TikTok.
        
        Args:
            video_url (str): URL de la vidéo
            
        Returns:
            dict: Métadonnées complètes de la vidéo
        """
        metadata = {
            "video_url": video_url,
            "video_id": self._generate_video_id(video_url),
            "scraped_at": datetime.now().isoformat(),
            "creator": {
                "username": None,
                "display_name": None,
                "profile_url": None,
                "avatar_url": None,
                "verified": False
            },
            "content": {
                "description": None,
                "prompt": None,
                "title": None
            },
            "engagement": {
                "likes": 0,
                "comments_count": 0,
                "shares": 0,
                "views": 0,
                "remixes": 0
            },
            "comments": [],
            "media": {
                "thumbnail_url": None,
                "duration": None,
                "resolution": None
            },
            "metadata": {
                "post_url": None,
                "created_at": None,
                "model_version": None
            }
        }
        
        try:
            # Trouver l'élément parent de la vidéo (le post complet)
            video_element = None
            try:
                # Chercher l'élément vidéo avec cette URL
                videos = self.driver.find_elements(By.TAG_NAME, "video")
                for vid in videos:
                    if vid.get_attribute("src") == video_url:
                        video_element = vid
                        break
            except:
                pass
            
            if not video_element:
                print(f"   ⚠️  Impossible de trouver l'élément vidéo pour: {video_url[:50]}...")
                return metadata
            
            # Remonter à l'article/post parent
            try:
                post_container = video_element.find_element(By.XPATH, "./ancestor::article | ./ancestor::div[contains(@class, 'post')] | ./ancestor::a[contains(@href, '/p/')]")
            except:
                # Essayer avec plusieurs ancêtres
                try:
                    post_container = video_element.find_element(By.XPATH, "./../../../..")
                except:
                    post_container = video_element
            
            # 1. EXTRAIRE LE CRÉATEUR
            try:
                # Chercher le username (plusieurs patterns possibles)
                username_selectors = [
                    "a[href*='/profile/']",
                    "a[href*='/user/']",
                    "[data-username]",
                    ".username",
                    ".creator-name"
                ]
                
                for selector in username_selectors:
                    try:
                        creator_link = post_container.find_element(By.CSS_SELECTOR, selector)
                        href = creator_link.get_attribute("href")
                        if href and ("/profile/" in href or "/user/" in href):
                            username = href.split("/")[-1]
                            metadata["creator"]["username"] = username
                            metadata["creator"]["profile_url"] = href
                            metadata["creator"]["display_name"] = creator_link.text.strip() or username
                            break
                    except:
                        continue
                
                # Chercher l'avatar
                try:
                    avatar = post_container.find_element(By.CSS_SELECTOR, "img[alt*='avatar'], img[src*='avatar'], img[class*='avatar']")
                    metadata["creator"]["avatar_url"] = avatar.get_attribute("src")
                except:
                    pass
                
                # Vérifier si vérifié (badge)
                try:
                    verified_badge = post_container.find_element(By.CSS_SELECTOR, "svg[class*='verified'], [data-verified='true'], .verified-badge")
                    metadata["creator"]["verified"] = True
                except:
                    pass
                    
            except Exception as e:
                print(f"   ⚠️  Erreur extraction créateur: {e}")
            
            # 2. EXTRAIRE LA DESCRIPTION / PROMPT
            try:
                description_selectors = [
                    "[data-description]",
                    ".description",
                    ".prompt",
                    ".caption",
                    "p[class*='description']",
                    "div[class*='prompt']"
                ]
                
                for selector in description_selectors:
                    try:
                        desc_elem = post_container.find_element(By.CSS_SELECTOR, selector)
                        desc_text = desc_elem.text.strip()
                        if desc_text:
                            if "prompt" in selector.lower():
                                metadata["content"]["prompt"] = desc_text
                            else:
                                metadata["content"]["description"] = desc_text
                            break
                    except:
                        continue
            except Exception as e:
                print(f"   ⚠️  Erreur extraction description: {e}")
            
            # 3. EXTRAIRE LES ENGAGEMENTS (likes, comments, etc.)
            try:
                # Likes
                like_selectors = [
                    "button[aria-label*='like']",
                    "button[aria-label*='Like']",
                    "[data-likes]",
                    ".like-count",
                    "span[class*='like']"
                ]
                
                for selector in like_selectors:
                    try:
                        like_elem = post_container.find_element(By.CSS_SELECTOR, selector)
                        like_text = like_elem.text.strip()
                        # Extraire le nombre
                        likes = self._parse_count(like_text)
                        if likes > 0:
                            metadata["engagement"]["likes"] = likes
                            break
                    except:
                        continue
                
                # Comments count
                comment_count_selectors = [
                    "button[aria-label*='comment']",
                    "[data-comments]",
                    ".comment-count",
                    "span[class*='comment']"
                ]
                
                for selector in comment_count_selectors:
                    try:
                        comment_elem = post_container.find_element(By.CSS_SELECTOR, selector)
                        comment_text = comment_elem.text.strip()
                        comments = self._parse_count(comment_text)
                        if comments > 0:
                            metadata["engagement"]["comments_count"] = comments
                            break
                    except:
                        continue
                
                # Remixes / Shares
                remix_selectors = [
                    "[data-remixes]",
                    ".remix-count",
                    "button[aria-label*='remix']"
                ]
                
                for selector in remix_selectors:
                    try:
                        remix_elem = post_container.find_element(By.CSS_SELECTOR, selector)
                        remix_text = remix_elem.text.strip()
                        remixes = self._parse_count(remix_text)
                        if remixes > 0:
                            metadata["engagement"]["remixes"] = remixes
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️  Erreur extraction engagements: {e}")
            
            # 4. EXTRAIRE LES COMMENTAIRES
            try:
                comments = []
                comment_selectors = [
                    ".comment",
                    "[data-comment]",
                    "div[class*='comment-item']"
                ]
                
                for selector in comment_selectors:
                    try:
                        comment_elements = post_container.find_elements(By.CSS_SELECTOR, selector)[:10]  # Max 10 commentaires
                        
                        for comment_elem in comment_elements:
                            comment_data = {
                                "author": None,
                                "text": None,
                                "likes": 0,
                                "timestamp": None
                            }
                            
                            try:
                                # Auteur du commentaire
                                author_elem = comment_elem.find_element(By.CSS_SELECTOR, ".comment-author, [class*='author'], a[href*='/profile']")
                                comment_data["author"] = author_elem.text.strip()
                            except:
                                pass
                            
                            try:
                                # Texte du commentaire
                                text_elem = comment_elem.find_element(By.CSS_SELECTOR, ".comment-text, p, span[class*='text']")
                                comment_data["text"] = text_elem.text.strip()
                            except:
                                pass
                            
                            try:
                                # Likes du commentaire
                                like_elem = comment_elem.find_element(By.CSS_SELECTOR, ".comment-likes, [class*='like']")
                                comment_data["likes"] = self._parse_count(like_elem.text)
                            except:
                                pass
                            
                            if comment_data["text"]:
                                comments.append(comment_data)
                        
                        if comments:
                            metadata["comments"] = comments
                            break
                            
                    except:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️  Erreur extraction commentaires: {e}")
            
            # 5. EXTRAIRE POST URL
            try:
                # Chercher le lien du post
                post_link = post_container.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                metadata["metadata"]["post_url"] = post_link.get_attribute("href")
            except:
                pass
            
            # 6. EXTRAIRE THUMBNAIL
            try:
                # Le poster de la vidéo ou une image de prévisualisation
                poster = video_element.get_attribute("poster")
                if poster:
                    metadata["media"]["thumbnail_url"] = poster
            except:
                pass
                
        except Exception as e:
            print(f"   ❌ Erreur extraction métadonnées: {e}")
        
        return metadata
    
    def _generate_video_id(self, video_url):
        """Génère un ID unique pour une vidéo basé sur son URL."""
        return hashlib.md5(video_url.encode()).hexdigest()[:16]
    
    def _parse_count(self, text):
        """Parse un texte avec un nombre (ex: '1.2K', '500', '3M')."""
        if not text:
            return 0
        
        text = text.strip().upper()
        # Enlever les caractères non numériques sauf K, M, B
        import re
        match = re.search(r'([\d.]+)\s*([KMB]?)', text)
        
        if not match:
            return 0
        
        number = float(match.group(1))
        suffix = match.group(2)
        
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        if suffix in multipliers:
            return int(number * multipliers[suffix])
        
        return int(number)
    
    def extract_and_save_metadata(self, video_urls, output_file='metadata.json', per_file=False, output_dir=None):
        """
        Extrait les métadonnées pour toutes les vidéos et les sauvegarde.
        
        Args:
            video_urls (set/list): URLs des vidéos
            output_file (str): Nom du fichier de sortie (si per_file=False)
            per_file (bool): Si True, sauvegarde chaque vidéo dans un fichier séparé
            output_dir (pathlib.Path): Dossier de sortie (pour mode per_file)
            
        Returns:
            list: Liste des métadonnées extraites
        """
        print("="*60)
        print("📋 EXTRACTION DES MÉTADONNÉES")
        print("="*60)
        print(f"🎯 Nombre de vidéos: {len(video_urls)}")
        
        if per_file:
            if not output_dir:
                output_dir = pathlib.Path("metadata")
            output_dir.mkdir(exist_ok=True)
            print(f"💾 Mode: Un fichier JSON par vidéo dans {output_dir.absolute()}")
        else:
            print(f"💾 Mode: Toutes les métadonnées dans {output_file}")
        print()
        
        all_metadata = []
        success_count = 0
        fail_count = 0
        
        for i, video_url in enumerate(video_urls, 1):
            print(f"[{i}/{len(video_urls)}] 🔍 Extraction des métadonnées...")
            print(f"   URL: {video_url[:70]}...")
            
            try:
                metadata = self.extract_video_metadata(video_url)
                
                # Afficher un résumé
                creator = metadata['creator']['username'] or 'Inconnu'
                description = metadata['content']['description'] or 'Aucune description'
                likes = metadata['engagement']['likes']
                comments_count = metadata['engagement']['comments_count']
                num_comments = len(metadata['comments'])
                
                print(f"   ✅ Créateur: {creator}")
                print(f"   ✅ Description: {description[:50]}{'...' if len(description) > 50 else ''}")
                print(f"   ✅ Engagement: {likes} likes, {comments_count} commentaires ({num_comments} extraits)")
                
                all_metadata.append(metadata)
                success_count += 1
                
                # Sauvegarder individuellement si demandé
                if per_file and output_dir:
                    video_id = metadata['video_id']
                    json_filename = f"{video_id}.json"
                    json_path = output_dir / json_filename
                    
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                    print(f"   💾 Sauvegardé: {json_filename}")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                fail_count += 1
                print()
        
        # Sauvegarder toutes les métadonnées dans un seul fichier si mode normal
        if not per_file:
            output_path = pathlib.Path(output_file)
            
            # Structure optimisée pour import dans app TikTok-like
            output_data = {
                "version": "1.0",
                "scraped_at": datetime.now().isoformat(),
                "total_videos": len(all_metadata),
                "source": "Sora (ChatGPT)",
                "videos": all_metadata
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Toutes les métadonnées sauvegardées dans: {output_path.absolute()}")
        
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE L'EXTRACTION")
        print("="*60)
        print(f"✅ Métadonnées extraites avec succès: {success_count}")
        print(f"❌ Échecs: {fail_count}")
        
        if per_file and output_dir:
            print(f"📁 Fichiers JSON sauvegardés dans: {output_dir.absolute()}")
        else:
            print(f"📁 Fichier JSON sauvegardé: {pathlib.Path(output_file).absolute()}")
        
        print("="*60)
        
        return all_metadata
    
    def extract_and_save_metadata_with_download(self, video_page_urls, output_file='metadata.json', per_file=False, output_dir=None, video_dir=None):
        """
        Extrait les métadonnées ET télécharge les vidéos pour toutes les URLs de pages.
        
        Args:
            video_page_urls (set/list): URLs des pages vidéo (ex: /p/s_xxx)
            output_file (str): Nom du fichier de sortie JSON
            per_file (bool): Si True, sauvegarde chaque vidéo dans un fichier séparé
            output_dir (pathlib.Path): Dossier de sortie pour JSONs (si per_file)
            video_dir (pathlib.Path): Dossier de sortie pour les vidéos
            
        Returns:
            list: Liste des métadonnées extraites
        """
        print("="*60)
        print("📋 EXTRACTION DES MÉTADONNÉES + TÉLÉCHARGEMENT")
        print("="*60)
        print(f"🎯 Nombre de vidéos: {len(video_page_urls)}")
        
        if per_file:
            if not output_dir:
                output_dir = pathlib.Path("metadata")
            output_dir.mkdir(exist_ok=True)
            print(f"💾 Mode JSON: Un fichier par vidéo dans {output_dir.absolute()}")
        else:
            print(f"💾 Mode JSON: Toutes les métadonnées dans {output_file}")
        
        if not video_dir:
            video_dir = pathlib.Path("videos")
        video_dir.mkdir(exist_ok=True)
        print(f"🎬 Dossier vidéos: {video_dir.absolute()}")
        print()
        
        all_metadata = []
        success_count = 0
        fail_count = 0
        
        for i, page_url in enumerate(video_page_urls, 1):
            print(f"[{i}/{len(video_page_urls)}] 🎬 Traitement de la vidéo...")
            print(f"   URL de la page: {page_url[:70]}...")
            
            try:
                # Navigate to the video page
                self.driver.get(page_url)
                time.sleep(3)  # Wait for page to load
                
                # Find the actual video element and get its source URL
                video_file_url = None
                try:
                    video_element = self.driver.find_element(By.TAG_NAME, "video")
                    video_file_url = video_element.get_attribute("src")
                    
                    if video_file_url:
                        print(f"   ✅ URL vidéo trouvée: {video_file_url[:60]}...")
                except Exception as e:
                    print(f"   ⚠️  Impossible de trouver l'élément vidéo: {e}")
                
                # Extract metadata from the page
                metadata = {
                    "video_page_url": page_url,
                    "video_file_url": video_file_url,
                    "video_id": self._generate_video_id(page_url),
                    "local_video_file": None,
                    "scraped_at": datetime.now().isoformat(),
                    "creator": {
                        "username": None,
                        "display_name": None,
                        "profile_url": None,
                        "avatar_url": None,
                        "verified": False
                    },
                    "content": {
                        "description": None,
                        "prompt": None,
                        "title": None
                    },
                    "engagement": {
                        "likes": 0,
                        "comments_count": 0,
                        "shares": 0,
                        "views": 0,
                        "remixes": 0
                    },
                    "comments": [],
                    "media": {
                        "thumbnail_url": None,
                        "duration": None,
                        "resolution": None
                    },
                    "metadata": {
                        "post_url": page_url,
                        "created_at": None,
                        "model_version": None
                    }
                }
                
                # Extract creator info, description, etc. from the page
                try:
                    # Look for username/profile links
                    profile_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/profile/'], a[href*='/@']")
                    if profile_links:
                        for link in profile_links[:1]:  # Take first one
                            href = link.get_attribute("href")
                            if href:
                                metadata["creator"]["profile_url"] = href
                                metadata["creator"]["username"] = href.split("/")[-1]
                                metadata["creator"]["display_name"] = link.text.strip() or metadata["creator"]["username"]
                                break
                except:
                    pass
                
                try:
                    # Look for description/prompt text
                    text_elements = self.driver.find_elements(By.CSS_SELECTOR, "p, div[class*='text'], div[class*='description']")
                    for elem in text_elements:
                        text = elem.text.strip()
                        if text and len(text) > 10:  # Meaningful text
                            if not metadata["content"]["description"]:
                                metadata["content"]["description"] = text
                            break
                except:
                    pass
                
                # Download the video file if URL found
                if video_file_url:
                    video_filename = f"video_{i:03d}_{metadata['video_id']}.mp4"
                    video_path = video_dir / video_filename
                    
                    print(f"   📥 Téléchargement de la vidéo...")
                    try:
                        response = requests.get(video_file_url, stream=True, timeout=60)
                        response.raise_for_status()
                        
                        total_size = int(response.headers.get('content-length', 0))
                        
                        with open(video_path, 'wb') as f:
                            if total_size == 0:
                                f.write(response.content)
                            else:
                                with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"      ") as pbar:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                            pbar.update(len(chunk))
                        
                        metadata["local_video_file"] = str(video_path)
                        file_size = video_path.stat().st_size
                        print(f"   ✅ Vidéo téléchargée: {video_filename} ({self._format_size(file_size)})")
                    except Exception as e:
                        print(f"   ❌ Échec du téléchargement: {e}")
                else:
                    print(f"   ⚠️  Aucune URL de fichier vidéo trouvée, téléchargement ignoré")
                
                # Display summary
                creator = metadata['creator']['username'] or 'Inconnu'
                description = metadata['content']['description'] or 'Aucune description'
                
                print(f"   ✅ Créateur: {creator}")
                print(f"   ✅ Description: {description[:50]}{'...' if len(description) > 50 else ''}")
                
                all_metadata.append(metadata)
                success_count += 1
                
                # Save individual JSON if requested
                if per_file and output_dir:
                    video_id = metadata['video_id']
                    json_filename = f"{video_id}.json"
                    json_path = output_dir / json_filename
                    
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                    print(f"   💾 JSON sauvegardé: {json_filename}")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
                print()
        
        # Save all metadata to single file if not per_file mode
        if not per_file:
            output_path = pathlib.Path(output_file)
            
            output_data = {
                "version": "1.0",
                "scraped_at": datetime.now().isoformat(),
                "total_videos": len(all_metadata),
                "source": "Sora (ChatGPT)",
                "videos": all_metadata
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Toutes les métadonnées sauvegardées dans: {output_path.absolute()}")
        
        print("\n" + "="*60)
        print("📊 RÉSUMÉ")
        print("="*60)
        print(f"✅ Vidéos traitées avec succès: {success_count}")
        print(f"❌ Échecs: {fail_count}")
        
        if per_file and output_dir:
            print(f"📁 Fichiers JSON: {output_dir.absolute()}")
        else:
            print(f"📁 Fichier JSON: {pathlib.Path(output_file).absolute()}")
        
        print(f"📁 Fichiers vidéo: {video_dir.absolute()}")
        print("="*60)
        
        return all_metadata
    
    def save_html_backup(self):
        """Sauvegarde le HTML de la page actuelle pour debugging."""
        if not self.driver:
            print("⚠️  Aucun driver actif, impossible de sauvegarder le HTML")
            return
        
        try:
            html = self.driver.page_source
            backup_file = pathlib.Path("page_backup.html")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"💾 HTML sauvegardé: {backup_file.absolute()}")
        except Exception as e:
            print(f"⚠️  Erreur lors de la sauvegarde du HTML: {e}")
    
    def close(self):
        """Ferme le driver proprement."""
        if self.driver:
            try:
                self.driver.quit()
                print("🔒 Navigateur fermé")
            except Exception as e:
                print(f"⚠️  Erreur lors de la fermeture du navigateur: {e}")
    
    def download_file(self, url, dest_dir, index=None):
        """
        Télécharge un fichier vidéo.
        
        Args:
            url (str): URL du fichier à télécharger
            dest_dir (pathlib.Path): Dossier de destination
            index (int): Index du fichier (pour nommage)
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Générer un nom de fichier
            if index:
                # Utiliser l'index pour nommer
                extension = self._get_extension_from_url(url)
                filename = f"video_{index:03d}{extension}"
            else:
                # Utiliser le nom depuis l'URL
                filename = url.split('/')[-1].split('?')[0]
                if not any(filename.endswith(ext) for ext in VIDEO_EXTENSIONS):
                    filename += '.mp4'
            
            filepath = dest_dir / filename
            
            # Vérifier si le fichier existe déjà
            if filepath.exists():
                print(f"⏭️  Fichier existe déjà: {filename}")
                return True
            
            # Télécharger
            print(f"📥 Téléchargement: {filename}")
            print(f"   URL: {url[:70]}...")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Obtenir la taille du fichier
            total_size = int(response.headers.get('content-length', 0))
            
            # Télécharger avec barre de progression
            with open(filepath, 'wb') as f:
                if total_size == 0:
                    # Pas de taille connue
                    f.write(response.content)
                else:
                    # Avec barre de progression
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"   ") as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            
            print(f"✅ Téléchargé: {filename} ({self._format_size(filepath.stat().st_size)})")
            return True
            
        except Exception as e:
            print(f"❌ Échec du téléchargement: {e}")
            # Supprimer le fichier partiel
            try:
                if filepath.exists():
                    filepath.unlink()
            except:
                pass
            return False
    
    def _get_extension_from_url(self, url):
        """Extrait l'extension depuis une URL."""
        for ext in VIDEO_EXTENSIONS:
            if ext in url.lower():
                return ext
        return '.mp4'  # Par défaut
    
    def _format_size(self, size):
        """Formate une taille en bytes en format lisible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

def main():
    """Fonction principale avec CLI."""
    parser = argparse.ArgumentParser(
        description='🎬 Scraper de vidéos Sora - Téléchargez vos vidéos depuis Sora',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Mode 1: Scraper 20 vidéos de la page d'accueil avec 3s de délai
  python scraper_sora_advanced.py --mode home --num-videos 20 --delay 3

  # Mode 2: Scraper 15 vidéos d'un profil utilisateur
  python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/johndoe" --num-videos 15

  # Mode 3: Scraper TOUTES les vidéos d'un profil en mode SLOW (recommandé)
  python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/johndoe" --all --slow

  # Mode 4: Scraper un profil en mode lent sans tout prendre
  python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/johndoe" --num-videos 50 --slow

  # Mode headless (sans interface graphique)
  python scraper_sora_advanced.py --mode home --num-videos 10 --headless
  
  # MODE MÉTADONNÉES: Extraire les infos détaillées (créateur, commentaires, etc.)
  # Pour import dans une app TikTok-like
  
  # Extraire métadonnées de 20 vidéos d'un profil (toutes dans un seul JSON)
  python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/johndoe" --num-videos 20 --metadata-mode
  
  # Extraire métadonnées avec un JSON par vidéo
  python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/johndoe" --num-videos 20 --metadata-mode --metadata-per-file
  
  # Extraire TOUTES les métadonnées d'un profil avec session Chrome existante
  python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/johndoe" --all --metadata-mode --use-existing-chrome --slow
  
  # MODE REMIX: Suivre la chaîne de remixes d'une vidéo (scraper des vidéos illimitées!)
  
  # Suivre tous les remixes d'une vidéo (profondeur illimitée)
  python scraper_sora_advanced.py --mode remix --video-url "https://sora.chatgpt.com/video/abc123"
  
  # Suivre les remixes avec profondeur limitée (max 5 niveaux)
  python scraper_sora_advanced.py --mode remix --video-url "https://sora.chatgpt.com/video/abc123" --max-depth 5
  
  # Suivre les remixes et extraire les métadonnées (sans télécharger)
  python scraper_sora_advanced.py --mode remix --video-url "https://sora.chatgpt.com/video/abc123" --metadata-mode
  
  # Suivre les remixes, télécharger toutes les vidéos en mode slow
  python scraper_sora_advanced.py --mode remix --video-url "https://sora.chatgpt.com/video/abc123" --slow
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['home', 'profile', 'remix'],
        help='Mode de scraping: "home" pour la page d\'accueil, "profile" pour un profil utilisateur, "remix" pour suivre la chaîne de remixes'
    )
    
    parser.add_argument(
        '--num-videos',
        type=int,
        default=10,
        help='Nombre de vidéos à télécharger (défaut: 10, utilisez "all" pour tout scraper)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Scraper TOUTES les vidéos disponibles (peut prendre beaucoup de temps)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Délai entre chaque scroll en secondes (défaut: 2.0)'
    )
    
    parser.add_argument(
        '--slow',
        action='store_true',
        help='Mode lent pour éviter les bans (delay 5s, scrolls limités, pauses aléatoires)'
    )
    
    parser.add_argument(
        '--profile-url',
        type=str,
        help='URL du profil utilisateur (requis pour mode "profile")'
    )
    
    parser.add_argument(
        '--video-url',
        type=str,
        help='URL de la vidéo de départ (requis pour mode "remix")'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        help='Profondeur maximale de la chaîne de remixes (défaut: illimité)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='videos',
        help='Dossier de destination des vidéos (défaut: videos)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Mode sans interface graphique'
    )
    
    parser.add_argument(
        '--use-existing-chrome',
        action='store_true',
        help='Se connecter à une session Chrome existante (reste connecté entre les exécutions)'
    )
    
    parser.add_argument(
        '--debug-port',
        type=int,
        default=9222,
        help='Port de débogage Chrome (défaut: 9222)'
    )
    
    parser.add_argument(
        '--metadata-mode',
        action='store_true',
        help='Mode extraction de métadonnées: collecte infos détaillées (créateur, description, commentaires) au lieu de télécharger'
    )
    
    parser.add_argument(
        '--metadata-output',
        type=str,
        default='metadata.json',
        help='Fichier de sortie pour les métadonnées (défaut: metadata.json)'
    )
    
    parser.add_argument(
        '--metadata-per-file',
        action='store_true',
        help='Sauvegarder chaque vidéo dans un JSON séparé au lieu d\'un seul fichier'
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.mode == 'profile' and not args.profile_url:
        parser.error("--profile-url est requis pour le mode 'profile'")
    
    if args.mode == 'remix' and not args.video_url:
        parser.error("--video-url est requis pour le mode 'remix'")
    
    if args.all and args.num_videos != 10:
        parser.error("Ne spécifiez pas --num-videos avec --all")
    
    # Appliquer le mode slow
    if args.slow:
        original_delay = args.delay
        args.delay = max(5.0, args.delay)  # Minimum 5s en mode slow
        print("🐌 MODE SLOW activé:")
        print(f"   - Délai entre scrolls: {args.delay}s (au lieu de {original_delay}s)")
        print(f"   - Pauses aléatoires: activées")
        print(f"   - Scrolling plus prudent")
        print(f"   - Recommandé pour éviter les détections/bans\n")
    
    # Gérer le mode --all
    if args.all:
        args.num_videos = 999999  # Très grand nombre pour scraper tout
        print("♾️  MODE ALL activé: scraping de TOUTES les vidéos disponibles")
        print("   ⚠️  Cela peut prendre BEAUCOUP de temps\n")
    
    # Configuration
    dest_dir = pathlib.Path(args.output_dir)
    dest_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("🎬 SCRAPER SORA - VERSION AVANCÉE")
    print("="*60)
    print(f"📁 Dossier de destination: {dest_dir.absolute()}\n")
    
    scraper = None
    
    try:
        # Créer le scraper
        scraper = SoraScraper(
            headless=args.headless,
            use_existing_chrome=args.use_existing_chrome,
            debug_port=args.debug_port
        )
        
        # Exécuter le mode approprié avec paramètres
        if args.mode == 'home':
            video_urls = scraper.scrape_homepage(
                num_videos=args.num_videos,
                scroll_delay=args.delay,
                all_mode=args.all
            )
        elif args.mode == 'profile':
            video_urls = scraper.scrape_user_profile(
                profile_url=args.profile_url,
                num_videos=args.num_videos,
                scroll_delay=args.delay,
                all_mode=args.all
            )
        else:  # mode == 'remix'
            if not args.video_url:
                print("❌ Erreur: --video-url requis pour le mode remix")
                print("\nExemple:")
                print('  python scraper_sora_advanced.py --mode remix --video-url "https://sora.chatgpt.com/video/abc123"')
                return
            
            video_urls = scraper.scrape_remix_chain(
                video_url=args.video_url,
                max_depth=args.max_depth,
                scroll_delay=args.delay
            )
        
        # Sauvegarder le HTML
        scraper.save_html_backup()
        
        # Afficher les résultats
        if not video_urls:
            print("\n⚠️  Aucune vidéo trouvée.")
            print("\n💡 CONSEILS:")
            print("   - Vérifiez 'page_backup.html' pour voir le contenu récupéré")
            print("   - Sora peut charger les vidéos différemment (API, blob://)")
            print("   - Essayez d'augmenter le délai (--delay)")
            print("   - Augmentez le nombre de scrolls en demandant plus de vidéos")
            return
        
        # Afficher les vidéos trouvées
        print(f"\n✨ {len(video_urls)} vidéo(s) trouvée(s):")
        print("-"*60)
        for i, url in enumerate(video_urls, 1):
            print(f"{i}. {url}")
        print("-"*60 + "\n")
        
        # MODE MÉTADONNÉES: Extraire les métadonnées ET télécharger les vidéos
        if args.metadata_mode:
            print("📋 MODE MÉTADONNÉES ACTIVÉ")
            print("   Extraction des informations détaillées + téléchargement des vidéos...")
            print("   (créateur, description, commentaires, engagement, fichier vidéo, etc.)\n")
            
            # Extraire et sauvegarder les métadonnées (avec téléchargement)
            metadata_output_dir = dest_dir if args.metadata_per_file else None
            scraper.extract_and_save_metadata_with_download(
                video_urls,
                output_file=args.metadata_output,
                per_file=args.metadata_per_file,
                output_dir=metadata_output_dir,
                video_dir=dest_dir
            )
            
            # Fermer le navigateur
            scraper.close()
            scraper = None
            
            print("\n✅ Extraction des métadonnées et téléchargement terminés!")
            print("\n💡 FORMAT DE SORTIE:")
            print("   Les données sont structurées pour un import facile dans une app TikTok-like")
            print("   Chaque vidéo contient:")
            print("   - Informations créateur (username, avatar, profil)")
            print("   - Description et prompt")
            print("   - Statistiques d'engagement (likes, commentaires, partages)")
            print("   - Liste des commentaires extraits")
            print("   - URLs de la vidéo et thumbnail")
            print("   - Fichier vidéo téléchargé localement")
            print("   - Métadonnées supplémentaires")
            
            return
        
        # MODE TÉLÉCHARGEMENT: Télécharger les vidéos
        # Fermer le navigateur avant de télécharger
        scraper.close()
        scraper = None
        
        # Télécharger les vidéos
        print("🚀 Début des téléchargements...\n")
        success_count = 0
        fail_count = 0
        
        # Créer un scraper temporaire pour les téléchargements
        temp_scraper = SoraScraper()
        
        for i, url in enumerate(video_urls, 1):
            print(f"[{i}/{len(video_urls)}]")
            
            # Télécharger
            if temp_scraper.download_file(url, dest_dir, index=i):
                success_count += 1
            else:
                fail_count += 1
            
            # Mode slow : pause aléatoire entre téléchargements
            if args.slow and i < len(video_urls):
                import random
                pause = random.uniform(3, 7)  # Entre 3 et 7 secondes
                print(f"🐌 Pause de {pause:.1f}s pour éviter la détection...")
                time.sleep(pause)
        
        # Résumé final
        print("="*60)
        print("📊 RÉSUMÉ")
        print("="*60)
        print(f"✅ Téléchargements réussis: {success_count}")
        print(f"❌ Téléchargements échoués: {fail_count}")
        print(f"📁 Fichiers sauvegardés dans: {dest_dir.absolute()}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur (Ctrl+C)")
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
