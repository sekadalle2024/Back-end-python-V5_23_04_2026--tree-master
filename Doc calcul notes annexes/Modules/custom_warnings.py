"""
Custom Warning Classes for SYSCOHADA Notes Annexes Calculation System

This module defines custom warning classes for different types of warnings
that can occur during the calculation of SYSCOHADA financial statement annexes.

All warnings are logged to calcul_notes_warnings.log via the logging infrastructure.

Requirements: 3.6, 4.7, 8.5, 8.6, Error Handling
"""

import warnings
import logging
from typing import Optional, Dict, Any
from datetime import datetime


# Configure warnings logger
warnings_logger = logging.getLogger('calcul_notes_warnings')


class CalculNotesWarning(UserWarning):
    """Base class for all calcul notes annexes warnings."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize warning with message and optional context.
        
        Args:
            message: Warning message
            context: Optional dictionary with additional context (note number, account, etc.)
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()
        
        # Log the warning
        self._log_warning()
    
    def _log_warning(self):
        """Log the warning to calcul_notes_warnings.log"""
        log_message = self._format_log_message()
        warnings_logger.warning(log_message)
    
    def _format_log_message(self) -> str:
        """Format warning message with context for logging"""
        parts = [f"[{self.__class__.__name__}] {self.message}"]
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        return " | ".join(parts)


class IncoherentBalanceWarning(CalculNotesWarning):
    """
    Warning for incoherent balance equations.
    
    Emitted when: Solde_Cloture ≠ Solde_Ouverture + Augmentations - Diminutions
    
    Requirements: 3.6, 8.5
    """
    
    def __init__(self, 
                 compte: str,
                 solde_ouverture: float,
                 augmentations: float,
                 diminutions: float,
                 solde_cloture: float,
                 ecart: float,
                 note_numero: Optional[str] = None):
        """
        Initialize incoherent balance warning.
        
        Args:
            compte: Account number or description
            solde_ouverture: Opening balance
            augmentations: Increases during period
            diminutions: Decreases during period
            solde_cloture: Closing balance
            ecart: Difference between expected and actual closing balance
            note_numero: Optional note number where warning occurred
        """
        message = (
            f"Balance incoherente pour compte '{compte}': "
            f"Solde cloture attendu = {solde_ouverture + augmentations - diminutions:.2f}, "
            f"Solde cloture reel = {solde_cloture:.2f}, "
            f"Ecart = {ecart:.2f}"
        )
        
        context = {
            'compte': compte,
            'solde_ouverture': solde_ouverture,
            'augmentations': augmentations,
            'diminutions': diminutions,
            'solde_cloture': solde_cloture,
            'ecart': ecart,
            'note_numero': note_numero
        }
        
        super().__init__(message, context)


class NegativeVNCWarning(CalculNotesWarning):
    """
    Warning for negative net book value (VNC).
    
    Emitted when: VNC = Brut - Amortissement < 0
    
    Requirements: 4.7, 8.5
    """
    
    def __init__(self,
                 libelle: str,
                 brut: float,
                 amortissement: float,
                 vnc: float,
                 note_numero: Optional[str] = None):
        """
        Initialize negative VNC warning.
        
        Args:
            libelle: Asset line description
            brut: Gross value
            amortissement: Accumulated depreciation
            vnc: Net book value (negative)
            note_numero: Optional note number where warning occurred
        """
        message = (
            f"VNC negative pour '{libelle}': "
            f"Brut = {brut:.2f}, "
            f"Amortissement = {amortissement:.2f}, "
            f"VNC = {vnc:.2f}"
        )
        
        context = {
            'libelle': libelle,
            'brut': brut,
            'amortissement': amortissement,
            'vnc': vnc,
            'note_numero': note_numero
        }
        
        super().__init__(message, context)


class AbnormalAccountBalanceWarning(CalculNotesWarning):
    """
    Warning for abnormal account balances.
    
    Emitted when: Account has both debit and credit balances simultaneously,
    or when balance sign is unexpected for account type.
    
    Requirements: 8.5, 8.6
    """
    
    def __init__(self,
                 compte: str,
                 solde_debit: float,
                 solde_credit: float,
                 raison: str,
                 note_numero: Optional[str] = None):
        """
        Initialize abnormal account balance warning.
        
        Args:
            compte: Account number
            solde_debit: Debit balance
            solde_credit: Credit balance
            raison: Reason why balance is considered abnormal
            note_numero: Optional note number where warning occurred
        """
        message = (
            f"Solde anormal pour compte '{compte}': "
            f"Solde Debit = {solde_debit:.2f}, "
            f"Solde Credit = {solde_credit:.2f}. "
            f"Raison: {raison}"
        )
        
        context = {
            'compte': compte,
            'solde_debit': solde_debit,
            'solde_credit': solde_credit,
            'raison': raison,
            'note_numero': note_numero
        }
        
        super().__init__(message, context)


class MissingAccountWarning(CalculNotesWarning):
    """
    Warning for missing accounts in balance.
    
    Emitted when: Expected account is not found in balance sheet.
    
    Requirements: 8.5, 8.6
    """
    
    def __init__(self,
                 compte: str,
                 note_numero: Optional[str] = None,
                 impact: str = "Valeurs nulles utilisees"):
        """
        Initialize missing account warning.
        
        Args:
            compte: Missing account number or root
            note_numero: Optional note number where warning occurred
            impact: Description of impact on calculations
        """
        message = (
            f"Compte manquant: '{compte}'. "
            f"Impact: {impact}"
        )
        
        context = {
            'compte': compte,
            'note_numero': note_numero,
            'impact': impact
        }
        
        super().__init__(message, context)


class LowCoherenceRateWarning(CalculNotesWarning):
    """
    Warning for low inter-note coherence rate.
    
    Emitted when: Global coherence rate < 95%
    
    Requirements: 8.5, 8.6
    """
    
    def __init__(self,
                 taux_coherence: float,
                 seuil: float = 95.0,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize low coherence rate warning.
        
        Args:
            taux_coherence: Calculated coherence rate (percentage)
            seuil: Threshold for acceptable coherence (default 95%)
            details: Optional dictionary with detailed coherence validation results
        """
        message = (
            f"Taux de coherence faible: {taux_coherence:.2f}% "
            f"(seuil: {seuil:.2f}%). "
            f"Verification des notes annexes recommandee."
        )
        
        context = {
            'taux_coherence': taux_coherence,
            'seuil': seuil,
            'details': details
        }
        
        super().__init__(message, context)


