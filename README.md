# 🎬 Scraper de Vidéos Sora - Version Avancée

Un scraper Python puissant pour télécharger automatiquement vos vidéos depuis Sora (ChatGPT) **OU** extraire leurs métadonnées complètes pour import dans une app TikTok-like.

## ✨ Nouveauté : Mode Métadonnées

🎉 **Nouveau !** Extrayez toutes les informations de chaque vidéo sans les télécharger :
- 👤 Créateur (username, avatar, profil)
- 📝 Description et prompt
- 📊 Engagement (likes, commentaires, partages, vues)
- 💬 Commentaires extraits
- 🎬 URLs vidéo et thumbnail
- ⏱️ Timestamps et métadonnées

**Format JSON prêt pour import dans votre app !**

[📖 Guide complet du Mode Métadonnées](METADATA_MODE.md) | [⚡ Quick Reference](METADATA_QUICK_REF.md)

## 🚨 Problème résolu : Virtual Scrolling

✅ **Corrigé !** Le scraper collecte maintenant **toutes** les vidéos même avec le virtual scrolling React de Sora.  
[📖 En savoir plus](VIRTUAL_SCROLLING_FIX.md)

## 📦 Fonctionnalités

### **Version Avancée - ⭐ RECOMMANDÉ** (`scraper_sora_advanced.py`)

#### 🎯 Deux modes de scraping
1. **Homepage** : Page d'accueil de Sora
2. **Profile** : Profil utilisateur spécifique

#### 💾 Deux modes de sortie
1. **Mode Téléchargement** : Télécharge les vidéos MP4
2. **Mode Métadonnées** : Extrait les infos détaillées en JSON

#### 🔧 Fonctionnalités avancées
- ✅ **Virtual Scrolling Fix** : Collecte toutes les vidéos même avec React virtual scrolling
- ✅ **Session Chrome existante** : Restez connecté entre les exécutions (plus de re-login !)
- ✅ **Mode SLOW** : Évite la détection avec délais aléatoires
- ✅ **Mode ALL** : Scrape jusqu'à la fin du contenu
- ✅ **Contrôle total** : Nombre de vidéos, délais personnalisables
- ✅ **Interface CLI intuitive**
- ✅ **Nommage intelligent** : Vidéos numérotées automatiquement
- ✅ **Architecture modulaire** : Classe réutilisable
- ✅ **Backup HTML** : Sauvegarde automatique pour debug

---

## 🚀 Installation

### Option A : Version Selenium (recommandée pour Sora)

```bash
pip install -r requirements_selenium.txt
```

### Option B : Version simple (pour sites non-protégés)

```bash
pip install -r requirements.txt
```

---

## 🎯 Utilisation

### **⭐ Méthode recommandée : Version avancée avec CLI**

#### **📥 Mode Téléchargement (vidéos MP4)**

##### **Exemple 1 : Scraper la page d'accueil**
```bash
python scraper_sora_advanced.py --mode home --num-videos 20 --delay 2
```

##### **Exemple 2 : Scraper un profil utilisateur**
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 15 \
  --delay 2
```

##### **Exemple 3 : Scraper TOUTES les vidéos d'un profil (mode sécurisé)**
```bash
# Étape 1 : Lancer Chrome avec remote debugging
./launch_chrome.sh

# Étape 2 : Se connecter à Sora dans Chrome

# Étape 3 : Scraper tout le profil
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --slow \
  --use-existing-chrome
```

#### **📋 Mode Métadonnées (JSON pour TikTok-like app)**

##### **Exemple 1 : Extraire métadonnées de 20 vidéos (un seul JSON)**
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 20 \
  --metadata-mode
```
**Sortie :** `metadata.json` avec toutes les vidéos

##### **Exemple 2 : Un fichier JSON par vidéo**
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 30 \
  --metadata-mode \
  --metadata-per-file
```
**Sortie :** Dossier `metadata/` avec `{video_id}.json` par vidéo

##### **Exemple 3 : Extraction complète d'un profil (RECOMMANDÉ)**
```bash
# Avec session Chrome existante pour éviter re-login
./launch_chrome.sh  # Une seule fois

python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --metadata-mode \
  --metadata-per-file \
  --use-existing-chrome \
  --slow
