"""
Test Graceful Degradation - Task 28.4

This test suite validates the graceful degradation implementation for:
- Missing accounts (return zero values with warnings)
- Missing N-2 exercise (continue with empty balance)
- Non-critical errors (continue processing with warnings)

Requirements: 8.1, 8.2, 8.3, 8.4

Author: Claraverse
Date: 2026-04-29
"""

import pytest
import pandas as pd
import sys
import os
import warnings
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Modules"))

from balance_reader import BalanceReader
from account_extractor import AccountExtractor
from custom_warnings import (
    MissingAccountWarning,
    warn_missing_account
)


class TestGracefulDegradation:
    """Test suite for graceful degradation functionality."""
    
    def test_missing_account_returns_zeros(self):
        """
        Test that missing accounts return zero values without raising exceptions.
        
        Validates: Requirement 8.1 - Handle missing accounts with zero values
        """
        # Create a simple balance with only account 211
        balance_data = {
            'Numéro': ['211'],
            'Intitulé': ['Frais de R&D'],
            'Ant Débit': [1000000.0],
            'Ant Crédit': [0.0],
            'Débit': [500000.0],
            'Crédit': [0.0],
            'Solde Débit': [1500000.0],
            'Solde Crédit': [0.0]
        }
        balance = pd.DataFrame(balance_data)
        
        # Create extractor
        extractor = AccountExtractor(balance)
        
        # Extract non-existent account 999
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            soldes = extractor.extraire_solde_compte("999", note_numero="TEST", emit_warning=True)
            
            # Verify warning was emitted
            assert len(w) == 1
            assert issubclass(w[0].category, MissingAccountWarning)
            assert "999" in str(w[0].message)
        
        # Verify all values are zero
        assert soldes['ant_debit'] == 0.0
        assert soldes['ant_credit'] == 0.0
        assert soldes['mvt_debit'] == 0.0
        assert soldes['mvt_credit'] == 0.0
        assert soldes['solde_debit'] == 0.0
        assert soldes['solde_credit'] == 0.0
        
        print("✓ Test passed: Missing account returns zeros with warning")
    
    def test_missing_account_no_warning_when_disabled(self):
        """
        Test that warnings can be disabled for missing accounts.
        
        Validates: Requirement 8.1 - Configurable warning emission
        """
        # Create a simple balance
        balance_data = {
            'Numéro': ['211'],
            'Intitulé': ['Frais de R&D'],
            'Ant Débit': [1000000.0],
            'Ant Crédit': [0.0],
            'Débit': [500000.0],
            'Crédit': [0.0],
            'Solde Débit': [1500000.0],
            'Solde Crédit': [0.0]
        }
        balance = pd.DataFrame(balance_data)
        
        # Create extractor
        extractor = AccountExtractor(balance)
        
        # Extract non-existent account with warnings disabled
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            soldes = extractor.extraire_solde_compte("999", emit_warning=False)
            
            # Verify no warning was emitted
            assert len(w) == 0
        
        # Verify all values are still zero
        assert soldes['solde_debit'] == 0.0
        
        print("✓ Test passed: Missing account warnings can be disabled")
    
    def test_missing_n2_creates_empty_balance(self):
        """
        Test that missing N-2 exercise creates an empty balance without error.
        
        Validates: Requirement 8.2 - Handle missing N-2 exercise gracefully
        """
        # Create a test Excel file with only N and N-1
        test_file = Path(__file__).parent / "fixtures" / "balance_sans_n2.xlsx"
        
        if not test_file.exists():
            # Create test file
            balance_data = {
                'Numéro': ['211', '212'],
                'Intitulé': ['Frais de R&D', 'Brevets'],
                'Ant Débit': [1000000.0, 500000.0],
                'Ant Crédit': [0.0, 0.0],
                'Débit': [500000.0, 200000.0],
                'Crédit': [0.0, 0.0],
                'Solde Débit': [1500000.0, 700000.0],
                'Solde Crédit': [0.0, 0.0]
            }
            df = pd.DataFrame(balance_data)
            
            with pd.ExcelWriter(test_file) as writer:
                df.to_excel(writer, sheet_name='BALANCE N', index=False)
                df.to_excel(writer, sheet_name='BALANCE N-1', index=False)
        
        # Load balances with graceful N-2 handling
        reader = BalanceReader(str(test_file))
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            balance_n, balance_n1, balance_n2 = reader.charger_balances()
            
            # Verify warning was logged (not necessarily a Python warning)
            # Check that N-2 is empty
            assert len(balance_n2) == 0
            assert list(balance_n2.columns) == [
                'Numéro', 'Intitulé',
                'Ant Débit', 'Ant Crédit',
                'Débit', 'Crédit',
                'Solde Débit', 'Solde Crédit'
            ]
        
        # Verify N and N-1 loaded correctly
        assert len(balance_n) == 2
        assert len(balance_n1) == 2
        
        print("✓ Test passed: Missing N-2 creates empty balance")
    
    def test_empty_balance_extraction_returns_zeros(self):
        """
        Test that extracting from empty balance returns zeros.
        
        Validates: Requirement 8.2 - Continue processing with empty N-2
        """
        # Create empty balance
        balance_vide = pd.DataFrame(columns=[
            'Numéro', 'Intitulé',
            'Ant Débit', 'Ant Crédit',
            'Débit', 'Crédit',
            'Solde Débit', 'Solde Crédit'
        ])
        
        # Create extractor
        extractor = AccountExtractor(balance_vide)
        
        # Extract any account
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            soldes = extractor.extraire_solde_compte("211", note_numero="TEST")
            
            # Verify warning was emitted
            assert len(w) == 1
            assert issubclass(w[0].category, MissingAccountWarning)
        
        # Verify all values are zero
        assert soldes['solde_debit'] == 0.0
        assert soldes['solde_credit'] == 0.0
        
        print("✓ Test passed: Empty balance extraction returns zeros")
    
    def test_multiple_missing_accounts_emit_multiple_warnings(self):
        """
        Test that multiple missing accounts emit individual warnings.
        
        Validates: Requirement 8.3 - Continue processing with warnings for non-critical errors
        """
        # Create a simple balance
        balance_data = {
            'Numéro': ['211'],
            'Intitulé': ['Frais de R&D'],
            'Ant Débit': [1000000.0],
            'Ant Crédit': [0.0],
            'Débit': [500000.0],
            'Crédit': [0.0],
            'Solde Débit': [1500000.0],
            'Solde Crédit': [0.0]
        }
        balance = pd.DataFrame(balance_data)
        
        # Create extractor
        extractor = AccountExtractor(balance)
        
        # Extract multiple non-existent accounts
        missing_accounts = ["212", "213", "214"]
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            for compte in missing_accounts:
                soldes = extractor.extraire_solde_compte(compte, note_numero="3A")
                assert soldes['solde_debit'] == 0.0
            
            # Verify one warning per missing account
            assert len(w) == len(missing_accounts)
            for warning in w:
                assert issubclass(warning.category, MissingAccountWarning)
        
        print("✓ Test passed: Multiple missing accounts emit multiple warnings")
    
    def test_partial_data_continues_processing(self):
        """
        Test that processing continues with partial data.
        
        Validates: Requirement 8.4 - Distinguish between missing and zero balance
        """
        # Create balance with some accounts
        balance_data = {
            'Numéro': ['211', '212'],
            'Intitulé': ['Frais de R&D', 'Brevets'],
            'Ant Débit': [1000000.0, 0.0],  # 212 has zero balance
            'Ant Crédit': [0.0, 0.0],
            'Débit': [500000.0, 0.0],
            'Crédit': [0.0, 0.0],
            'Solde Débit': [1500000.0, 0.0],
            'Solde Crédit': [0.0, 0.0]
        }
        balance = pd.DataFrame(balance_data)
        
        # Create extractor
        extractor = AccountExtractor(balance)
        
        # Extract existing account with zero balance (should not warn)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            soldes_212 = extractor.extraire_solde_compte("212", note_numero="3A")
            
            # No warning for existing account with zero balance
            assert len(w) == 0
            assert soldes_212['solde_debit'] == 0.0
        
        # Extract non-existent account (should warn)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            soldes_999 = extractor.extraire_solde_compte("999", note_numero="3A")
            
            # Warning for missing account
            assert len(w) == 1
            assert issubclass(w[0].category, MissingAccountWarning)
            assert soldes_999['solde_debit'] == 0.0
        
        print("✓ Test passed: System distinguishes between missing and zero balance accounts")
    
    def test_extraire_comptes_multiples_with_missing_accounts(self):
        """
        Test that extracting multiple accounts handles missing ones gracefully.
        
        Validates: Requirement 8.1, 8.3 - Handle missing accounts in batch operations
        """
        # Create balance with only one account
        balance_data = {
            'Numéro': ['211'],
            'Intitulé': ['Frais de R&D'],
            'Ant Débit': [1000000.0],
            'Ant Crédit': [0.0],
            'Débit': [500000.0],
            'Crédit': [0.0],
            'Solde Débit': [1500000.0],
            'Solde Crédit': [0.0]
        }
        balance = pd.DataFrame(balance_data)
        
        # Create extractor
        extractor = AccountExtractor(balance)
        
        # Extract multiple accounts (some missing)
        racines = ["211", "212", "213"]  # Only 211 exists
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            soldes_total = extractor.extraire_comptes_multiples(racines, note_numero="3A")
            
            # Verify warnings for missing accounts
            assert len(w) == 2  # 212 and 213 are missing
            
            # Verify total includes only existing account
            assert soldes_total['solde_debit'] == 1500000.0
        
        print("✓ Test passed: Multiple account extraction handles missing accounts")


def run_tests():
    """Run all graceful degradation tests."""
    print("=" * 70)
    print("GRACEFUL DEGRADATION TESTS - Task 28.4")
    print("=" * 70)
    print()
    
    test_suite = TestGracefulDegradation()
    
    tests = [
        ("Missing Account Returns Zeros", test_suite.test_missing_account_returns_zeros),
        ("Missing Account No Warning When Disabled", test_suite.test_missing_account_no_warning_when_disabled),
        ("Missing N-2 Creates Empty Balance", test_suite.test_missing_n2_creates_empty_balance),
        ("Empty Balance Extraction Returns Zeros", test_suite.test_empty_balance_extraction_returns_zeros),
        ("Multiple Missing Accounts Emit Multiple Warnings", test_suite.test_multiple_missing_accounts_emit_multiple_warnings),
        ("Partial Data Continues Processing", test_suite.test_partial_data_continues_processing),
        ("Extract Multiple Accounts With Missing", test_suite.test_extraire_comptes_multiples_with_missing_accounts),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            print("-" * 70)
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {test_name}")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
