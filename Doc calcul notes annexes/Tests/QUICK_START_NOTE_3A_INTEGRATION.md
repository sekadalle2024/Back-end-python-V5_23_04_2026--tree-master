# Quick Start - Note 3A Integration Test

## What This Test Does

This integration test validates the complete workflow for calculating Note 3A (Immobilisations Incorporelles):
1. ✅ Loads balance sheets from Excel (N, N-1, N-2)
2. ✅ Calculates all 11 columns for 4 asset lines
3. ✅ Verifies accounting equation coherence
4. ✅ Generates HTML output
5. ✅ Creates trace file for audit

## Run the Test

### Option 1: Quick Run (Recommended)
```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Tests
pytest test_note_3a_integration.py -v
```

### Option 2: Run from Python
```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Tests
python test_note_3a_integration.py
```

### Option 3: Run Specific Test
```bash
pytest test_note_3a_integration.py::TestNote3AIntegration::test_complete_workflow_execution -v
```

## Expected Result

```
test_note_3a_integration.py::TestNote3AIntegration::test_complete_workflow_execution PASSED
test_note_3a_integration.py::TestNote3AIntegration::test_all_11_columns_calculated PASSED
test_note_3a_integration.py::TestNote3AIntegration::test_accounting_equation_coherence PASSED
test_note_3a_integration.py::TestNote3AIntegration::test_total_line_calculation PASSED
test_note_3a_integration.py::TestNote3AIntegration::test_html_structure_validation PASSED
test_note_3a_integration.py::TestNote3AIntegration::test_trace_file_content PASSED
test_note_3a_integration.py::TestNote3AIntegration::test_vnc_non_negative PASSED

========================= 7 passed in X.XXs =========================
```

## What Gets Tested

### 1. Complete Workflow ✓
- Balance loading from Excel
- Note calculation
- HTML generation
- Trace file creation

### 2. All 11 Columns ✓
- `libelle` (label)
- **Brut**: ouverture, augmentations, diminutions, clôture
- **Amortissements**: ouverture, dotations, reprises, clôture
- **VNC**: ouverture, clôture

### 3. Accounting Equations ✓
- Brut: `Clôture = Ouverture + Augmentations - Diminutions`
- Amort: `Clôture = Ouverture + Dotations - Reprises`
- VNC: `VNC = Brut - Amortissements`

### 4. HTML Structure ✓
- Valid HTML with title and headers
- Table with 5 rows (4 detail + 1 total)
- Each row has 11 cells

### 5. Trace File ✓
- Valid JSON format
- Contains metadata and calculation details
- Includes source account information

## Prerequisites

### 1. Install Dependencies
```bash
pip install pytest pandas beautifulsoup4 openpyxl
```

### 2. Verify Balance File Exists
```bash
ls py_backend/P000\ -BALANCE\ DEMO\ N_N-1_N-2.xlsx
```

If missing, the test will be skipped automatically.

## Troubleshooting

### ❌ "Balance file not found"
**Solution**: Ensure `P000 -BALANCE DEMO N_N-1_N-2.xlsx` exists in `py_backend` directory

### ❌ "ModuleNotFoundError"
**Solution**: Install missing dependencies:
```bash
pip install pytest pandas beautifulsoup4 openpyxl
```

### ❌ "ImportError: cannot import name 'CalculateurNote3A'"
**Solution**: Ensure you're running from the Tests directory or PYTHONPATH is set correctly

### ❌ Test fails with calculation errors
**Solution**: 
1. Check balance file format (must have 8 columns)
2. Verify account numbers match SYSCOHADA plan
3. Check for missing or invalid data

## What Happens During Test

1. **Setup**: Creates temporary directory for output files
2. **Load**: Reads balance sheets from Excel file
3. **Calculate**: Computes all 11 columns for each line
4. **Verify**: Checks accounting equations and data validity
5. **Generate**: Creates HTML and trace files
6. **Validate**: Verifies HTML structure and trace content
7. **Cleanup**: Removes temporary files

## Output Files (Temporary)

During test execution, these files are created in a temp directory:
- `note_3a_test.html` - HTML visualization
- `note_3a_trace_test.json` - Calculation trace
- `note_3a_structure_test.html` - HTML structure test
- `note_3a_trace_content_test.json` - Trace content test

All files are automatically deleted after test completion.

## Next Steps

After this test passes:
1. ✅ Task 13.4 is complete
2. ➡️ Move to Task 14: Create calculators for Notes 3B-3E
3. ➡️ Create similar integration tests for other notes

## Requirements Validated

This test validates the following requirements:
- **5.1**: Script structure and initialization
- **5.2**: Balance loading via Balance_Reader
- **5.3**: Note calculation with all columns
- **5.4**: Accounting equation coherence
- **5.5**: HTML generation via HTML_Generator
- **5.6**: HTML file saving
- **5.7**: Trace file generation

## Performance

Expected execution time: **< 5 seconds** for all 7 tests

## Success Indicators

✅ All 7 tests pass
✅ No warnings or errors
✅ Execution time < 5 seconds
✅ All accounting equations coherent
✅ HTML and trace files generated correctly
