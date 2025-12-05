#!/usr/bin/env python3
"""
Script de démonstration pour afficher les commandes disponibles
"""

BANNER = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║              🎬 SCRAPER SORA - VERSION AVANCÉE 🎬              ║
║                                                                ║
║              Téléchargez vos vidéos depuis Sora                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""

MODES = """
📋 MODES DISPONIBLES:

  🏠 MODE 1: PAGE D'ACCUEIL
     → Scrape les vidéos trending de la page principale
     → Parfait pour: découverte, tendances, collection variée
  
  👤 MODE 2: PROFIL UTILISATEUR
     → Scrape toutes les vidéos d'un utilisateur spécifique
     → Parfait pour: archivage, créateur préféré, backup personnel
"""

QUICK_EXAMPLES = """
⚡ EXEMPLES RAPIDES:

  1️⃣  Test rapide (5 vidéos):
      python scraper_sora_advanced.py --mode home --num-videos 5 --delay 2

  2️⃣  Page d'accueil (20 vidéos):
      python scraper_sora_advanced.py --mode home --num-videos 20 --delay 2

  3️⃣  Profil utilisateur (15 vidéos):
      python scraper_sora_advanced.py --mode profile \\
        --profile-url "https://sora.chatgpt.com/user/USERNAME" \\
        --num-videos 15 --delay 2

  4️⃣  🌟 TOUT un profil en mode SLOW (RECOMMANDÉ):
      python scraper_sora_advanced.py --mode profile \\
        --profile-url "https://sora.chatgpt.com/user/USERNAME" \\
        --all --slow
"""

PARAMETERS = """
🔧 PARAMÈTRES:

  --mode {home,profile}     Mode de scraping (REQUIS)
  --num-videos N            Nombre de vidéos (défaut: 10)
  --all                     🌟 Scraper TOUTES les vidéos
  --delay SECONDS           Délai entre scrolls (défaut: 2.0)
  --slow                    🐌 Mode lent anti-ban (delay 5s + pauses)
  --profile-url URL         URL du profil (requis si mode=profile)
  --output-dir DIR          Dossier destination (défaut: videos)
  --headless                Mode sans interface graphique
"""

TIPS = """
💡 CONSEILS:

  ✅ Commencez avec 5 vidéos pour tester
  ✅ Utilisez --slow pour éviter les bans (> 20 vidéos)
  ✅ Utilisez --all --slow pour un profil complet
  ✅ Augmentez --delay si vidéos manquantes
  ✅ Vérifiez page_backup.html si problème
  ✅ Connectez-vous manuellement si demandé
  
  🌟 RECOMMANDÉ pour archivage:
     --all --slow (sécurisé mais lent)
"""

DOCS = """
📚 DOCUMENTATION:

  📖 START_HERE.md          → Commencez ici !
  📖 USAGE_GUIDE.md         → Guide complet
  📖 MODES_COMPARISON.md    → Comparaison des modes
  � SLOW_MODE_GUIDE.md     → 🌟 Guide --all --slow
  �💡 examples.sh            → Tous les exemples
  ⚡ QUICK_COMMANDS_SLOW.md → Commandes rapides
"""

HELP_CMD = """
🆘 AIDE:

  python scraper_sora_advanced.py --help
"""

FOOTER = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  🚀 Prêt à commencer ? Lancez votre première commande !       ║
║                                                                ║
║  python scraper_sora_advanced.py --mode home --num-videos 5   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""


def main():
    """Affiche le guide interactif."""
    print(BANNER)
    print(MODES)
    print(QUICK_EXAMPLES)
    print(PARAMETERS)
    print(TIPS)
    print(DOCS)
    print(HELP_CMD)
    print(FOOTER)


if __name__ == "__main__":
    main()
