"""
Module de calcul des valeurs nettes comptables (VNC).

Ce module calcule les VNC en soustrayant les amortissements des valeurs brutes.
"""

import logging
from typing import Tuple, List
import pandas as pd

logger = logging.getLogger(__name__)


class VNCCalculator:
    """Calculateur de valeurs nettes comptables."""
    
    @staticmethod
    def calculer_vnc_ouverture(brut_ouverture: float, amort_ouverture: float) -> float:
        """
        Calcule VNC Ouverture = Brut Ouverture - Amortissement Ouverture.
        
        Args:
            brut_ouverture: Valeur brute d'ouverture
            amort_ouverture: Amortissement d'ouverture
            
        Returns:
            VNC d'ouverture
        """
        return brut_ouverture - amort_ouverture
    
    @staticmethod
    def calculer_vnc_cloture(brut_cloture: float, amort_cloture: float) -> float:
        """
        Calcule VNC Clôture = Brut Clôture - Amortissement Clôture.
        
        Args:
            brut_cloture: Valeur brute de clôture
            amort_cloture: Amortissement de clôture
            
        Returns:
            VNC de clôture
        """
        return brut_cloture - amort_cloture
    
    @staticmethod
    def extraire_dotations(comptes_amort: List[str], balance_n: pd.DataFrame) -> float:
        """
        Extrait les dotations aux amortissements (mouvements crédit 28X).
        
        Args:
            comptes_amort: Liste des racines de comptes d'amortissement
            balance_n: Balance de l'exercice N
            
        Returns:
            Total des dotations
        """
        from .account_extractor import AccountExtractor
        
        extractor = AccountExtractor(balance_n)
        soldes = extractor.extraire_comptes_multiples(comptes_amort)
        
        dotations = soldes['mvt_credit']
        logger.debug(f"Dotations extraites: {dotations:.2f}")
        
        return dotations
    
    @staticmethod
    def extraire_reprises(comptes_amort: List[str], balance_n: pd.DataFrame) -> float:
        """
        Extrait les reprises d'amortissements (mouvements débit 28X).
        
        Args:
            comptes_amort: Liste des racines de comptes d'amortissement
            balance_n: Balance de l'exercice N
            
        Returns:
            Total des reprises
        """
        from .account_extractor import AccountExtractor
        
        extractor = AccountExtractor(balance_n)
        soldes = extractor.extraire_comptes_multiples(comptes_amort)
        
        reprises = soldes['mvt_debit']
        logger.debug(f"Reprises extraites: {reprises:.2f}")
        
        return reprises
    
    @staticmethod
    def valider_vnc(vnc: float, libelle: str = "") -> Tuple[bool, str]:
        """
        Valide que VNC >= 0.
        
        Args:
            vnc: Valeur nette comptable
            libelle: Libellé de la ligne (pour le message)
            
        Returns:
            Tuple (valide: bool, message_avertissement: str)
        """
        if vnc < 0:
            message = f"VNC négative détectée pour '{libelle}': {vnc:.2f}"
            logger.warning(message)
            return False, message
        
        return True, ""
