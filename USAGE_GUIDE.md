# 🎯 Guide d'utilisation du Scraper Sora Avancé

## 📋 Modes disponibles

### 🏠 **Mode 1 : Page d'accueil (Homepage)**

Scrape les vidéos depuis la page principale de Sora (Explore/Top).

**Commande :**
```bash
python scraper_sora_advanced.py --mode home --num-videos 20 --delay 2
```

**Paramètres :**
- `--mode home` : Mode page d'accueil
- `--num-videos 20` : Nombre de vidéos à télécharger (défaut: 10)
- `--delay 2` : Délai entre chaque scroll en secondes (défaut: 2)

**Exemple :**
```bash
# Télécharger les 50 premières vidéos avec 3s de délai
python scraper_sora_advanced.py --mode home --num-videos 50 --delay 3

# Mode rapide (1s de délai)
python scraper_sora_advanced.py --mode home --num-videos 10 --delay 1
```

---

### 👤 **Mode 2 : Profil utilisateur (Profile)**

Scrape toutes les vidéos d'un utilisateur spécifique.

**Commande :**
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/johndoe" \
  --num-videos 15 \
  --delay 2
```

**Paramètres :**
- `--mode profile` : Mode profil utilisateur
- `--profile-url "URL"` : URL du profil (REQUIS)
- `--num-videos 15` : Nombre de vidéos à télécharger
- `--delay 2` : Délai entre chaque scroll

**Exemple :**
```bash
# Télécharger toutes les vidéos d'un utilisateur
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/janedoe" \
  --num-videos 100 \
  --delay 2
```

---

## 🛠️ Options additionnelles

### **Dossier de destination personnalisé**
```bash
python scraper_sora_advanced.py --mode home --num-videos 10 \
  --output-dir "mes_videos_sora"
```

### **Mode headless (sans interface graphique)**
```bash
python scraper_sora_advanced.py --mode home --num-videos 10 --headless
```
⚠️ Utile pour les serveurs, mais peut poser des problèmes de détection.

### **Aide complète**
```bash
python scraper_sora_advanced.py --help
```

---

## 📊 Comprendre les paramètres

### `--num-videos` (Nombre de vidéos)
- **10-20** : Rapide, pour tester
- **20-50** : Usage normal
- **50-100+** : Scraping complet (prend du temps)

### `--delay` (Délai entre scrolls)
- **1s** : Très rapide, risque de manquer des vidéos
- **2s** : Bon équilibre (RECOMMANDÉ)
- **3-5s** : Lent mais sûr, pour connexions lentes

**💡 Astuce :** Si vous ne trouvez pas toutes les vidéos, augmentez le délai !

---

## 🎬 Exemples concrets

### Télécharger les 30 meilleures vidéos du jour
```bash
python scraper_sora_advanced.py --mode home --num-videos 30 --delay 2
```

### Sauvegarder toutes les vidéos d'un artiste préféré
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/artist123" \
  --num-videos 100 \
  --delay 3 \
  --output-dir "videos_artist123"
```

### Scraping discret (headless) pour serveur
```bash
python scraper_sora_advanced.py --mode home --num-videos 20 --headless
```

---

## 🔍 Que se passe-t-il pendant l'exécution ?

1. **🚀 Initialisation** : Chrome s'ouvre
2. **🌐 Chargement** : Page Sora se charge
3. **🔐 Authentification** : Si nécessaire, connectez-vous manuellement
4. **📜 Scrolling** : Le script scrolle automatiquement
5. **🔍 Extraction** : Recherche des URLs de vidéos
6. **💾 Sauvegarde HTML** : `page_backup.html` créé pour debug
7. **📥 Téléchargement** : Une par une avec barre de progression
8. **✅ Résumé** : Statistiques finales

---

## 📁 Organisation des fichiers

Les vidéos sont sauvegardées avec des noms numérotés :
```
videos/
├── video_001.mp4
├── video_002.mp4
├── video_003.mp4
└── ...
```

Pour un dossier personnalisé :
```bash
--output-dir "videos_sora_2024"
```

---

## 🚨 Dépannage

### Aucune vidéo trouvée
1. Vérifiez `page_backup.html`
2. Augmentez `--num-videos` (plus de scrolls)
3. Augmentez `--delay` (plus de temps de chargement)
4. Vérifiez que vous êtes connecté

### Erreur de téléchargement
- Les URLs peuvent expirer rapidement
- Certaines vidéos peuvent être protégées
- Vérifiez votre connexion internet

### Chrome ne s'ouvre pas
```bash
# Installez Chrome si nécessaire
# Ou essayez --headless
python scraper_sora_advanced.py --mode home --num-videos 5 --headless
```

---

## 💡 Conseils pro

1. **Commencez petit** : Testez avec `--num-videos 5` d'abord
2. **Ajustez le délai** : Selon votre connexion
3. **Surveillez** : Ne mettez pas `--headless` au début pour voir ce qui se passe
4. **Patience** : Le scraping prend du temps, c'est normal
5. **Respect** : N'abusez pas, Sora a des limites

---

## 🎓 Comprendre les modes

| Mode | URL | Usage | Avantage |
|------|-----|-------|----------|
| `home` | Page d'accueil | Découvrir les tendances | Variété de contenu |
| `profile` | Profil utilisateur | Archiver un créateur | Contenu spécifique |

---

**Prêt à commencer ? Lancez votre première commande ! 🚀**

```bash
python scraper_sora_advanced.py --mode home --num-videos 10 --delay 2
```
