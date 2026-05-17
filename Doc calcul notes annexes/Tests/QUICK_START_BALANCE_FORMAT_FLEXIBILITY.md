# Quick Start: Balance Format Flexibility Property Test

**Property 21: Balance Format Flexibility**

**Validates: Requirements 14.1, 14.2, 14.3, 14.5, 14.6**

---

## What This Test Does

This property-based test validates that the Balance_Reader module can handle various balance file formats with flexibility:

✓ Column names with multiple spaces
✓ Different decimal separators (comma and period)
✓ Different thousand separators (space, comma, period, or none)
✓ Mixed format combinations

## Quick Run

### Option 1: Run All Tests
```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Tests
pytest test_balance_format_flexibility.py -v
```

### Option 2: Run Specific Test
```bash
pytest test_balance_format_flexibility.py::test_property_balance_format_flexibility -v
```

### Option 3: Direct Python Execution
```bash
python test_balance_format_flexibility.py
```

## What Gets Tested

### Test 1: Main Property Test (50 examples)
```
test_property_balance_format_flexibility
├─ Generates 50 random Excel files
├─ Each with different format combinations
├─ Verifies column normalization
├─ Verifies decimal separator handling
├─ Verifies thousand separator handling
└─ Verifies data integrity
```

### Test 2: Decimal Separator Test (20 examples)
```
test_property_decimal_separator_handling
├─ Tests 20 combinations of separators
├─ Verifies comma as decimal separator
├─ Verifies period as decimal separator
├─ Verifies thousand separators don't interfere
└─ Verifies no NaN values introduced
```

### Test 3: Demo File Validation
```
test_property_format_flexibility_with_demo_file
├─ Loads P000 -BALANCE DEMO N_N-1_N-2.xls
├─ Verifies all monetary columns are numeric
├─ Verifies no NaN values
├─ Verifies all values >= 0
└─ Validates all three balances (N, N-1, N-2)
```

## Expected Output

```
test_balance_format_flexibility.py::test_property_balance_format_flexibility PASSED
test_balance_format_flexibility.py::test_property_decimal_separator_handling PASSED
test_balance_format_flexibility.py::test_property_format_flexibility_with_demo_file PASSED

✓ Propriété de flexibilité de format validée avec le fichier de démonstration
  - Balance N:   XXX comptes, tous les montants numériques
  - Balance N-1: XXX comptes, tous les montants numériques
  - Balance N-2: XXX comptes, tous les montants numériques

======================== 3 passed in X.XXs ========================
```

## Format Examples Tested

### Decimal Separators
- `1000.50` (period)
- `1000,50` (comma)

### Thousand Separators
- `1 000.50` (space)
- `1,000.50` (comma)
- `1.000,50` (period)
- `1000.50` (none)

### Column Names
- `Ant  Débit` (double space)
- `Ant   Débit` (triple space)
- ` Ant Débit ` (leading/trailing spaces)

## Troubleshooting

### Test Fails: "File not found"
**Solution**: Make sure the demo file exists at:
```
py_backend/P000 -BALANCE DEMO N_N-1_N-2.xls
```

### Test Fails: "Module not found"
**Solution**: Run from the correct directory:
```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Tests
```

### Test Fails: "Hypothesis deadline exceeded"
**Solution**: This is normal for property-based tests. The deadline is set to 60 seconds.
If it consistently fails, try:
```bash
pytest test_balance_format_flexibility.py -v --hypothesis-seed=0
```

### Test Fails: "NaN values in column"
**Solution**: This indicates the Balance_Reader is not correctly handling the format.
Check that the `convertir_montants()` method properly handles:
- Comma as decimal separator
- Thousand separators (space, comma, period)

## Key Validations

### Column Normalization
```python
# Before: 'Ant  Débit', ' Ant Débit ', 'Ant   Débit'
# After:  'Ant Débit', 'Ant Débit', 'Ant Débit'
```

### Decimal Separator Handling
```python
# Input: '1000,50' (comma)
# Output: 1000.5 (float)

# Input: '1000.50' (period)
# Output: 1000.5 (float)
```

### Thousand Separator Handling
```python
# Input: '1 000,50' (space + comma)
# Output: 1000.5 (float)

# Input: '1,000.50' (comma + period)
# Output: 1000.5 (float)
```

## Test Statistics

| Metric | Value |
|--------|-------|
| Total Examples | 70 (50 + 20) |
| Decimal Separators Tested | 2 (comma, period) |
| Thousand Separators Tested | 4 (space, comma, period, none) |
| Format Combinations | 8 (2 × 4) |
| Column Variations | Multiple (spaces, leading, trailing) |
| Timeout per Test | 60 seconds |

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Balance Format Flexibility Tests
  run: |
    cd py_backend/Doc\ calcul\ notes\ annexes/Tests
    pytest test_balance_format_flexibility.py -v
```

### Local Pre-commit Hook
```bash
#!/bin/bash
pytest py_backend/Doc\ calcul\ notes\ annexes/Tests/test_balance_format_flexibility.py -v
```

## Related Documentation

- **Property Test Summary**: `PROPERTY_TEST_BALANCE_FORMAT_FLEXIBILITY_SUMMARY.md`
- **Balance_Reader Module**: `../Modules/balance_reader.py`
- **Requirements**: `../../../.kiro/specs/calcul-notes-annexes-syscohada/requirements.md`
- **Design Document**: `../../../.kiro/specs/calcul-notes-annexes-syscohada/design.md`

## Next Steps

After this test passes:

1. **Task 25**: Checkpoint - Ensure integration and flexibility features work
2. **Task 26**: Create comprehensive documentation
3. **Task 27**: Create test infrastructure and fixtures
4. **Task 28**: Implement error handling and logging
5. **Task 29**: Optimize performance
6. **Task 30**: Final integration and end-to-end testing

## Questions?

For more information about:
- **Property-Based Testing**: See `PROPERTY_TEST_BALANCE_FORMAT_FLEXIBILITY_SUMMARY.md`
- **Balance_Reader Implementation**: See `../Modules/balance_reader.py`
- **Requirements**: See `../../../.kiro/specs/calcul-notes-annexes-syscohada/requirements.md`
