# Property Test Summary: Warning Logging Completeness

## Property Statement

**Property 14: Warning Logging Completeness**

*For any* warning emitted during processing (incoherent balances, negative VNC, abnormal account balances), the system must log it to `calcul_notes_warnings.log` with timestamp and details.

**Validates: Requirements 3.6, 4.7, 8.5, 8.6**

## Test Strategy

This property test uses Hypothesis to generate various warning scenarios and verify that:

1. **Every warning is logged** - No warnings are lost
2. **Complete information is captured** - All context fields are present
3. **Consistent format** - All log entries follow the same structure
4. **No duplication** - Each warning appears exactly once
5. **Proper timestamps** - All entries have valid timestamps

## Test Coverage

### Warning Types Tested

1. **IncoherentBalanceWarning** (Requirement 3.6, 8.5)
   - Validates: Solde_Cloture ≠ Solde_Ouverture + Augmentations - Diminutions
   - Context: compte, solde_ouverture, augmentations, diminutions, solde_cloture, ecart, note_numero

2. **NegativeVNCWarning** (Requirement 4.7, 8.5)
   - Validates: VNC = Brut - Amortissement < 0
   - Context: libelle, brut, amortissement, vnc, note_numero

3. **AbnormalAccountBalanceWarning** (Requirement 8.5, 8.6)
   - Validates: Accounts with both debit and credit balances or unexpected signs
   - Context: compte, solde_debit, solde_credit, raison, note_numero

4. **MissingAccountWarning** (Requirement 8.5, 8.6)
   - Validates: Expected accounts not found in balance
   - Context: compte, note_numero, impact

5. **LowCoherenceRateWarning** (Requirement 8.5, 8.6)
   - Validates: Global coherence rate < 95%
   - Context: taux_coherence, seuil, details

## Hypothesis Strategies

### Data Generation

```python
# Account numbers (SYSCOHADA format)
compte_strategy() -> str  # e.g., "211", "2811", "41"

# Monetary amounts
montant_strategy() -> float  # Range: -1M to +1M

# Note numbers
note_numero_strategy() -> str | None  # e.g., "3A", "12", None

# Incoherent balance data
incoherent_balance_data() -> dict
# Generates: compte, solde_ouverture, augmentations, diminutions, 
#            solde_cloture (with intentional discrepancy), ecart

# Negative VNC data
negative_vnc_data() -> dict
# Generates: libelle, brut, amortissement (> brut), vnc (< 0)

# Abnormal balance data
abnormal_balance_data() -> dict
# Generates: compte, solde_debit, solde_credit, raison

# Missing account data
missing_account_data() -> dict
# Generates: compte, note_numero, impact

# Low coherence data
low_coherence_data() -> dict
# Generates: taux_coherence (< 95%), seuil, details
```

## Property Tests

### 1. Individual Warning Type Completeness

Each warning type has a dedicated property test:

```python
@given(data=incoherent_balance_data())
def test_incoherent_balance_logged_completely(data, logging_config, warnings_log_file):
    """Verify IncoherentBalanceWarning is logged with all context"""
```

**Assertions:**
- Warning type name appears in log
- All context fields are present
- Timestamp is included
- Log level is WARNING

### 2. Multiple Warnings Logging

```python
@given(warnings_list=st.lists(st.one_of(...), min_size=1, max_size=10))
def test_multiple_warnings_all_logged(warnings_list, logging_config, warnings_log_file):
    """Verify all warnings in a batch are logged"""
```

**Assertions:**
- Number of log entries equals number of warnings emitted
- No warnings are lost
- Order is preserved

### 3. Log Format Consistency

```python
@given(data=incoherent_balance_data())
def test_warning_log_format_consistency(data, logging_config, warnings_log_file):
    """Verify consistent log format across all warnings"""
```

**Expected Format:**
```
YYYY-MM-DD HH:MM:SS | WARNING | logger_name | function:line | [WarningType] message | Context: key=value, ...
```

**Assertions:**
- Pipe separators present
- Timestamp format valid (YYYY-MM-DD HH:MM:SS)
- Log level is WARNING
- At least 4 parts in log line

### 4. Context Completeness

```python
@given(data=negative_vnc_data())
def test_warning_context_completeness(data, logging_config, warnings_log_file):
    """Verify all context fields are included in log"""
```

**Assertions:**
- All required context keys present (libelle=, brut=, amortissement=, vnc=)
- Optional fields included when provided (note_numero=)
- Values are correctly formatted

### 5. No Duplication

```python
@given(data=missing_account_data())
def test_no_warning_duplication(data, logging_config, warnings_log_file):
    """Verify each warning is logged exactly once"""
```

**Assertions:**
- Warning type name appears exactly once
- No duplicate log entries

## Edge Cases Tested

### 1. None Values
- Warnings with `note_numero=None` are logged correctly
- None values appear as "note_numero=None" in context

### 2. Special Characters
- Account numbers with hyphens: "401-FOURNISSEUR"
- French characters in descriptions: "é, à, ç"
- UTF-8 encoding is preserved

### 3. Large Amounts
- Very large monetary values (999,999,999.99)
- Negative values
- Precision is maintained

## Test Configuration

```python
@settings(max_examples=50, deadline=None)  # Individual tests
@settings(max_examples=20, deadline=None)  # Multiple warnings tests
```

- **max_examples**: Number of random test cases to generate
- **deadline**: No time limit (some tests involve file I/O)

## Fixtures

### temp_log_dir
Creates temporary directory for log files, cleaned up after tests.

### logging_config
Configures logging system with temporary directory.

### warnings_log_file
Provides path to `calcul_notes_warnings.log` in temp directory.

## Running the Tests

```bash
# Run with verbose output and Hypothesis statistics
pytest test_warning_logging_completeness.py -v --hypothesis-show-statistics

# Run specific test
pytest test_warning_logging_completeness.py::TestWarningLoggingCompleteness::test_incoherent_balance_logged_completely -v

# Run with increased examples
pytest test_warning_logging_completeness.py --hypothesis-max-examples=100 -v
```

## Expected Results

All property tests should pass, demonstrating that:

1. ✅ Every warning type is logged completely
2. ✅ All context information is captured
3. ✅ Log format is consistent
4. ✅ No warnings are lost or duplicated
5. ✅ Timestamps are always present
6. ✅ Edge cases are handled correctly

## Integration with Requirements

| Requirement | Validation Method |
|-------------|-------------------|
| 3.6 | IncoherentBalanceWarning logged with ecart details |
| 4.7 | NegativeVNCWarning logged with VNC calculation details |
| 8.5 | All warnings logged to calcul_notes_warnings.log |
| 8.6 | Warnings include timestamp and complete context |

## Maintenance Notes

- Tests use temporary directories to avoid polluting the file system
- Each test clears the log file before emitting warnings
- Hypothesis generates diverse test cases automatically
- Add new warning types by creating corresponding strategies and tests
