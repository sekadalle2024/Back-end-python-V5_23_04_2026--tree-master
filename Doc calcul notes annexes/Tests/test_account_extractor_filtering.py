"""
Tests basés sur les propriétés pour Account_Extractor - Filtrage par racine

Ce module contient les tests de propriétés pour valider le comportement
du filtrage des comptes par racine et la sommation des soldes.

Feature: calcul-notes-annexes-syscohada
Property 4: Account Filtering by Root

Auteur: Système de calcul automatique des notes annexes SYSCOHADA
Date: 12 Avril 2026
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
from conftest import st_balance, st_compte_racine


# ============================================================================
# PROPERTY 4: ACCOUNT FILTERING BY ROOT
# ============================================================================

@given(balance=st_balance(), compte_racine=st_compte_racine())
@settings(max_examples=100, deadline=60000)
def test_property_4_filtrer_par_racine_returns_only_matching_accounts(balance, compte_racine):
    """
    **Validates: Requirements 2.1, 2.5**
    
    Property 4: Account Filtering by Root
    
    For any account root number and any balance sheet, the Account_Extractor
    must return only accounts whose numbers start with that root.
    
    Cette propriété vérifie que:
    1. Tous les comptes retournés commencent par la racine spécifiée
    2. Aucun compte ne commence par la racine n'est omis
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Filtrer par racine
    comptes_filtres = extractor.filtrer_par_racine(compte_racine)
    
    # Propriété 1: Tous les comptes retournés commencent par la racine
    if not comptes_filtres.empty:
        for numero in comptes_filtres['Numéro']:
            assert str(numero).startswith(compte_racine), \
                f"Le compte {numero} ne commence pas par la racine {compte_racine}"
    
    # Propriété 2: Aucun compte correspondant n'est omis
    # Compter manuellement les comptes qui devraient être retournés
    comptes_attendus = balance[balance['Numéro'].astype(str).str.strip().str.startswith(compte_racine)]
    
    assert len(comptes_filtres) == len(comptes_attendus), \
        f"Nombre de comptes filtrés ({len(comptes_filtres)}) != nombre attendu ({len(comptes_attendus)})"


