# 🎬 Scraper de Vidéos Sora

Un scraper Python pour télécharger automatiquement vos vidéos depuis Sora (ChatGPT).

## 🚨 Problème actuel : Erreur 403 Forbidden

Sora bloque les requêtes simples car le site nécessite :
- ✅ Authentification ChatGPT (cookies/session)
- ✅ JavaScript pour charger le contenu dynamique
- ✅ Headers de navigateur réalistes

## 📦 Deux versions disponibles

### **Version 1 : Simple (requests + BeautifulSoup)**
- ✅ Rapide et léger
- ❌ Ne fonctionne pas avec Sora (403 Forbidden)
- ✅ Bon pour les sites statiques simples

**Fichier :** `scraper_videos.py`

### **Version 2 : Avancée (Selenium) - RECOMMANDÉ**
- ✅ Automatise un vrai navigateur Chrome
- ✅ Gère l'authentification ChatGPT
- ✅ Charge le JavaScript dynamique
- ✅ Scrolle pour charger les vidéos lazy-loaded

**Fichier :** `scraper_videos_selenium.py`

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

### **Méthode recommandée : Selenium**

```bash
python scraper_videos_selenium.py
```

**Ce qui va se passer :**
1. 🌐 Chrome s'ouvre automatiquement
2. 🔐 Si connexion requise : connectez-vous manuellement
3. 📜 Le script scrolle pour charger les vidéos
4. 🔍 Extraction des URLs de vidéos
5. 📥 Téléchargement automatique dans `videos/`

**Configuration :**
- Modifiez `BASE_URL` dans le script
- Ajustez `WAIT_TIME` si la page est lente
- `HEADLESS = True` pour mode invisible

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

## 📁 Structure du projet

```
scrapper_sora2/
├── scraper_videos.py              # Version simple (requests)
├── scraper_videos_selenium.py     # Version Selenium (RECOMMANDÉ)
├── requirements.txt               # Dépendances version simple
├── requirements_selenium.txt      # Dépendances Selenium
├── get_cookies_guide.md          # Guide cookies
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