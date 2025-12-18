# 🚀 AWS EC2 - Guide Étape par Étape (Compte Créé)

## Étape 1: Lancer une Instance EC2

### 1.1 Accéder à EC2
```
1. Connectez-vous à https://console.aws.amazon.com/
2. En haut à droite: Changer la région → "US East (N. Virginia)" us-east-1
3. Dans la barre de recherche: Tapez "EC2" → Cliquez sur "EC2"
4. Cliquez sur "Launch Instance" (bouton orange)
```

### 1.2 Configuration de l'Instance

**Nom:**
```
Name: sora-scraper
```

**Système d'exploitation:**
```
Application and OS Images:
→ Quick Start
→ Ubuntu
→ Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
→ Architecture: 64-bit (x86)
```

**Type d'instance:**
```
Instance type: t3.medium
- 2 vCPU
- 4 GB RAM
- ~$30/mois
```

💡 **Pour tester d'abord (moins cher):**
```
Instance type: t3.small
- 2 GB RAM
- ~$15/mois
```

**Paire de clés (Key pair):**
```
1. Cliquez sur "Create new key pair"
2. Nom: sora-scraper-key
3. Type: RSA
4. Format: .pem (pour Mac)
5. Cliquez "Create key pair"
6. ⚠️ IMPORTANT: Le fichier .pem se télécharge automatiquement
   → Déplacez-le dans un endroit sûr: ~/Documents/aws-keys/
```

**Stockage (Storage):**
```
Configure storage: 100 GiB gp3
(100 GB pour stocker vos vidéos)
```

**Paramètres réseau (Network settings):**
```
1. Cliquez "Edit" à côté de "Network settings"

2. Firewall (security groups):
   ☑ Create security group
   
3. Ajoutez ces règles:
   
   Rule 1 - SSH:
   ✅ Allow SSH traffic from: My IP
   
   Rule 2 - VNC (Important!):
   → Cliquez "Add security group rule"
   Type: Custom TCP
   Port range: 5901
   Source: My IP
   Description: VNC access

   Rule 3 - HTTP (Optionnel):
   → Cliquez "Add security group rule"  
   Type: HTTP
   Port range: 80
   Source: Anywhere
   Description: Web monitoring
```

**Résumé:**
```
Vérifiez:
- Région: US East (N. Virginia) ✅
- OS: Ubuntu 22.04 ✅
- Type: t3.medium ✅
- Stockage: 100 GB ✅
- Key pair: Téléchargée ✅
- Ports: 22 (SSH), 5901 (VNC) ✅
```

### 1.3 Lancer!
```
1. Cliquez "Launch Instance" (bouton orange en bas à droite)
2. Attendez 1-2 minutes
3. Cliquez "View all instances"
4. Votre instance apparaît avec:
   - Instance ID: i-xxxxxxxxxxxxx
   - State: Running (après ~1 min)
   - Public IPv4 address: XX.XXX.XX.XX ← Notez cette IP!
```

---

## Étape 2: Se Connecter à votre VM

### 2.1 Préparer la clé SSH sur votre Mac

```bash
# Ouvrez Terminal sur votre Mac

# Déplacez la clé dans un dossier sécurisé
mkdir -p ~/Documents/aws-keys
mv ~/Downloads/sora-scraper-key.pem ~/Documents/aws-keys/

# Sécurisez la clé (obligatoire)
chmod 400 ~/Documents/aws-keys/sora-scraper-key.pem

# Vérifiez
ls -l ~/Documents/aws-keys/sora-scraper-key.pem
# Devrait afficher: -r-------- (permissions correctes)
```

### 2.2 Connexion SSH

```bash
# Remplacez YOUR_EC2_IP par l'IP de votre instance
ssh -i ~/Documents/aws-keys/sora-scraper-key.pem ubuntu@YOUR_EC2_IP

# Exemple:
# ssh -i ~/Documents/aws-keys/sora-scraper-key.pem ubuntu@54.123.45.67

# Première connexion: Tapez "yes" quand demandé
# Vous devriez voir:
# ubuntu@ip-XX-XXX-XX-XX:~$
```

