# Property Test: Balance Format Flexibility

**Property 21: Balance Format Flexibility**

**Validates: Requirements 14.1, 14.2, 14.3, 14.5, 14.6**

**Date: 28 Avril 2026**

---

## Overview

This property-based test validates that the Balance_Reader module can handle various balance file formats with flexibility, including:

- Column name variations (multiple spaces, leading/trailing spaces)
- Different decimal separators (comma and period)
- Different thousand separators (space, comma, period, or none)
- Mixed format combinations within the same file

## Property Statement

**For any balance file with column name variations (multiple spaces, different separators), the Balance_Parser must automatically detect and normalize column names, and must accept both comma and period as decimal separators, and must accept formats of numbers with or without thousand separators.**

## Requirements Validated

| Requirement | Description |
|-------------|-------------|
| 14.1 | WHEN une balance est chargée, THE Balance_Parser SHALL détecter automatiquement les variations de noms de colonnes |
| 14.2 | THE Balance_Parser SHALL normaliser les noms de colonnes en supprimant les espaces multiples |
| 14.3 | WHEN les colonnes ont des noms différents, THE Balance_Parser SHALL utiliser un mapping flexible |
| 14.5 | THE Balance_Parser SHALL accepter les formats de nombres avec virgule ou point comme séparateur décimal |
| 14.6 | THE Balance_Parser SHALL accepter les formats de nombres avec ou sans séparateur de milliers |

## Test Implementation

### Test File
- **Location**: `py_backend/Doc calcul notes annexes/Tests/test_balance_format_flexibility.py`
- **Framework**: Hypothesis (Property-Based Testing)
- **Language**: Python 3.8+

### Test Functions

#### 1. `test_property_balance_format_flexibility(data)`
**Main property-based test**

Tests that the Balance_Reader correctly handles various format combinations:

```python
@given(data=st.data())
@settings(max_examples=50, deadline=60000)
def test_property_balance_format_flexibility(data):
    """
    Generates Excel files with format variations and verifies:
    1. Column names with multiple spaces are normalized
    2. Decimal separators (comma and period) are handled correctly
    3. Thousand separators are handled correctly
    4. All monetary values are converted to float correctly
    5. No data is lost during format conversion
    6. The system handles mixed formats gracefully
    """
```

**Test Strategy**:
- Generate 50 random Excel files with various format combinations
- Use different decimal separators (comma, period)
- Use different thousand separators (space, comma, period, none)
- Mix column name variations with number format variations
- Verify that Balance_Reader correctly normalizes and converts all data

**Assertions**:
- Column names are normalized to standard format
- All monetary columns are numeric after loading
- No NaN values are introduced
- All values are >= 0
- Number of rows is preserved
- Numéro and Intitulé columns are preserved

#### 2. `test_property_decimal_separator_handling(decimal_sep, thousand_sep)`
**Focused test for decimal separator handling**

Tests specific combinations of decimal and thousand separators:

```python
@given(decimal_sep=st_decimal_separator(), thousand_sep=st_thousand_separator())
@settings(max_examples=20, deadline=30000)
def test_property_decimal_separator_handling(decimal_sep, thousand_sep):
    """
    Tests that the Balance_Reader correctly handles:
    1. Comma as decimal separator
    2. Period as decimal separator
    3. Thousand separators don't interfere with decimal conversion
    4. All values are converted to float without loss of precision
    5. No NaN values are introduced during conversion
    """
```

**Test Strategy**:
- Generate 20 combinations of decimal and thousand separators
- Create Excel files with formatted numbers
- Verify that Balance_Reader correctly converts all numbers
- Verify that converted values are numeric and valid

#### 3. `test_property_format_flexibility_with_demo_file()`
**Validation with real demo file**

Tests that the demo file respects format flexibility properties:

```python
def test_property_format_flexibility_with_demo_file():
    """
    Verifies that the demo file P000 -BALANCE DEMO N_N-1_N-2.xls
    respects the format flexibility properties.
    """
```

**Validations**:
- All monetary columns are numeric
- No NaN values in any column
- All values are >= 0
- All three balances (N, N-1, N-2) are loaded correctly

## Hypothesis Strategies

### `st_decimal_separator()`
Generates a decimal separator (comma or period).

```python
@st.composite
def st_decimal_separator(draw):
    return draw(st.sampled_from([',', '.']))
```

### `st_thousand_separator()`
Generates a thousand separator (space, comma, period, or none).

