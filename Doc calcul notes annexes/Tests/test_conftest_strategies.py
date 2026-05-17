"""
Test rapide pour vérifier que les stratégies Hypothesis fonctionnent correctement.
"""

from hypothesis import given
import hypothesis.strategies as st
import pandas as pd
import sys
import os

# Ajouter le répertoire Tests au path pour importer conftest
sys.path.insert(0, os.path.dirname(__file__))

from conftest import st_balance, st_compte_racine, st_montant, st_ligne_note_annexe


@given(st_balance())
def test_st_balance_generates_valid_dataframe(balance):
    """Vérifie que st_balance génère un DataFrame valide."""
    assert isinstance(balance, pd.DataFrame)
    assert len(balance) >= 10
    assert len(balance) <= 100
    assert 'Numéro' in balance.columns
    assert 'Intitulé' in balance.columns
    assert 'Ant Débit' in balance.columns
    assert 'Ant Crédit' in balance.columns
    assert 'Débit' in balance.columns
    assert 'Crédit' in balance.columns
    assert 'Solde Débit' in balance.columns
    assert 'Solde Crédit' in balance.columns


@given(st_compte_racine())
def test_st_compte_racine_generates_valid_root(racine):
    """Vérifie que st_compte_racine génère une racine valide."""
    assert isinstance(racine, str)
    assert len(racine) >= 2
    assert len(racine) <= 5
    assert racine[0] in '123456789'
    assert racine[1] in '0123456789'
    assert all(c in '0123456789' for c in racine)


@given(st_montant())
def test_st_montant_generates_valid_amount(montant):
    """Vérifie que st_montant génère un montant valide."""
    assert isinstance(montant, float)
    assert montant >= 0
    assert montant <= 100000000
    assert not pd.isna(montant)


@given(st_ligne_note_annexe())
def test_st_ligne_note_annexe_coherence(ligne):
    """Vérifie la cohérence des lignes de note annexe générées."""
    # Vérifier la formule du brut
    brut_calcule = ligne['brut_ouverture'] + ligne['augmentations'] - ligne['diminutions']
    assert abs(brut_calcule - ligne['brut_cloture']) < 0.01
    
    # Vérifier la formule des amortissements
    amort_calcule = ligne['amort_ouverture'] + ligne['dotations'] - ligne['reprises']
    assert abs(amort_calcule - ligne['amort_cloture']) < 0.01
    
    # Vérifier la formule de la VNC
    vnc_ouverture_calcule = ligne['brut_ouverture'] - ligne['amort_ouverture']
    vnc_cloture_calcule = ligne['brut_cloture'] - ligne['amort_cloture']
    assert abs(vnc_ouverture_calcule - ligne['vnc_ouverture']) < 0.01
    assert abs(vnc_cloture_calcule - ligne['vnc_cloture']) < 0.01


if __name__ == '__main__':
    print("✓ Test des stratégies Hypothesis")
    print("  - st_balance: Génère des balances valides")
    print("  - st_compte_racine: Génère des racines de compte SYSCOHADA")
    print("  - st_montant: Génère des montants comptables")
    print("  - st_ligne_note_annexe: Génère des lignes cohérentes")
    print("\nExécutez: pytest test_conftest_strategies.py -v")
