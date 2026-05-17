# Property Test Summary: Graceful Degradation with Missing Data

## Property 13: Graceful Degradation

### Property Statement
**For any** balance sheet with missing accounts or missing exercise data (N-2), the system **must** continue processing and produce complete note annexes with zero values for missing data, **without** interrupting execution.

### Requirements Validated
- **Requirement 8.1:** Missing accounts return 0.0 without interruption
- **Requirement 8.2:** Missing exercise data handled gracefully
- **Requirement 8.3:** Zero-value lines still displayed in output
- **Requirement 8.4:** Distinguish between missing and zero-balance accounts

---

## Test Coverage

### Test 1: Missing Accounts Return Zeros
**Function:** `test_property_missing_accounts_return_zeros`

**Property Tested:**
- Missing accounts return dictionary with all values = 0.0
- No exceptions raised
- Processing continues

**Strategy:**
- Generate balance with randomly selected accounts
- Query for account that doesn't exist
- Verify all 6 values are 0.0

**Example:**
```python
# Balance has accounts: ["211", "212", "221"]
# Query for account "999" (missing)
result = extractor.extraire_solde_compte("999")
# Expected: {'ant_debit': 0.0, 'ant_credit': 0.0, ...}
```

---

### Test 2: NaN Values Replaced with Zeros
**Function:** `test_property_nan_values_replaced_with_zeros`

**Property Tested:**
- NaN values in balance columns are replaced with 0.0
- No NaN values propagate to results
- All values are numeric

**Strategy:**
- Generate balance with some NaN values
- Extract accounts with NaN columns
- Verify no NaN in results

**Example:**
```python
# Balance has: Ant Débit = NaN, Ant Crédit = 1000.0
result = extractor.extraire_solde_compte("211")
# Expected: ant_debit = 0.0 (not NaN)
```

---

### Test 3: Complete Notes with Missing Data
**Function:** `test_property_complete_note_with_missing_data`

**Property Tested:**
- Complete note annexe produced even with missing accounts
- VNC calculations work with zero values
- All line items present in output

**Strategy:**
- Define note line with multiple accounts (some missing)
- Extract all accounts (missing return zeros)
- Calculate totals and VNC
- Verify complete line produced

**Example:**
```python
# Note line needs: ["211", "212", "213"]
# Balance only has: ["211"]
# Missing ["212", "213"] return zeros
# Total = value_211 + 0.0 + 0.0
# VNC calculated successfully
```

---

### Test 4: No Execution Interruption
**Function:** `test_property_no_execution_interruption`

**Property Tested:**
- System never interrupts execution due to missing data
- Multiple missing accounts handled in sequence
- All extractions complete

**Strategy:**
- Query multiple missing accounts in sequence
- Verify all complete without exception
- Verify all return zero dictionaries

**Example:**
```python
# Query 4 missing accounts: ["999", "888", "777", "666"]
# All complete successfully
# All return zeros
```

---

### Test 5: Distinguish Missing vs Zero
**Function:** `test_property_distinguish_missing_vs_zero`

**Property Tested:**
- System distinguishes missing accounts from zero-balance accounts
- Both return zero values
- System knows which exists in balance

**Strategy:**
- Add account with explicit zero balance
- Query zero-balance account (exists)
- Query missing account (doesn't exist)
- Verify both return zeros
- Verify system can check existence

**Example:**
```python
# Account "214" exists with all zeros
# Account "999" doesn't exist
# Both return: {'ant_debit': 0.0, ...}
# But: "214" in balance.Numéro = True
#      "999" in balance.Numéro = False
```

---

## Hypothesis Strategies

### Strategy 1: Balance with Missing Accounts
```python
@st.composite
def st_balance_with_missing_accounts(draw):
    """
    Generates balance with randomly selected subset of accounts.
    
    Parameters:
    - All possible accounts: ["211", "212", "221", "2811", ...]
    - Randomly select 1 to N accounts to include
    - Generate valid monetary values for selected accounts
    
    Returns:
    - DataFrame with selected accounts
    - List of existing account numbers
    """
```

### Strategy 2: Balance with NaN Values
```python
@st.composite
def st_balance_with_missing_columns(draw):
    """
    Generates balance with NaN in some columns.
    
    Parameters:
    - Create 1-5 accounts
    - Randomly assign NaN to Ant Débit/Crédit
    - Other columns have valid values
    
    Returns:
    - DataFrame with some NaN values
    """
```

---

## Test Execution

### Command
```bash
pytest py_backend/Doc` calcul` notes` annexes/Tests/test_graceful_degradation_property.py -v
```

### Expected Output
```
test_graceful_degradation_property.py::test_property_missing_accounts_return_zeros PASSED [16%]
test_graceful_degradation_property.py::test_property_nan_values_replaced_with_zeros PASSED [33%]
test_graceful_degradation_property.py::test_property_complete_note_with_missing_data PASSED [50%]
test_graceful_degradation_property.py::test_property_no_execution_interruption PASSED [66%]
test_graceful_degradation_property.py::test_property_distinguish_missing_vs_zero PASSED [83%]
test_graceful_degradation_property.py::test_graceful_degradation_summary PASSED [100%]

======================== 6 passed in 15.23s ========================
```

---

## Success Criteria

### ✅ All Tests Pass
- 50 examples per property test
- No exceptions raised
- All assertions pass

### ✅ Graceful Degradation Verified
- Missing accounts return zeros
- NaN values replaced
- Complete notes produced
- No execution interruption
- Missing vs zero distinguished

### ✅ Requirements Satisfied
- **8.1:** ✓ Missing accounts handled
- **8.2:** ✓ Missing exercise data handled
- **8.3:** ✓ Zero-value lines displayed
- **8.4:** ✓ Missing vs zero distinguished

---

## Integration Points

### Modules Tested
- `balance_reader.py` - NaN handling
- `account_extractor.py` - Missing account handling
- `movement_calculator.py` - Zero value calculations
- `vnc_calculator.py` - VNC with zero values

### Related Tests
- `test_account_extractor_missing_accounts.py` - Unit tests
- `test_graceful_degradation.py` - Integration tests
- `test_custom_warnings.py` - Warning system

---

## Failure Scenarios

### Scenario 1: Exception on Missing Account
**Symptom:** Test fails with KeyError or AttributeError
**Cause:** `AccountExtractor` doesn't handle missing accounts
**Fix:** Return default zero dictionary for missing accounts

### Scenario 2: NaN Propagation
**Symptom:** Test fails with "NaN should not be present"
**Cause:** NaN values not replaced in balance loading
**Fix:** Add `df.fillna(0.0)` in `BalanceReader`

### Scenario 3: Incomplete Note
**Symptom:** Test fails with missing line items
**Cause:** Zero-value lines filtered out
**Fix:** Display all lines regardless of value

---

## Documentation References

- **Design Document:** `design.md` - Property 13
- **Requirements:** `requirements.md` - Requirement 8
- **Implementation:** `Modules/account_extractor.py`
- **Quick Start:** `QUICK_START_GRACEFUL_DEGRADATION_PROPERTY.md`

---

## Task Completion

**Task 28.5:** Write property test for graceful degradation ✅

**Deliverables:**
1. ✅ `test_graceful_degradation_property.py` - Property tests
2. ✅ `QUICK_START_GRACEFUL_DEGRADATION_PROPERTY.md` - Quick start guide
3. ✅ `PROPERTY_TEST_GRACEFUL_DEGRADATION_SUMMARY.md` - This summary

**Next Steps:**
- Task 28.6 (optional): Warning logging completeness
- Task 29: Performance optimization