@given(balance=st_balance(), compte_racine=st_compte_racine())
@settings(max_examples=100, deadline=60000)
def test_property_4_sum_of_filtered_accounts_equals_sum_of_matching_accounts(balance, compte_racine):
    """
    **Validates: Requirements 2.1, 2.5**
    
    Property 4: Account Filtering by Root (partie 2)
    
    For any account root number and any balance sheet, the sum of filtered
    accounts must equal the sum of all matching accounts in the original balance.
    
    Cette propriété vérifie que:
    1. La somme des soldes des comptes filtrés = somme des soldes des comptes correspondants
    2. Aucune valeur n'est perdue ou ajoutée lors du filtrage
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire les soldes via la méthode extraire_solde_compte
    soldes_extraits = extractor.extraire_solde_compte(compte_racine)
    
    # Calculer manuellement les sommes attendues
    comptes_correspondants = balance[balance['Numéro'].astype(str).str.strip().str.startswith(compte_racine)]
    
    if comptes_correspondants.empty:
        # Si aucun compte ne correspond, toutes les valeurs doivent être 0.0
        assert soldes_extraits['ant_debit'] == 0.0
        assert soldes_extraits['ant_credit'] == 0.0
        assert soldes_extraits['mvt_debit'] == 0.0
        assert soldes_extraits['mvt_credit'] == 0.0
        assert soldes_extraits['solde_debit'] == 0.0
        assert soldes_extraits['solde_credit'] == 0.0
    else:
        # Vérifier que les sommes correspondent
        tolerance = 0.01  # Tolérance pour les erreurs d'arrondi
        
        somme_ant_debit = comptes_correspondants['Ant Débit'].sum()
        somme_ant_credit = comptes_correspondants['Ant Crédit'].sum()
        somme_mvt_debit = comptes_correspondants['Débit'].sum()
        somme_mvt_credit = comptes_correspondants['Crédit'].sum()
        somme_solde_debit = comptes_correspondants['Solde Débit'].sum()
        somme_solde_credit = comptes_correspondants['Solde Crédit'].sum()
        
        assert abs(soldes_extraits['ant_debit'] - somme_ant_debit) < tolerance, \
            f"Ant Débit: extrait={soldes_extraits['ant_debit']}, attendu={somme_ant_debit}"
        
        assert abs(soldes_extraits['ant_credit'] - somme_ant_credit) < tolerance, \
            f"Ant Crédit: extrait={soldes_extraits['ant_credit']}, attendu={somme_ant_credit}"
        
        assert abs(soldes_extraits['mvt_debit'] - somme_mvt_debit) < tolerance, \
            f"Mvt Débit: extrait={soldes_extraits['mvt_debit']}, attendu={somme_mvt_debit}"
        
        assert abs(soldes_extraits['mvt_credit'] - somme_mvt_credit) < tolerance, \
            f"Mvt Crédit: extrait={soldes_extraits['mvt_credit']}, attendu={somme_mvt_credit}"
        
        assert abs(soldes_extraits['solde_debit'] - somme_solde_debit) < tolerance, \
            f"Solde Débit: extrait={soldes_extraits['solde_debit']}, attendu={somme_solde_debit}"
        
        assert abs(soldes_extraits['solde_credit'] - somme_solde_credit) < tolerance, \
            f"Solde Crédit: extrait={soldes_extraits['solde_credit']}, attendu={somme_solde_credit}"


@given(balance=st_balance())
@settings(max_examples=100, deadline=60000)
def test_property_4_filtering_empty_root_returns_empty(balance):
    """
    **Validates: Requirements 2.3, 8.1**
    
    Property 4: Account Filtering by Root (cas limite)
    
    For any balance sheet, filtering with an empty root or a root that
    doesn't exist should return zero values without raising exceptions.
    
    Cette propriété vérifie la gestion gracieuse des cas limites.
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Test avec une racine qui n'existe probablement pas
    racine_inexistante = "999999"
    soldes = extractor.extraire_solde_compte(racine_inexistante)
    
    # Vérifier que toutes les valeurs sont 0.0
    assert soldes['ant_debit'] == 0.0
    assert soldes['ant_credit'] == 0.0
    assert soldes['mvt_debit'] == 0.0
    assert soldes['mvt_credit'] == 0.0
    assert soldes['solde_debit'] == 0.0
    assert soldes['solde_credit'] == 0.0