```

**Paramètres disponibles :**
- `--mode` : `home` (page d'accueil) ou `profile` (profil utilisateur)
- `--num-videos` : Nombre de vidéos à scraper (défaut: 10)
- `--all` : Scraper TOUTES les vidéos disponibles
- `--delay` : Délai entre chaque scroll en secondes (défaut: 2.0)
- `--slow` : Mode lent (5s min) pour éviter détection/ban
- `--profile-url` : URL du profil (requis pour mode `profile`)
- `--output-dir` : Dossier de destination (défaut: `videos`)
- `--headless` : Mode sans interface graphique
- `--use-existing-chrome` : Se connecter à Chrome existant (pas de re-login)
- `--debug-port` : Port de débogage Chrome (défaut: 9222)
- `--metadata-mode` : Extraire métadonnées au lieu de télécharger
- `--metadata-output` : Fichier de sortie pour métadonnées (défaut: `metadata.json`)
- `--metadata-per-file` : Un JSON par vidéo au lieu d'un seul fichier

**📖 Guides détaillés :**
- Mode Métadonnées complet : `METADATA_MODE.md`
- Quick Reference : `METADATA_QUICK_REF.md`
- Chrome existant : `USE_EXISTING_CHROME.md`
- Fix Virtual Scrolling : `VIRTUAL_SCROLLING_FIX.md`

**💡 Scripts de test :**
```bash
./test_metadata_mode.sh    # Test le mode métadonnées
./test_existing_chrome.sh   # Test Chrome remote debugging
./run_test.sh              # Test complet
```

---

### **Alternative : Selenium de base**

```bash
python scraper_videos_selenium.py
```

**Ce qui va se passer :**
1. 🌐 Chrome s'ouvre automatiquement
2. 🔐 Si connexion requise : connectez-vous manuellement
3. 📜 Le script scrolle pour charger les vidéos
4. 🔍 Extraction des URLs de vidéos
5. 📥 Téléchargement automatique dans `videos/`

---

## 🍪 Alternative : Utiliser des cookies

Si vous voulez éviter Selenium, récupérez vos cookies :

1. **Ouvrez DevTools** (F12) sur sora.chatgpt.com
2. **Onglet Application** → Cookies
3. **Copiez** `__Secure-next-auth.session-token` et autres
4. **Ajoutez** dans `scraper_videos.py` :

```python
COOKIES = {
    "__Secure-next-auth.session-token": "votre_token_ici",
}
```

📖 **Guide détaillé :** Voir `get_cookies_guide.md`

---

## 🛠️ Configuration

### Dans `scraper_videos_selenium.py` :

```python
BASE_URL = "https://sora.chatgpt.com/explore?feed=top"  # URL à scraper
DEST_DIR = pathlib.Path("videos")  # Dossier de destination
HEADLESS = False  # True = navigateur invisible
WAIT_TIME = 10  # Temps d'attente (secondes)
```

---

## � What's the Metadata Mode?

The metadata mode extracts **structured information** about each video without downloading the actual video files. Perfect for:

- 🎬 **Building a TikTok-like app** - Get all video info in JSON format
- 📊 **Analytics dashboards** - Track engagement, popular creators
- 🔍 **Search engines** - Index video descriptions and prompts
- 📈 **Trend analysis** - Monitor likes, comments, shares over time
- 💾 **Archiving** - Store metadata without huge video files

### Example Output

```json
{
  "video_id": "abc123",
  "creator": {
    "username": "johndoe",
    "avatar_url": "https://...",
    "verified": true
  },
  "content": {
    "description": "Amazing sunset over ocean",
    "prompt": "Cinematic shot..."
  },
  "engagement": {
    "likes": 1250,
    "comments_count": 45,
    "views": 5600
  },
  "comments": [
    {"author": "user123", "text": "Great work!", "likes": 23}
  ]
}
```

**[📖 Complete Metadata Mode Guide](METADATA_MODE.md)** | **[⚡ Quick Reference](METADATA_QUICK_REF.md)** | **[🚀 Getting Started](GETTING_STARTED.md)**

---

## �📁 Structure du projet

```
scrapper_sora2/
├── scraper_videos.py              # Version simple (requests)
├── scraper_videos_selenium.py     # Version Selenium de base
├── scraper_sora_advanced.py       # ⭐ Version avancée avec CLI (RECOMMANDÉ)
├── requirements.txt               # Dépendances version simple
├── requirements_selenium.txt      # Dépendances Selenium
├── get_cookies_guide.md          # Guide cookies
├── USAGE_GUIDE.md                # 📖 Guide complet d'utilisation
├── QUICK_START.md                # ⚡ Démarrage rapide
├── examples.sh                    # 💡 Exemples de commandes
├── README.md                      # Ce fichier
└── videos/                        # Vidéos téléchargées (créé auto)
```

---

## 🔧 Dépannage

### ❌ Erreur : "403 Forbidden"
→ Utilisez `scraper_videos_selenium.py` au lieu de `scraper_videos.py`

### ❌ Erreur : "No such file or directory: 'chromedriver'"
→ Selenium va télécharger chromedriver automatiquement au premier lancement

### ❌ Aucune vidéo trouvée
→ Sora charge peut-être les vidéos via API ou blob://
→ Vérifiez `page_backup.html` (créé automatiquement)
→ Les vidéos Sora utilisent peut-être un système de streaming spécial

### ❌ Chrome ne s'ouvre pas
→ Vérifiez que Chrome est installé
→ Essayez `HEADLESS = False` pour voir le navigateur

---

## ⚠️ Avertissement légal

- ✅ N'utilisez ce script QUE pour vos propres vidéos
- ✅ Respectez les CGU de Sora/OpenAI
- ❌ Ne distribuez pas les vidéos téléchargées
- ❌ N'abusez pas du service (rate limiting)

---

## 🎓 Ce que j'ai appris

Sora est un site moderne protégé qui :
- Nécessite une authentification forte
- Charge le contenu dynamiquement en JavaScript
- Utilise probablement des techniques anti-scraping
- Peut servir les vidéos via CDN/API plutôt que HTML direct

**Solution :** Automatisation avec un vrai navigateur (Selenium)

---

## 🚀 Prochaines étapes

Si Selenium ne trouve toujours pas les vidéos, on peut :

1. **Intercepter les requêtes réseau** avec Selenium
2. **Analyser l'API** utilisée par Sora
3. **Extraire les blob:// URLs** si les vidéos sont en blob
4. **Utiliser l'onglet Network** pour trouver les vraies URLs

Besoin d'aide ? Dites-moi ce que vous voyez ! 💪

---

## 🎉 NEW: Metadata Extraction Mode

### What's New?

The scraper now includes a **powerful metadata extraction mode** that collects comprehensive information about each video without downloading the video files. Perfect for building TikTok-like apps!

### Quick Start

```bash
# Extract metadata from 20 videos
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 20 \
  --metadata-mode
