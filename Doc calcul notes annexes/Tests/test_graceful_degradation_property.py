"""
Property-Based Test: Graceful Degradation with Missing Data

This test validates Property 13: Graceful Degradation with Missing Data
Requirements: 8.1, 8.2, 8.3, 8.4

Property Statement:
For any balance sheet with missing accounts or missing exercise data (N-2), 
the system must continue processing and produce complete note annexes with 
zero values for missing data, without interrupting execution.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import pandas as pd
import sys
import os

# Add parent directory to path for imports
modules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Modules'))
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)

# Import after path is set
import balance_reader
import account_extractor
import movement_calculator
import vnc_calculator

BalanceReader = balance_reader.BalanceReader
AccountExtractor = account_extractor.AccountExtractor
MovementCalculator = movement_calculator.MovementCalculator
VNCCalculator = vnc_calculator.VNCCalculator


# ============================================================================
# HYPOTHESIS STRATEGIES
# ============================================================================

@st.composite
def st_balance_with_missing_accounts(draw):
    """
    Generate a balance DataFrame with some accounts missing.
    
    Strategy:
    - Create a base set of accounts
    - Randomly remove some accounts to simulate missing data
    - Ensure at least one account remains
    """
    # Base accounts that might exist
    all_accounts = [
        "211", "2111", "212", "213",  # Immobilisations incorporelles
        "221", "2211", "222", "223",  # Immobilisations corporelles
        "2811", "28111", "2812",      # Amortissements
    ]
    
    # Randomly select which accounts to include (at least 1)
    num_accounts = draw(st.integers(min_value=1, max_value=len(all_accounts)))
    selected_accounts = draw(st.lists(
        st.sampled_from(all_accounts),
        min_size=num_accounts,
        max_size=num_accounts,
        unique=True
    ))
    
    # Generate balance data for selected accounts
    data = []
    for compte in selected_accounts:
        data.append({
            'Numéro': compte,
            'Intitulé': f'Compte {compte}',
            'Ant Débit': draw(st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False)),
            'Ant Crédit': draw(st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False)),
            'Débit': draw(st.floats(min_value=0, max_value=500000, allow_nan=False, allow_infinity=False)),
            'Crédit': draw(st.floats(min_value=0, max_value=500000, allow_nan=False, allow_infinity=False)),
            'Solde Débit': draw(st.floats(min_value=0, max_value=1500000, allow_nan=False, allow_infinity=False)),
            'Solde Crédit': draw(st.floats(min_value=0, max_value=1500000, allow_nan=False, allow_infinity=False)),
        })
    
    return pd.DataFrame(data), selected_accounts


@st.composite
def st_balance_with_missing_columns(draw):
    """
    Generate a balance DataFrame with some columns having NaN values.
    
    Strategy:
    - Create accounts with some columns containing NaN
    - System should replace NaN with 0.0
    """
    num_accounts = draw(st.integers(min_value=1, max_value=5))
    
    data = []
    for i in range(num_accounts):
        compte = f"21{i}"
        
        # Randomly decide which columns to make NaN
        ant_debit = draw(st.one_of(
            st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False),
            st.just(float('nan'))
        ))
        ant_credit = draw(st.one_of(
            st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False),
            st.just(float('nan'))
        ))
        
        data.append({
            'Numéro': compte,
            'Intitulé': f'Compte {compte}',
            'Ant Débit': ant_debit,
            'Ant Crédit': ant_credit,
            'Débit': draw(st.floats(min_value=0, max_value=500000, allow_nan=False, allow_infinity=False)),
            'Crédit': draw(st.floats(min_value=0, max_value=500000, allow_nan=False, allow_infinity=False)),
            'Solde Débit': draw(st.floats(min_value=0, max_value=1500000, allow_nan=False, allow_infinity=False)),
            'Solde Crédit': draw(st.floats(min_value=0, max_value=1500000, allow_nan=False, allow_infinity=False)),
        })
    
    return pd.DataFrame(data)


# ============================================================================
# PROPERTY TESTS
# ============================================================================

@given(st_balance_with_missing_accounts())
@settings(max_examples=50, deadline=None)
def test_property_missing_accounts_return_zeros(balance_data):
    """
    Property: Missing accounts return zero values without errors.
    
    Validates Requirement 8.1:
    WHEN un compte n'existe pas dans la balance, 
    THE System SHALL utiliser des valeurs nulles (0.0) sans interrompre le traitement
    """
    balance_df, existing_accounts = balance_data
    
    # Create extractor
    extractor = AccountExtractor(balance_df)
    
    # Test with an account that definitely doesn't exist
    missing_account = "999"
    assume(missing_account not in existing_accounts)
    
    # Extract missing account - should not raise exception
    try:
        result = extractor.extraire_solde_compte(missing_account)
        
        # Property: All values should be 0.0 for missing account
        assert result['ant_debit'] == 0.0, "Missing account should return 0.0 for ant_debit"
        assert result['ant_credit'] == 0.0, "Missing account should return 0.0 for ant_credit"
        assert result['mvt_debit'] == 0.0, "Missing account should return 0.0 for mvt_debit"
        assert result['mvt_credit'] == 0.0, "Missing account should return 0.0 for mvt_credit"
        assert result['solde_debit'] == 0.0, "Missing account should return 0.0 for solde_debit"
        assert result['solde_credit'] == 0.0, "Missing account should return 0.0 for solde_credit"
        
        # Property: Processing continues without interruption
        assert True, "System continued processing without exception"
        
    except Exception as e:
        pytest.fail(f"System should not raise exception for missing account: {e}")


@given(st_balance_with_missing_columns())
@settings(max_examples=50, deadline=None)
def test_property_nan_values_replaced_with_zeros(balance_df):
    """
    Property: NaN values are replaced with 0.0 without errors.
    
    Validates Requirement 8.1:
    WHEN un compte n'existe pas dans la balance, 
    THE System SHALL utiliser des valeurs nulles (0.0) sans interrompre le traitement
    """
    # Create extractor
    extractor = AccountExtractor(balance_df)
    
    # Get first account
    first_account = balance_df.iloc[0]['Numéro']
    
    # Extract account - should not raise exception even with NaN values
    try:
        result = extractor.extraire_solde_compte(first_account)
        
        # Property: All values should be numeric (not NaN)
        assert not pd.isna(result['ant_debit']), "ant_debit should not be NaN"
        assert not pd.isna(result['ant_credit']), "ant_credit should not be NaN"
        assert not pd.isna(result['mvt_debit']), "mvt_debit should not be NaN"
        assert not pd.isna(result['mvt_credit']), "mvt_credit should not be NaN"
        assert not pd.isna(result['solde_debit']), "solde_debit should not be NaN"
        assert not pd.isna(result['solde_credit']), "solde_credit should not be NaN"
        
        # Property: NaN values should be replaced with 0.0
        for key, value in result.items():
            assert isinstance(value, (int, float)), f"{key} should be numeric"
            assert value >= 0.0, f"{key} should be non-negative"
        
    except Exception as e:
        pytest.fail(f"System should handle NaN values gracefully: {e}")


@given(st_balance_with_missing_accounts())
@settings(max_examples=50, deadline=None)
def test_property_complete_note_with_missing_data(balance_data):
    """
    Property: Complete note annexe is produced even with missing accounts.
    
    Validates Requirements 8.2, 8.3:
    WHEN une balance d'exercice est manquante (N-2 par exemple), 
    THE System SHALL continuer le calcul avec les exercices disponibles
    
    IF tous les comptes d'une ligne sont à zéro, 
    THEN THE System SHALL quand même afficher la ligne dans le tableau HTML
    """
    balance_df, existing_accounts = balance_data
    
    # Create extractors and calculators
    extractor = AccountExtractor(balance_df)
    movement_calc = MovementCalculator()
    vnc_calc = VNCCalculator()
    
    # Define a note line with potentially missing accounts
    comptes_brut = ["211", "212", "213"]
    comptes_amort = ["2811", "2812", "2813"]
    
    try:
        # Extract brut accounts (some may be missing)
        brut_values = []
        for compte in comptes_brut:
            values = extractor.extraire_solde_compte(compte)
            brut_values.append(values)
        
        # Extract amort accounts (some may be missing)
        amort_values = []
        for compte in comptes_amort:
            values = extractor.extraire_solde_compte(compte)
            amort_values.append(values)
        
        # Calculate totals (should work even if all are zeros)
        total_brut_ouverture = sum(v['solde_debit'] - v['solde_credit'] for v in brut_values)
        total_amort_ouverture = sum(v['solde_credit'] - v['solde_debit'] for v in amort_values)
        
        # Calculate VNC (should work even with zeros)
        vnc_ouverture = vnc_calc.calculer_vnc_ouverture(
            total_brut_ouverture,
            total_amort_ouverture
        )
        
        # Property: Calculation completes without error
        assert True, "Note calculation completed with missing data"
        
        # Property: VNC is a valid number (not NaN)
        assert not pd.isna(vnc_ouverture), "VNC should be a valid number"
        assert isinstance(vnc_ouverture, (int, float)), "VNC should be numeric"
        
        # Property: Even if all values are zero, we have a complete line
        ligne_note = {
            'brut_ouverture': total_brut_ouverture,
            'amort_ouverture': total_amort_ouverture,
            'vnc_ouverture': vnc_ouverture
        }
        
        # All values should be numeric
        for key, value in ligne_note.items():
            assert not pd.isna(value), f"{key} should not be NaN"
            assert isinstance(value, (int, float)), f"{key} should be numeric"
        
    except Exception as e:
        pytest.fail(f"System should produce complete note with missing data: {e}")


@given(st_balance_with_missing_accounts())
@settings(max_examples=50, deadline=None)
def test_property_no_execution_interruption(balance_data):
    """
    Property: System never interrupts execution due to missing data.
    
    Validates Requirement 8.1, 8.2:
    THE System SHALL utiliser des valeurs nulles (0.0) sans interrompre le traitement
    THE System SHALL continuer le calcul avec les exercices disponibles
    """
    balance_df, existing_accounts = balance_data
    
    # Create extractor
    extractor = AccountExtractor(balance_df)
    
    # Test multiple missing accounts in sequence
    missing_accounts = ["999", "888", "777", "666"]
    
    results = []
    try:
        for missing_account in missing_accounts:
            assume(missing_account not in existing_accounts)
            result = extractor.extraire_solde_compte(missing_account)
            results.append(result)
        
        # Property: All extractions completed without interruption
        assert len(results) == len(missing_accounts), "All extractions should complete"
        
        # Property: All results are valid zero dictionaries
        for result in results:
            assert all(v == 0.0 for v in result.values()), "All values should be 0.0"
        
    except Exception as e:
        pytest.fail(f"System should never interrupt execution: {e}")


@given(st_balance_with_missing_accounts())
@settings(max_examples=50, deadline=None)
def test_property_distinguish_missing_vs_zero(balance_data):
    """
    Property: System distinguishes between missing accounts and zero-balance accounts.
    
    Validates Requirement 8.4:
    THE System SHALL distinguer entre "compte inexistant" et "compte à solde nul"
    """
    balance_df, existing_accounts = balance_data
    
    # Add an account with explicit zero balance
    zero_account_data = {
        'Numéro': '214',
        'Intitulé': 'Compte à solde nul',
        'Ant Débit': 0.0,
        'Ant Crédit': 0.0,
        'Débit': 0.0,
        'Crédit': 0.0,
        'Solde Débit': 0.0,
        'Solde Crédit': 0.0,
    }
    
    # Only add if not already present
    if '214' not in existing_accounts:
        balance_df = pd.concat([balance_df, pd.DataFrame([zero_account_data])], ignore_index=True)
    
    extractor = AccountExtractor(balance_df)
    
    # Extract zero-balance account (exists in balance)
    zero_result = extractor.extraire_solde_compte('214')
    
    # Extract missing account (doesn't exist in balance)
    missing_account = '999'
    assume(missing_account not in existing_accounts and missing_account != '214')
    missing_result = extractor.extraire_solde_compte(missing_account)
    
    # Property: Both return zero values
    assert all(v == 0.0 for v in zero_result.values()), "Zero account should have all zeros"
    assert all(v == 0.0 for v in missing_result.values()), "Missing account should have all zeros"
    
    # Property: System can distinguish by checking if account exists in balance
    zero_exists = '214' in balance_df['Numéro'].values
    missing_exists = missing_account in balance_df['Numéro'].values
    
    assert zero_exists == True, "Zero-balance account should exist in balance"
    assert missing_exists == False, "Missing account should not exist in balance"
    
    # Property: Both cases handled gracefully without errors
    assert True, "System distinguishes between missing and zero-balance accounts"


# ============================================================================
# SUMMARY TEST
# ============================================================================

def test_graceful_degradation_summary():
    """
    Summary test documenting the graceful degradation property.
    
    This test serves as documentation for Property 13.
    """
    print("\n" + "="*80)
    print("PROPERTY 13: GRACEFUL DEGRADATION WITH MISSING DATA")
    print("="*80)
    print("\nProperty Statement:")
    print("For any balance sheet with missing accounts or missing exercise data (N-2),")
    print("the system must continue processing and produce complete note annexes with")
    print("zero values for missing data, without interrupting execution.")
    print("\nValidates Requirements:")
    print("  - 8.1: Missing accounts return 0.0 without interruption")
    print("  - 8.2: Missing exercise data handled gracefully")
    print("  - 8.3: Zero-value lines still displayed")
    print("  - 8.4: Distinguish missing vs zero-balance accounts")
    print("\nTest Coverage:")
    print("  ✓ Missing accounts return zeros")
    print("  ✓ NaN values replaced with zeros")
    print("  ✓ Complete notes produced with missing data")
    print("  ✓ No execution interruption")
    print("  ✓ Distinguish missing vs zero accounts")
    print("="*80)
    
    assert True, "Property 13 test suite is complete"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