✅ **Connecté! Vous êtes maintenant sur votre VM aux USA!**

---

## Étape 3: Installation (Sur la VM)

### 3.1 Vérifier que vous êtes aux USA

```bash
# Vérifiez votre localisation
curl https://ipapi.co/json/

# Devrait afficher:
# "country": "US"  ← ✅ Important!
```

### 3.2 Installer tout automatiquement

```bash
# Téléchargez et exécutez le script d'installation
curl -sSL https://raw.githubusercontent.com/ethan0905/scrapper_sora2/main/scripts/aws_setup_vnc.sh | bash

# L'installation prend ~5-10 minutes
# Attendez que tout soit installé...
```

**Ce script installe:**
- ✅ Bureau XFCE (interface graphique)
- ✅ Serveur VNC (accès visuel)
- ✅ Google Chrome
- ✅ Python 3.11
- ✅ Votre projet scrapper_sora2
- ✅ Toutes les dépendances

---

## Étape 4: Démarrer VNC (Accès Visuel)

### 4.1 Sur la VM

```bash
# Démarrer le serveur VNC (première fois)
vncserver :1 -geometry 1920x1080 -depth 24

# Il va demander un mot de passe VNC:
# → Créez un mot de passe (8 caractères minimum)
# → Confirmez-le
# → View-only password? → Tapez "n"

# Vous devriez voir:
# New 'X' desktop is ip-XXX:1
```

### 4.2 Sur votre Mac - Créer un tunnel SSH

```bash
# Ouvrez un NOUVEAU Terminal sur votre Mac
# (Gardez le premier ouvert avec SSH!)

# Créez le tunnel VNC (remplacez YOUR_EC2_IP)
ssh -i ~/Documents/aws-keys/sora-scraper-key.pem \
    -L 5901:localhost:5901 \
    ubuntu@YOUR_EC2_IP \
    -N -f

# Pas de message = succès!
# Le tunnel tourne en arrière-plan
```

### 4.3 Se connecter avec VNC Viewer

**Sur Mac (méthode intégrée):**
```
1. Finder → Menu "Aller" → "Se connecter au serveur..." (Cmd+K)
2. Adresse du serveur: vnc://localhost:5901
3. Cliquez "Se connecter"
4. Entrez le mot de passe VNC que vous avez créé
5. ✅ Le bureau Ubuntu s'ouvre!
```

**Ou téléchargez RealVNC Viewer:**
```
https://www.realvnc.com/fr/connect/download/viewer/
→ Connectez-vous à: localhost:5901
```

---

## Étape 5: Login Manuel à Sora (Dans VNC)

### 5.1 Ouvrir Terminal dans VNC

```
Clic droit sur le bureau → "Open Terminal Here"
```

### 5.2 Démarrer Chrome avec debugging

```bash
# Dans le terminal VNC
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.chrome-profile" &

# Chrome s'ouvre dans VNC!
```

### 5.3 Login manuel à Sora

```
1. Dans Chrome (dans VNC):
   → Allez sur: https://sora.chatgpt.com/
   
2. Connectez-vous avec votre compte ChatGPT:
   → Email/mot de passe
   → Authentification 2FA si demandée
   → Résolvez les CAPTCHA si nécessaire
   
3. Une fois connecté:
   → Naviguez normalement sur le site
   → Testez: ouvrez quelques vidéos Sora
   → Cliquez sur des remix
   
4. ⚠️ IMPORTANT: GARDEZ CHROME OUVERT!
   → Ne fermez pas la fenêtre
   → Minimisez-la si besoin
```

---

## Étape 6: Configuration du Scraper

### 6.1 Configurer les credentials

```bash
# Dans le terminal VNC (ou SSH)
cd ~/scrapper_sora2

# Ajouter votre clé OpenAI
nano .env
```

