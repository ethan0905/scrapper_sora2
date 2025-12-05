# 🔧 Guide de Dépannage - Mode Profile

## 🚨 Problème : Le scraper charge la homepage au lieu du profil

### ✅ Solution appliquée

Le scraper a été mis à jour avec :

1. **Vérification de l'URL** : Détecte si l'URL actuelle correspond à celle demandée
2. **Détection du type de page** : Identifie si on est sur un profil ou la homepage
3. **Tentatives de redirection** : Essaie de naviguer à nouveau vers le profil
4. **Messages d'avertissement clairs** : Vous informe des problèmes

---

## 🎯 Comment tester la correction

### Test 1 : Vérifier la logique de détection
```bash
python test_scraper.py
```

**Résultat attendu :** Tous les tests doivent passer ✅

### Test 2 : Tester avec un profil réel
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 5 --delay 2
```

**Ce qui va se passer maintenant :**
1. 🌐 Chrome s'ouvre et charge l'URL du profil
2. 📍 Affiche l'URL actuelle (vérification)
3. 🔍 Détecte le type de page (profile/homepage/unknown)
4. ⚠️ **SI problème** : Affiche un avertissement clair
5. 🔄 Tente de recharger le profil si nécessaire
6. 📥 Continue le scraping sur la bonne page

---

## 🔍 Nouveaux messages de débogage

Vous verrez maintenant ces informations :

```
📍 URL demandée: https://sora.chatgpt.com/user/artist
📍 URL actuelle: https://sora.chatgpt.com/user/artist
🔍 Type de page détecté: profile
```

### Si problème détecté :

```
⚠️  ATTENTION: L'URL actuelle ne correspond pas à l'URL demandée!
   Demandée: https://sora.chatgpt.com/user/artist
   Actuelle: https://sora.chatgpt.com/explore

❌ ERREUR: Vous êtes sur la page d'accueil, pas sur le profil!

💡 Tentative de navigation vers le bon profil...
```

---

## 🐛 Causes possibles du problème

### 1. **Profil inexistant**
- ❌ L'utilisateur n'existe pas
- ❌ Le nom d'utilisateur est incorrect
- ❌ Le profil a été supprimé

**Solution :** Vérifiez l'URL dans votre navigateur manuellement

### 2. **Profil privé ou bloqué**
- ❌ Le profil est privé
- ❌ Vous êtes bloqué par l'utilisateur
- ❌ Accès restreint

**Solution :** Connectez-vous avec un compte qui a accès

### 3. **Redirection automatique**
- ❌ Sora vous redirige vers la homepage
- ❌ Authentification requise
- ❌ Pas de connexion

**Solution :** Le script détectera et affichera un message

### 4. **Format d'URL incorrect**

**Formats acceptés :**
```bash
✅ https://sora.chatgpt.com/user/username
✅ https://sora.chatgpt.com/profile/username
✅ https://sora.chatgpt.com/@username
```

**Formats incorrects :**
```bash
❌ sora.chatgpt.com/user/username       (manque https://)
❌ https://sora.chatgpt.com/username    (manque /user/)
❌ https://sora.chatgpt.com/           (pas de username)
```

---

## 💡 Comment trouver l'URL correcte d'un profil

### Méthode 1 : Via le navigateur

1. Ouvrez https://sora.chatgpt.com dans votre navigateur
2. Cherchez l'utilisateur ou ses vidéos
3. Cliquez sur son nom/avatar
4. Copiez l'URL complète de la barre d'adresse

### Méthode 2 : Via une vidéo

1. Trouvez une vidéo de l'utilisateur
2. Cliquez sur le nom de l'auteur
3. Copiez l'URL du profil

---

## 🧪 Test manuel complet

### Étape 1 : Vérifier l'URL dans le navigateur
```bash
# Ouvrez cette URL dans Chrome manuellement
https://sora.chatgpt.com/user/USERNAME
```

**Questions à vérifier :**
- ✅ La page se charge-t-elle ?
- ✅ Voyez-vous les vidéos de l'utilisateur ?
- ✅ Êtes-vous connecté ?

### Étape 2 : Lancer le scraper
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 5 --delay 2
```

### Étape 3 : Vérifier les messages

**Si tout va bien :**
```
📍 URL demandée: https://sora.chatgpt.com/user/USERNAME
📍 URL actuelle: https://sora.chatgpt.com/user/USERNAME
🔍 Type de page détecté: profile
✅ Tout est OK !
```

**Si problème :**
```
⚠️  ATTENTION: L'URL actuelle ne correspond pas à l'URL demandée!
💡 Le script va essayer de corriger automatiquement
```

---

## 🎯 Exemples corrigés

### Exemple 1 : Profil public simple
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/artist_public" \
  --num-videos 10 --delay 2 \
  --output-dir "videos_artist_public"
```

### Exemple 2 : Votre propre profil
```bash
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/VOTRE_USERNAME" \
  --num-videos 50 --delay 2 \
  --output-dir "backup_mes_videos"
```

### Exemple 3 : Test avec verbose
```bash
# Le script affichera maintenant tous les détails de navigation
python scraper_sora_advanced.py --mode profile \
  --profile-url "https://sora.chatgpt.com/user/test" \
  --num-videos 5 --delay 2
```

---

## 🆘 Si ça ne marche toujours pas

### Option 1 : Connexion manuelle pendant l'exécution

Quand le script demande :
```
👉 Veuillez vous connecter manuellement dans le navigateur.
👉 Naviguez vers la page souhaitée si nécessaire.
👉 Appuyez sur ENTRÉE une fois connecté et sur la bonne page...
```

**Actions à faire :**
1. Connectez-vous à Sora
2. **NAVIGUEZ MANUELLEMENT** vers le profil voulu
3. Attendez que la page soit complètement chargée
4. Appuyez sur ENTRÉE dans le terminal

### Option 2 : Vérifier le HTML généré

Le script crée `page_backup.html` automatiquement :
```bash
# Ouvrir le backup HTML
open page_backup.html  # macOS
```

**Vérifiez :**
- Est-ce le HTML du profil ou de la homepage ?
- Voyez-vous les vidéos dans le HTML ?

### Option 3 : Utiliser le mode home à la place

Si le mode profile ne fonctionne pas, utilisez le mode home :
```bash
python scraper_sora_advanced.py --mode home --num-videos 30 --delay 2
```

---

## 📊 Améliorations apportées

| Avant | Après |
|-------|-------|
| ❌ Pas de vérification d'URL | ✅ Vérification automatique |
| ❌ Pas de détection de redirection | ✅ Détecte et alerte |
| ❌ Aucun message d'erreur clair | ✅ Messages détaillés |
| ❌ Une seule tentative | ✅ Tentatives multiples |
| ❌ Pas de détection du type de page | ✅ Détecte profile/homepage |

---

## ✅ Checklist de dépannage

Avant de signaler un problème, vérifiez :

- [ ] L'URL est correcte et complète (avec https://)
- [ ] Le profil existe (testez dans le navigateur)
- [ ] Vous êtes connecté à Sora
- [ ] Le profil n'est pas privé/bloqué
- [ ] Vous avez lu les messages d'erreur du script
- [ ] Vous avez vérifié `page_backup.html`
- [ ] Vous avez essayé avec `--num-videos 5` (test rapide)

---

**Le mode profile devrait maintenant fonctionner correctement ! 🎉**

Si problème persistant, le script vous guidera avec des messages clairs.
