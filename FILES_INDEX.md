# 📦 Index des Fichiers - Scraper Sora

## 🎯 Fichiers principaux

### 🚀 Scripts de scraping

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| **scraper_sora_advanced.py** ⭐ | Version avancée avec CLI (2 modes) | **RECOMMANDÉ** - Utilisez celui-ci ! |
| scraper_videos_selenium.py | Version Selenium basique | Alternative simple |
| scraper_videos.py | Version requests (ne marche pas) | Référence seulement |

### 🎨 Scripts d'aide

| Fichier | Description |
|---------|-------------|
| **show_help.py** | Affiche un guide visuel dans le terminal |
| examples.sh | Liste tous les exemples de commandes |

---

## 📚 Documentation

### 🌟 À lire en premier

| Fichier | Contenu | Pour qui |
|---------|---------|----------|
| **START_HERE.md** ⭐ | Point de départ complet | **Commencez ici !** |
| QUICK_START.md ⚡ | Démarrage ultra-rapide | Vous êtes pressé |

### 📖 Guides détaillés

| Fichier | Contenu |
|---------|---------|
| **USAGE_GUIDE.md** | Guide complet avec tous les paramètres et exemples |
| **MODES_COMPARISON.md** | Comparaison détaillée : HOME vs PROFILE |
| get_cookies_guide.md | Comment récupérer vos cookies (si besoin) |
| README.md | Documentation générale du projet |

---

## ⚙️ Fichiers de configuration

| Fichier | Description |
|---------|-------------|
| requirements.txt | Dépendances version simple (requests, beautifulsoup4) |
| requirements_selenium.txt | Dépendances version Selenium ✅ |

---

## 📁 Dossiers créés automatiquement

| Dossier | Contenu |
|---------|---------|
| videos/ | Vidéos téléchargées (créé au premier lancement) |

---

## 📄 Fichiers générés pendant l'exécution

| Fichier | Description |
|---------|-------------|
| page_backup.html | Backup du HTML récupéré (pour debugging) |
| video_001.mp4, video_002.mp4... | Vidéos téléchargées dans `videos/` |

---

## 🎯 Quel fichier utiliser ?

### Vous voulez scraper maintenant ?
→ **Lancez :** `python scraper_sora_advanced.py --mode home --num-videos 5`

### Première fois ?
→ **Lisez :** `START_HERE.md`

### Vous voulez voir des exemples ?
→ **Exécutez :** `python show_help.py` ou `./examples.sh`

### Vous hésitez entre HOME et PROFILE ?
→ **Lisez :** `MODES_COMPARISON.md`

### Vous voulez tous les détails ?
→ **Lisez :** `USAGE_GUIDE.md`

### Problème avec l'erreur 403 ?
→ **Lisez :** `get_cookies_guide.md` (mais utilisez plutôt Selenium)

---

## 🗂️ Structure complète

```
scrapper_sora2/
│
├── 🎯 SCRIPTS PRINCIPAUX
│   ├── scraper_sora_advanced.py    ⭐ VERSION RECOMMANDÉE
│   ├── scraper_videos_selenium.py  (alternative)
│   └── scraper_videos.py           (référence)
│
├── 🎨 SCRIPTS D'AIDE
│   ├── show_help.py                Affiche le guide
│   └── examples.sh                 Exemples de commandes
│
├── 📚 DOCUMENTATION
│   ├── START_HERE.md               ⭐ COMMENCEZ ICI
│   ├── QUICK_START.md              Démarrage rapide
│   ├── USAGE_GUIDE.md              Guide complet
│   ├── MODES_COMPARISON.md         HOME vs PROFILE
│   ├── get_cookies_guide.md        Guide cookies
│   ├── README.md                   Doc générale
│   └── FILES_INDEX.md              Ce fichier
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt
│   └── requirements_selenium.txt   ✅ Utilisé
│
└── 📁 DOSSIERS
    └── videos/                     Vidéos téléchargées
```

---

## 💡 Commandes rapides

### Afficher le guide visuel
```bash
python show_help.py
```

### Voir tous les exemples
```bash
./examples.sh
```

### Voir l'aide du scraper
```bash
python scraper_sora_advanced.py --help
```

### Test rapide
```bash
python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
```

---

## 🔄 Mise à jour du projet

Si vous voulez mettre à jour :

1. **Scripts** : Modifiez `scraper_sora_advanced.py`
2. **Dépendances** : Mettez à jour `requirements_selenium.txt`
3. **Documentation** : Éditez les fichiers `.md`

---

## 🎓 Ordre de lecture recommandé

Si c'est votre première fois :

1. **START_HERE.md** - Vue d'ensemble et première commande
2. **Testez** - Lancez `python scraper_sora_advanced.py --mode home --num-videos 5`
3. **USAGE_GUIDE.md** - Approfondissez avec le guide complet
4. **MODES_COMPARISON.md** - Choisissez entre HOME et PROFILE
5. **examples.sh** - Inspirez-vous des exemples

---

**Prêt à commencer ? Ouvrez START_HERE.md ! 🚀**