**Ajoutez cette ligne:**
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Sauvegardez:** `Ctrl+O` → `Entrée` → `Ctrl+X`

### 6.2 Créer le fichier avec vos URLs

```bash
nano batch_urls.txt
```

**Ajoutez vos 500 URLs (une par ligne):**
```
https://sora.chatgpt.com/p/s_xxxxxxxxxxxxx
https://sora.chatgpt.com/p/s_yyyyyyyyyyyyy
https://sora.chatgpt.com/p/s_zzzzzzzzzzzzz
...
(500 URLs)
```

**Sauvegardez:** `Ctrl+O` → `Entrée` → `Ctrl+X`

### 6.3 (Optionnel) Configuration YouTube

```bash
# Si vous voulez uploader sur YouTube
nano youtube_credentials.json

# Collez vos credentials YouTube API
```

---

## Étape 7: Lancer le Scraping! 🚀

### 7.1 Démarrer une session screen

```bash
# Session screen = continue après déconnexion
screen -S scraper
```

### 7.2 Activer l'environnement Python

```bash
cd ~/scrapper_sora2
source venv/bin/activate
```

### 7.3 Lancer le scraper

```bash
python main.py \
  --batch batch_urls.txt \
  --max 999 \
  --slow \
  --use-existing \
  --output videos_batch

# Paramètres:
# --batch: Votre fichier avec 500 URLs
# --max 999: Tous les remix de chaque URL
# --slow: Mode lent (évite détection)
# --use-existing: Utilise VOTRE Chrome déjà connecté ✅
# --output: Dossier pour les vidéos
```

**Vous devriez voir:**
```
🚀 Connecting to existing Chrome session...
✅ Connected successfully!
📋 Processing batch file: batch_urls.txt
🔄 Processing URL 1/500...
📹 Found 12 remix buttons
⏬ Downloading video 1/12...
```

### 7.4 Détacher de screen (important!)

```
Appuyez sur: Ctrl+A puis D

Vous verrez: [detached from XXXXX.scraper]
```

✅ **Le scraping continue en arrière-plan!**

---

## Étape 8: Monitoring

### 8.1 Dashboard en temps réel

```bash
# Sur la VM (SSH ou VNC terminal)
~/scrapper_sora2/scripts/monitor.sh

# Affiche:
# - Status du scraper
# - Nombre de vidéos
# - Utilisation disque/RAM
# - Logs récents
# Rafraîchit toutes les 5 secondes
```

### 8.2 Voir Chrome travailler

```
Dans VNC:
→ Regardez Chrome naviguer automatiquement
→ Cliquez sur les remix
→ Télécharger les vidéos
→ Tout est visible en temps réel!
```

### 8.3 Vérifier les logs

```bash
# Logs détaillés
tail -f ~/scrapper_sora2/logs/scraper.log

# Compter les vidéos
ls ~/scrapper_sora2/videos_batch/*.mp4 | wc -l

# Taille totale
du -sh ~/scrapper_sora2/videos_batch/
```

### 8.4 Se reconnecter à screen

```bash
# Liste des sessions
screen -ls

# Reconnecter
screen -r scraper

# Détacher à nouveau: Ctrl+A puis D
```

---

## Étape 9: Récupérer les Vidéos (Sur votre Mac)

### 9.1 Synchroniser vers votre Mac

```bash
# Sur votre Mac (Terminal local)
cd /Users/ethan/Desktop/scrapper_sora2

# Télécharger toutes les vidéos
./scripts/sync_videos.sh YOUR_EC2_IP

# Les vidéos se téléchargent dans: ./videos_synced/
```

### 9.2 Automatiser la sync (optionnel)

```bash
# Créer un cron job pour sync quotidienne
crontab -e

# Ajouter cette ligne (sync tous les jours à 3h du matin):
0 3 * * * cd /Users/ethan/Desktop/scrapper_sora2 && ./scripts/sync_videos.sh YOUR_EC2_IP
```

