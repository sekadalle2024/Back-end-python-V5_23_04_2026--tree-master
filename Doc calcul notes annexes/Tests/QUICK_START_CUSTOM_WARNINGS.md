# Quick Start Guide - Custom Warnings System

## Overview

The custom warnings system provides specialized warning classes for different types of issues that can occur during SYSCOHADA notes annexes calculation. All warnings are automatically logged to `calcul_notes_warnings.log`.

## Requirements Validated

- **3.6**: Incoherent balance warnings
- **4.7**: Negative VNC warnings  
- **8.5**: Warning logging to calcul_notes_warnings.log
- **8.6**: Comprehensive warning coverage
- **Error Handling**: Graceful degradation with warnings

## Available Warning Classes

### 1. IncoherentBalanceWarning
Emitted when accounting equation doesn't balance:
```
Solde_Cloture ≠ Solde_Ouverture + Augmentations - Diminutions
```

### 2. NegativeVNCWarning
Emitted when net book value is negative:
```
VNC = Brut - Amortissement < 0
```

### 3. AbnormalAccountBalanceWarning
Emitted when account has unexpected balance characteristics:
- Both debit and credit balances simultaneously
- Wrong sign for account type (e.g., asset with credit balance)

### 4. MissingAccountWarning
Emitted when expected account is not found in balance sheet.

### 5. LowCoherenceRateWarning
Emitted when global coherence rate < 95%.

## Usage Examples

### Using Warning Classes Directly

```python
from Modules.custom_warnings import IncoherentBalanceWarning

warning = IncoherentBalanceWarning(
    compte="211",
    solde_ouverture=1000.0,
    augmentations=500.0,
    diminutions=200.0,
    solde_cloture=1250.0,
    ecart=50.0,
    note_numero="3A"
)
```

### Using Convenience Functions (Recommended)

```python
from Modules.custom_warnings import (
    warn_incoherent_balance,
    warn_negative_vnc,
    warn_abnormal_account_balance,
    warn_missing_account,
    warn_low_coherence_rate
)

# Incoherent balance
warn_incoherent_balance(
    compte="211",
    solde_ouverture=1000.0,
    augmentations=500.0,
    diminutions=200.0,
    solde_cloture=1250.0,
    ecart=50.0,
    note_numero="3A"
)

# Negative VNC
warn_negative_vnc(
    libelle="Frais de recherche",
    brut=1000.0,
    amortissement=1200.0,
    vnc=-200.0,
    note_numero="3A"
)

# Abnormal account balance
warn_abnormal_account_balance(
    compte="401",
    solde_debit=100.0,
    solde_credit=0.0,
    raison="Compte fournisseur avec solde debiteur",
    note_numero="13"
)

# Missing account
warn_missing_account(
    compte="218",
    note_numero="3A",
    impact="Ligne 'Autres immobilisations' sera a zero"
)

# Low coherence rate
warn_low_coherence_rate(
    taux_coherence=92.5,
    seuil=95.0,
    details={'failed_validations': ['total_immobilisations']}
)
```

## Integration with Modules

### In Movement_Calculator

```python
from Modules.custom_warnings import warn_incoherent_balance

class MovementCalculator:
    def verifier_coherence(self, solde_ouverture, augmentations, 
                          diminutions, solde_cloture, compte="", note_numero=None):
        attendu = solde_ouverture + augmentations - diminutions
        ecart = abs(solde_cloture - attendu)
        
        if ecart > 0.01:  # Tolerance of 1 centime
            warn_incoherent_balance(
                compte=compte,
                solde_ouverture=solde_ouverture,
                augmentations=augmentations,
                diminutions=diminutions,
                solde_cloture=solde_cloture,
                ecart=ecart,
                note_numero=note_numero
            )
            return False, ecart
        
        return True, 0.0
```

### In VNC_Calculator

```python
from Modules.custom_warnings import warn_negative_vnc

class VNCCalculator:
    def valider_vnc(self, vnc, libelle="", brut=0.0, amort=0.0, note_numero=None):
        if vnc < 0:
            warn_negative_vnc(
                libelle=libelle,
                brut=brut,
                amortissement=amort,
                vnc=vnc,
                note_numero=note_numero
            )
            return False, f"VNC negative: {vnc:.2f}"
        
        return True, ""
```