# Convenience functions for emitting warnings

def warn_incoherent_balance(compte: str,
                           solde_ouverture: float,
                           augmentations: float,
                           diminutions: float,
                           solde_cloture: float,
                           ecart: float,
                           note_numero: Optional[str] = None):
    """
    Emit an incoherent balance warning.
    
    Args:
        compte: Account number or description
        solde_ouverture: Opening balance
        augmentations: Increases during period
        diminutions: Decreases during period
        solde_cloture: Closing balance
        ecart: Difference between expected and actual closing balance
        note_numero: Optional note number where warning occurred
    """
    warning = IncoherentBalanceWarning(
        compte=compte,
        solde_ouverture=solde_ouverture,
        augmentations=augmentations,
        diminutions=diminutions,
        solde_cloture=solde_cloture,
        ecart=ecart,
        note_numero=note_numero
    )
    warnings.warn(warning)


def warn_negative_vnc(libelle: str,
                     brut: float,
                     amortissement: float,
                     vnc: float,
                     note_numero: Optional[str] = None):
    """
    Emit a negative VNC warning.
    
    Args:
        libelle: Asset line description
        brut: Gross value
        amortissement: Accumulated depreciation
        vnc: Net book value (negative)
        note_numero: Optional note number where warning occurred
    """
    warning = NegativeVNCWarning(
        libelle=libelle,
        brut=brut,
        amortissement=amortissement,
        vnc=vnc,
        note_numero=note_numero
    )
    warnings.warn(warning)


def warn_abnormal_account_balance(compte: str,
                                  solde_debit: float,
                                  solde_credit: float,
                                  raison: str,
                                  note_numero: Optional[str] = None):
    """
    Emit an abnormal account balance warning.
    
    Args:
        compte: Account number
        solde_debit: Debit balance
        solde_credit: Credit balance
        raison: Reason why balance is considered abnormal
        note_numero: Optional note number where warning occurred
    """
    warning = AbnormalAccountBalanceWarning(
        compte=compte,
        solde_debit=solde_debit,
        solde_credit=solde_credit,
        raison=raison,
        note_numero=note_numero
    )
    warnings.warn(warning)


def warn_missing_account(compte: str,
                        note_numero: Optional[str] = None,
                        impact: str = "Valeurs nulles utilisees"):
    """
    Emit a missing account warning.
    
    Args:
        compte: Missing account number or root
        note_numero: Optional note number where warning occurred
        impact: Description of impact on calculations
    """
    warning = MissingAccountWarning(
        compte=compte,
        note_numero=note_numero,
        impact=impact
    )
    warnings.warn(warning)


def warn_low_coherence_rate(taux_coherence: float,
                           seuil: float = 95.0,
                           details: Optional[Dict[str, Any]] = None):
    """
    Emit a low coherence rate warning.
    
    Args:
        taux_coherence: Calculated coherence rate (percentage)
        seuil: Threshold for acceptable coherence (default 95%)
        details: Optional dictionary with detailed coherence validation results
    """
    warning = LowCoherenceRateWarning(
        taux_coherence=taux_coherence,
        seuil=seuil,
        details=details
    )
    warnings.warn(warning)
