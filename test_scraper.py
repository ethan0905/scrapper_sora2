#!/usr/bin/env python3
"""
Script de test pour vérifier la logique de navigation du scraper
"""

import sys
from scraper_sora_advanced import SoraScraper

def test_url_detection():
    """Test de la détection d'URL similaires."""
    scraper = SoraScraper()
    
    print("🧪 TEST 1: Détection d'URLs similaires")
    print("-" * 60)
    
    test_cases = [
        ("https://sora.chatgpt.com/user/john", "https://sora.chatgpt.com/user/john", True),
        ("https://sora.chatgpt.com/user/john", "https://sora.chatgpt.com/user/john/", True),
        ("https://sora.chatgpt.com/user/john?tab=videos", "https://sora.chatgpt.com/user/john", True),
        ("https://sora.chatgpt.com/user/john", "https://sora.chatgpt.com/user/jane", False),
        ("https://sora.chatgpt.com/user/john", "https://sora.chatgpt.com/explore", False),
    ]
    
    passed = 0
    failed = 0
    
    for url1, url2, expected in test_cases:
        result = scraper._is_similar_url(url1, url2)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status}: {url1} vs {url2} -> {result} (attendu: {expected})")
        if result == expected:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Résultat: {passed} tests réussis, {failed} tests échoués\n")
    
    return failed == 0

def test_page_type_detection():
    """Test de la détection du type de page (simulé)."""
    print("🧪 TEST 2: Détection du type de page")
    print("-" * 60)
    
    test_cases = [
        ("/user/john", "profile"),
        ("/profile/jane", "profile"),
        ("/@artist", "profile"),
        ("/explore?feed=top", "homepage"),
        ("/feed", "homepage"),
        ("/about", "unknown"),
    ]
    
    print("ℹ️  Ce test nécessite un navigateur actif (test manuel)")
    print("   Types attendus pour chaque URL:")
    
    for path, expected_type in test_cases:
        full_url = f"https://sora.chatgpt.com{path}"
        print(f"   {full_url:<50} -> {expected_type}")
    
    print("-" * 60)
    print("✅ Test simulé terminé\n")
    
    return True

def main():
    """Exécute tous les tests."""
    print("="*60)
    print("🧪 TESTS DU SCRAPER SORA")
    print("="*60)
    print()
    
    all_passed = True
    
    # Test 1: Détection d'URLs similaires
    if not test_url_detection():
        all_passed = False
    
    # Test 2: Détection du type de page
    if not test_page_type_detection():
        all_passed = False
    
    # Résumé
    print("="*60)
    if all_passed:
        print("✅ TOUS LES TESTS SONT PASSÉS")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
