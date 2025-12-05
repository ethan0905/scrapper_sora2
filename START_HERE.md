# ✅ INSTALLATION COMPLÈTE - SCRAPER SORA

## 🎉 Félicitations ! Votre scraper est prêt

Tout est installé et configuré. Voici votre point de départ.

---

## ⚡ DÉMARRAGE RAPIDE (30 secondes)

### Test immédiat (5 vidéos)
```bash
python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
```

**Ce qui va se passer :**
1. Chrome s'ouvre automatiquement
2. Page Sora se charge
3. Connectez-vous si demandé (puis ENTRÉE)
4. Le script scrolle et trouve les vidéos
5. Téléchargement dans `videos/`

---

## 📚 DOCUMENTATION DISPONIBLE

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| **QUICK_START.md** | Démarrage ultra-rapide | Vous êtes pressé |
| **USAGE_GUIDE.md** | Guide complet d'utilisation | Première utilisation |
| **MODES_COMPARISON.md** | Comparaison des modes | Choisir entre HOME/PROFILE |
| **examples.sh** | Exemples de commandes | Inspiration/copier-coller |
| **get_cookies_guide.md** | Guide cookies (si besoin) | Version simple ne marche pas |
| **README.md** | Documentation complète | Vue d'ensemble |

---

## 🎯 LES 2 MODES

### 🏠 Mode 1 : Page d'accueil
**Pour :** Découvrir, tendances, collection variée

```bash
python scraper_sora_advanced.py --mode home --num-videos 20 --delay 2
```

### 👤 Mode 2 : Profil utilisateur
**Pour :** Archiver un créateur, style spécifique

```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 15 --delay 2
```

---

## 🔧 PARAMÈTRES ESSENTIELS

- `--num-videos` : Combien de vidéos télécharger
- `--delay` : Délai entre scrolls (2s = bon équilibre)
- `--output-dir` : Dossier de destination (défaut: `videos`)
- `--headless` : Mode invisible (pour serveurs)

---

## 💡 EXEMPLES PRÊTS À L'EMPLOI

### Test rapide
```bash
python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
```

### Usage quotidien
```bash
python scraper_sora_advanced.py --mode home --num-videos 30 --delay 2
```

### Profil d'un artiste
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/artist" \
  --num-videos 50 --delay 2 \
  --output-dir "videos_artist"
```

### Voir tous les exemples
```bash
./examples.sh
```

---

## 🆘 AIDE

### Afficher l'aide
```bash
python scraper_sora_advanced.py --help
```

### Problème ?
1. Lisez `USAGE_GUIDE.md`
2. Vérifiez `page_backup.html` (créé automatiquement)
3. Augmentez `--delay` si vidéos manquantes
4. Commencez avec `--num-videos 5` pour tester

---

## 📁 FICHIERS CRÉÉS

```
scrapper_sora2/
├── 🎯 scraper_sora_advanced.py    ⭐ UTILISEZ CELUI-CI
├── 📖 USAGE_GUIDE.md              Documentation complète
├── ⚡ QUICK_START.md              Démarrage rapide
├── 💡 examples.sh                 Exemples de commandes
├── 📊 MODES_COMPARISON.md         Comparaison des modes
├── ✅ START_HERE.md               Ce fichier
└── 📁 videos/                     Vidéos téléchargées
```

---

## 🚀 VOTRE PREMIÈRE COMMANDE

Copiez-collez ceci dans votre terminal :

```bash
python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
```

**Appuyez sur ENTRÉE et c'est parti ! 🎬**

---

## 🎓 WORKFLOW RECOMMANDÉ

1. **Test** : 5 vidéos pour valider
   ```bash
   python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
   ```

2. **Ajustement** : Trouvez vos paramètres idéaux
   - Trop lent ? Réduisez `--delay`
   - Vidéos manquantes ? Augmentez `--delay`

3. **Production** : Lancez avec les bons paramètres
   ```bash
   python scraper_sora_advanced.py --mode home --num-videos 50 --delay 2
   ```

---

## ⚠️ IMPORTANT

- ✅ Utilisez UNIQUEMENT pour vos propres vidéos
- ✅ Respectez les CGU de Sora/OpenAI
- ✅ Ajoutez des délais pour ne pas surcharger
- ❌ Ne distribuez pas les vidéos téléchargées

---

## 📞 BESOIN D'AIDE ?

- 📖 Lisez `USAGE_GUIDE.md` (très détaillé)
- 📊 Comparez les modes dans `MODES_COMPARISON.md`
- 💡 Copiez les exemples de `examples.sh`
- 🔍 Vérifiez `page_backup.html` si problème

---

**Prêt à commencer ? Lancez votre première commande ! 🚀**

```bash
python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2
```
