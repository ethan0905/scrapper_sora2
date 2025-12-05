import os
import time
import pathlib
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

# Configuration
BASE_URL = "https://sora.chatgpt.com/explore?feed=top"
DEST_DIR = pathlib.Path("videos")
DEST_DIR.mkdir(exist_ok=True)

# Extensions vidéo supportées
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.mkv', '.avi', '.flv')

# Configuration Selenium
HEADLESS = False  # False = voir le navigateur, True = mode invisible
WAIT_TIME = 10  # Temps d'attente pour le chargement de la page (secondes)
SCROLL_PAUSE = 2  # Temps entre chaque scroll


def create_driver():
    """
    Crée un driver Selenium configuré pour Chrome.
    
    Returns:
        webdriver.Chrome: Le driver Selenium
    """
    print("🚀 Initialisation du navigateur Chrome...")
    
    chrome_options = Options()
    
    if HEADLESS:
        chrome_options.add_argument("--headless")
    
    # Options pour éviter la détection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # User agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Créer le service et le driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Masquer l'automatisation
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("✅ Navigateur prêt\n")
    return driver


def scroll_page(driver, scrolls=5):
    """
    Fait défiler la page pour charger les vidéos lazy-loaded.
    
    Args:
        driver: Le driver Selenium
        scrolls (int): Nombre de scrolls à effectuer
    """
    print(f"📜 Scrolling de la page ({scrolls} fois)...")
    
    for i in range(scrolls):
        # Scroller jusqu'en bas
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        print(f"   Scroll {i+1}/{scrolls} effectué")
    
    print("✅ Scrolling terminé\n")


def get_html_with_selenium(url):
    """
    Récupère le HTML d'une page avec Selenium (gère le JavaScript).
    
    Args:
        url (str): L'URL à charger
        
    Returns:
        tuple: (html, driver) - Le HTML et le driver (pour fermer plus tard)
    """
    driver = None
    try:
        driver = create_driver()
        
        print(f"🌐 Chargement de la page: {url}")
        driver.get(url)
        
        # Attendre que la page charge
        print(f"⏳ Attente du chargement ({WAIT_TIME}s)...")
        time.sleep(WAIT_TIME)
        
        # Vérifier si on est sur une page de connexion
        if "login" in driver.current_url.lower() or "auth" in driver.current_url.lower():
            print("\n" + "="*60)
            print("🔐 CONNEXION REQUISE")
            print("="*60)
            print("Le site nécessite une authentification.")
            print("Le navigateur va rester ouvert.")
            print("\n👉 Veuillez vous connecter manuellement dans le navigateur.")
            print("👉 Appuyez sur ENTRÉE une fois connecté et que la page est chargée...")
            input()
            print("\n✅ Reprise du scraping...\n")
        
        # Scroller pour charger les vidéos lazy-loaded
        scroll_page(driver)
        
        # Récupérer le HTML
        html = driver.page_source
        print("✅ HTML récupéré avec succès\n")
        
        return html, driver
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement avec Selenium: {e}")
        if driver:
            driver.quit()
        raise


def extract_video_urls(html, base_url):
    """
    Extrait toutes les URLs de vidéos depuis le HTML.
    
    Args:
        html (str): Le contenu HTML
        base_url (str): L'URL de base pour construire les URLs absolues
        
    Returns:
        set: Un ensemble d'URLs de vidéos (dédupliquées)
    """
    soup = BeautifulSoup(html, 'html.parser')
    video_urls = set()
    
    print("🔍 Recherche de vidéos dans le HTML...")
    
    # 1. Chercher les balises <video> avec attribut src
    video_tags = soup.find_all('video', src=True)
    print(f"   Trouvé {len(video_tags)} balises <video> avec src")
    for video_tag in video_tags:
        url = urljoin(base_url, video_tag['src'])
        video_urls.add(url)
    
    # 2. Chercher les balises <source> dans les <video>
    source_tags = soup.find_all('source', src=True)
    print(f"   Trouvé {len(source_tags)} balises <source>")
    for source_tag in source_tags:
        url = urljoin(base_url, source_tag['src'])
        video_urls.add(url)
    
    # 3. Chercher les liens <a> pointant vers des fichiers vidéo
    links = soup.find_all('a', href=True)
    video_links = [link for link in links if any(link['href'].lower().endswith(ext) for ext in VIDEO_EXTENSIONS)]
    print(f"   Trouvé {len(video_links)} liens vers des fichiers vidéo")
    for link in video_links:
        url = urljoin(base_url, link['href'])
        video_urls.add(url)
    
    # 4. Chercher dans les attributs data-* et autres
    all_tags = soup.find_all(True)
    for tag in all_tags:
        for attr, value in tag.attrs.items():
            if isinstance(value, str) and any(ext in value.lower() for ext in VIDEO_EXTENSIONS):
                url = urljoin(base_url, value)
                if url.startswith('http'):
                    video_urls.add(url)
    
    print(f"✅ Extraction terminée\n")
    return video_urls


