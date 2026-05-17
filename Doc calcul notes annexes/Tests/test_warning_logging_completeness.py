"""
Property Test: Warning Logging Completeness

This module implements Property 14: Warning Logging Completeness

Property Statement:
For any warning emitted during processing (incoherent balances, negative VNC, 
abnormal account balances), the system must log it to calcul_notes_warnings.log 
with timestamp and details.

Validates: Requirements 3.6, 4.7, 8.5, 8.6

Test Strategy:
- Use Hypothesis to generate various warning scenarios
- Verify that each warning type is logged with complete information
- Check that log entries contain all required fields (timestamp, warning type, context)
- Ensure no warnings are lost or duplicated
- Validate log format consistency
"""

import pytest
import logging
import warnings
from pathlib import Path
import sys
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Modules.custom_warnings import (
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
from Modules.logging_config import LoggingConfig


# Hypothesis strategies for generating test data

@st.composite
def compte_strategy(draw):
    """Generate valid account numbers"""
    # SYSCOHADA account numbers: 1-9 digits
    prefix = draw(st.sampled_from(['2', '21', '211', '28', '281', '2811', '4', '41', '5']))
    suffix = draw(st.text(alphabet='0123456789', min_size=0, max_size=3))
    return prefix + suffix


@st.composite
def montant_strategy(draw):
    """Generate monetary amounts"""
    return draw(st.floats(
        min_value=-1000000.0,
        max_value=1000000.0,
        allow_nan=False,
        allow_infinity=False
    ))


@st.composite
def note_numero_strategy(draw):
    """Generate note numbers"""
    return draw(st.sampled_from([
        '3A', '3B', '3C', '3D', '3E', '4', '5', '6', '7', '8', '9', '10',
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
        '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
        '31', '32', '33', None
    ]))


@st.composite
def incoherent_balance_data(draw):
    """Generate data for incoherent balance warnings"""
    compte = draw(compte_strategy())
    solde_ouverture = draw(montant_strategy())
    augmentations = draw(st.floats(min_value=0.0, max_value=100000.0))
    diminutions = draw(st.floats(min_value=0.0, max_value=100000.0))
    
    # Calculate expected closing balance
    expected_cloture = solde_ouverture + augmentations - diminutions
    
    # Generate actual closing balance with some difference
    ecart = draw(st.floats(min_value=0.1, max_value=1000.0))
    solde_cloture = expected_cloture + ecart
    
    note_numero = draw(note_numero_strategy())
    
    return {
        'compte': compte,
        'solde_ouverture': solde_ouverture,
        'augmentations': augmentations,
        'diminutions': diminutions,
        'solde_cloture': solde_cloture,
        'ecart': ecart,
        'note_numero': note_numero
    }


@st.composite
def negative_vnc_data(draw):
    """Generate data for negative VNC warnings"""
    libelle = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), whitelist_characters=' -'
    )))
    brut = draw(st.floats(min_value=0.0, max_value=100000.0))
    
    # Ensure amortissement > brut to get negative VNC
    amortissement = draw(st.floats(min_value=brut + 0.01, max_value=brut + 50000.0))
    vnc = brut - amortissement
    
    note_numero = draw(note_numero_strategy())
    
    return {
        'libelle': libelle,
        'brut': brut,
        'amortissement': amortissement,
        'vnc': vnc,
        'note_numero': note_numero
    }


@st.composite
def abnormal_balance_data(draw):
    """Generate data for abnormal account balance warnings"""
    compte = draw(compte_strategy())
    solde_debit = draw(montant_strategy())
    solde_credit = draw(montant_strategy())
    
    raisons = [
        "Compte actif avec solde crediteur",
        "Compte passif avec solde debiteur",
        "Soldes debit et credit simultanement",
        "Signe inattendu pour ce type de compte"
    ]
    raison = draw(st.sampled_from(raisons))
    note_numero = draw(note_numero_strategy())
    
    return {
        'compte': compte,
        'solde_debit': solde_debit,
        'solde_credit': solde_credit,
        'raison': raison,
        'note_numero': note_numero
    }


@st.composite
def missing_account_data(draw):
    """Generate data for missing account warnings"""
    compte = draw(compte_strategy())
    note_numero = draw(note_numero_strategy())
    
    impacts = [
        "Valeurs nulles utilisees",
        "Ligne sera a zero",
        "Calcul incomplet",
        "Donnees manquantes"
    ]
    impact = draw(st.sampled_from(impacts))
    
    return {
        'compte': compte,
        'note_numero': note_numero,
        'impact': impact
    }


@st.composite
def low_coherence_data(draw):
    """Generate data for low coherence rate warnings"""
    taux_coherence = draw(st.floats(min_value=0.0, max_value=94.9))
    seuil = 95.0
    
    details = {
        'validation_count': draw(st.integers(min_value=1, max_value=50)),
        'failed_count': draw(st.integers(min_value=1, max_value=10))
    }
    
    return {
        'taux_coherence': taux_coherence,
        'seuil': seuil,
        'details': details
    }


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def logging_config(temp_log_dir):
    """Configure logging with temporary directory"""
    config = LoggingConfig(log_directory=temp_log_dir)
    config.configure()
    return config


