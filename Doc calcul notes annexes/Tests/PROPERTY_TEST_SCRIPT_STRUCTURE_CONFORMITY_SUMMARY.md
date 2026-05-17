# Property Test: Script Structure Conformity - Summary

## Overview

This document summarizes the property-based test for **Property 10: Script Structure Conformity**, which validates that all generated `calculer_note_XX.py` scripts conform to the required structure defined in the template.

**Validates: Requirements 5.2, 5.3, 5.4**

## Property Statement

**Property 10: Script Structure Conformity**

*For any* generated `calculer_note_XX.py` script, it must contain a class `CalculateurNoteXX` with methods `charger_balances()`, `calculer_note()`, and `generer_html()`, and must define a `mapping_comptes` dictionary.

## Test File

- **Location**: `py_backend/Doc calcul notes annexes/Tests/test_script_structure_conformity.py`
- **Test Framework**: pytest + Hypothesis
- **Language**: Python 3.9+

## Test Cases

### 1. Template Structure Validation

**Function**: `test_property_template_structure()`

**Purpose**: Verifies that the base template `calculateur_note_template.py` itself respects the expected structure.

**Validates**:
- ✓ `CalculateurNote` base class exists
- ✓ Required methods present: `__init__`, `charger_balances`, `calculer_ligne_note`, `generer_note`, `generer_html`, `sauvegarder_html`, `executer`
- ✓ Required attributes defined: `fichier_balance`, `numero_note`, `titre_note`, `balance_n`, `balance_n1`, `balance_n2`, `mapping_comptes`, `trace_manager`
- ✓ Proper imports from shared modules: `balance_reader`, `account_extractor`, `movement_calculator`, `vnc_calculator`, `html_generator`, `trace_manager`

**Strategy**: Uses Python AST parsing to analyze the template file structure without executing it.

---

### 2. Note 3A Structure Validation

**Function**: `test_property_note_3a_structure()`

**Purpose**: Verifies that the Note 3A calculator respects the structure requirements.

**Validates**:
- ✓ `CalculateurNote3A` class exists
- ✓ Class inherits from `CalculateurNote`
- ✓ Required methods implemented: `__init__`, `generer_note`
- ✓ `mapping_comptes` dictionary defined in `__init__`
- ✓ Template imported correctly

**Strategy**: Uses AST parsing to verify inheritance, method presence, and attribute definitions.

---

### 3. Naming Convention Validation (Property-Based)

**Function**: `test_property_script_naming_convention(note_number)`

**Purpose**: Verifies that file and class names follow the naming convention for any note number.

**Validates**:
- ✓ File names follow pattern: `calculer_note_XX.py` (lowercase, underscores)
- ✓ Class names follow pattern: `CalculateurNoteXX` (PascalCase, no separators)
- ✓ Consistency between file and class names
- ✓ Note number present in both names

**Strategy**: 
- Generates random note numbers (1-33, including 3A-3E) using Hypothesis
- Verifies expected naming patterns
- Runs 10 examples by default

**Hypothesis Configuration**:
```python
@given(note_number=st_note_number())
@settings(max_examples=10, deadline=10000)
```

---

### 4. All Calculators Structure Validation

**Function**: `test_property_all_calculators_have_required_structure()`

**Purpose**: Scans all existing calculator scripts and verifies they conform to the structure.

**Validates**:
- ✓ All `calculer_note_*.py` files in Scripts directory
- ✓ Each has a class inheriting from `CalculateurNote`
- ✓ Each implements required methods
- ✓ Each defines `mapping_comptes`
- ✓ Each imports the template correctly

**Strategy**: 
- Scans Scripts directory for all calculator files
- Parses each file using AST
- Reports conforming and non-conforming scripts
- Test fails if any script is non-conforming

**Output Example**:
```
================================================================================
Validation de 2 calculateurs
================================================================================

Vérification: calculer_note_3a.py...
  ✓ Structure conforme
    - Classe: CalculateurNote3A
    - Méthodes: __init__, generer_note, calculer_total
    - mapping_comptes: présent

Vérification: calculer_note_1.py...
  ✓ Structure conforme
    - Classe: CalculateurNote1
    - Méthodes: __init__, generer_note
    - mapping_comptes: présent

================================================================================
RÉSUMÉ
================================================================================

Total de calculateurs: 2
Conformes: 2
Non conformes: 0
```

---

### 5. Instantiation Validation

**Function**: `test_property_script_can_be_instantiated()`

**Purpose**: Verifies that a conforming calculator can be imported and instantiated at runtime.

