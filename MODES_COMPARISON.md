# 🎯 Comparaison des Modes de Scraping

## 📊 Tableau comparatif

| Caractéristique | Mode HOME | Mode PROFILE |
|----------------|-----------|--------------|
| **URL** | Page d'accueil Sora | Profil utilisateur spécifique |
| **Contenu** | Vidéos en tendance | Vidéos d'un créateur |
| **Commande** | `--mode home` | `--mode profile` |
| **URL requise** | ❌ Non (automatique) | ✅ Oui (`--profile-url`) |
| **Use case** | Découverte, tendances | Archivage, créateur préféré |
| **Variété** | ⭐⭐⭐⭐⭐ Très haute | ⭐⭐ Spécifique à l'artiste |

---

## 🏠 MODE 1: PAGE D'ACCUEIL

### 📍 Quand l'utiliser ?
- Découvrir les vidéos populaires
- Télécharger le top du jour
- Explorer le contenu trending
- Créer une collection variée

### ✅ Avantages
- Pas besoin de connaître des profils
- Contenu frais et populaire
- Grande diversité
- Facile à lancer

### 📝 Exemples

**Test rapide (5 vidéos) :**
```bash
python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
```

**Usage quotidien (30 vidéos) :**
```bash
python scraper_sora_advanced.py --mode home --num-videos 30 --delay 2
```

**Collection complète (100 vidéos) :**
```bash
python scraper_sora_advanced.py --mode home --num-videos 100 --delay 3
```

**Dossier personnalisé :**
```bash
python scraper_sora_advanced.py --mode home --num-videos 50 \
  --delay 2 --output-dir "sora_trending_2024"
```

---

## 👤 MODE 2: PROFIL UTILISATEUR

### 📍 Quand l'utiliser ?
- Archiver les vidéos d'un artiste préféré
- Sauvegarder votre propre contenu
- Suivre un créateur spécifique
- Créer une collection thématique

### ✅ Avantages
- Contenu cohérent (même style)
- Archivage complet d'un créateur
- Suivi de créateurs spécifiques
- Création de datasets thématiques

### 📝 Exemples

**Profil basique (15 vidéos) :**
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/artist_name" \
  --num-videos 15 --delay 2
```

**Archive complète d'un artiste (100 vidéos) :**
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/artist_name" \
  --num-videos 100 --delay 3 \
  --output-dir "videos_artist_name"
```

**Votre propre profil :**
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/YOUR_USERNAME" \
  --num-videos 50 --delay 2 \
  --output-dir "mes_videos_sora"
```

---

## 🔧 Paramètres expliqués

### `--num-videos` (Nombre de vidéos)

| Valeur | Temps approximatif | Usage |
|--------|-------------------|-------|
| 5 | ~1-2 min | Test rapide |
| 10 | ~2-3 min | Petite collection |
| 20-30 | ~5-10 min | Usage normal |
| 50 | ~15-20 min | Grande collection |
| 100+ | ~30-60 min | Archive complète |

⚠️ **Note :** Temps incluant scrolling + téléchargement

### `--delay` (Délai entre scrolls)

| Valeur | Avantage | Inconvénient |
|--------|----------|--------------|
| 1s | ⚡ Très rapide | Peut manquer des vidéos |
| 2s | ✅ Équilibré (RECOMMANDÉ) | - |
| 3s | 🎯 Sûr et stable | Un peu plus lent |
| 5s+ | 💯 Garantit tout charger | Très lent |

**💡 Conseil :** Commencez avec 2s, augmentez si problèmes

---

## 🎬 Cas d'usage réels

### 📚 Cas 1 : Recherche & Inspiration
**Objectif :** Explorer les tendances
```bash
python scraper_sora_advanced.py --mode home --num-videos 50 --delay 2
```

### 🎨 Cas 2 : Suivre un artiste préféré
**Objectif :** Archiver toutes ses créations
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/favorite_artist" \
  --num-videos 100 --delay 3 \
  --output-dir "collection_favorite_artist"
```

### 💾 Cas 3 : Backup personnel
**Objectif :** Sauvegarder vos propres vidéos
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/MY_USERNAME" \
  --num-videos 200 --delay 2 \
  --output-dir "backup_mes_videos"
```

### 🤖 Cas 4 : Dataset pour ML
**Objectif :** Créer un dataset vidéo
```bash
# Top 100 vidéos populaires
python scraper_sora_advanced.py --mode home --num-videos 100 --delay 2 \
  --output-dir "dataset_sora_top100"

# Vidéos d'un style spécifique
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/style_specific" \
  --num-videos 50 --delay 2 \
  --output-dir "dataset_style_specific"
```

---

## 🚀 Workflow recommandé

### Étape 1 : Test
```bash
# Toujours commencer par un petit test
python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
```

### Étape 2 : Ajustement
- ✅ Ça marche ? Augmentez `--num-videos`
- ❌ Vidéos manquantes ? Augmentez `--delay`
- 🐌 Trop lent ? Réduisez `--delay`

### Étape 3 : Production
```bash
# Une fois les paramètres optimaux trouvés
python scraper_sora_advanced.py --mode home --num-videos 50 --delay 2
```

---

## 💡 Astuces pro

1. **Testez d'abord** : Toujours commencer avec 5-10 vidéos
2. **Adaptez le délai** : Selon votre connexion internet
3. **Nommage intelligent** : Utilisez `--output-dir` pour organiser
4. **Mode headless** : Uniquement quand ça marche déjà
5. **Patience** : Le scraping de qualité prend du temps
6. **Vérifiez** : Regardez `page_backup.html` si problème

---

## ⚠️ Limites à connaître

- **Rate limiting** : Sora peut limiter les requêtes
- **Authentification** : Connexion ChatGPT requise
- **Expiration** : URLs de vidéos peuvent expirer
- **Contenu dynamique** : Certaines vidéos en blob://
- **Protection** : Sora peut détecter l'automatisation

**Solution :** Respectez les délais, ne soyez pas trop agressif

---

## 🎓 Quelle mode choisir ?

**Choisissez HOME si :**
- ✅ Vous voulez découvrir du contenu
- ✅ Vous cherchez de l'inspiration
- ✅ Vous voulez une collection variée

**Choisissez PROFILE si :**
- ✅ Vous avez un créateur préféré
- ✅ Vous voulez archiver un style spécifique
- ✅ Vous voulez sauvegarder votre propre contenu

**💡 Conseil :** Vous pouvez utiliser les deux ! Créez des dossiers séparés.

---

**Prêt à scraper ? Choisissez votre mode et lancez-vous ! 🚀**
