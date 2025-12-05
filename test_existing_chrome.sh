#!/bin/bash

echo "🧪 TEST: Connexion à Chrome Existant"
echo "======================================"
echo ""

# Vérifier si Chrome est déjà lancé avec remote debugging
if lsof -i :9222 > /dev/null 2>&1; then
    echo "✅ Chrome est déjà lancé avec remote debugging (port 9222)"
else
    echo "⚠️  Chrome n'est PAS lancé avec remote debugging"
    echo ""
    echo "Lancez d'abord:"
    echo "  ./launch_chrome.sh"
    echo ""
    echo "Puis réessayez ce test."
    exit 1
fi

echo ""
echo "🔗 Tentative de connexion..."
echo ""

# Tester avec un mode simple (home, 1 vidéo)
python3 scraper_sora_advanced.py \
    --use-existing-chrome \
    --mode home \
    --num-videos 1

echo ""
echo "✅ Test terminé!"
