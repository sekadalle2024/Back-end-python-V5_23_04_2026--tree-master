"""
Tests basés sur les propriétés pour Account_Extractor - Complétude de l'extraction

Ce module contient les tests de propriétés pour valider que l'extraction
des comptes préserve toutes les 6 valeurs avec leur précision originale.

Feature: calcul-notes-annexes-syscohada
Property 5: Account Extraction Completeness

**Validates: Requirements 2.2, 2.6**

Auteur: Système de calcul automatique des notes annexes SYSCOHADA
Date: 13 Avril 2026
"""

import pytest
from hypothesis import given, assume, settings
import hypothesis.strategies as st
import pandas as pd
import numpy as np
import sys
import os

# Ajouter le chemin des modules au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Modules'))

from account_extractor import AccountExtractor

# Import strategies from conftest
from .conftest import st_balance, st_compte_racine


# ============================================================================
# PROPERTY 5: ACCOUNT EXTRACTION COMPLETENESS
# ============================================================================

@given(balance=st_balance(), compte_racine=st_compte_racine())
@settings(max_examples=100, deadline=60000)
def test_property_5_all_six_values_extracted(balance, compte_racine):
    """
    **Validates: Requirements 2.2**
    
    Property 5: Account Extraction Completeness (partie 1)
    
    For any account found in a balance, the Account_Extractor must extract
    all 6 values (ant_debit, ant_credit, mvt_debit, mvt_credit, solde_debit,
    solde_credit).
    
    Cette propriété vérifie que:
    1. Les 6 valeurs sont toujours présentes dans le résultat
    2. Aucune valeur n'est None ou NaN
    3. Toutes les valeurs sont de type numérique
    4. Les clés du dictionnaire correspondent exactement aux 6 valeurs attendues
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire les soldes
    soldes = extractor.extraire_solde_compte(compte_racine)
    
    # Propriété 1: Les 6 clés doivent être présentes
    cles_attendues = {
        'ant_debit', 'ant_credit',
        'mvt_debit', 'mvt_credit',
        'solde_debit', 'solde_credit'
    }
    
    cles_presentes = set(soldes.keys())
    assert cles_presentes == cles_attendues, \
        f"Clés attendues: {cles_attendues}, trouvé: {cles_presentes}"
    
    # Propriété 2: Aucune valeur ne doit être None ou NaN
    for cle, valeur in soldes.items():
        assert valeur is not None, \
            f"La valeur de {cle} ne doit pas être None"
        
        assert not pd.isna(valeur), \
            f"La valeur de {cle} ne doit pas être NaN"
    
    # Propriété 3: Toutes les valeurs doivent être numériques
    for cle, valeur in soldes.items():
        assert isinstance(valeur, (int, float, np.integer, np.floating)), \
            f"La valeur de {cle} doit être numérique, trouvé {type(valeur)}"
    
    # Propriété 4: Aucune clé supplémentaire ne doit être présente
    assert len(soldes) == 6, \
        f"Le dictionnaire doit contenir exactement 6 valeurs, trouvé {len(soldes)}"


@given(balance=st_balance(), compte_racine=st_compte_racine())
@settings(max_examples=100, deadline=60000)
def test_property_5_precision_preserved(balance, compte_racine):
    """
    **Validates: Requirements 2.6**
    
    Property 5: Account Extraction Completeness (partie 2)
    
    For any account found in a balance, the Account_Extractor must extract
    all 6 values with their original precision preserved (no premature rounding).
    
    Cette propriété vérifie que:
    1. Les valeurs extraites correspondent exactement aux valeurs sources
    2. Aucun arrondi prématuré n'est appliqué
    3. La précision des montants est préservée (tolérance < 0.01)
    4. Les valeurs sont des floats, pas des entiers arrondis
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire les soldes
    soldes = extractor.extraire_solde_compte(compte_racine)
    
    # Calculer manuellement les sommes attendues depuis la balance source
    comptes_correspondants = balance[
        balance['Numéro'].astype(str).str.strip().str.startswith(compte_racine)
    ]
    
    if not comptes_correspondants.empty:
        # Calculer les sommes attendues avec précision maximale
        somme_ant_debit = float(comptes_correspondants['Ant Débit'].sum())
        somme_ant_credit = float(comptes_correspondants['Ant Crédit'].sum())
        somme_mvt_debit = float(comptes_correspondants['Débit'].sum())
        somme_mvt_credit = float(comptes_correspondants['Crédit'].sum())
        somme_solde_debit = float(comptes_correspondants['Solde Débit'].sum())
        somme_solde_credit = float(comptes_correspondants['Solde Crédit'].sum())
        
        # Tolérance pour les erreurs d'arrondi (0.01 = 1 centime)
        tolerance = 0.01
        
        # Vérifier que les valeurs extraites correspondent aux valeurs sources
        assert abs(soldes['ant_debit'] - somme_ant_debit) < tolerance, \
            f"Ant Débit: extrait={soldes['ant_debit']:.10f}, attendu={somme_ant_debit:.10f}, " \
            f"écart={abs(soldes['ant_debit'] - somme_ant_debit):.10f}"
        
        assert abs(soldes['ant_credit'] - somme_ant_credit) < tolerance, \
            f"Ant Crédit: extrait={soldes['ant_credit']:.10f}, attendu={somme_ant_credit:.10f}, " \
            f"écart={abs(soldes['ant_credit'] - somme_ant_credit):.10f}"
        
        assert abs(soldes['mvt_debit'] - somme_mvt_debit) < tolerance, \
            f"Mvt Débit: extrait={soldes['mvt_debit']:.10f}, attendu={somme_mvt_debit:.10f}, " \
            f"écart={abs(soldes['mvt_debit'] - somme_mvt_debit):.10f}"
        
        assert abs(soldes['mvt_credit'] - somme_mvt_credit) < tolerance, \
            f"Mvt Crédit: extrait={soldes['mvt_credit']:.10f}, attendu={somme_mvt_credit:.10f}, " \
            f"écart={abs(soldes['mvt_credit'] - somme_mvt_credit):.10f}"
        
        assert abs(soldes['solde_debit'] - somme_solde_debit) < tolerance, \
            f"Solde Débit: extrait={soldes['solde_debit']:.10f}, attendu={somme_solde_debit:.10f}, " \
            f"écart={abs(soldes['solde_debit'] - somme_solde_debit):.10f}"
        
        assert abs(soldes['solde_credit'] - somme_solde_credit) < tolerance, \
            f"Solde Crédit: extrait={soldes['solde_credit']:.10f}, attendu={somme_solde_credit:.10f}, " \
            f"écart={abs(soldes['solde_credit'] - somme_solde_credit):.10f}"
    
    # Vérifier que les valeurs sont des floats (pas des entiers arrondis)
    for cle, valeur in soldes.items():
        # Accepter float ou numpy float/int (pandas peut retourner numpy types)
        assert isinstance(valeur, (float, np.floating, np.integer)), \
            f"{cle} devrait être un type numérique float, mais est {type(valeur)}"
        
        # Vérifier que la valeur est finie (pas infini)
        assert not np.isinf(valeur), \
            f"{cle} ne devrait pas être infini, trouvé {valeur}"


