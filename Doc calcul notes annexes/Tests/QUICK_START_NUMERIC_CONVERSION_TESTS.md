# Quick Start: Numeric Conversion Robustness Tests

**Task:** 2.4 Write property test for numeric conversion robustness  
**Status:** ✅ COMPLETED  
**File:** `test_balance_reader_numeric_conversion.py`

## 🚀 Quick Commands

### Run All Tests
```bash
pytest test_balance_reader_numeric_conversion.py -v
```

### Run Specific Test
```bash
# Unit test only
pytest test_balance_reader_numeric_conversion.py::test_convertir_montants_unit -v

# Demo file test only
pytest test_balance_reader_numeric_conversion.py::test_property_numeric_conversion_with_demo_file -v

# Property-based tests only
pytest test_balance_reader_numeric_conversion.py::test_property_numeric_conversion_robustness -v
```

### Run with Statistics
```bash
pytest test_balance_reader_numeric_conversion.py -v --hypothesis-show-statistics
```

### Run Direct Python Execution
```bash
python test_balance_reader_numeric_conversion.py
```

## 📊 What Gets Tested

### 1. Unit Test: `test_convertir_montants_unit()`
Tests the `convertir_montants()` method directly with:
- Empty strings → 0.0
- None values → 0.0
- Text values → 0.0
- Excel errors → 0.0
- Special characters → 0.0
- Valid numbers → preserved

**Expected Result:** ✅ PASS

### 2. Demo File Test: `test_property_numeric_conversion_with_demo_file()`
Tests with the real demo balance file:
- Loads all 3 exercises (N, N-1, N-2)
- Verifies all 6 monetary columns
- Checks for NaN and infinite values
- Validates all values >= 0

**Expected Result:** ✅ PASS (if demo file exists)

### 3. Property Test: `test_property_numeric_conversion_robustness()`
Hypothesis-based test with 50 generated Excel files:
- Each file has 30-70% invalid values
- Tests all combinations of invalid types
- Verifies conversion to 0.0
- Checks type consistency

**Expected Result:** ✅ PASS (50 examples)

### 4. Specific Types Test: `test_property_specific_invalid_value_types()`
Tests specific categories of invalid values:
- Empty columns
- None-only columns
- Text-only columns
- Excel error columns
- Special character columns
- Mixed invalid columns

**Expected Result:** ✅ PASS (30 examples)

## 📋 Test Coverage

| Category | Coverage |
|----------|----------|
| Invalid value types | 6+ types |
| Monetary columns | 6 columns |
| Exercises | 3 (N, N-1, N-2) |
| Generated examples | 80+ |
| Unit test cases | 6+ |

## 🔍 What's Being Validated

### Requirements 1.5 & 1.6

**Requirement 1.5:** All monetary values must be converted to float type

✅ Verified by:
- Type checking: `pd.api.types.is_numeric_dtype()`
- Dtype validation: `balance[col].dtype in [np.float64, np.float32, float]`

**Requirement 1.6:** Invalid/empty values must be replaced with 0.0

✅ Verified by:
- Empty string conversion: `'' → 0.0`
- None conversion: `None → 0.0`
- Text conversion: `'N/A' → 0.0`
- Excel error conversion: `'#DIV/0!' → 0.0`
- Special char conversion: `'###' → 0.0`

## 📈 Expected Output

### Successful Run
```
test_balance_reader_numeric_conversion.py::test_convertir_montants_unit PASSED
test_balance_reader_numeric_conversion.py::test_property_numeric_conversion_with_demo_file PASSED
test_balance_reader_numeric_conversion.py::test_property_numeric_conversion_robustness PASSED [50 examples]
test_balance_reader_numeric_conversion.py::test_property_specific_invalid_value_types PASSED [30 examples]

======================== 4 passed in X.XXs ========================
```

### With Statistics
```
test_balance_reader_numeric_conversion.py::test_property_numeric_conversion_robustness

  - 50 passing examples, 0 failing examples, 0 invalid examples
  - Typical runtimes: 0-100ms, ~ 50ms
  - Seed: 1234567890
```

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'balance_reader'"
**Solution:** Run from the Tests directory or ensure PYTHONPATH includes Modules:
```bash
cd "py_backend/Doc calcul notes annexes/Tests"
pytest test_balance_reader_numeric_conversion.py -v
```

### Issue: "FileNotFoundError: P000 -BALANCE DEMO N_N-1_N-2.xls"
**Solution:** The demo file test will be skipped if the file doesn't exist. This is normal.

### Issue: "Test failed: Exception inattendue"
**Solution:** Check the error message. Common causes:
- Balance file format issue
- Missing columns
- Invalid data types

## 📚 Test Structure

```
test_balance_reader_numeric_conversion.py
├── Strategies (Hypothesis)
│   ├── st_invalid_monetary_value()
│   ├── st_valid_monetary_value()
│   ├── st_mixed_monetary_column()
│   ├── st_balance_with_invalid_values()
│   ├── st_balance_with_specific_invalid_values()
│   └── st_balance_with_specific_invalid_values()
│
├── Property-Based Tests
│   ├── test_property_numeric_conversion_robustness()
│   ├── test_property_numeric_conversion_with_demo_file()
│   └── test_property_specific_invalid_value_types()
│
└── Unit Tests
    └── test_convertir_montants_unit()
```

## 🎯 Key Test Scenarios

### Scenario 1: Empty Values
```python
Input:  ['', '', '', '', '', '']
Output: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

### Scenario 2: None Values
```python
Input:  [None, None, None, None, None, None]
Output: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

### Scenario 3: Text Values
```python
Input:  ['N/A', 'abc', 'ERROR', 'xyz', 'text', 'n/a']
Output: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

### Scenario 4: Excel Errors
```python
Input:  ['#DIV/0!', '#VALUE!', '#REF!', '#NAME?', '#NUM!', '#N/A']
Output: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

### Scenario 5: Mixed Valid/Invalid
```python
Input:  [1000.0, '', 500.0, None, 'N/A', 2000.0]
Output: [1000.0, 0.0, 500.0, 0.0, 0.0, 2000.0]
```

## 📝 Test Execution Workflow

1. **Setup Phase**
   - Create temporary Excel files with invalid values
   - Initialize BalanceReader
   - Load balances

2. **Conversion Phase**
   - Call `convertir_montants()`
   - Convert all monetary columns to float
   - Replace invalid values with 0.0

3. **Validation Phase**
   - Check all columns are numeric type
   - Verify no NaN values remain
   - Verify no infinite values remain
   - Verify all values >= 0

4. **Cleanup Phase**
   - Delete temporary files
   - Report results

## ✅ Success Criteria

All tests pass when:
- ✅ All monetary columns are float type
- ✅ All invalid values are converted to 0.0
- ✅ No NaN or infinite values exist
- ✅ No exceptions are raised
- ✅ All values are >= 0

## 🔗 Related Files

- **Implementation:** `../Modules/balance_reader.py`
- **Configuration:** `conftest.py`
- **Requirements:** `.kiro/specs/calcul-notes-annexes-syscohada/requirements.md`
- **Design:** `.kiro/specs/calcul-notes-annexes-syscohada/design.md`
- **Tasks:** `.kiro/specs/calcul-notes-annexes-syscohada/tasks.md`

## 📞 Support

For issues or questions:
1. Check the error message carefully
2. Review the test file comments
3. Check the balance_reader.py implementation
4. Verify the demo file exists and is valid

---

**Test File:** `test_balance_reader_numeric_conversion.py`  
**Status:** ✅ COMPLETE  
**Last Updated:** 08 Avril 2026
