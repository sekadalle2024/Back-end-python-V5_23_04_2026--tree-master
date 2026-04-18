"""
Module de calcul des mouvements et soldes avec validation de cohérence.

Ce module calcule les soldes d'ouverture, augmentations, diminutions et soldes de clôture.
"""

import logging
from typing import Tuple, Dict
import pandas as pd

logger = logging.getLogger(__name__)


class MovementCalculator:
    """Calculateur de mouvements et soldes."""
    
    @staticmethod
    def calculer_solde_ouverture(solde_debit_n1: float, solde_credit_n1: float) -> float:
        """
        Calcule le solde d'ouverture: Solde Débit N-1 - Solde Crédit N-1.
        
        Args:
            solde_debit_n1: Solde débiteur N-1
            solde_credit_n1: Solde créditeur N-1
            
        Returns:
            Solde d'ouverture
        """
        return solde_debit_n1 - solde_credit_n1
    
    @staticmethod
    def calculer_augmentations(mvt_debit_n: float) -> float:
        """
        Calcule les augmentations: Mouvement Débit N.
        
        Args:
            mvt_debit_n: Mouvement débiteur N
            
        Returns:
            Augmentations
        """
        return mvt_debit_n
    
    @staticmethod
    def calculer_diminutions(mvt_credit_n: float) -> float:
        """
        Calcule les diminutions: Mouvement Crédit N.
        
        Args:
            mvt_credit_n: Mouvement créditeur N
            
        Returns:
            Diminutions
        """
        return mvt_credit_n
    
    @staticmethod
    def calculer_solde_cloture(solde_debit_n: float, solde_credit_n: float) -> float:
        """
        Calcule le solde de clôture: Solde Débit N - Solde Crédit N.
        
        Args:
            solde_debit_n: Solde débiteur N
            solde_credit_n: Solde créditeur N
            
        Returns:
            Solde de clôture
        """
        return solde_debit_n - solde_credit_n
    
    @staticmethod
    def verifier_coherence(solde_ouverture: float, augmentations: float,
                          diminutions: float, solde_cloture: float,
                          tolerance: float = 0.01) -> Tuple[bool, float]:
        """
        Vérifie: Solde_Cloture = Solde_Ouverture + Augmentations - Diminutions.
        
        Args:
            solde_ouverture: Solde d'ouverture
            augmentations: Augmentations
            diminutions: Diminutions
            solde_cloture: Solde de clôture
            tolerance: Tolérance d'écart acceptable
            
        Returns:
            Tuple (coherent: bool, ecart: float)
        """
        solde_calcule = solde_ouverture + augmentations - diminutions
        ecart = abs(solde_cloture - solde_calcule)
        coherent = ecart <= tolerance
        
        if not coherent:
            logger.warning(
                f"Incohérence détectée: "
                f"Solde ouverture={solde_ouverture:.2f}, "
                f"Augmentations={augmentations:.2f}, "
                f"Diminutions={diminutions:.2f}, "
                f"Solde clôture attendu={solde_calcule:.2f}, "
                f"Solde clôture réel={solde_cloture:.2f}, "
                f"Écart={ecart:.2f}"
            )
        
        return coherent, ecart
    
    @staticmethod
    def calculer_mouvements_amortissement(compte_amort: str, 
                                         balance_n: pd.DataFrame) -> Dict[str, float]:
        """
        Calcule les mouvements d'amortissement (signes inversés).
        
        Pour les comptes d'amortissement (28X, 29X):
        - Dotations = Mouvements crédit (augmentation de l'amortissement)
        - Reprises = Mouvements débit (diminution de l'amortissement)
        
        Args:
            compte_amort: Racine du compte d'amortissement
            balance_n: Balance de l'exercice N
            
        Returns:
            Dict avec clés: dotations (crédit), reprises (débit)
        """
        from .account_extractor import AccountExtractor
        
        extractor = AccountExtractor(balance_n)
        soldes = extractor.extraire_solde_compte(compte_amort)
        
        return {
            'dotations': soldes['mvt_credit'],  # Crédit = augmentation amortissement
            'reprises': soldes['mvt_debit']     # Débit = diminution amortissement
        }
