import os
import pathlib
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Configuration
BASE_URL = "https://sora.chatgpt.com/explore?feed=top"  # ✏️ Modifiez cette URL avec votre page web
DEST_DIR = pathlib.Path("videos")
DEST_DIR.mkdir(exist_ok=True)

# Extensions vidéo supportées
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.mkv', '.avi', '.flv')

# Headers pour simuler un navigateur réel
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# 🔑 AUTHENTIFICATION (optionnel)
# Si le site nécessite une authentification, ajoutez votre token ici
# Vous pouvez le récupérer depuis les cookies de votre navigateur
AUTH_TOKEN = None  # Exemple: "votre_token_ici"
COOKIES = {}  # Exemple: {"session": "votre_session_id"}


def get_html(url):
    """
    Récupère le contenu HTML d'une page web.
    
    Args:
        url (str): L'URL de la page à récupérer
        
    Returns:
        str: Le contenu HTML de la page
        
    Raises:
        requests.RequestException: Si la requête échoue
    """
    try:
        print(f"🌐 Chargement de la page: {url}")
        
        # Créer une session pour gérer les cookies
        session = requests.Session()
        
        # Ajouter les headers
        headers = HEADERS.copy()
        
        # Ajouter le token d'authentification si fourni
        if AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
        
        # Faire la requête avec headers et cookies
        response = session.get(url, headers=headers, cookies=COOKIES, timeout=30)
        
        # Afficher le code de statut pour debugging
        print(f"📊 Code de statut: {response.status_code}")
        
        response.raise_for_status()
        print("✅ Page chargée avec succès\n")
        return response.text
        
    except requests.RequestException as e:
        print(f"❌ Erreur lors du chargement de la page: {e}")
        print("\n💡 CONSEIL:")
        print("   - Le site bloque probablement les requêtes automatiques")
        print("   - Sora nécessite une authentification ChatGPT")
        print("   - Options alternatives:")
        print("     1. Récupérez vos cookies depuis le navigateur")
        print("     2. Utilisez Selenium/Playwright pour automatiser un vrai navigateur")
        print("     3. Téléchargez le HTML manuellement et pointez vers un fichier local")
        raise


def extract_video_urls(html, base_url):
    """
    Extrait toutes les URLs de vidéos depuis le HTML.
    
    Cherche:
    - <video src="...">
    - <video><source src="..."></video>
    - <a href="..."> pointant vers .mp4, .mov, .webm, .mkv, etc.
    
    Args:
        html (str): Le contenu HTML
        base_url (str): L'URL de base pour construire les URLs absolues
        
    Returns:
        set: Un ensemble d'URLs de vidéos (dédupliquées)
    """
    soup = BeautifulSoup(html, 'html.parser')
    video_urls = set()
    
    # 1. Chercher les balises <video> avec attribut src
    for video_tag in soup.find_all('video', src=True):
        url = urljoin(base_url, video_tag['src'])
        video_urls.add(url)
    
    # 2. Chercher les balises <source> dans les <video>
    for source_tag in soup.find_all('source', src=True):
        url = urljoin(base_url, source_tag['src'])
        video_urls.add(url)
    
    # 3. Chercher les liens <a> pointant vers des fichiers vidéo
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(href.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            url = urljoin(base_url, href)
            video_urls.add(url)
    
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
        
        # Faire la requête avec streaming et headers
        print(f"📥 Téléchargement: {filename}")
        headers = HEADERS.copy()
        if AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
        response = requests.get(url, stream=True, headers=headers, cookies=COOKIES, timeout=30)
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


def main():
    """
    Fonction principale qui orchestre le scraping et le téléchargement.
    """
    print("="*60)
    print("🎬 SCRAPER DE VIDÉOS - DÉMARRAGE")
    print("="*60)
    print(f"📍 URL cible: {BASE_URL}")
    print(f"📁 Dossier de destination: {DEST_DIR.absolute()}\n")
    
    try:
        # 1. Récupérer le HTML
        html = get_html(BASE_URL)
        
        # 2. Extraire les URLs de vidéos
        print("🔍 Recherche de vidéos...")
        video_urls = extract_video_urls(html, BASE_URL)
        
        if not video_urls:
            print("⚠️  Aucune vidéo trouvée sur cette page.")
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
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        raise


if __name__ == "__main__":
    main()
