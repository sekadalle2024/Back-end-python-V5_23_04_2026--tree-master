"""
Configuration pytest et stratégies Hypothesis pour les tests.

Ce fichier contient les fixtures pytest et les stratégies de génération
de données pour les tests basés sur les propriétés.
"""

import pytest
import hypothesis.strategies as st
from hypothesis import assume
import pandas as pd
import os


# ============================================================================
# FIXTURES PYTEST
# ============================================================================

@pytest.fixture
def fichier_balance_demo():
    """Retourne le chemin vers le fichier de balance de démonstration."""
    return os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'P000 -BALANCE DEMO N_N-1_N-2.xls'
    )


@pytest.fixture
def balance_simple():
    """Retourne une balance simple pour les tests."""
    return pd.DataFrame({
        'Numéro': ['211', '2111', '212', '2811', '2812'],
        'Intitulé': [
            'Frais de recherche',
            'Frais de recherche détail',
            'Brevets',
            'Amort frais recherche',
            'Amort brevets'
        ],
        'Ant Débit': [1000000.0, 500000.0, 800000.0, 0.0, 0.0],
        'Ant Crédit': [0.0, 0.0, 0.0, 200000.0, 150000.0],
        'Débit': [300000.0, 100000.0, 200000.0, 0.0, 0.0],
        'Crédit': [0.0, 0.0, 0.0, 100000.0, 80000.0],
        'Solde Débit': [1300000.0, 600000.0, 1000000.0, 0.0, 0.0],
        'Solde Crédit': [0.0, 0.0, 0.0, 300000.0, 230000.0]
    })


@pytest.fixture
def correspondances_test():
    """Retourne un dictionnaire de correspondances pour les tests."""
    return {
        'bilan_actif': {
            'Immobilisations incorporelles': {
                'brut': ['211', '212', '213'],
                'amort': ['2811', '2812', '2813']
            }
        }
    }


# ============================================================================
# STRATÉGIES HYPOTHESIS
# ============================================================================

@st.composite
def st_balance(draw):
    """
    Génère une balance comptable valide avec cohérence des soldes.
    
    Cette stratégie génère des balances avec:
    - 10 à 100 comptes
    - Numéros de compte valides (3 à 5 chiffres)
    - Soldes cohérents (Solde Clôture = Solde Ouverture + Mvt Débit - Mvt Crédit)
    """
    num_comptes = draw(st.integers(min_value=10, max_value=100))
    
    comptes = []
    for _ in range(num_comptes):
        # Générer un numéro de compte SYSCOHADA valide
        classe = draw(st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9']))
        sous_classe = draw(st.integers(min_value=0, max_value=9))
        detail = draw(st.text(alphabet='0123456789', min_size=0, max_size=3))
        numero = f"{classe}{sous_classe}{detail}"
        
        # Générer un intitulé
        intitule = draw(st.text(min_size=5, max_size=50))
        
        # Générer les soldes d'ouverture
        ant_debit = draw(st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False))
        ant_credit = draw(st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False))
        
        # Générer les mouvements
        mvt_debit = draw(st.floats(min_value=0, max_value=5000000, allow_nan=False, allow_infinity=False))
        mvt_credit = draw(st.floats(min_value=0, max_value=5000000, allow_nan=False, allow_infinity=False))
        
        # Calculer les soldes de clôture cohérents
        solde_ouverture = ant_debit - ant_credit
        solde_cloture = solde_ouverture + mvt_debit - mvt_credit
        
        solde_debit = max(0, solde_cloture)
        solde_credit = max(0, -solde_cloture)
        
        comptes.append({
            'Numéro': numero,
            'Intitulé': intitule,
            'Ant Débit': ant_debit,
            'Ant Crédit': ant_credit,
            'Débit': mvt_debit,
            'Crédit': mvt_credit,
            'Solde Débit': solde_debit,
            'Solde Crédit': solde_credit
        })
    
    return pd.DataFrame(comptes)


@st.composite
def st_compte_racine(draw):
    """
    Génère une racine de compte SYSCOHADA valide.
    
    Format: Classe (1-9) + Sous-classe (0-9) + optionnel détail (0-3 chiffres)
    """
    classe = draw(st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9']))
    sous_classe = draw(st.integers(min_value=0, max_value=9))
    detail = draw(st.text(alphabet='0123456789', min_size=0, max_size=2))
    return f"{classe}{sous_classe}{detail}"


@st.composite
def st_montant(draw):
    """
    Génère un montant comptable valide.
    
    Montants entre 0 et 100 millions, sans NaN ni infini.
    """
    return draw(st.floats(
        min_value=0,
        max_value=100000000,
        allow_nan=False,
        allow_infinity=False
    ))


@st.composite
def st_ligne_note_annexe(draw):
    """
    Génère une ligne de note annexe cohérente.
    
    Respecte les formules:
    - Brut Clôture = Brut Ouverture + Augmentations - Diminutions
    - VNC = Brut - Amortissement
    """
    libelle = draw(st.text(min_size=5, max_size=50))
    
    # Valeurs brutes
    brut_ouverture = draw(st_montant())
    augmentations = draw(st_montant())
    diminutions = draw(st.floats(min_value=0, max_value=augmentations + brut_ouverture))
    brut_cloture = brut_ouverture + augmentations - diminutions
    
    # Amortissements
    amort_ouverture = draw(st.floats(min_value=0, max_value=brut_ouverture))
    dotations = draw(st_montant())
    reprises = draw(st.floats(min_value=0, max_value=amort_ouverture + dotations))
    amort_cloture = amort_ouverture + dotations - reprises
    
    # VNC
    vnc_ouverture = brut_ouverture - amort_ouverture
    vnc_cloture = brut_cloture - amort_cloture
    
    return {
        'libelle': libelle,
        'brut_ouverture': brut_ouverture,
        'augmentations': augmentations,
        'diminutions': diminutions,
        'brut_cloture': brut_cloture,
        'amort_ouverture': amort_ouverture,
        'dotations': dotations,
        'reprises': reprises,
        'amort_cloture': amort_cloture,
        'vnc_ouverture': vnc_ouverture,
        'vnc_cloture': vnc_cloture
    }


# ============================================================================
# CONFIGURATION HYPOTHESIS
# ============================================================================

# Configuration globale pour tous les tests de propriétés
from hypothesis import settings

settings.register_profile("default", max_examples=100, deadline=60000)
settings.register_profile("ci", max_examples=200, deadline=120000)
settings.register_profile("dev", max_examples=50, deadline=30000)

# Activer le profil par défaut
settings.load_profile("default")
