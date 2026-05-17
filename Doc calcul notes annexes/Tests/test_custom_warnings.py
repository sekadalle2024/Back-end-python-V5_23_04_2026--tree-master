"""
Tests for Custom Warning System

This module tests all custom warning classes and their integration with
the logging infrastructure.

Requirements: 3.6, 4.7, 8.5, 8.6, Error Handling
"""

import pytest
import warnings
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Modules.custom_warnings import (
    CalculNotesWarning,
    IncoherentBalanceWarning,
    NegativeVNCWarning,
    AbnormalAccountBalanceWarning,
    MissingAccountWarning,
    LowCoherenceRateWarning,
    warn_incoherent_balance,
    warn_negative_vnc,
    warn_abnormal_account_balance,
    warn_missing_account,
    warn_low_coherence_rate
)


@pytest.fixture
def capture_warnings():
    """Fixture to capture warnings during tests"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        yield w


@pytest.fixture
def capture_logs(caplog):
    """Fixture to capture log messages"""
    caplog.set_level(logging.WARNING, logger='calcul_notes_warnings')
    return caplog


class TestIncoherentBalanceWarning:
    """Test IncoherentBalanceWarning class"""
    
    def test_warning_creation(self, capture_warnings):
        """Test that IncoherentBalanceWarning can be created"""
        warning = IncoherentBalanceWarning(
            compte="211",
            solde_ouverture=1000.0,
            augmentations=500.0,
            diminutions=200.0,
            solde_cloture=1250.0,
            ecart=50.0,
            note_numero="3A"
        )
        
        assert warning.context['compte'] == "211"
        assert warning.context['ecart'] == 50.0
        assert warning.context['note_numero'] == "3A"
        assert "Balance incoherent" in warning.message
    
    def test_warning_logged(self, capture_logs):
        """Test that warning is logged to calcul_notes_warnings.log"""
        warning = IncoherentBalanceWarning(
            compte="211",
            solde_ouverture=1000.0,
            augmentations=500.0,
            diminutions=200.0,
            solde_cloture=1250.0,
            ecart=50.0
        )
        
        assert len(capture_logs.records) == 1
        assert "IncoherentBalanceWarning" in capture_logs.records[0].message
        assert "211" in capture_logs.records[0].message
        assert "50.00" in capture_logs.records[0].message
    
    def test_convenience_function(self, capture_warnings, capture_logs):
        """Test warn_incoherent_balance convenience function"""
        warn_incoherent_balance(
            compte="2811",
            solde_ouverture=500.0,
            augmentations=100.0,
            diminutions=50.0,
            solde_cloture=600.0,
            ecart=50.0,
            note_numero="3A"
        )
        
        assert len(capture_warnings) == 1
        assert issubclass(capture_warnings[0].category, IncoherentBalanceWarning)
        assert len(capture_logs.records) == 1


class TestNegativeVNCWarning:
    """Test NegativeVNCWarning class"""
    
    def test_warning_creation(self, capture_warnings):
        """Test that NegativeVNCWarning can be created"""
        warning = NegativeVNCWarning(
            libelle="Frais de recherche",
            brut=1000.0,
            amortissement=1200.0,
            vnc=-200.0,
            note_numero="3A"
        )
        
        assert warning.context['libelle'] == "Frais de recherche"
        assert warning.context['vnc'] == -200.0
        assert warning.context['note_numero'] == "3A"
        assert "VNC negative" in warning.message
    
    def test_warning_logged(self, capture_logs):
        """Test that warning is logged"""
        warning = NegativeVNCWarning(
            libelle="Brevets",
            brut=5000.0,
            amortissement=5500.0,
            vnc=-500.0
        )
        
        assert len(capture_logs.records) == 1
        assert "NegativeVNCWarning" in capture_logs.records[0].message
        assert "Brevets" in capture_logs.records[0].message
        assert "-500.00" in capture_logs.records[0].message
    
    def test_convenience_function(self, capture_warnings, capture_logs):
        """Test warn_negative_vnc convenience function"""
        warn_negative_vnc(
            libelle="Logiciels",
            brut=2000.0,
            amortissement=2100.0,
            vnc=-100.0,
            note_numero="3A"
        )
        
        assert len(capture_warnings) == 1
        assert issubclass(capture_warnings[0].category, NegativeVNCWarning)
        assert len(capture_logs.records) == 1


class TestAbnormalAccountBalanceWarning:
    """Test AbnormalAccountBalanceWarning class"""
    
    def test_warning_creation(self, capture_warnings):
        """Test that AbnormalAccountBalanceWarning can be created"""
        warning = AbnormalAccountBalanceWarning(
            compte="211",
            solde_debit=1000.0,
            solde_credit=500.0,
            raison="Compte actif avec solde crediteur",
            note_numero="3A"
        )
        
        assert warning.context['compte'] == "211"
        assert warning.context['solde_debit'] == 1000.0
        assert warning.context['solde_credit'] == 500.0
        assert "Solde anormal" in warning.message
    
    def test_warning_logged(self, capture_logs):
        """Test that warning is logged"""
        warning = AbnormalAccountBalanceWarning(
            compte="401",
            solde_debit=200.0,
            solde_credit=0.0,
            raison="Compte fournisseur avec solde debiteur"
        )
        
        assert len(capture_logs.records) == 1
        assert "AbnormalAccountBalanceWarning" in capture_logs.records[0].message
        assert "401" in capture_logs.records[0].message
    
    def test_convenience_function(self, capture_warnings, capture_logs):
        """Test warn_abnormal_account_balance convenience function"""
        warn_abnormal_account_balance(
            compte="512",
            solde_debit=0.0,
            solde_credit=1000.0,
            raison="Compte banque avec solde crediteur negatif",
            note_numero="7"
        )
        
        assert len(capture_warnings) == 1
        assert issubclass(capture_warnings[0].category, AbnormalAccountBalanceWarning)
        assert len(capture_logs.records) == 1


class TestMissingAccountWarning:
    """Test MissingAccountWarning class"""
    
    def test_warning_creation(self, capture_warnings):
        """Test that MissingAccountWarning can be created"""
        warning = MissingAccountWarning(
            compte="218",
            note_numero="3A",
            impact="Ligne 'Autres immobilisations' sera a zero"
        )
        
        assert warning.context['compte'] == "218"
        assert warning.context['note_numero'] == "3A"
        assert "Compte manquant" in warning.message
    
    def test_warning_logged(self, capture_logs):
        """Test that warning is logged"""
        warning = MissingAccountWarning(
            compte="2918",
            impact="Amortissements non calcules"
        )
        
        assert len(capture_logs.records) == 1
        assert "MissingAccountWarning" in capture_logs.records[0].message
        assert "2918" in capture_logs.records[0].message
    
    def test_convenience_function(self, capture_warnings, capture_logs):
        """Test warn_missing_account convenience function"""
        warn_missing_account(
            compte="26",
            note_numero="3C",
            impact="Immobilisations financieres non calculees"
        )
        
        assert len(capture_warnings) == 1
        assert issubclass(capture_warnings[0].category, MissingAccountWarning)
        assert len(capture_logs.records) == 1
    
    def test_default_impact(self, capture_warnings):
        """Test that default impact message is used"""
        warning = MissingAccountWarning(compte="999")
        
        assert warning.context['impact'] == "Valeurs nulles utilisees"


class TestLowCoherenceRateWarning:
    """Test LowCoherenceRateWarning class"""
    
    def test_warning_creation(self, capture_warnings):
        """Test that LowCoherenceRateWarning can be created"""
        details = {
            'total_immobilisations': {'coherent': False, 'ecart': 1000.0},
            'dotations_amortissements': {'coherent': True, 'ecart': 0.0}
        }
        
        warning = LowCoherenceRateWarning(
            taux_coherence=92.5,
            seuil=95.0,
            details=details
        )
        
        assert warning.context['taux_coherence'] == 92.5
        assert warning.context['seuil'] == 95.0
        assert warning.context['details'] == details
        assert "Taux de coherence faible" in warning.message
    
    def test_warning_logged(self, capture_logs):
        """Test that warning is logged"""
        warning = LowCoherenceRateWarning(
            taux_coherence=90.0,
            seuil=95.0
        )
        
        assert len(capture_logs.records) == 1
        assert "LowCoherenceRateWarning" in capture_logs.records[0].message
        assert "90.00%" in capture_logs.records[0].message
    
    def test_convenience_function(self, capture_warnings, capture_logs):
        """Test warn_low_coherence_rate convenience function"""
        warn_low_coherence_rate(
            taux_coherence=88.5,
            seuil=95.0,
            details={'validation_count': 10, 'failed_count': 2}
        )
        
        assert len(capture_warnings) == 1
        assert issubclass(capture_warnings[0].category, LowCoherenceRateWarning)
        assert len(capture_logs.records) == 1


class TestWarningIntegration:
    """Test integration of warnings with logging system"""
    
    def test_multiple_warnings_logged(self, capture_logs):
        """Test that multiple warnings are all logged"""
        warn_missing_account("211", note_numero="3A")
        warn_negative_vnc("Test", 100.0, 150.0, -50.0, note_numero="3A")
        warn_incoherent_balance("2811", 100.0, 50.0, 20.0, 125.0, 5.0)
        
        assert len(capture_logs.records) == 3
        assert any("MissingAccountWarning" in r.message for r in capture_logs.records)
        assert any("NegativeVNCWarning" in r.message for r in capture_logs.records)
        assert any("IncoherentBalanceWarning" in r.message for r in capture_logs.records)
    
    def test_warning_context_in_logs(self, capture_logs):
        """Test that warning context is included in log messages"""
        warn_abnormal_account_balance(
            compte="401",
            solde_debit=100.0,
            solde_credit=50.0,
            raison="Test reason",
            note_numero="13"
        )
        
        log_message = capture_logs.records[0].message
        assert "compte=401" in log_message
        assert "note_numero=13" in log_message
    
    def test_warning_timestamp(self, capture_warnings):
        """Test that warnings have timestamps"""
        warning = MissingAccountWarning(compte="999")
        
        assert hasattr(warning, 'timestamp')
        assert warning.timestamp is not None


class TestWarningFormatting:
    """Test warning message formatting"""
    
    def test_incoherent_balance_format(self):
        """Test IncoherentBalanceWarning message format"""
        warning = IncoherentBalanceWarning(
            compte="211",
            solde_ouverture=1000.0,
            augmentations=500.0,
            diminutions=200.0,
            solde_cloture=1250.0,
            ecart=50.0
        )
        
        assert "211" in warning.message
        assert "1300.00" in warning.message  # Expected closing: 1000 + 500 - 200
        assert "1250.00" in warning.message  # Actual closing
        assert "50.00" in warning.message    # Difference
    
    def test_negative_vnc_format(self):
        """Test NegativeVNCWarning message format"""
        warning = NegativeVNCWarning(
            libelle="Test Asset",
            brut=1000.0,
            amortissement=1200.0,
            vnc=-200.0
        )
        
        assert "Test Asset" in warning.message
        assert "1000.00" in warning.message
        assert "1200.00" in warning.message
        assert "-200.00" in warning.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