def download_file(url, dest_dir):
    """
    Télécharge un fichier vidéo avec barre de progression.
    
    Args:
        url (str): L'URL du fichier à télécharger
        dest_dir (pathlib.Path): Le dossier de destination
        
    Returns:
        bool: True si le téléchargement a réussi, False sinon
    """
    try:
        # Extraire le nom du fichier depuis l'URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # Si pas de nom de fichier, utiliser un nom par défaut
        if not filename or '.' not in filename:
            filename = f"video_{hash(url) % 100000}.mp4"
        
        dest_path = dest_dir / filename
        
        # Vérifier si le fichier existe déjà
        if dest_path.exists():
            print(f"⏭️  Fichier déjà existant: {filename}")
            return True
        
        # Faire la requête avec streaming
        print(f"📥 Téléchargement: {filename}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Obtenir la taille totale
        total_size = int(response.headers.get('content-length', 0))
        
        # Télécharger avec barre de progression
        with open(dest_path, 'wb') as file:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        pbar.update(len(chunk))
        
        print(f"✅ Téléchargé: {filename}\n")
        return True
        
    except requests.RequestException as e:
        print(f"❌ Erreur lors du téléchargement de {url}: {e}\n")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue pour {url}: {e}\n")
        return False


def save_html_backup(html, filename="page_backup.html"):
    """
    Sauvegarde le HTML pour inspection manuelle.
    
    Args:
        html (str): Le contenu HTML
        filename (str): Le nom du fichier de sauvegarde
    """
    backup_path = pathlib.Path(filename)
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"💾 HTML sauvegardé dans: {backup_path.absolute()}")


def main():
    """
    Fonction principale qui orchestre le scraping et le téléchargement.
    """
    print("="*60)
    print("🎬 SCRAPER DE VIDÉOS SORA - VERSION SELENIUM")
    print("="*60)
    print(f"📍 URL cible: {BASE_URL}")
    print(f"📁 Dossier de destination: {DEST_DIR.absolute()}\n")
    
    driver = None
    
    try:
        # 1. Récupérer le HTML avec Selenium
        html, driver = get_html_with_selenium(BASE_URL)
        
        # Sauvegarder le HTML pour debugging
        save_html_backup(html)
        
        # 2. Extraire les URLs de vidéos
        video_urls = extract_video_urls(html, BASE_URL)
        
        # Fermer le navigateur maintenant qu'on a le HTML
        if driver:
            print("🔒 Fermeture du navigateur...\n")
            driver.quit()
            driver = None
        
        if not video_urls:
            print("⚠️  Aucune vidéo trouvée sur cette page.")
            print("\n💡 CONSEILS:")
            print("   - Vérifiez le fichier 'page_backup.html' pour voir le HTML récupéré")
            print("   - Sora charge peut-être les vidéos différemment")
            print("   - Les vidéos sont peut-être dans un blob:// ou via API")
            return
        
        # 3. Afficher les vidéos trouvées
        print(f"\n✨ {len(video_urls)} vidéo(s) trouvée(s):")
        print("-"*60)
        for i, url in enumerate(video_urls, 1):
            print(f"{i}. {url}")
        print("-"*60 + "\n")
        
        # 4. Télécharger chaque vidéo
        print("🚀 Début des téléchargements...\n")
        success_count = 0
        fail_count = 0
        
        for url in video_urls:
            if download_file(url, DEST_DIR):
                success_count += 1
            else:
                fail_count += 1
        
        # 5. Résumé final
        print("="*60)
        print("📊 RÉSUMÉ")
        print("="*60)
        print(f"✅ Téléchargements réussis: {success_count}")
        print(f"❌ Téléchargements échoués: {fail_count}")
        print(f"📁 Fichiers sauvegardés dans: {DEST_DIR.absolute()}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur (Ctrl+C)")
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # S'assurer que le driver est fermé
        if driver:
            print("\n🔒 Fermeture du navigateur...")
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    main()