@pytest.fixture
def warnings_log_file(temp_log_dir):
    """Get path to warnings log file"""
    return Path(temp_log_dir) / "calcul_notes_warnings.log"


class TestWarningLoggingCompleteness:
    """Property tests for warning logging completeness"""
    
    @given(data=incoherent_balance_data())
    @settings(max_examples=50, deadline=None)
    def test_incoherent_balance_logged_completely(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: Every IncoherentBalanceWarning must be logged with complete information
        
        Validates: Requirements 3.6, 8.5
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning
        warn_incoherent_balance(**data)
        
        # Read log file
        assert warnings_log_file.exists(), "Warnings log file should exist"
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Verify warning was logged
        assert "IncoherentBalanceWarning" in log_content, \
            "Warning type should be in log"
        
        # Verify all context fields are present
        assert data['compte'] in log_content, \
            "Account number should be in log"
        
        assert f"compte={data['compte']}" in log_content, \
            "Account context should be in log"
        
        # Verify timestamp is present (format: YYYY-MM-DD HH:MM:SS)
        assert any(char.isdigit() for char in log_content), \
            "Timestamp should be in log"
        
        # Verify log level
        assert "WARNING" in log_content, \
            "Log level should be WARNING"
    
    @given(data=negative_vnc_data())
    @settings(max_examples=50, deadline=None)
    def test_negative_vnc_logged_completely(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: Every NegativeVNCWarning must be logged with complete information
        
        Validates: Requirements 4.7, 8.5
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning
        warn_negative_vnc(**data)
        
        # Read log file
        assert warnings_log_file.exists(), "Warnings log file should exist"
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Verify warning was logged
        assert "NegativeVNCWarning" in log_content, \
            "Warning type should be in log"
        
        # Verify context fields
        assert f"libelle={data['libelle']}" in log_content, \
            "Asset description should be in log"
        
        # Verify timestamp
        assert any(char.isdigit() for char in log_content), \
            "Timestamp should be in log"
        
        # Verify log level
        assert "WARNING" in log_content, \
            "Log level should be WARNING"
    
    @given(data=abnormal_balance_data())
    @settings(max_examples=50, deadline=None)
    def test_abnormal_balance_logged_completely(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: Every AbnormalAccountBalanceWarning must be logged completely
        
        Validates: Requirements 8.5, 8.6
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning
        warn_abnormal_account_balance(**data)
        
        # Read log file
        assert warnings_log_file.exists(), "Warnings log file should exist"
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Verify warning was logged
        assert "AbnormalAccountBalanceWarning" in log_content, \
            "Warning type should be in log"
        
        # Verify context
        assert data['compte'] in log_content, \
            "Account number should be in log"
        
        assert data['raison'] in log_content, \
            "Reason should be in log"
        
        # Verify timestamp and log level
        assert "WARNING" in log_content
    
    @given(data=missing_account_data())
    @settings(max_examples=50, deadline=None)
    def test_missing_account_logged_completely(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: Every MissingAccountWarning must be logged completely
        
        Validates: Requirements 8.5, 8.6
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning
        warn_missing_account(**data)
        
        # Read log file
        assert warnings_log_file.exists(), "Warnings log file should exist"
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Verify warning was logged
        assert "MissingAccountWarning" in log_content, \
            "Warning type should be in log"
        
        # Verify context
        assert data['compte'] in log_content, \
            "Missing account should be in log"
        
        assert data['impact'] in log_content, \
            "Impact description should be in log"
        
        # Verify timestamp and log level
        assert "WARNING" in log_content
    
    @given(data=low_coherence_data())
    @settings(max_examples=50, deadline=None)
    def test_low_coherence_logged_completely(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: Every LowCoherenceRateWarning must be logged completely
        
        Validates: Requirements 8.5, 8.6
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning
        warn_low_coherence_rate(**data)
        
        # Read log file
        assert warnings_log_file.exists(), "Warnings log file should exist"
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Verify warning was logged
        assert "LowCoherenceRateWarning" in log_content, \
            "Warning type should be in log"
        
        # Verify coherence rate is in log
        assert str(round(data['taux_coherence'], 2)) in log_content or \
               f"{data['taux_coherence']:.2f}" in log_content, \
            "Coherence rate should be in log"
        
        # Verify timestamp and log level
        assert "WARNING" in log_content
    
    @given(
        warnings_list=st.lists(
            st.one_of(
                incoherent_balance_data(),
                negative_vnc_data(),
                abnormal_balance_data(),
                missing_account_data(),
                low_coherence_data()
            ),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_multiple_warnings_all_logged(
        self, 
        warnings_list, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: When multiple warnings are emitted, all must be logged
        
        Validates: Requirements 8.5, 8.6
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit all warnings
        for warning_data in warnings_list:
            if 'solde_ouverture' in warning_data:
                warn_incoherent_balance(**warning_data)
            elif 'brut' in warning_data and 'amortissement' in warning_data:
                warn_negative_vnc(**warning_data)
            elif 'raison' in warning_data:
                warn_abnormal_account_balance(**warning_data)
            elif 'impact' in warning_data:
                warn_missing_account(**warning_data)
            elif 'taux_coherence' in warning_data:
                warn_low_coherence_rate(**warning_data)
        
        # Read log file
        assert warnings_log_file.exists(), "Warnings log file should exist"
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Count warning entries in log
        warning_count = log_content.count("WARNING")
        
        # Verify all warnings were logged
        assert warning_count == len(warnings_list), \
            f"Expected {len(warnings_list)} warnings in log, found {warning_count}"
    
    @given(data=incoherent_balance_data())
    @settings(max_examples=20, deadline=None)
    def test_warning_log_format_consistency(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: All warning log entries must follow consistent format
        
        Format: TIMESTAMP | LEVEL | LOGGER | LOCATION | MESSAGE
        
        Validates: Requirements 8.5, 8.6
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning
        warn_incoherent_balance(**data)
        
        # Read log file
        log_content = warnings_log_file.read_text(encoding='utf-8')
        lines = [line for line in log_content.split('\n') if line.strip()]
        
        assert len(lines) > 0, "Log should contain at least one line"
        
        for line in lines:
            # Verify pipe separators
            assert '|' in line, "Log line should contain pipe separators"
            
            parts = line.split('|')
            assert len(parts) >= 4, "Log line should have at least 4 parts"
            
            # Verify timestamp format (YYYY-MM-DD HH:MM:SS)
            timestamp_part = parts[0].strip()
            assert len(timestamp_part) >= 19, "Timestamp should be at least 19 characters"
            
            # Verify log level
            level_part = parts[1].strip()
            assert level_part == "WARNING", "Log level should be WARNING"
    
    @given(data=negative_vnc_data())
    @settings(max_examples=20, deadline=None)
    def test_warning_context_completeness(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: Warning log entries must include all context information
        
        Validates: Requirements 8.5, 8.6
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning
        warn_negative_vnc(**data)
        
        # Read log file
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Verify all context keys are present
        assert "libelle=" in log_content, "Context should include libelle"
        assert "brut=" in log_content, "Context should include brut"
        assert "amortissement=" in log_content, "Context should include amortissement"
        assert "vnc=" in log_content, "Context should include vnc"
        
        if data['note_numero'] is not None:
            assert "note_numero=" in log_content, "Context should include note_numero"
    
    @given(data=missing_account_data())
    @settings(max_examples=20, deadline=None)
    def test_no_warning_duplication(
        self, 
        data, 
        logging_config, 
        warnings_log_file
    ):
        """
        Property: Each warning should be logged exactly once (no duplication)
        
        Validates: Requirements 8.5, 8.6
        """
        # Clear log file
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        # Emit warning once
        warn_missing_account(**data)
        
        # Read log file
        log_content = warnings_log_file.read_text(encoding='utf-8')
        
        # Count occurrences of the warning
        warning_count = log_content.count("MissingAccountWarning")
        
        # Verify warning appears exactly once
        assert warning_count == 1, \
            f"Warning should appear exactly once, found {warning_count} times"


class TestWarningLoggingEdgeCases:
    """Test edge cases for warning logging"""
    
    def test_warning_with_none_note_numero(self, logging_config, warnings_log_file):
        """Test that warnings with None note_numero are logged correctly"""
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        warn_missing_account(compte="999", note_numero=None)
        
        log_content = warnings_log_file.read_text(encoding='utf-8')
        assert "MissingAccountWarning" in log_content
        assert "note_numero=None" in log_content
    
    def test_warning_with_special_characters(self, logging_config, warnings_log_file):
        """Test that warnings with special characters are logged correctly"""
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        warn_abnormal_account_balance(
            compte="401-FOURNISSEUR",
            solde_debit=100.0,
            solde_credit=50.0,
            raison="Compte avec caractères spéciaux: é, à, ç"
        )
        
        log_content = warnings_log_file.read_text(encoding='utf-8')
        assert "AbnormalAccountBalanceWarning" in log_content
        assert "401-FOURNISSEUR" in log_content
    
    def test_warning_with_very_large_amounts(self, logging_config, warnings_log_file):
        """Test that warnings with very large amounts are logged correctly"""
        if warnings_log_file.exists():
            warnings_log_file.unlink()
        
        warn_negative_vnc(
            libelle="Test",
            brut=999999999.99,
            amortissement=1000000000.00,
            vnc=-0.01
        )
        
        log_content = warnings_log_file.read_text(encoding='utf-8')
        assert "NegativeVNCWarning" in log_content
        assert "999999999" in log_content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
