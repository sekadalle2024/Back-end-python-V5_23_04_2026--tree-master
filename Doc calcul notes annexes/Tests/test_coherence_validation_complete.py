"""
Test Script: test_coherence_validation_complete.py
Description: Test complet de validation de cohérence pour la tâche 30.4

Ce script teste:
- Taux de cohérence inter-notes >= 95%
- Total immobilisations correspond au bilan
- Dotations amortissements correspondent au compte de résultat
- Continuité temporelle (N-1 clôture = N ouverture)

Requirements: 10.1, 10.2, 10.3, 10.5, 10.6
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin des modules au PYTHONPATH
current_dir = Path(__file__).parent
modules_dir = current_dir.parent / "Modules"
sys.path.insert(0, str(modules_dir))

import pandas as pd
import logging
from datetime import datetime
from coherence_validator import CoherenceValidator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def creer_notes_test_coherentes():
    """
    Crée un ensemble de notes de test avec une cohérence >= 95%
    
    Returns:
        Dict[str, pd.DataFrame]: Notes de test cohérentes
    """
    logger.info("Création des notes de test cohérentes...")
    
    # Note 3A - Immobilisations Incorporelles
    df_3a = pd.DataFrame({
        'libelle': ['Frais R&D', 'Brevets', 'Logiciels', 'Autres', 'TOTAL'],
        'brut_ouverture': [1000000, 500000, 300000, 200000, 2000000],
        'brut_cloture_n1': [1000000, 500000, 300000, 200000, 2000000],  # Pour continuité
        'augmentations': [200000, 100000, 50000, 30000, 380000],
        'diminutions': [50000, 0, 0, 10000, 60000],
        'brut_cloture': [1150000, 600000, 350000, 220000, 2320000],
        'amort_ouverture': [200000, 100000, 60000, 40000, 400000],
        'dotations': [100000, 50000, 30000, 20000, 200000],
        'reprises': [10000, 0, 0, 5000, 15000],
        'amort_cloture': [290000, 150000, 90000, 55000, 585000],
        'vnc_ouverture': [800000, 400000, 240000, 160000, 1600000],
        'vnc_cloture': [860000, 450000, 260000, 165000, 1735000]
    })
    
    # Note 3B - Immobilisations Corporelles
    df_3b = pd.DataFrame({
        'libelle': ['Terrains', 'Bâtiments', 'Matériel', 'Mobilier', 'TOTAL'],
        'brut_ouverture': [2000000, 3000000, 1500000, 500000, 7000000],
        'brut_cloture_n1': [2000000, 3000000, 1500000, 500000, 7000000],
        'augmentations': [0, 500000, 300000, 100000, 900000],
        'diminutions': [0, 0, 100000, 0, 100000],
        'brut_cloture': [2000000, 3500000, 1700000, 600000, 7800000],
        'amort_ouverture': [0, 600000, 450000, 150000, 1200000],
        'dotations': [0, 150000, 180000, 60000, 390000],
        'reprises': [0, 0, 30000, 0, 30000],
        'amort_cloture': [0, 750000, 600000, 210000, 1560000],
        'vnc_ouverture': [2000000, 2400000, 1050000, 350000, 5800000],
        'vnc_cloture': [2000000, 2750000, 1100000, 390000, 6240000]
    })
    
    # Note 3C - Immobilisations Financières
    df_3c = pd.DataFrame({
        'libelle': ['Titres de participation', 'Prêts', 'TOTAL'],
        'brut_ouverture': [1500000, 500000, 2000000],
        'brut_cloture_n1': [1500000, 500000, 2000000],
        'augmentations': [300000, 100000, 400000],
        'diminutions': [0, 50000, 50000],
        'brut_cloture': [1800000, 550000, 2350000],
        'amort_ouverture': [0, 0, 0],
        'dotations': [0, 0, 0],
        'reprises': [0, 0, 0],
        'amort_cloture': [0, 0, 0],
        'vnc_ouverture': [1500000, 500000, 2000000],
        'vnc_cloture': [1800000, 550000, 2350000]
    })
    
    # Note 3D - Charges Immobilisées
    df_3d = pd.DataFrame({
        'libelle': ['Frais d\'établissement', 'Charges à répartir', 'TOTAL'],
        'brut_ouverture': [300000, 200000, 500000],
        'brut_cloture_n1': [300000, 200000, 500000],
        'augmentations': [50000, 30000, 80000],
        'diminutions': [0, 0, 0],
        'brut_cloture': [350000, 230000, 580000],
        'amort_ouverture': [60000, 40000, 100000],
        'dotations': [35000, 23000, 58000],
        'reprises': [0, 0, 0],
        'amort_cloture': [95000, 63000, 158000],
        'vnc_ouverture': [240000, 160000, 400000],
        'vnc_cloture': [255000, 167000, 422000]
    })
    
    # Note 3E - Écarts de Conversion Actif
    df_3e = pd.DataFrame({
        'libelle': ['Écarts de conversion', 'TOTAL'],
        'brut_ouverture': [100000, 100000],
        'brut_cloture_n1': [100000, 100000],
        'augmentations': [20000, 20000],
        'diminutions': [10000, 10000],
        'brut_cloture': [110000, 110000],
        'amort_ouverture': [0, 0],
        'dotations': [0, 0],
        'reprises': [0, 0],
        'amort_cloture': [0, 0],
        'vnc_ouverture': [100000, 100000],
        'vnc_cloture': [110000, 110000]
    })
    
    # Note 26 - Dotations aux Amortissements (Compte de Résultat)
    df_26 = pd.DataFrame({
        'libelle': ['Dotations aux amortissements', 'TOTAL'],
        'montant': [648000, 648000]  # 200000 + 390000 + 0 + 58000 + 0 = 648000
    })
    
    notes = {
        'note_3a': df_3a,
        'note_3b': df_3b,
        'note_3c': df_3c,
        'note_3d': df_3d,
        'note_3e': df_3e,
        'note_26': df_26
    }
    
    logger.info(f"✓ {len(notes)} notes de test créées")
    return notes


def test_taux_coherence_superieur_95():
    """
    Test: Vérifier que le taux de cohérence inter-notes >= 95%
    
    Requirements: 10.5, 10.6
    """
    print("\n" + "="*80)
    print("TEST 1: Taux de cohérence inter-notes >= 95%")
    print("="*80)
    
    notes = creer_notes_test_coherentes()
    validator = CoherenceValidator(notes)
    
    # Effectuer toutes les validations
    validator.valider_total_immobilisations()
    validator.valider_dotations_amortissements()
    validator.valider_continuite_temporelle()
    
    # Calculer le taux de cohérence
    taux = validator.calculer_taux_coherence()
    
    print(f"\n📊 Taux de cohérence global: {taux:.1f}%")
    print(f"   Seuil requis: 95.0%")
    
    if taux >= 95.0:
        print(f"   ✓ TEST RÉUSSI: Taux de cohérence >= 95%")
        return True
    else:
        print(f"   ✗ TEST ÉCHOUÉ: Taux de cohérence < 95%")
        print(f"\n   Alertes émises:")
        for alerte in validator.alertes:
            print(f"   - [{alerte['niveau'].upper()}] {alerte['message']}")
        return False


def test_total_immobilisations():
    """
    Test: Vérifier que le total des immobilisations (Notes 3A-3E) correspond au bilan
    
    Requirements: 10.1, 10.2
    """
    print("\n" + "="*80)
    print("TEST 2: Total immobilisations correspond au bilan")
    print("="*80)
    
    notes = creer_notes_test_coherentes()
    validator = CoherenceValidator(notes)
    
    coherent, ecart = validator.valider_total_immobilisations()
    
    validation = validator.validations['total_immobilisations']
    
    print(f"\n🏢 Validation du total des immobilisations:")
    print(f"   Total Notes 3A-3E: {validation['total_notes']:,.2f}")
    print(f"   Total Bilan Actif: {validation['total_bilan']:,.2f}")
    print(f"   Écart absolu: {validation['ecart']:,.2f}")
    print(f"   Écart relatif: {validation['ecart_pct']:.2f}%")
    
    print(f"\n   Détail par note:")
    for note, montant in validation['details'].items():
        print(f"   - {note.upper()}: {montant:,.2f}")
    
    if coherent:
        print(f"\n   ✓ TEST RÉUSSI: Total immobilisations cohérent (écart < 1%)")
        return True
    else:
        print(f"\n   ✗ TEST ÉCHOUÉ: Total immobilisations incohérent (écart >= 1%)")
        return False


def test_dotations_amortissements():
    """
    Test: Vérifier que les dotations aux amortissements correspondent au compte de résultat
    
    Requirements: 10.1, 10.2
    """
    print("\n" + "="*80)
    print("TEST 3: Dotations amortissements correspondent au compte de résultat")
    print("="*80)
    
    notes = creer_notes_test_coherentes()
    validator = CoherenceValidator(notes)
    
    coherent, ecart = validator.valider_dotations_amortissements()
    
    validation = validator.validations['dotations_amortissements']
    
    print(f"\n📉 Validation des dotations aux amortissements:")
    print(f"   Total Notes 3A-3E: {validation['total_notes']:,.2f}")
    print(f"   Compte de Résultat: {validation['total_compte_resultat']:,.2f}")
    print(f"   Écart absolu: {validation['ecart']:,.2f}")
    print(f"   Écart relatif: {validation['ecart_pct']:.2f}%")
    
    print(f"\n   Détail par note:")
    for note, montant in validation['details'].items():
        print(f"   - {note.upper()}: {montant:,.2f}")
    
    if coherent:
        print(f"\n   ✓ TEST RÉUSSI: Dotations cohérentes (écart < 1%)")
        return True
    else:
        print(f"\n   ✗ TEST ÉCHOUÉ: Dotations incohérentes (écart >= 1%)")
        return False


def test_continuite_temporelle():
    """
    Test: Vérifier la continuité temporelle (N-1 clôture = N ouverture)
    
    Requirements: 10.3
    """
    print("\n" + "="*80)
    print("TEST 4: Continuité temporelle (N-1 clôture = N ouverture)")
    print("="*80)
    
    notes = creer_notes_test_coherentes()
    validator = CoherenceValidator(notes)
    
    resultats = validator.valider_continuite_temporelle()
    
    print(f"\n📅 Validation de la continuité temporelle:")
    print(f"   Nombre de notes vérifiées: {len(resultats)}")
    
    notes_coherentes = sum(1 for coh, _ in resultats.values() if coh)
    taux_continuite = (notes_coherentes / len(resultats) * 100) if resultats else 0
    
    print(f"\n   Résultats par note:")
    for note, (coherent, ecart) in resultats.items():
        statut = "✓ Cohérent" if coherent else "✗ Incohérent"
        print(f"   - {note.upper()}: {statut} (écart: {ecart:,.2f})")
    
    print(f"\n   Taux de continuité: {taux_continuite:.1f}% ({notes_coherentes}/{len(resultats)} notes)")
    
    if taux_continuite >= 95.0:
        print(f"\n   ✓ TEST RÉUSSI: Continuité temporelle >= 95%")
        return True
    else:
        print(f"\n   ✗ TEST ÉCHOUÉ: Continuité temporelle < 95%")
        return False


def test_generation_rapport():
    """
    Test: Vérifier la génération du rapport HTML de cohérence
    
    Requirements: 10.7
    """
    print("\n" + "="*80)
    print("TEST 5: Génération du rapport HTML de cohérence")
    print("="*80)
    
    notes = creer_notes_test_coherentes()
    validator = CoherenceValidator(notes)
    
    # Effectuer toutes les validations
    validator.valider_total_immobilisations()
    validator.valider_dotations_amortissements()
    validator.valider_continuite_temporelle()
    
    # Générer le rapport
    html = validator.generer_rapport_coherence()
    
    # Vérifier que le rapport contient les éléments essentiels
    elements_requis = [
        'Rapport de Cohérence',
        'Taux de Cohérence Global',
        'Total des Immobilisations',
        'Dotations aux Amortissements',
        'Continuité Temporelle',
        'Date de validation'
    ]
    
    print(f"\n📄 Vérification du contenu du rapport:")
    tous_presents = True
    for element in elements_requis:
        present = element in html
        statut = "✓" if present else "✗"
        print(f"   {statut} {element}")
        if not present:
            tous_presents = False
    
    # Sauvegarder le rapport
    output_dir = Path(__file__).parent
    rapport_path = output_dir / "rapport_coherence_validation_30_4.html"
    
    with open(rapport_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n   📁 Rapport sauvegardé: {rapport_path}")
    print(f"   📏 Taille du rapport: {len(html):,} caractères")
    
    if tous_presents:
        print(f"\n   ✓ TEST RÉUSSI: Rapport HTML généré avec tous les éléments requis")
        return True
    else:
        print(f"\n   ✗ TEST ÉCHOUÉ: Éléments manquants dans le rapport")
        return False


def main():
    """
    Fonction principale pour exécuter tous les tests de validation de cohérence
    """
    print("\n" + "="*80)
    print("VALIDATION DE COHÉRENCE - TÂCHE 30.4")
    print("Calcul Automatique des Notes Annexes SYSCOHADA Révisé")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Exécuter tous les tests
    resultats = {
        'Test 1 - Taux cohérence >= 95%': test_taux_coherence_superieur_95(),
        'Test 2 - Total immobilisations': test_total_immobilisations(),
        'Test 3 - Dotations amortissements': test_dotations_amortissements(),
        'Test 4 - Continuité temporelle': test_continuite_temporelle(),
        'Test 5 - Génération rapport': test_generation_rapport()
    }
    
    # Résumé final
    print("\n" + "="*80)
    print("RÉSUMÉ DES TESTS")
    print("="*80)
    
    tests_reussis = sum(1 for reussi in resultats.values() if reussi)
    total_tests = len(resultats)
    taux_reussite = (tests_reussis / total_tests * 100)
    
    print(f"\n📊 Résultats:")
    for test_name, reussi in resultats.items():
        statut = "✓ RÉUSSI" if reussi else "✗ ÉCHOUÉ"
        print(f"   {statut} - {test_name}")
    
    print(f"\n   Total: {tests_reussis}/{total_tests} tests réussis ({taux_reussite:.0f}%)")
    
    if tests_reussis == total_tests:
        print("\n" + "="*80)
        print("✓ VALIDATION COMPLÈTE RÉUSSIE")
        print("="*80)
        print("\nTous les critères de la tâche 30.4 sont satisfaits:")
        print("  ✓ Taux de cohérence inter-notes >= 95%")
        print("  ✓ Total immobilisations correspond au bilan")
        print("  ✓ Dotations amortissements correspondent au compte de résultat")
        print("  ✓ Continuité temporelle vérifiée (N-1 clôture = N ouverture)")
        print("  ✓ Rapport HTML de cohérence généré")
        return 0
    else:
        print("\n" + "="*80)
        print("✗ VALIDATION INCOMPLÈTE")
        print("="*80)
        print(f"\n{total_tests - tests_reussis} test(s) ont échoué.")
        print("Veuillez corriger les problèmes identifiés.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