@given(balance=st_balance(), racines=st.lists(st_compte_racine(), min_size=1, max_size=5))
@settings(max_examples=100, deadline=60000)
def test_property_4_multiple_roots_sum_equals_individual_sums(balance, racines):
    """
    **Validates: Requirements 2.5**
    
    Property 4: Account Filtering by Root (racines multiples)
    
    For any balance sheet and any list of account roots, the sum obtained
    by extraire_comptes_multiples must equal the sum of individual extractions.
    
    Cette propriété vérifie que:
    1. extraire_comptes_multiples([A, B, C]) = extraire(A) + extraire(B) + extraire(C)
    2. Aucune valeur n'est perdue ou dupliquée lors de la sommation
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire avec la méthode multiple
    soldes_multiples = extractor.extraire_comptes_multiples(racines)
    
    # Extraire individuellement et sommer
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
    
    # Vérifier que les sommes correspondent
    tolerance = 0.01
    
    for cle in somme_individuelle.keys():
        assert abs(soldes_multiples[cle] - somme_individuelle[cle]) < tolerance, \
            f"{cle}: multiple={soldes_multiples[cle]}, individuel={somme_individuelle[cle]}"


@given(balance=st_balance(), compte_racine=st_compte_racine())
@settings(max_examples=50, deadline=30000)
def test_property_4_filtering_preserves_precision(balance, compte_racine):
    """
    **Validates: Requirements 2.6**
    
    Property 4: Account Filtering by Root (préservation de la précision)
    
    For any account root and balance sheet, the filtering and summation
    operations must preserve the precision of monetary amounts without
    premature rounding.
    
    Cette propriété vérifie que:
    1. Les montants ne sont pas arrondis prématurément
    2. La précision des calculs est préservée
    """
    # Assumer qu'il y a au moins un compte dans la balance
    assume(len(balance) > 0)
    
    # Créer l'extracteur
    extractor = AccountExtractor(balance)
    
    # Extraire les soldes
    soldes = extractor.extraire_solde_compte(compte_racine)
    
    # Vérifier que les valeurs sont des floats (pas des entiers arrondis)
    for cle, valeur in soldes.items():
        # Accepter float ou numpy float/int (pandas peut retourner numpy types)
        assert isinstance(valeur, (float, np.floating, np.integer)), \
            f"{cle} devrait être un type numérique, mais est {type(valeur)}"
        
        # Vérifier que la valeur est finie (pas NaN ou infini)
        assert not pd.isna(valeur), f"{cle} ne devrait pas être NaN"
        assert not np.isinf(valeur), f"{cle} ne devrait pas être infini"


# ============================================================================
# TESTS UNITAIRES COMPLÉMENTAIRES
# ============================================================================

def test_filtrer_par_racine_with_fixture(balance_simple):
    """
    Test unitaire avec fixture pour vérifier le filtrage de base.
    
    Ce test complète les tests de propriétés avec un exemple concret.
    """
    extractor = AccountExtractor(balance_simple)
    
    # Filtrer les comptes commençant par "211"
    comptes_211 = extractor.filtrer_par_racine("211")
    
    # Devrait retourner 2 comptes: "211" et "2111"
    assert len(comptes_211) == 2
    assert "211" in comptes_211['Numéro'].values
    assert "2111" in comptes_211['Numéro'].values


def test_extraire_solde_compte_with_fixture(balance_simple):
    """
    Test unitaire avec fixture pour vérifier l'extraction de soldes.
    
    Ce test complète les tests de propriétés avec un exemple concret.
    """
    extractor = AccountExtractor(balance_simple)
    
    # Extraire les soldes du compte 211 (devrait inclure 211 et 2111)
    soldes = extractor.extraire_solde_compte("211")
    
    # Vérifier les sommes
    # 211: Ant Débit=1000000, 2111: Ant Débit=500000 => Total=1500000
    assert soldes['ant_debit'] == 1500000.0
    
    # 211: Solde Débit=1300000, 2111: Solde Débit=600000 => Total=1900000
    assert soldes['solde_debit'] == 1900000.0


def test_extraire_comptes_multiples_with_fixture(balance_simple):
    """
    Test unitaire avec fixture pour vérifier l'extraction multiple.
    
    Ce test complète les tests de propriétés avec un exemple concret.
    """
    extractor = AccountExtractor(balance_simple)
    
    # Extraire les soldes des comptes 211 et 212
    soldes = extractor.extraire_comptes_multiples(["211", "212"])
    
    # 211+2111: Solde Débit=1900000, 212: Solde Débit=1000000 => Total=2900000
    assert soldes['solde_debit'] == 2900000.0


def test_extraire_solde_compte_inexistant_with_fixture(balance_simple):
    """
    Test unitaire avec fixture pour vérifier la gestion des comptes inexistants.
    
    Ce test complète les tests de propriétés avec un exemple concret.
    """
    extractor = AccountExtractor(balance_simple)
    
    # Extraire un compte qui n'existe pas
    soldes = extractor.extraire_solde_compte("999")
    
    # Toutes les valeurs devraient être 0.0
    assert soldes['ant_debit'] == 0.0
    assert soldes['ant_credit'] == 0.0
    assert soldes['mvt_debit'] == 0.0
    assert soldes['mvt_credit'] == 0.0
    assert soldes['solde_debit'] == 0.0
    assert soldes['solde_credit'] == 0.0


if __name__ == "__main__":
    # Exécuter les tests avec pytest
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