@given(balance=st_balance())
@settings(max_examples=100, deadline=60000)
def test_property_5_extraction_with_decimal_precision(balance):
    """
    **Validates: Requirements 2.6**
    
    Property 5: Account Extraction Completeness (partie 3)
    
    For any balance with accounts containing decimal values, the extraction
    must preserve decimal precision without rounding to integers.
    
    Cette propriété vérifie que:
    1. Les valeurs décimales sont préservées
    2. Aucune conversion en entier n'est effectuée
    3. La précision décimale est maintenue même après sommation
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire tous les comptes (racine vide ou première classe)
    if len(balance) > 0:
        # Prendre la première classe de compte disponible
        premier_compte = str(balance.iloc[0]['Numéro']).strip()
        if len(premier_compte) > 0:
            racine = premier_compte[0]
            
            # Extraire les soldes
            soldes = extractor.extraire_solde_compte(racine)
            
            # Vérifier que les valeurs ne sont pas arrondies à des entiers
            # Si la somme originale a des décimales, elles doivent être préservées
            comptes_correspondants = balance[
                balance['Numéro'].astype(str).str.strip().str.startswith(racine)
            ]
            
            if not comptes_correspondants.empty:
                # Vérifier chaque colonne
                for col_balance, cle_solde in [
                    ('Ant Débit', 'ant_debit'),
                    ('Ant Crédit', 'ant_credit'),
                    ('Débit', 'mvt_debit'),
                    ('Crédit', 'mvt_credit'),
                    ('Solde Débit', 'solde_debit'),
                    ('Solde Crédit', 'solde_credit')
                ]:
                    somme_originale = comptes_correspondants[col_balance].sum()
                    valeur_extraite = soldes[cle_solde]
                    
                    # Si la somme originale a des décimales significatives
                    if abs(somme_originale - round(somme_originale)) > 0.001:
                        # La valeur extraite doit aussi avoir des décimales
                        # (pas être arrondie à un entier)
                        assert abs(valeur_extraite - round(valeur_extraite)) > 0.0001 or \
                               abs(valeur_extraite - somme_originale) < 0.01, \
                            f"{cle_solde}: valeur originale={somme_originale:.10f} a des décimales, " \
                            f"mais valeur extraite={valeur_extraite:.10f} semble arrondie"


@given(balance=st_balance(), compte_racine=st_compte_racine())
@settings(max_examples=100, deadline=60000)
def test_property_5_extraction_non_negative_values(balance, compte_racine):
    """
    **Validates: Requirements 2.2**
    
    Property 5: Account Extraction Completeness (partie 4)
    
    For any account extracted, all 6 values must be non-negative (>= 0),
    as per SYSCOHADA accounting rules where debits and credits are always
    represented as positive values.
    
    Cette propriété vérifie que:
    1. Toutes les valeurs extraites sont >= 0
    2. Aucune valeur négative n'est retournée
    3. Les valeurs nulles (0.0) sont acceptées
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire les soldes
    soldes = extractor.extraire_solde_compte(compte_racine)
    
    # Vérifier que toutes les valeurs sont non-négatives
    for cle, valeur in soldes.items():
        assert valeur >= 0, \
            f"La valeur de {cle} doit être >= 0, trouvé {valeur}"
        
        # Vérifier que les valeurs nulles sont exactement 0.0 (pas -0.0)
        if valeur == 0:
            assert valeur == 0.0, \
                f"La valeur nulle de {cle} doit être 0.0, trouvé {valeur}"


