#!/bin/bash

# Script pour lancer Chrome avec remote debugging
# Cela permet au scraper de se connecter à votre session Chrome existante
# et de réutiliser votre session déjà connectée (pas besoin de re-login!)

PORT=9222
PROFILE_DIR="$HOME/chrome-selenium-profile"

echo "🚀 Lancement de Chrome avec remote debugging..."
echo "   Port: $PORT"
echo "   Profil: $PROFILE_DIR"
echo ""
echo "💡 Une fois Chrome ouvert:"
echo "   1. Connectez-vous à Sora (https://sora.chatgpt.com)"
echo "   2. Naviguez vers le profil ou la page que vous voulez scraper"
echo "   3. Lancez le scraper avec: python3 scraper_sora_advanced.py --use-existing-chrome --mode profile --profile-url <URL>"
echo ""
echo "⚠️  Ne fermez PAS cette fenêtre Chrome - le scraper y sera connecté!"
echo ""

# Lancer Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=$PORT \
    --user-data-dir="$PROFILE_DIR" \
    &

echo "✅ Chrome lancé! PID: $!"
echo ""
echo "Pour arrêter Chrome plus tard:"
echo "   kill $!"