---

## Étape 10: Arrêter/Redémarrer

### Arrêter le scraper
```bash
# Reconnecter à screen
screen -r scraper

# Arrêter avec Ctrl+C

# Sortir de screen
exit
```

### Redémarrer le scraper
```bash
screen -S scraper
cd ~/scrapper_sora2
source venv/bin/activate
python main.py --batch batch_urls.txt --max 999 --slow --use-existing
# Ctrl+A puis D pour détacher
```

### Arrêter la VM (économiser $$$)
```
AWS Console → EC2 → Instances → 
→ Sélectionnez votre instance
→ "Instance state" → "Stop instance"

💡 Vous payez seulement le stockage quand arrêté (~$10/mois)
```

### Redémarrer la VM
```
AWS Console → EC2 → Instances → 
→ Sélectionnez votre instance
→ "Instance state" → "Start instance"

⚠️ L'IP publique CHANGE!
→ Notez la nouvelle IP
→ Reconnectez-vous avec la nouvelle IP
```

---

## Résumé - Commandes Essentielles

### Sur votre Mac:
```bash
# Connexion SSH
ssh -i ~/Documents/aws-keys/sora-scraper-key.pem ubuntu@YOUR_EC2_IP

# Tunnel VNC
ssh -i ~/Documents/aws-keys/sora-scraper-key.pem -L 5901:localhost:5901 ubuntu@YOUR_EC2_IP -N -f

# VNC: vnc://localhost:5901

# Sync vidéos
./scripts/sync_videos.sh YOUR_EC2_IP
```

### Sur la VM:
```bash
# Démarrer VNC
vncserver :1 -geometry 1920x1080 -depth 24

# Démarrer Chrome
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-profile" &

# Lancer scraper
screen -S scraper
cd ~/scrapper_sora2 && source venv/bin/activate
python main.py --batch batch_urls.txt --max 999 --slow --use-existing
# Ctrl+A puis D

# Monitoring
~/scrapper_sora2/scripts/monitor.sh
tail -f ~/scrapper_sora2/logs/scraper.log
screen -r scraper
```

---

## Dépannage

### "Permission denied" lors du SSH
```bash
chmod 400 ~/Documents/aws-keys/sora-scraper-key.pem
```

### "Connection refused" sur VNC
```bash
# Vérifiez que le tunnel SSH est actif
ps aux | grep "ssh.*5901"

# Recréez le tunnel
ssh -i ~/Documents/aws-keys/sora-scraper-key.pem -L 5901:localhost:5901 ubuntu@YOUR_EC2_IP -N -f
```

### Chrome ne se lance pas
```bash
# Tuer les processus Chrome
pkill chrome

# Relancer
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-profile" &
```

### Scraper bloqué
```bash
# Vérifier les logs
tail -100 ~/scrapper_sora2/logs/scraper.log

# Redémarrer
screen -r scraper
# Ctrl+C
# Relancer: python main.py ...
```

### Plus d'espace disque
```bash
# Vérifier
df -h

# Sync vers Mac puis supprimer
./scripts/sync_videos.sh YOUR_EC2_IP
ssh -i ~/Documents/aws-keys/sora-scraper-key.pem ubuntu@YOUR_EC2_IP "rm ~/scrapper_sora2/videos_batch/*.mp4"
```

---

## Prochaines Étapes

✅ **Votre VM tourne aux USA**  
✅ **Chrome est connecté manuellement**  
✅ **Le scraping est lancé**  
✅ **Monitoring actif**  

**Laissez tourner pendant quelques jours!**

Le scraper va:
- Traiter vos 500 URLs
- Télécharger tous les remix
- Tourner en --slow mode (évite détection)
- Continuer même si vous vous déconnectez

**Vérifiez quotidiennement:**
```bash
~/scrapper_sora2/scripts/monitor.sh
```

Bonne chance! 🚀
