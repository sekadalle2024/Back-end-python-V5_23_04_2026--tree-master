# Quick Start: Property Test - Graceful Degradation

## Overview

This property test validates **Property 13: Graceful Degradation with Missing Data**.

**Property Statement:**
> For any balance sheet with missing accounts or missing exercise data (N-2), the system must continue processing and produce complete note annexes with zero values for missing data, without interrupting execution.

**Validates Requirements:** 8.1, 8.2, 8.3, 8.4

## Running the Test

### Quick Run
```powershell
# Run the property test
pytest py_backend/Doc` calcul` notes` annexes/Tests/test_graceful_degradation_property.py -v
```

### With Coverage
```powershell
# Run with detailed output
pytest py_backend/Doc` calcul` notes` annexes/Tests/test_graceful_degradation_property.py -v --tb=short

# Run with hypothesis statistics
pytest py_backend/Doc` calcul` notes` annexes/Tests/test_graceful_degradation_property.py -v --hypothesis-show-statistics
```

## What This Test Validates

### 1. Missing Accounts Return Zeros (Req 8.1)
- **Property:** When an account doesn't exist in the balance, the system returns 0.0 for all values
- **Test:** `test_property_missing_accounts_return_zeros`
- **Validates:** No exceptions raised, all values are 0.0

### 2. NaN Values Replaced (Req 8.1)
- **Property:** NaN values in balance columns are replaced with 0.0
- **Test:** `test_property_nan_values_replaced_with_zeros`
- **Validates:** No NaN values in results, all numeric

### 3. Complete Notes with Missing Data (Req 8.2, 8.3)
- **Property:** Complete note annexe is produced even when accounts are missing
- **Test:** `test_property_complete_note_with_missing_data`
- **Validates:** Calculations complete, VNC is valid, all lines present

### 4. No Execution Interruption (Req 8.1, 8.2)
- **Property:** System never interrupts execution due to missing data
- **Test:** `test_property_no_execution_interruption`
- **Validates:** Multiple missing accounts handled in sequence

### 5. Distinguish Missing vs Zero (Req 8.4)
- **Property:** System distinguishes between missing accounts and zero-balance accounts
- **Test:** `test_property_distinguish_missing_vs_zero`
- **Validates:** Both return zeros, but system knows which exists

## Test Strategies

### Strategy 1: Balance with Missing Accounts
```python
@st.composite
def st_balance_with_missing_accounts(draw):
    """
    Generates balances with randomly missing accounts.
    - Selects subset of possible accounts
    - Ensures at least 1 account present
    - Returns balance + list of existing accounts
    """
```

### Strategy 2: Balance with NaN Values
```python
@st.composite
def st_balance_with_missing_columns(draw):
    """
    Generates balances with NaN in some columns.
    - Randomly assigns NaN to Ant Débit/Crédit
    - Tests system's NaN handling
    """
```

## Expected Results

### ✅ Success Criteria
- All property tests pass with 50 examples each
- No exceptions raised for missing accounts
- All missing values replaced with 0.0
- Complete note annexes produced
- System distinguishes missing vs zero accounts

### 📊 Example Output
```
test_graceful_degradation_property.py::test_property_missing_accounts_return_zeros PASSED
test_graceful_degradation_property.py::test_property_nan_values_replaced_with_zeros PASSED
test_graceful_degradation_property.py::test_property_complete_note_with_missing_data PASSED
test_graceful_degradation_property.py::test_property_no_execution_interruption PASSED
test_graceful_degradation_property.py::test_property_distinguish_missing_vs_zero PASSED
test_graceful_degradation_property.py::test_graceful_degradation_summary PASSED

======================== 6 passed in 15.23s ========================
```

## Troubleshooting

### Issue: Tests fail with NaN errors
**Solution:** Check that `AccountExtractor` properly handles NaN values:
```python
# In account_extractor.py
df = df.fillna(0.0)  # Replace NaN with 0.0
```

### Issue: Tests fail with KeyError
**Solution:** Ensure missing accounts return default dictionary:
```python
# In account_extractor.py
if compte_df.empty:
    return {
        'ant_debit': 0.0,
        'ant_credit': 0.0,
        'mvt_debit': 0.0,
        'mvt_credit': 0.0,
        'solde_debit': 0.0,
        'solde_credit': 0.0
    }
```

### Issue: Tests timeout
**Solution:** Reduce max_examples or increase deadline:
```python
@settings(max_examples=20, deadline=5000)  # 5 second deadline
```

## Integration with Other Tests

This property test complements:
- **test_account_extractor_missing_accounts.py** - Unit tests for missing accounts
- **test_graceful_degradation.py** - Integration tests for graceful degradation
- **test_custom_warnings.py** - Warning system for missing data

## Requirements Traceability

| Requirement | Description | Test Method |
|-------------|-------------|-------------|
| 8.1 | Missing accounts return 0.0 | `test_property_missing_accounts_return_zeros` |
| 8.1 | NaN values replaced | `test_property_nan_values_replaced_with_zeros` |
| 8.2 | Continue with available exercises | `test_property_complete_note_with_missing_data` |
| 8.3 | Display zero-value lines | `test_property_complete_note_with_missing_data` |
| 8.4 | Distinguish missing vs zero | `test_property_distinguish_missing_vs_zero` |

## Next Steps

After this test passes:
1. ✅ Task 28.5 completed
2. ➡️ Continue to Task 28.6 (optional): Warning logging completeness
3. ➡️ Or proceed to Task 29: Performance optimization

## Documentation

- **Property Definition:** See `design.md` - Property 13
- **Requirements:** See `requirements.md` - Requirement 8
- **Implementation:** See `Modules/account_extractor.py`
