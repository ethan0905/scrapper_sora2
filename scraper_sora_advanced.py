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
    
    def _is_similar_url(self, url1, url2):
        """
        Vérifie si deux URLs sont similaires (ignore les paramètres de requête).
        
        Args:
            url1 (str): Première URL
            url2 (str): Deuxième URL
            
        Returns:
            bool: True si les URLs sont similaires
        """
        from urllib.parse import urlparse
        
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # Comparer le domaine et le chemin (ignorer les query params)
        return (parsed1.netloc == parsed2.netloc and 
                parsed1.path.rstrip('/') == parsed2.path.rstrip('/'))
    
    def _detect_page_type(self):
        """
        Détecte le type de page actuelle (homepage, profil, etc.).
        
        Returns:
            str: Type de page détecté
        """
        current_url = self.driver.current_url.lower()
        
        if "/user/" in current_url or "/profile/" in current_url or "/@" in current_url:
            return "profile"
        elif "/explore" in current_url or "/feed" in current_url:
            return "homepage"
        else:
            return "unknown"
    
    def download_file(self, url, dest_dir, index=None):
        """
        Télécharge un fichier vidéo avec barre de progression.
        
        Args:
            url (str): L'URL du fichier à télécharger
            dest_dir (pathlib.Path): Le dossier de destination
            index (int): Index de la vidéo (pour nommage)
            
        Returns:
            bool: True si le téléchargement a réussi, False sinon
        """
        try:
            # Extraire le nom du fichier depuis l'URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Si pas de nom de fichier, utiliser un nom par défaut
            if not filename or '.' not in filename:
                ext = '.mp4'
                for video_ext in VIDEO_EXTENSIONS:
                    if video_ext in url.lower():
                        ext = video_ext
                        break
                
                if index is not None:
                    filename = f"video_{index:03d}{ext}"
                else:
                    filename = f"video_{hash(url) % 100000}{ext}"
            
            dest_path = dest_dir / filename
            
            # Vérifier si le fichier existe déjà
            if dest_path.exists():
                print(f"⏭️  Fichier déjà existant: {filename}")
                return True
            
            # Faire la requête avec streaming
            print(f"📥 Téléchargement: {filename}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://sora.chatgpt.com/'
            }
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Obtenir la taille totale
            total_size = int(response.headers.get('content-length', 0))
            
            # Télécharger avec barre de progression
            with open(dest_path, 'wb') as file:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                                pbar.update(len(chunk))
                else:
                    # Pas de taille connue, télécharger sans barre
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
            
            print(f"✅ Téléchargé: {filename}\n")
            return True
            
        except requests.RequestException as e:
            print(f"❌ Erreur lors du téléchargement de {url}: {e}\n")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue pour {url}: {e}\n")
            return False
    
    def save_html_backup(self, filename="page_backup.html"):
        """Sauvegarde le HTML pour inspection manuelle."""
        if self.driver:
            html = self.driver.page_source
            backup_path = pathlib.Path(filename)
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"💾 HTML sauvegardé: {backup_path.absolute()}")
    
    def close(self):
        """Ferme le driver Selenium."""
        if self.driver:
            print("\n🔒 Fermeture du navigateur...")
            try:
                self.driver.quit()
            except:
                pass
    
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
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['home', 'profile'],
        help='Mode de scraping: "home" pour la page d\'accueil, "profile" pour un profil utilisateur'
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
        else:  # mode == 'profile'
            video_urls = scraper.scrape_user_profile(
                profile_url=args.profile_url,
                num_videos=args.num_videos,
                scroll_delay=args.delay,
                all_mode=args.all
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
        
        # MODE MÉTADONNÉES: Extraire les métadonnées au lieu de télécharger
        if args.metadata_mode:
            print("📋 MODE MÉTADONNÉES ACTIVÉ")
            print("   Extraction des informations détaillées pour chaque vidéo...")
            print("   (créateur, description, commentaires, engagement, etc.)\n")
            
            # Extraire et sauvegarder les métadonnées
            metadata_output_dir = dest_dir if args.metadata_per_file else None
            scraper.extract_and_save_metadata(
                video_urls,
                output_file=args.metadata_output,
                per_file=args.metadata_per_file,
                output_dir=metadata_output_dir
            )
            
            # Fermer le navigateur
            scraper.close()
            scraper = None
            
            print("\n✅ Extraction des métadonnées terminée!")
            print("\n💡 FORMAT DE SORTIE:")
            print("   Les données sont structurées pour un import facile dans une app TikTok-like")
            print("   Chaque vidéo contient:")
            print("   - Informations créateur (username, avatar, profil)")
            print("   - Description et prompt")
            print("   - Statistiques d'engagement (likes, commentaires, partages)")
            print("   - Liste des commentaires extraits")
            print("   - URLs de la vidéo et thumbnail")
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
