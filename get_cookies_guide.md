# 🍪 Guide : Récupérer vos cookies pour accéder à Sora

Le site **sora.chatgpt.com** nécessite une authentification ChatGPT. Voici comment récupérer vos cookies :

---

## 📋 **Méthode 1 : Depuis Chrome/Edge (Recommandé)**

1. **Ouvrez** https://sora.chatgpt.com dans votre navigateur
2. **Connectez-vous** à votre compte ChatGPT
3. **Ouvrez les DevTools** :
   - Mac : `Cmd + Option + I`
   - Windows/Linux : `F12` ou `Ctrl + Shift + I`

4. **Allez dans l'onglet "Application"** (ou "Storage" sur Firefox)
5. **Cliquez sur "Cookies"** → `https://sora.chatgpt.com`
6. **Cherchez** ces cookies importants :
   - `__Secure-next-auth.session-token`
   - `__Host-next-auth.csrf-token`
   - Ou tout cookie commençant par `_cfuvid`, `__cf_bm`

7. **Copiez les valeurs** et ajoutez-les dans `scraper_videos.py` :

```python
COOKIES = {
    "__Secure-next-auth.session-token": "votre_valeur_ici",
    "__Host-next-auth.csrf-token": "autre_valeur_ici",
    # Ajoutez tous les cookies importants
}
```

---

## 📋 **Méthode 2 : Utiliser l'extension EditThisCookie**

1. **Installez** l'extension [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/)
2. **Allez sur** https://sora.chatgpt.com
3. **Cliquez** sur l'icône de l'extension
4. **Exportez** les cookies (icône d'export en bas)
5. **Collez** dans votre script

---

## 📋 **Méthode 3 : Approche alternative - Téléchargement manuel du HTML**

Si vous ne voulez pas gérer les cookies :

1. **Ouvrez** https://sora.chatgpt.com/explore?feed=top dans votre navigateur
2. **Attendez** que la page charge complètement
3. **Clic droit** → "Enregistrer sous..." → Sauvegardez comme `sora_page.html`
4. **Modifiez** votre script :

```python
BASE_URL = "file:///Users/ethan/Desktop/scrapper_sora2/sora_page.html"
```

⚠️ **Limitation** : Cette méthode ne fonctionne que si les vidéos sont dans le HTML statique (pas chargées dynamiquement en JavaScript)

---

## 📋 **Méthode 4 : Utiliser Selenium (automatisation complète)**

Si rien ne fonctionne, il faut utiliser un vrai navigateur automatisé.

Je peux créer une version avec **Selenium** qui :
- Ouvre Chrome automatiquement
- Se connecte avec vos credentials
- Scrape les vidéos comme un humain

Voulez-vous que je crée cette version ? 🤖

---

## ⚠️ **Important : Respect des CGU**

- Sora est un service payant de OpenAI
- N'utilisez ce script QUE pour télécharger **vos propres vidéos**
- Ne distribuez pas les vidéos téléchargées
- Respectez les limites de taux (rate limiting)

---

## 🔧 **Test rapide**

Une fois les cookies ajoutés, testez :

```bash
python scraper_videos.py
```

Si ça ne fonctionne toujours pas, dites-moi et je créerai la version Selenium ! 🚀
