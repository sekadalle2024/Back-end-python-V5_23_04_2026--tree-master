# Quick Start Guide - Graceful Degradation (Task 28.4)

## Overview

This guide explains how to use the graceful degradation features implemented in Task 28.4 for handling missing data in the SYSCOHADA notes annexes calculation system.

## Features Implemented

### 1. Missing Account Handling (Requirement 8.1)

The system now handles missing accounts gracefully by:
- Returning zero values for all monetary fields
- Emitting warnings to `calcul_notes_warnings.log`
- Continuing processing without interruption

**Example:**
```python
from account_extractor import AccountExtractor

extractor = AccountExtractor(balance_n)

# Extract non-existent account - returns zeros with warning
soldes = extractor.extraire_solde_compte("999", note_numero="3A")
# Result: {'ant_debit': 0.0, 'ant_credit': 0.0, ..., 'solde_credit': 0.0}
```

### 2. Missing N-2 Exercise Handling (Requirement 8.2)

The system handles missing N-2 exercise gracefully by:
- Creating an empty balance DataFrame with correct structure
- Logging a warning about the missing exercise
- Continuing calculation with N and N-1 only

**Example:**
```python
from balance_reader import BalanceReader

reader = BalanceReader("balance_sans_n2.xlsx")

# Loads N and N-1, creates empty N-2
balance_n, balance_n1, balance_n2 = reader.charger_balances()
# balance_n2 is empty but has correct columns
```

### 3. Configurable Warning Emission (Requirement 8.3)

Warnings can be disabled for specific operations:

**Example:**
```python
# With warnings (default)
soldes = extractor.extraire_solde_compte("999", note_numero="3A", emit_warning=True)

# Without warnings
soldes = extractor.extraire_solde_compte("999", emit_warning=False)
```

### 4. Distinction Between Missing and Zero Balance (Requirement 8.4)

The system distinguishes between:
- **Missing account**: Not found in balance → Warning emitted
- **Zero balance account**: Found in balance with zero values → No warning

## Running Tests

### Quick Test
```bash
cd "py_backend/Doc calcul notes annexes/Tests"
python test_graceful_degradation.py
```

### Expected Output
```
======================================================================
GRACEFUL DEGRADATION TESTS - Task 28.4
======================================================================

Running: Missing Account Returns Zeros
----------------------------------------------------------------------
✓ Test passed: Missing account returns zeros with warning

Running: Missing Account No Warning When Disabled
----------------------------------------------------------------------
✓ Test passed: Missing account warnings can be disabled

...

======================================================================
TEST RESULTS: 7 passed, 0 failed
======================================================================
```

## Integration with Existing Code

### Balance Reader Changes

The `BalanceReader.charger_balances()` method now:
1. Accepts `graceful_n2=True` parameter (enabled by default)
2. Returns empty DataFrame for N-2 if missing
3. Logs warning instead of raising exception

### Account Extractor Changes

The `AccountExtractor.extraire_solde_compte()` method now:
1. Accepts `note_numero` parameter for better logging
2. Accepts `emit_warning` parameter to control warnings
3. Emits `MissingAccountWarning` for missing accounts
4. Returns zeros for all fields when account not found

### Custom Warnings

New warning class `MissingAccountWarning` provides:
- Structured warning information
- Automatic logging to `calcul_notes_warnings.log`
- Context information (account number, note number, impact)

## Best Practices

### 1. Always Provide Note Number
```python
# Good - provides context for warnings
soldes = extractor.extraire_solde_compte("211", note_numero="3A")

# Less informative
soldes = extractor.extraire_solde_compte("211")
```

### 2. Check for Empty Balances
```python
if len(balance_n2) == 0:
    print("⚠ N-2 exercise not available - using N and N-1 only")
```

### 3. Review Warning Logs
```python
# Check warning log after processing
with open("calcul_notes_warnings.log", "r") as f:
    warnings = f.read()
    if "MissingAccountWarning" in warnings:
        print("⚠ Some accounts were missing during calculation")
```

## Error Handling Strategy

The system follows this strategy:

| Situation | Behavior | User Impact |
|-----------|----------|-------------|
| Missing account | Return zeros + warn | Calculation continues |
| Missing N-2 | Empty balance + warn | Calculation continues |
| Missing N or N-1 | Raise exception | Calculation stops |
| Invalid format | Raise exception | Calculation stops |

## Troubleshooting

### Problem: Too many missing account warnings

**Solution:** Review your balance file to ensure all expected accounts are present.

### Problem: N-2 always empty

**Solution:** Check that your Excel file has a worksheet named "BALANCE N-2" or similar.

### Problem: Warnings not appearing in log

**Solution:** Ensure logging is configured correctly:
```python
import logging
logging.basicConfig(
    filename='calcul_notes_warnings.log',
    level=logging.WARNING
)
```

## Requirements Validation

| Requirement | Implementation | Test Coverage |
|-------------|----------------|---------------|
| 8.1 - Missing accounts with zeros | ✓ `AccountExtractor.extraire_solde_compte()` | ✓ `test_missing_account_returns_zeros` |
| 8.2 - Missing N-2 gracefully | ✓ `BalanceReader.charger_balances()` | ✓ `test_missing_n2_creates_empty_balance` |
| 8.3 - Continue with warnings | ✓ `MissingAccountWarning` | ✓ `test_multiple_missing_accounts_emit_multiple_warnings` |
| 8.4 - Distinguish missing vs zero | ✓ Account filtering logic | ✓ `test_partial_data_continues_processing` |

## Next Steps

After implementing graceful degradation:
1. Run all integration tests to ensure compatibility
2. Review warning logs from real balance files
3. Update documentation for end users
4. Consider implementing optional property tests (Task 28.5, 28.6)

## Related Documentation

- `custom_warnings.py` - Warning class definitions
- `custom_exceptions.py` - Exception class definitions
- `logging_config.py` - Logging infrastructure (Task 28.1)
- `TROUBLESHOOTING.md` - Common issues and solutions
