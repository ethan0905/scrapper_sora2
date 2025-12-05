#!/bin/bash

# 🎬 Exemples de commandes Scraper Sora
# Copiez-collez directement dans votre terminal

echo "🎬 SCRAPER SORA - EXEMPLES DE COMMANDES"
echo "========================================"
echo ""

# ============================================
# MODE 1: PAGE D'ACCUEIL
# ============================================

echo "📌 MODE 1: SCRAPING DE LA PAGE D'ACCUEIL"
echo ""

# Exemple 1: Usage basique (10 vidéos)
echo "✅ Exemple 1: 10 vidéos de la page d'accueil"
echo "python scraper_sora_advanced.py --mode home --num-videos 10 --delay 2"
echo ""

# Exemple 2: Scraping rapide
echo "✅ Exemple 2: Scraping rapide (20 vidéos, 1s de délai)"
echo "python scraper_sora_advanced.py --mode home --num-videos 20 --delay 1"
echo ""

# Exemple 3: Scraping complet
echo "✅ Exemple 3: Scraping complet (50 vidéos, 3s de délai)"
echo "python scraper_sora_advanced.py --mode home --num-videos 50 --delay 3"
echo ""

# ============================================
# MODE 2: PROFIL UTILISATEUR
# ============================================

echo "📌 MODE 2: SCRAPING D'UN PROFIL UTILISATEUR"
echo ""

# Exemple 4: Profil utilisateur
echo "✅ Exemple 4: Vidéos d'un profil (15 vidéos)"
echo 'python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/USERNAME" --num-videos 15 --delay 2'
echo ""

# Exemple 5: Archive complète d'un artiste
echo "✅ Exemple 5: Archive complète d'un artiste (100 vidéos)"
echo 'python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/USERNAME" --num-videos 100 --delay 3 --output-dir "videos_artiste"'
echo ""

# ============================================
# OPTIONS AVANCÉES
# ============================================

echo "📌 OPTIONS AVANCÉES"
echo ""

# Exemple 6: Dossier personnalisé
echo "✅ Exemple 6: Sauvegarder dans un dossier spécifique"
echo 'python scraper_sora_advanced.py --mode home --num-videos 20 --output-dir "videos_sora_top"'
echo ""

# Exemple 7: Mode headless (sans interface)
echo "✅ Exemple 7: Mode headless (serveur/background)"
echo "python scraper_sora_advanced.py --mode home --num-videos 10 --headless"
echo ""

# ============================================
# COMMANDES PRÊTES À L'EMPLOI
# ============================================

echo "📌 COMMANDES PRÊTES À L'EMPLOI"
echo ""

echo "🚀 Pour tester (5 vidéos rapide):"
echo "python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2"
echo ""

echo "🎯 Pour usage quotidien (30 vidéos):"
echo "python scraper_sora_advanced.py --mode home --num-videos 30 --delay 2"
echo ""

echo "💎 Pour scraping intensif (100 vidéos):"
echo "python scraper_sora_advanced.py --mode home --num-videos 100 --delay 3"
echo ""

echo "👤 Pour un profil utilisateur:"
echo 'python scraper_sora_advanced.py --mode profile --profile-url "https://sora.chatgpt.com/user/USERNAME" --num-videos 50 --delay 2'
echo ""

echo "========================================"
echo "💡 Pour voir toutes les options:"
echo "python scraper_sora_advanced.py --help"
echo ""