```

**Output:** `metadata.json` with structured data ready for import!

### What You Get

For each video:
- 👤 **Creator info** (username, avatar, verified status)
- 📝 **Content** (description, prompt, title)
- 📊 **Engagement** (likes, comments, shares, views, remixes)
- 💬 **Comments** (up to 10 comments with details)
- 🎬 **Media** (video URL, thumbnail, duration)
- 📌 **Metadata** (timestamps, unique ID, post URL)

### Documentation

| Guide | Purpose |
|-------|---------|
| **[🚀 Getting Started](GETTING_STARTED.md)** | Step-by-step tutorial |
| **[⚡ Quick Reference](METADATA_QUICK_REF.md)** | Command cheat sheet |
| **[📖 Complete Guide](METADATA_MODE.md)** | Full documentation |
| **[🔄 Flow Diagrams](METADATA_FLOW.md)** | Architecture overview |
| **[📚 Docs Index](DOCS_INDEX.md)** | All documentation |

### Example: Import to MongoDB

```bash
# Extract metadata
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --all \
  --metadata-mode

# Import to database
mongoimport --db tiktok --collection videos --file metadata.json --jsonArray
```

### Why Use Metadata Mode?

| Feature | Download Mode | Metadata Mode |
|---------|---------------|---------------|
| **Output** | MP4 video files | Structured JSON |
| **Speed** | Slow (downloads) | Fast (no downloads) |
| **Storage** | Large (GBs) | Small (KBs) |
| **Use case** | Video archiving | App development, analytics |
| **Data** | Video only | All info (creator, engagement, comments) |

### Ready to Start?

```bash
# Quick test (takes 2 minutes)
python scraper_sora_advanced.py --mode home --num-videos 5 --metadata-mode

# View results
cat metadata.json | head -50

# See usage examples
python example_metadata_usage.py
```

**[📖 Read the Getting Started Guide](GETTING_STARTED.md)** for a complete tutorial!

---

## 📞 Support & Help

- **New to the scraper?** Start with [GETTING_STARTED.md](GETTING_STARTED.md)
- **Quick commands?** Check [METADATA_QUICK_REF.md](METADATA_QUICK_REF.md)
- **Need help?** Read [DOCS_INDEX.md](DOCS_INDEX.md) for all documentation
- **Command help:** Run `python scraper_sora_advanced.py --help`

---

**Happy scraping! 🎬✨**