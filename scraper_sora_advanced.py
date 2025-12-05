import os
import time
import pathlib
import argparse
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
    
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        
    def create_driver(self):
        """
        Crée un driver Selenium configuré pour Chrome.
        
        Returns:
            webdriver.Chrome: Le driver Selenium
        """
        print("🚀 Initialisation du navigateur Chrome...")
        
        chrome_options = Options()
        
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
        if "login" in self.driver.current_url.lower() or "auth" in self.driver.current_url.lower():
            print("\n" + "="*60)
            print("🔐 CONNEXION REQUISE")
            print("="*60)
            print("Le site nécessite une authentification.")
            print("\n👉 Veuillez vous connecter manuellement dans le navigateur.")
            print("👉 Appuyez sur ENTRÉE une fois connecté et que la page est chargée...")
            input()
            print("\n✅ Reprise du scraping...\n")
    
    def scroll_and_load(self, num_scrolls=5, delay=2):
        """
        Fait défiler la page pour charger les vidéos lazy-loaded.
        
        Args:
            num_scrolls (int): Nombre de scrolls à effectuer
            delay (float): Délai entre chaque scroll en secondes
        """
        print(f"📜 Scrolling de la page ({num_scrolls} fois, délai: {delay}s)...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(num_scrolls):
            # Scroller jusqu'en bas
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)
            
            # Vérifier si la hauteur a changé (nouveau contenu chargé)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print(f"   ⚠️ Plus de contenu à charger après {i+1} scrolls")
                break
            
            last_height = new_height
            print(f"   Scroll {i+1}/{num_scrolls} effectué")
        
        print("✅ Scrolling terminé\n")
    
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
    
    def scrape_homepage(self, num_videos=10, scroll_delay=2):
        """
        Mode 1: Scrape la page d'accueil de Sora.
        
        Args:
            num_videos (int): Nombre de vidéos à scraper
            scroll_delay (float): Délai entre chaque scroll
            
        Returns:
            set: Ensemble d'URLs de vidéos
        """
        url = "https://sora.chatgpt.com/explore?feed=top"
        
        print("="*60)
        print("🏠 MODE 1: SCRAPING DE LA PAGE D'ACCUEIL")
        print("="*60)
        print(f"📍 URL: {url}")
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
        num_scrolls = max(5, (num_videos // 3) + 2)
        
        # Scroller pour charger les vidéos
        self.scroll_and_load(num_scrolls=num_scrolls, delay=scroll_delay)
        
        # Extraire les éléments vidéo
        elements = self.extract_video_elements(max_videos=num_videos)
        
        # Extraire les URLs
        video_urls = self.extract_video_urls_from_elements(elements)
        
        # Backup: parser le HTML
        if not video_urls:
            print("⚠️ Aucune URL trouvée avec Selenium, tentative avec BeautifulSoup...")
            html = self.driver.page_source
            video_urls = self.extract_all_video_urls(html, url)
        
        return video_urls
    
    def scrape_user_profile(self, profile_url, num_videos=10, scroll_delay=2):
        """
        Mode 2: Scrape le profil d'un utilisateur spécifique.
        
        Args:
            profile_url (str): URL du profil utilisateur
            num_videos (int): Nombre de vidéos à scraper
            scroll_delay (float): Délai entre chaque scroll
            
        Returns:
            set: Ensemble d'URLs de vidéos
        """
        print("="*60)
        print("👤 MODE 2: SCRAPING D'UN PROFIL UTILISATEUR")
        print("="*60)
        print(f"📍 URL: {profile_url}")
        print(f"🎯 Nombre de vidéos: {num_videos}")
        print(f"⏱️  Délai entre scrolls: {scroll_delay}s\n")
        
        # Créer le driver si nécessaire
        if not self.driver:
            self.create_driver()
        
        # Charger la page
        print(f"🌐 Chargement du profil...")
        self.driver.get(profile_url)
        time.sleep(5)  # Attente initiale
        
        # Vérifier si connexion nécessaire
        self.wait_for_login()
        
        # Calculer le nombre de scrolls
        num_scrolls = max(5, (num_videos // 3) + 2)
        
        # Scroller pour charger les vidéos
        self.scroll_and_load(num_scrolls=num_scrolls, delay=scroll_delay)
        
        # Extraire les éléments vidéo
        elements = self.extract_video_elements(max_videos=num_videos)
        
        # Extraire les URLs
        video_urls = self.extract_video_urls_from_elements(elements)
        
        # Backup: parser le HTML
        if not video_urls:
            print("⚠️ Aucune URL trouvée avec Selenium, tentative avec BeautifulSoup...")
            html = self.driver.page_source
            video_urls = self.extract_all_video_urls(html, profile_url)
        
        return video_urls
    
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

  # Mode headless (sans interface graphique)
  python scraper_sora_advanced.py --mode home --num-videos 10 --headless
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
        help='Nombre de vidéos à télécharger (défaut: 10)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Délai entre chaque scroll en secondes (défaut: 2.0)'
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
    
    args = parser.parse_args()
    
    # Validation
    if args.mode == 'profile' and not args.profile_url:
        parser.error("--profile-url est requis pour le mode 'profile'")
    
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
        scraper = SoraScraper(headless=args.headless)
        
        # Exécuter le mode approprié
        if args.mode == 'home':
            video_urls = scraper.scrape_homepage(
                num_videos=args.num_videos,
                scroll_delay=args.delay
            )
        else:  # mode == 'profile'
            video_urls = scraper.scrape_user_profile(
                profile_url=args.profile_url,
                num_videos=args.num_videos,
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
        
        # Fermer le navigateur avant de télécharger
        scraper.close()
        scraper = None
        
        # Télécharger les vidéos
        print("🚀 Début des téléchargements...\n")
        success_count = 0
        fail_count = 0
        
        for i, url in enumerate(video_urls, 1):
            print(f"[{i}/{len(video_urls)}]")
            if scraper.download_file(url, dest_dir, index=i) if scraper else SoraScraper().download_file(url, dest_dir, index=i):
                success_count += 1
            else:
                fail_count += 1
        
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
