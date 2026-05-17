# Quick Start Guide - Note 3C (Immobilisations Financières)

## Overview

This guide explains how to test the Note 3C calculator for Financial Investments (Immobilisations Financières).

## File Created

- **Script**: `py_backend/Doc calcul notes annexes/Scripts/calculer_note_3c.py`
- **Test Output**: `py_backend/Doc calcul notes annexes/Tests/test_note_3c.html`
- **Trace File**: `py_backend/Doc calcul notes annexes/Tests/trace_note_3c.json`

## Account Mapping

The Note 3C calculator uses the following SYSCOHADA account mappings:

### Financial Investment Lines

1. **Titres de participation** (Equity investments)
   - Brut: 261
   - Provisions: 271

2. **Autres titres immobilisés** (Other fixed securities)
   - Brut: 262, 263
   - Provisions: 272, 273

3. **Prêts et créances** (Loans and receivables)
   - Brut: 264, 265
   - Provisions: 274, 275

4. **Dépôts et cautionnements versés** (Deposits and guarantees paid)
   - Brut: 266, 267
   - Provisions: 276, 277

5. **Autres immobilisations financières** (Other financial investments)
   - Brut: 268
   - Provisions: 278

## Important Note

Financial investments (26X accounts) are **not depreciated** (no amortissements). However, they can be subject to **provisions for impairment** (27X accounts). The calculator treats provisions similarly to depreciation in the calculation logic.

## How to Run

### Command Line

```bash
python "py_backend/Doc calcul notes annexes/Scripts/calculer_note_3c.py" \
  "py_backend/BALANCES_N_N1_N2.xlsx" \
  --output-html "py_backend/Doc calcul notes annexes/Tests/test_note_3c.html" \
  --output-trace "py_backend/Doc calcul notes annexes/Tests/trace_note_3c.json"
```

### PowerShell (Windows)

```powershell
python "py_backend/Doc calcul notes annexes/Scripts/calculer_note_3c.py" `
  "py_backend/BALANCES_N_N1_N2.xlsx" `
  --output-html "py_backend/Doc calcul notes annexes/Tests/test_note_3c.html" `
  --output-trace "py_backend/Doc calcul notes annexes/Tests/trace_note_3c.json"
```

## Expected Output

The calculator will:

1. Load balances from 3 fiscal years (N, N-1, N-2)
2. Calculate 5 lines of financial investments
3. Calculate totals
4. Generate HTML output with formatted table
5. Generate JSON trace file for audit

## Output Structure

The generated HTML table will contain:

- **VALEURS BRUTES** (Gross Values)
  - Début exercice (Opening balance)
  - Augmentations (Increases)
  - Diminutions (Decreases)
  - Fin exercice (Closing balance)

- **PROVISIONS** (Provisions for impairment)
  - Début exercice (Opening provisions)
  - Dotations (Provision charges)
  - Reprises (Provision reversals)
  - Fin exercice (Closing provisions)

- **VALEURS NETTES** (Net Values)
  - Début exercice (Opening net value)
  - Fin exercice (Closing net value)

## Verification

After running the calculator, verify:

1. ✓ HTML file created in Tests folder
2. ✓ Trace JSON file created
3. ✓ All 5 financial investment lines calculated
4. ✓ Total line present
5. ✓ Accounting equation coherence: Closing = Opening + Increases - Decreases

## Requirements Validated

This implementation validates:

- **Requirement 5.1**: Script structure following template
- **Requirement 5.2**: Mapping for accounts 26X (brut) and 27X (provisions)
- **Requirement 5.3**: Calculation logic for financial investments
- **Requirement 5.4**: HTML generation conforming to SYSCOHADA format

## Next Steps

After successful testing of Note 3C, proceed to:

- Task 14.3: Create calculer_note_3d.py for Charges Immobilisées
- Task 14.4: Create calculer_note_3e.py for Écarts de Conversion Actif

## Troubleshooting

### Balance File Not Found

Ensure the balance file exists at the specified path. The default test uses:
- `py_backend/BALANCES_N_N1_N2.xlsx`

### Import Errors

If you encounter import errors, ensure:
- The Modules folder is in the Python path
- All required modules are present (balance_reader, account_extractor, etc.)

### Calculation Errors

Check the console output for warnings about:
- Missing accounts (will use 0.0 values)
- Incoherent balances (accounting equation not satisfied)
- Negative net values (unusual but possible for provisions)

## Date

Created: 25 April 2026
Task: 14.2 - Create calculer_note_3c.py for Immobilisations Financières
