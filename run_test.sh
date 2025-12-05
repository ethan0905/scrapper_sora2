#!/bin/bash

# 🎯 GUIDE RAPIDE: Test de la Solution Complète

echo "============================================================"
echo "🧪 TEST DU SCRAPER SORA - Solution Complète"
echo "============================================================"
echo ""

# Vérifier que Chrome tourne
if ! lsof -i :9222 > /dev/null 2>&1; then
    echo "❌ Chrome n'est pas lancé avec remote debugging!"
    echo ""
    echo "Lancez d'abord:"
    echo "  ./launch_chrome.sh"
    echo ""
    echo "Puis:"
    echo "  1. Connectez-vous à Sora dans le Chrome qui s'ouvre"
    echo "  2. Relancez ce script"
    exit 1
fi

echo "✅ Chrome détecté sur port 9222"
echo ""

# Vérifier si l'utilisateur est connecté
echo "⚠️  IMPORTANT: Êtes-vous connecté à Sora dans Chrome?"
echo ""
read -p "   Appuyez sur ENTRÉE si vous êtes connecté, ou Ctrl+C pour annuler... " 

echo ""
echo "🚀 Lancement du test avec 30 vidéos..."
echo "   (Cela va prendre ~2-3 minutes en mode slow)"
echo ""
echo "📊 ATTENDU:"
echo "   - Scroll 1: ~6 URLs collectées"
echo "   - Scroll 2: ~12 URLs collectées"
echo "   - Scroll 3: ~18 URLs collectées"
echo "   - Scroll 4: ~24 URLs collectées"
echo "   - Scroll 5: ~30 URLs collectées"
echo "   - etc..."
echo ""
echo "   Au lieu de juste '6 URLs' à la fin!"
echo ""
read -p "Appuyez sur ENTRÉE pour commencer... "

echo ""
echo "============================================================"
echo ""

# Activer venv et lancer
cd /Users/ethan/Desktop/scrapper_sora2
source venv/bin/activate

python scraper_sora_advanced.py \
    --use-existing-chrome \
    --mode profile \
    --profile-url 'https://sora.chatgpt.com/profile/rickyberwick' \
    --num-videos 30 \
    --slow

echo ""
echo "============================================================"
echo "✅ Test terminé!"
echo "============================================================"
