# Quick Start: Warning Logging Completeness Property Test

## Overview

This property test validates that all warnings emitted during SYSCOHADA notes calculation are logged completely to `calcul_notes_warnings.log` with timestamps and full context.

**Property 14: Warning Logging Completeness**  
**Validates: Requirements 3.6, 4.7, 8.5, 8.6**

## Quick Test

```bash
# Navigate to tests directory
cd "py_backend/Doc calcul notes annexes/Tests"

# Run the property test
pytest test_warning_logging_completeness.py -v

# Run with Hypothesis statistics
pytest test_warning_logging_completeness.py -v --hypothesis-show-statistics
```

## What This Test Does

The test uses **Hypothesis** to generate random warning scenarios and verifies:

1. ✅ **Every warning is logged** - No warnings are lost
2. ✅ **Complete context** - All fields (compte, montants, note_numero) are captured
3. ✅ **Consistent format** - Timestamp | WARNING | Logger | Message | Context
4. ✅ **No duplication** - Each warning appears exactly once
5. ✅ **All warning types** - Tests 5 different warning classes

## Warning Types Tested

| Warning Type | Requirement | What It Validates |
|--------------|-------------|-------------------|
| IncoherentBalanceWarning | 3.6, 8.5 | Balance equation coherence |
| NegativeVNCWarning | 4.7, 8.5 | Negative net book values |
| AbnormalAccountBalanceWarning | 8.5, 8.6 | Unusual account balances |
| MissingAccountWarning | 8.5, 8.6 | Missing accounts in balance |
| LowCoherenceRateWarning | 8.5, 8.6 | Inter-note coherence < 95% |

## Example Test Output

```
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_incoherent_balance_logged_completely PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_negative_vnc_logged_completely PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_abnormal_balance_logged_completely PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_missing_account_logged_completely PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_low_coherence_logged_completely PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_multiple_warnings_all_logged PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_warning_log_format_consistency PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_warning_context_completeness PASSED
test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_no_warning_duplication PASSED

======================== 9 passed in 12.34s ========================
```

## Expected Log Format

Each warning should be logged in this format:

```
2026-04-29 14:30:15 | WARNING  | calcul_notes_warnings | warn_incoherent_balance:123 | [IncoherentBalanceWarning] Balance incoherente pour compte '211': Solde cloture attendu = 1300.00, Solde cloture reel = 1250.00, Ecart = 50.00 | Context: compte=211, solde_ouverture=1000.0, augmentations=500.0, diminutions=200.0, solde_cloture=1250.0, ecart=50.0, note_numero=3A
```

**Components:**
1. **Timestamp**: `2026-04-29 14:30:15`
2. **Level**: `WARNING`
3. **Logger**: `calcul_notes_warnings`
4. **Location**: `warn_incoherent_balance:123`
5. **Message**: `[IncoherentBalanceWarning] Balance incoherente...`
6. **Context**: `Context: compte=211, solde_ouverture=1000.0, ...`

## Running Specific Tests

```bash
# Test only IncoherentBalanceWarning
pytest test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_incoherent_balance_logged_completely -v

# Test only NegativeVNCWarning
pytest test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_negative_vnc_logged_completely -v

# Test multiple warnings scenario
pytest test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_multiple_warnings_all_logged -v

# Test edge cases
pytest test_warning_logging_completeness.py::TestWarningLoggingEdgeCases -v
```

## Adjusting Test Parameters

Modify Hypothesis settings in the test file:

```python
@settings(max_examples=100, deadline=None)  # More test cases
@settings(max_examples=10, deadline=None)   # Faster testing
```

## Common Issues

### Issue 1: Log File Not Found
**Symptom**: `AssertionError: Warnings log file should exist`

**Solution**: Ensure logging is configured before emitting warnings. The test fixtures handle this automatically.

### Issue 2: Missing Context Fields
**Symptom**: `AssertionError: Context should include libelle`

**Solution**: Verify that the warning class includes all required context fields in its `__init__` method.

### Issue 3: Duplicate Warnings
**Symptom**: `AssertionError: Warning should appear exactly once, found 2 times`

**Solution**: Check that warnings are not being emitted multiple times in the code path.

## Integration with CI/CD

Add to your test pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Warning Logging Property Tests
  run: |
    cd "py_backend/Doc calcul notes annexes/Tests"
    pytest test_warning_logging_completeness.py -v --hypothesis-show-statistics
```

## Next Steps

After this test passes:

1. ✅ Task 28.6 complete - Warning logging completeness validated
2. ➡️ Continue to Task 29: Performance optimization
3. 📝 Review warning logs in production to ensure completeness

## Related Files

- **Test File**: `test_warning_logging_completeness.py`
- **Warning Classes**: `../Modules/custom_warnings.py`
- **Logging Config**: `../Modules/logging_config.py`
- **Summary**: `PROPERTY_TEST_WARNING_LOGGING_COMPLETENESS_SUMMARY.md`

## Questions?

- Check the detailed summary: `PROPERTY_TEST_WARNING_LOGGING_COMPLETENESS_SUMMARY.md`
- Review warning system tests: `test_custom_warnings.py`
- Review logging config tests: `test_logging_config.py`