```python
@st.composite
def st_thousand_separator(draw):
    return draw(st.sampled_from([' ', ',', '.', '']))
```

### `st_formatted_number(draw, decimal_sep='.', thousand_sep='')`
Generates a formatted number with specified separators.

```python
@st.composite
def st_formatted_number(draw, decimal_sep='.', thousand_sep=''):
    # Generates numbers like:
    # - "1000.50" (period, no thousand separator)
    # - "1,000.50" (period, comma thousand separator)
    # - "1 000,50" (comma, space thousand separator)
    # - "1000,50" (comma, no thousand separator)
```

### `st_balance_with_format_variations()`
Generates Excel files with various format combinations.

```python
@st.composite
def st_balance_with_format_variations(draw):
    # Generates:
    # - Column names with multiple spaces
    # - Numbers with different decimal separators
    # - Numbers with different thousand separators
    # - Mixed formats in the same file
```

## Test Execution

### Run All Tests
```bash
pytest test_balance_format_flexibility.py -v
```

### Run Specific Test
```bash
pytest test_balance_format_flexibility.py::test_property_balance_format_flexibility -v
```

### Run with Specific Number of Examples
```bash
pytest test_balance_format_flexibility.py -v --hypothesis-seed=0
```

### Direct Execution
```bash
python test_balance_format_flexibility.py
```

## Expected Results

### Test Coverage
- **50 random format combinations** tested in main property test
- **20 decimal/thousand separator combinations** tested in focused test
- **1 real demo file** tested for validation

### Success Criteria
✓ All 50 format combinations handled correctly
✓ All 20 separator combinations handled correctly
✓ Demo file loads without errors
✓ All monetary values are numeric
✓ No data loss during conversion
✓ Column names normalized correctly

### Example Output
```
test_balance_format_flexibility.py::test_property_balance_format_flexibility PASSED [100%]
test_balance_format_flexibility.py::test_property_decimal_separator_handling PASSED [100%]
test_balance_format_flexibility.py::test_property_format_flexibility_with_demo_file PASSED [100%]

✓ Property validée avec le fichier de démonstration
  - Balance N:   XXX comptes, tous les montants numériques
  - Balance N-1: XXX comptes, tous les montants numériques
  - Balance N-2: XXX comptes, tous les montants numériques
```

## Format Examples Tested

### Decimal Separators
- **Period**: `1000.50`, `1000.00`
- **Comma**: `1000,50`, `1000,00`

### Thousand Separators
- **Space**: `1 000.50`, `1 000,50`
- **Comma**: `1,000.50`, `1,000,50`
- **Period**: `1.000,50`, `1.000.50`
- **None**: `1000.50`, `1000,50`

### Column Name Variations
- **Multiple spaces**: `Ant  Débit`, `Ant   Débit`, `Ant    Débit`
- **Leading spaces**: ` Ant Débit`, `  Ant Débit`
- **Trailing spaces**: `Ant Débit `, `Ant Débit  `
- **Mixed**: ` Ant  Débit `, `  Ant   Débit  `

## Implementation Notes

### Key Features
1. **Automatic Format Detection**: The Balance_Reader automatically detects and normalizes various formats
2. **Flexible Decimal Handling**: Supports both comma and period as decimal separators
3. **Flexible Thousand Handling**: Supports space, comma, period, or no thousand separator
4. **Data Preservation**: No data loss during format conversion
5. **Error Handling**: Graceful handling of mixed formats

### Edge Cases Handled
- Empty thousand separator (no thousand separator)
- Mixed formats in the same file
- Leading/trailing spaces in column names
- Multiple consecutive spaces in column names
- Very large numbers (up to 999,999.99)
- Very small numbers (0.00)

## Related Tasks

- **Task 24.1**: Enhance Balance_Reader for format variations (Implementation)
- **Task 24.2**: Write property test for balance format flexibility (This task)
- **Task 25**: Checkpoint - Ensure integration and flexibility features work

## References

- **Design Document**: `.kiro/specs/calcul-notes-annexes-syscohada/design.md`
- **Requirements**: `.kiro/specs/calcul-notes-annexes-syscohada/requirements.md`
- **Balance_Reader Module**: `py_backend/Doc calcul notes annexes/Modules/balance_reader.py`
- **Hypothesis Documentation**: https://hypothesis.readthedocs.io/

## Author

Système de calcul automatique des notes annexes SYSCOHADA
Date: 28 Avril 2026