**Validates**:
- ✓ Calculator class can be imported
- ✓ Class can be instantiated with a balance file path
- ✓ All required attributes are accessible
- ✓ All required methods are callable
- ✓ `mapping_comptes` is a non-empty dictionary with correct structure

**Strategy**: 
- Imports and instantiates Note 3A calculator
- Uses Python introspection (`hasattr`, `callable`)
- Validates `mapping_comptes` structure
- Serves as a smoke test for runtime conformity

---

## Hypothesis Strategies

### `st_note_number()`

Generates valid SYSCOHADA note numbers:
- Notes with alphabetic suffixes: `3A`, `3B`, `3C`, `3D`, `3E`
- Numeric notes: `1`, `2`, `4`-`33` (excluding `3` which has sub-notes)

### `st_class_name(note_number)`

Generates expected class names from note numbers:
- Input: `"3A"` → Output: `"CalculateurNote3A"`
- Input: `"15"` → Output: `"CalculateurNote15"`

---

## Helper Functions

### AST Parsing Functions

1. **`parse_python_file(file_path)`**: Parses a Python file and returns its AST
2. **`extract_class_names(tree)`**: Extracts all class names from an AST
3. **`extract_class_methods(tree, class_name)`**: Extracts method names from a specific class
4. **`extract_class_attributes(tree, class_name)`**: Extracts attributes defined in `__init__`
5. **`check_class_inherits_from(tree, class_name, base_class)`**: Checks class inheritance
6. **`extract_imports(tree)`**: Extracts all imports from a file

These functions enable structural analysis without code execution, making tests safe and fast.

---

## Running the Tests

### Run all tests with pytest:
```bash
pytest py_backend/Doc\ calcul\ notes\ annexes/Tests/test_script_structure_conformity.py -v
```

### Run with Hypothesis statistics:
```bash
pytest py_backend/Doc\ calcul\ notes\ annexes/Tests/test_script_structure_conformity.py -v --hypothesis-show-statistics
```

### Run specific test:
```bash
pytest py_backend/Doc\ calcul\ notes\ annexes/Tests/test_script_structure_conformity.py::test_property_template_structure -v
```

### Run directly (quick validation):
```bash
python py_backend/Doc\ calcul\ notes\ annexes/Tests/test_script_structure_conformity.py
```

---

## Expected Output

### Successful Test Run:
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

### Failed Test Example:
```
FAILED test_script_structure_conformity.py::test_property_all_calculators_have_required_structure
AssertionError: 1 calculateur(s) ne respectent pas la structure requise

Calculateurs non conformes:
  - calculer_note_4.py: Méthodes manquantes: {'generer_note'}
```

---

## Integration with CI/CD

This test should be run:
- ✓ Before committing new calculator scripts
- ✓ In CI/CD pipeline for every push
- ✓ Before generating new notes from templates
- ✓ As part of the test suite for task 13.3

---

## Maintenance

### Adding New Calculators

When adding a new calculator (e.g., `calculer_note_4.py`):

1. Ensure it inherits from `CalculateurNote`
2. Implement `__init__` and `generer_note` methods
3. Define `mapping_comptes` in `__init__`
4. Import the template: `from calculateur_note_template import CalculateurNote`
5. Run this test to verify conformity

### Modifying the Template

If the template structure changes:

1. Update `test_property_template_structure()` to reflect new requirements
2. Update all calculator scripts to match new structure
3. Run `test_property_all_calculators_have_required_structure()` to verify all scripts

---

## Related Files

- **Template**: `py_backend/Doc calcul notes annexes/Scripts/calculateur_note_template.py`
- **Example**: `py_backend/Doc calcul notes annexes/Scripts/calculer_note_3a.py`
- **Requirements**: `.kiro/specs/calcul-notes-annexes-syscohada/requirements.md` (5.2, 5.3, 5.4)
- **Design**: `.kiro/specs/calcul-notes-annexes-syscohada/design.md` (Property 10)
- **Tasks**: `.kiro/specs/calcul-notes-annexes-syscohada/tasks.md` (Task 13.3)

---

## Success Criteria

✅ All 5 test cases pass  
✅ Template structure validated  
✅ Note 3A structure validated  
✅ Naming conventions verified for all note numbers  
✅ All existing calculators conform to structure  
✅ Calculator can be instantiated and used at runtime  

---

## Notes

- This test uses **static analysis** (AST parsing) rather than dynamic execution for safety and speed
- The test is **non-destructive** - it only reads files, never modifies them
- The test is **comprehensive** - it validates both structural and runtime conformity
- The test is **maintainable** - helper functions can be reused for other structural tests

---

**Status**: ✅ Implemented and ready for execution  
**Date**: 25 Avril 2026  
**Task**: 13.3 Write property test for script structure conformity
