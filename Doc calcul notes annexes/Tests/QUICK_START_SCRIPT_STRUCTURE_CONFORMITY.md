# Quick Start: Script Structure Conformity Test

## What is this test?

This property-based test validates that all calculator scripts (`calculer_note_XX.py`) follow the required structure defined in the template.

**Property 10**: *For any generated script, it must have a class `CalculateurNoteXX` with methods `charger_balances()`, `calculer_note()`, `generer_html()`, and a `mapping_comptes` dictionary.*

---

## Quick Run

### Option 1: Run with pytest (recommended)

```bash
cd py_backend/Doc\ calcul\ notes\ annexes

pytest Tests/test_script_structure_conformity.py -v
```

### Option 2: Run directly

```bash
cd py_backend/Doc\ calcul\ notes\ annexes

python Tests/test_script_structure_conformity.py
```

---

## What does it test?

1. ✅ **Template structure** - Validates the base template has all required components
2. ✅ **Note 3A structure** - Validates the example calculator is correct
3. ✅ **Naming conventions** - Verifies file and class names follow the pattern
4. ✅ **All calculators** - Scans and validates all existing calculator scripts
5. ✅ **Runtime instantiation** - Verifies calculators can be imported and used

---

## Expected Output

### ✅ All tests pass:

```
======================== test session starts =========================
collected 5 items

test_script_structure_conformity.py::test_property_template_structure PASSED
test_script_structure_conformity.py::test_property_note_3a_structure PASSED
test_script_structure_conformity.py::test_property_script_naming_convention PASSED
test_script_structure_conformity.py::test_property_all_calculators_have_required_structure PASSED
test_script_structure_conformity.py::test_property_script_can_be_instantiated PASSED

========================= 5 passed in 2.34s ==========================
```

### ❌ Test fails:

```
FAILED test_script_structure_conformity.py::test_property_all_calculators_have_required_structure

Calculateurs non conformes:
  - calculer_note_4.py: Méthodes manquantes: {'generer_note'}
```

**Action**: Fix the non-conforming calculator by adding the missing method.

---

## What to check if tests fail?

### Missing class:
```
✗ Aucune classe héritant de CalculateurNote
```
**Fix**: Add a class that inherits from `CalculateurNote`:
```python
from calculateur_note_template import CalculateurNote

class CalculateurNote4(CalculateurNote):
    def __init__(self, fichier_balance: str):
        super().__init__(fichier_balance, "4", "Titre de la note")
```

### Missing methods:
```
✗ Méthodes manquantes: {'generer_note'}
```
**Fix**: Implement the `generer_note()` method:
```python
def generer_note(self) -> pd.DataFrame:
    lignes = []
    # ... calcul des lignes
    return pd.DataFrame(lignes)
```

### Missing mapping_comptes:
```
✗ Attribut mapping_comptes non trouvé
```
**Fix**: Define `mapping_comptes` in `__init__`:
```python
def __init__(self, fichier_balance: str):
    super().__init__(fichier_balance, "4", "Titre")
    self.mapping_comptes = {
        'Ligne 1': {'brut': ['401'], 'amort': ['4801']},
        # ...
    }
```

### Missing import:
```
✗ Import du template manquant
```
**Fix**: Add the import at the top of the file:
```python
from calculateur_note_template import CalculateurNote
```

---

## File Structure

```
py_backend/Doc calcul notes annexes/
├── Scripts/
│   ├── calculateur_note_template.py    ← Base template
│   ├── calculer_note_3a.py             ← Example calculator
│   ├── calculer_note_1.py              ← Your calculators
│   └── ...
└── Tests/
    ├── test_script_structure_conformity.py           ← The test
    ├── PROPERTY_TEST_SCRIPT_STRUCTURE_CONFORMITY_SUMMARY.md
    └── QUICK_START_SCRIPT_STRUCTURE_CONFORMITY.md   ← This file
```

---

## Required Structure

Every calculator script must have:

### 1. Import the template
```python
from calculateur_note_template import CalculateurNote
```

### 2. Define a class that inherits from CalculateurNote
```python
class CalculateurNoteXX(CalculateurNote):
    pass
```

### 3. Implement __init__ with mapping_comptes
```python
def __init__(self, fichier_balance: str):
    super().__init__(fichier_balance, "XX", "Titre de la note")
    self.mapping_comptes = {
        'Ligne 1': {'brut': ['211'], 'amort': ['2811']},
        # ...
    }
```

### 4. Implement generer_note()
```python
def generer_note(self) -> pd.DataFrame:
    lignes = []
    for libelle, comptes in self.mapping_comptes.items():
        ligne = self.calculer_ligne_note(
            libelle=libelle,
            comptes_brut=comptes['brut'],
            comptes_amort=comptes.get('amort')
        )
        lignes.append(ligne)
    
    df = pd.DataFrame(lignes)
    # Add total line
    return df
```

---

## Naming Convention

### File names:
- Pattern: `calculer_note_XX.py`
- Lowercase with underscores
- Examples: `calculer_note_3a.py`, `calculer_note_15.py`

### Class names:
- Pattern: `CalculateurNoteXX`
- PascalCase, no separators
- Examples: `CalculateurNote3A`, `CalculateurNote15`

---

## When to run this test?

- ✅ After creating a new calculator script
- ✅ After modifying the template
- ✅ Before committing changes
- ✅ In CI/CD pipeline
- ✅ As part of task 13.3 validation

---

## Need help?

1. **Check the template**: `Scripts/calculateur_note_template.py`
2. **Check the example**: `Scripts/calculer_note_3a.py`
3. **Read the summary**: `PROPERTY_TEST_SCRIPT_STRUCTURE_CONFORMITY_SUMMARY.md`
4. **Check requirements**: `.kiro/specs/calcul-notes-annexes-syscohada/requirements.md` (5.2, 5.3, 5.4)

---

## Success!

If all tests pass, your calculator scripts conform to the required structure and are ready to use! 🎉

---

**Task**: 13.3 Write property test for script structure conformity  
**Status**: ✅ Complete  
**Date**: 25 Avril 2026