### In Account_Extractor

```python
from Modules.custom_warnings import warn_missing_account

class AccountExtractor:
    def extraire_solde_compte(self, numero_compte, note_numero=None):
        comptes = self.filtrer_par_racine(numero_compte)
        
        if comptes.empty:
            warn_missing_account(
                compte=numero_compte,
                note_numero=note_numero,
                impact="Valeurs nulles utilisees pour ce compte"
            )
            return {
                'ant_debit': 0.0,
                'ant_credit': 0.0,
                'mvt_debit': 0.0,
                'mvt_credit': 0.0,
                'solde_debit': 0.0,
                'solde_credit': 0.0
            }
        
        # ... rest of extraction logic
```

### In Coherence_Validator

```python
from Modules.custom_warnings import warn_low_coherence_rate

class CoherenceValidator:
    def calculer_taux_coherence(self):
        # ... calculate coherence rate
        
        if taux_coherence < 95.0:
            warn_low_coherence_rate(
                taux_coherence=taux_coherence,
                seuil=95.0,
                details=self.validations
            )
        
        return taux_coherence
```

## Running Tests

### Run all warning tests:
```powershell
cd "py_backend/Doc calcul notes annexes/Tests"
pytest test_custom_warnings.py -v
```

### Run specific test class:
```powershell
pytest test_custom_warnings.py::TestIncoherentBalanceWarning -v
```

### Run with coverage:
```powershell
pytest test_custom_warnings.py --cov=../Modules/custom_warnings --cov-report=html
```

## Log Output Format

Warnings are logged with the following format:
```
[WarningClassName] Warning message | Context: key1=value1, key2=value2, ...
```

Example:
```
[IncoherentBalanceWarning] Balance incoherente pour compte '211': Solde cloture attendu = 1300.00, Solde cloture reel = 1250.00, Ecart = 50.00 | Context: compte=211, solde_ouverture=1000.0, augmentations=500.0, diminutions=200.0, solde_cloture=1250.0, ecart=50.0, note_numero=3A
```

## Viewing Warning Logs

Warnings are written to: `calcul_notes_warnings.log`

```powershell
# View recent warnings
Get-Content calcul_notes_warnings.log -Tail 20

# Search for specific warning type
Select-String -Path calcul_notes_warnings.log -Pattern "NegativeVNCWarning"

# Count warnings by type
Get-Content calcul_notes_warnings.log | Select-String -Pattern "\[.*Warning\]" | Group-Object
```

## Best Practices

1. **Always provide context**: Include note_numero when available
2. **Use convenience functions**: They're simpler and more consistent
3. **Don't suppress warnings**: They indicate data quality issues
4. **Review warning logs**: Check after each calculation run
5. **Document warning causes**: Add comments explaining why warnings occur

## Warning Summary Report

Generate a summary of warnings after calculation:

```python
import logging
from collections import Counter

def generer_resume_warnings():
    """Generate summary of warnings from log file"""
    warnings_by_type = Counter()
    warnings_by_note = Counter()
    
    with open('calcul_notes_warnings.log', 'r', encoding='utf-8') as f:
        for line in f:
            if '[' in line and 'Warning]' in line:
                # Extract warning type
                warning_type = line.split('[')[1].split(']')[0]
                warnings_by_type[warning_type] += 1
                
                # Extract note number if present
                if 'note_numero=' in line:
                    note = line.split('note_numero=')[1].split(',')[0].split(')')[0]
                    warnings_by_note[note] += 1
    
    print("\n=== RESUME DES AVERTISSEMENTS ===")
    print(f"\nTotal: {sum(warnings_by_type.values())} avertissements")
    
    print("\nPar type:")
    for warning_type, count in warnings_by_type.most_common():
        print(f"  {warning_type}: {count}")
    
    print("\nPar note:")
    for note, count in warnings_by_note.most_common():
        print(f"  Note {note}: {count}")
```

## Task Completion

✅ **Task 28.3 Completed**: Warning system implemented with:
- 5 custom warning classes
- Automatic logging to calcul_notes_warnings.log
- Convenience functions for easy usage
- Comprehensive test coverage
- Integration examples for all modules
- Requirements 3.6, 4.7, 8.5, 8.6 validated
