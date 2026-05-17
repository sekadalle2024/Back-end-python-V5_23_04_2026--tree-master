# Quick Start Guide - Note 8: Capital

## Overview

The Note 8 calculator (`calculer_note_8.py`) automates the calculation of capital movements for SYSCOHADA financial statements. It tracks share capital movements across 3 fiscal years (N, N-1, N-2).

## Features

- **5 Capital Lines**:
  1. Capital social (Share capital)
  2. Capital par dotation (Capital by allocation)
  3. Capital personnel (Personal capital)
  4. Compte de l'exploitant (Owner's account)
  5. Primes liées au capital social (Share premiums)

- **Account Mapping**:
  - Capital social: 1011, 1012, 1013
  - Capital par dotation: 102
  - Capital personnel: 103
  - Compte de l'exploitant: 104
  - Primes: 1051, 1052, 1053, 1054

## Usage

### Basic Usage

```bash
python calculer_note_8.py
```

This uses the default balance file: `../../../P000 -BALANCE DEMO N_N-1_N-2.xls`

### Custom Balance File

```bash
python calculer_note_8.py path/to/your/balance.xls
```

### Custom Output Paths

```bash
python calculer_note_8.py path/to/balance.xls \
  --output-html path/to/output.html \
  --output-trace path/to/trace.json
```

## Output Files

1. **HTML File**: `../Tests/test_note_8.html`
   - Formatted table with SYSCOHADA styling
   - Shows opening balance, increases, decreases, closing balance
   - Includes total row

2. **Trace File**: `../Tests/trace_note_8.json`
   - Complete calculation traceability
   - Source accounts and balances
   - Metadata (timestamp, file hash)

## Example Output

```
================================================================================
  CALCULATEUR NOTE 8 - CAPITAL
================================================================================

📂 Chargement des balances depuis: py_backend/P000 -BALANCE DEMO N_N-1_N-2.xls
✓ Balance N   : 441 lignes chargées
✓ Balance N-1 : 405 lignes chargées
✓ Balance N-2 : 438 lignes chargées

🔢 Calcul de la note 8...
  Calcul: Capital social...
  Calcul: Capital par dotation...
  Calcul: Capital personnel...
  Calcul: Compte de l'exploitant...
  Calcul: Primes liées au capital social...
✓ Note calculée: 6 lignes

📄 Génération du HTML...
✓ HTML généré

✓ Fichier HTML sauvegardé: ../Tests/test_note_8.html
✓ Fichier de trace sauvegardé: ../Tests/trace_note_8.json

────────────────────────────────────────────────────────────────────────────────
  RÉSUMÉ NOTE 8
────────────────────────────────────────────────────────────────────────────────

  Nombre de lignes: 5
  VNC Ouverture:                  0
  VNC Clôture:         -100,000,000
  Variation:           -100,000,000

================================================================================
  ✓ NOTE 8 CALCULÉE AVEC SUCCÈS EN 0.50s
================================================================================
```

## Important Notes

### Capital Accounts are Credit Accounts

Capital accounts (10X) are **liability accounts** (passif) in SYSCOHADA, which means:
- They normally have **credit balances** (negative in the calculation)
- Increases are recorded as **credits** (not debits)
- Decreases are recorded as **debits** (not credits)

This is the opposite of asset accounts, which is why you may see negative VNC values - this is **normal and expected** for capital accounts.

### No Depreciation

Capital accounts do not have depreciation or provisions, so:
- `amort_ouverture` = 0
- `dotations` = 0
- `reprises` = 0
- `amort_cloture` = 0

### Calculation Formula

For each capital line:
- **Opening Balance** = Solde Débit N-1 - Solde Crédit N-1
- **Increases** = Mouvement Débit N (capital contributions)
- **Decreases** = Mouvement Crédit N (capital reductions)
- **Closing Balance** = Solde Débit N - Solde Crédit N

**Coherence Check**: Closing Balance = Opening Balance + Increases - Decreases

## Testing

Run the test script:

```bash
./test-note-8.ps1
```

Or run directly with Python:

```bash
python "py_backend/Doc calcul notes annexes/Scripts/calculer_note_8.py" "py_backend/P000 -BALANCE DEMO N_N-1_N-2.xls"
```

## Troubleshooting

### Balance File Not Found

**Error**: `Fichier de balance non trouvé`

**Solution**: Verify the path to your balance file. Use absolute path or correct relative path from the Scripts directory.

### Incoherence Warnings

**Warning**: `Incohérence détectée pour 'Capital social': écart de X`

**Explanation**: This indicates the accounting equation doesn't balance. Check:
- Data entry errors in the balance
- Missing movements
- Incorrect account classifications

### Negative VNC

**Warning**: `VNC négative détectée`

**Explanation**: For capital accounts, this is **normal** because they are credit accounts (liabilities). The negative sign indicates a credit balance.

## Architecture

The calculator uses the modular architecture:

```
CalculateurNote8
├── Balance_Reader (load balances)
├── Account_Extractor (extract account balances)
├── Movement_Calculator (calculate movements)
├── VNC_Calculator (calculate net values)
├── HTML_Generator (generate HTML output)
└── Trace_Manager (traceability)
```

## Requirements Validated

This calculator validates:
- **Requirement 5.1**: Script structure with mapping_comptes
- **Requirement 5.2**: Class with charger_balances(), calculer_note(), generer_html()
- **Requirement 5.3**: Mapping for accounts 10X
- **Requirement 5.4**: Template structure conformity

## Next Steps

After Note 8, continue with:
- **Note 9**: Réserves (Reserves) - accounts 11X
- **Note 10**: Résultat (Retained earnings) - accounts 12X, 13X

## Support

For issues or questions:
1. Check the main documentation: `py_backend/Doc calcul notes annexes/README.md`
2. Review the template: `calculateur_note_template.py`
3. Check similar notes: `calculer_note_7.py` (Trésorerie Actif)

---

**Date**: 25 April 2026  
**Version**: 1.0  
**Status**: ✓ Completed