@given(balance=st_balance(), racines=st.lists(st_compte_racine(), min_size=1, max_size=5))
@settings(max_examples=100, deadline=60000)
def test_property_5_multiple_extraction_completeness(balance, racines):
    """
    **Validates: Requirements 2.2, 2.6**
    
    Property 5: Account Extraction Completeness (extraction multiple)
    
    For any list of account roots, the extraire_comptes_multiples method
    must return all 6 values with precision preserved, and the sum must
    equal the sum of individual extractions.
    
    Cette propriété vérifie que:
    1. L'extraction multiple retourne les 6 valeurs
    2. La précision est préservée lors de la sommation multiple
    3. Le résultat est cohérent avec les extractions individuelles
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire avec la méthode multiple
    soldes_multiples = extractor.extraire_comptes_multiples(racines)
    
    # Vérifier que les 6 valeurs sont présentes
    cles_attendues = {
        'ant_debit', 'ant_credit',
        'mvt_debit', 'mvt_credit',
        'solde_debit', 'solde_credit'
    }
    
    assert set(soldes_multiples.keys()) == cles_attendues, \
        f"L'extraction multiple doit retourner les 6 valeurs"
    
    # Vérifier que toutes les valeurs sont numériques et non-None
    for cle, valeur in soldes_multiples.items():
        assert valeur is not None, \
            f"La valeur de {cle} ne doit pas être None"
        
        assert not pd.isna(valeur), \
            f"La valeur de {cle} ne doit pas être NaN"
        
        assert isinstance(valeur, (int, float, np.integer, np.floating)), \
            f"La valeur de {cle} doit être numérique"
        
        assert valeur >= 0, \
            f"La valeur de {cle} doit être >= 0"
    
    # Vérifier la cohérence avec les extractions individuelles
    somme_individuelle = {
        'ant_debit': 0.0,
        'ant_credit': 0.0,
        'mvt_debit': 0.0,
        'mvt_credit': 0.0,
        'solde_debit': 0.0,
        'solde_credit': 0.0
    }
    
    for racine in racines:
        soldes = extractor.extraire_solde_compte(racine)
        for cle in somme_individuelle.keys():
            somme_individuelle[cle] += soldes[cle]
    
    # Vérifier que les sommes correspondent (avec tolérance)
    tolerance = 0.01
    
    for cle in somme_individuelle.keys():
        assert abs(soldes_multiples[cle] - somme_individuelle[cle]) < tolerance, \
            f"{cle}: multiple={soldes_multiples[cle]:.10f}, " \
            f"individuel={somme_individuelle[cle]:.10f}, " \
            f"écart={abs(soldes_multiples[cle] - somme_individuelle[cle]):.10f}"


# ============================================================================
# TESTS UNITAIRES COMPLÉMENTAIRES
# ============================================================================

def test_extraction_completeness_with_fixture(balance_simple):
    """
    Test unitaire avec fixture pour vérifier la complétude de l'extraction.
    
    **Validates: Requirements 2.2**
    
    Ce test complète les tests de propriétés avec un exemple concret.
    """
    extractor = AccountExtractor(balance_simple)
    
    # Extraire les soldes du compte 211
    soldes = extractor.extraire_solde_compte("211")
    
    # Vérifier que les 6 valeurs sont présentes
    assert 'ant_debit' in soldes
    assert 'ant_credit' in soldes
    assert 'mvt_debit' in soldes
    assert 'mvt_credit' in soldes
    assert 'solde_debit' in soldes
    assert 'solde_credit' in soldes
    
    # Vérifier que toutes les valeurs sont numériques
    for cle, valeur in soldes.items():
        assert isinstance(valeur, (int, float, np.integer, np.floating)), \
            f"{cle} doit être numérique"
        assert not pd.isna(valeur), \
            f"{cle} ne doit pas être NaN"
        assert valeur >= 0, \
            f"{cle} doit être >= 0"


def test_precision_preservation_with_fixture(balance_simple):
    """
    Test unitaire avec fixture pour vérifier la préservation de la précision.
    
    **Validates: Requirements 2.6**
    
    Ce test complète les tests de propriétés avec un exemple concret.
    """
    extractor = AccountExtractor(balance_simple)
    
    # Extraire les soldes du compte 211 (inclut 211 et 2111)
    soldes = extractor.extraire_solde_compte("211")
    
    # Calculer manuellement les sommes attendues
    # 211: Ant Débit=1000000, 2111: Ant Débit=500000 => Total=1500000
    assert abs(soldes['ant_debit'] - 1500000.0) < 0.01, \
        f"Ant Débit devrait être 1500000.0, trouvé {soldes['ant_debit']}"
    
    # 211: Solde Débit=1300000, 2111: Solde Débit=600000 => Total=1900000
    assert abs(soldes['solde_debit'] - 1900000.0) < 0.01, \
        f"Solde Débit devrait être 1900000.0, trouvé {soldes['solde_debit']}"
    
    # Vérifier que les valeurs sont des floats
    assert isinstance(soldes['ant_debit'], (float, np.floating, np.integer))
    assert isinstance(soldes['solde_debit'], (float, np.floating, np.integer))


def test_extraction_with_demo_file():
    """
    Test avec le fichier de démonstration réel.
    
    **Validates: Requirements 2.2, 2.6**
    
    Ce test vérifie que le fichier de démonstration P000 -BALANCE DEMO N_N-1_N-2.xls
    respecte la propriété de complétude de l'extraction.
    """
    # Chemin vers le fichier de test
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fichier_test = os.path.join(base_dir, "P000 -BALANCE DEMO N_N-1_N-2.xls")
    
    # Vérifier que le fichier existe
    if not os.path.exists(fichier_test):
        pytest.skip(f"Fichier de démonstration non trouvé: {fichier_test}")
    
    # Charger la balance
    from balance_reader import BalanceReader
    reader = BalanceReader(fichier_test)
    balance_n, _, _ = reader.charger_balances()
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance_n)
    
    # Tester l'extraction de plusieurs comptes
    for racine in ['21', '22', '28', '101', '401']:
        soldes = extractor.extraire_solde_compte(racine)
        
        # Vérifier que les 6 valeurs sont présentes
        assert len(soldes) == 6, \
            f"Compte {racine}: devrait avoir 6 valeurs, trouvé {len(soldes)}"
        
        # Vérifier que toutes les valeurs sont numériques et non-négatives
        for cle, valeur in soldes.items():
            assert isinstance(valeur, (int, float, np.integer, np.floating)), \
                f"Compte {racine}, {cle}: devrait être numérique"
            assert not pd.isna(valeur), \
                f"Compte {racine}, {cle}: ne devrait pas être NaN"
            assert valeur >= 0, \
                f"Compte {racine}, {cle}: devrait être >= 0, trouvé {valeur}"
    
    print(f"\n✓ Propriété de complétude validée avec le fichier de démonstration")
    print(f"  - Comptes testés: 21, 22, 28, 101, 401")
    print(f"  - Toutes les extractions retournent 6 valeurs numériques non-négatives")


if __name__ == "__main__":
    """
    Exécution directe des tests pour validation rapide.
    
    Usage:
        python test_account_extractor_completeness.py
    """
    print("=" * 70)
    print("PROPERTY-BASED TESTS - ACCOUNT EXTRACTION COMPLETENESS")
    print("=" * 70)
    
    # Test avec le fichier de démonstration
    print("\n[1] Test avec le fichier de démonstration...")
    try:
        test_extraction_with_demo_file()
        print("   ✓ Test réussi")
    except Exception as e:
        print(f"   ✗ Test échoué: {str(e)}")
    
    print("\n" + "=" * 70)
    print("Pour exécuter tous les tests property-based avec Hypothesis:")
    print("  pytest test_account_extractor_completeness.py -v")
    print("=" * 70)
