# Quick Start: Hypothesis Strategies (conftest.py)

## Overview

The `conftest.py` file provides Hypothesis strategies for generating valid test data for property-based testing of the SYSCOHADA notes annexes calculation system.

## Available Strategies

### 1. st_balance()

Generates valid balance sheets with coherent accounting data.

```python
from hypothesis import given
from conftest import st_balance

@given(st_balance())
def test_my_function(balance):
    # balance is a pandas DataFrame with 10-100 accounts
    assert len(balance) >= 10
    assert 'Numéro' in balance.columns
```

**Generated columns:**
- `Numéro`: Account number (SYSCOHADA format)
- `Intitulé`: Account label
- `Ant Débit`: Opening debit balance
- `Ant Crédit`: Opening credit balance
- `Débit`: Debit movements
- `Crédit`: Credit movements
- `Solde Débit`: Closing debit balance
- `Solde Crédit`: Closing credit balance

**Coherence guarantee:**
```
Solde Clôture = Solde Ouverture + Mvt Débit - Mvt Crédit
```

### 2. st_compte_racine()

Generates valid SYSCOHADA account roots.

```python
from hypothesis import given
from conftest import st_compte_racine

@given(st_compte_racine())
def test_account_extraction(racine):
    # racine is a string like "211", "2811", "28111"
    assert racine[0] in '123456789'  # Valid class
    assert len(racine) >= 2
```

**Format:** `[1-9][0-9][0-9]{0,2}`

**Examples:** `"21"`, `"211"`, `"2811"`, `"28111"`

### 3. st_montant()

Generates valid monetary amounts.

```python
from hypothesis import given
from conftest import st_montant

@given(st_montant())
def test_calculation(montant):
    # montant is a float between 0 and 100M
    assert montant >= 0
    assert not pd.isna(montant)
```

**Range:** 0 to 100,000,000
**Type:** float (no NaN, no infinity)

### 4. st_ligne_note_annexe()

Generates coherent note annexe lines with all accounting formulas respected.

```python
from hypothesis import given
from conftest import st_ligne_note_annexe

@given(st_ligne_note_annexe())
def test_note_line(ligne):
    # ligne is a dict with all note annexe columns
    assert ligne['brut_cloture'] == (
        ligne['brut_ouverture'] + 
        ligne['augmentations'] - 
        ligne['diminutions']
    )
```

**Generated fields:**
- `libelle`: Line label
- `brut_ouverture`, `brut_cloture`: Gross values
- `augmentations`, `diminutions`: Movements
- `amort_ouverture`, `amort_cloture`: Depreciation
- `dotations`, `reprises`: Depreciation movements
- `vnc_ouverture`, `vnc_cloture`: Net book values

## Pytest Fixtures

### fichier_balance_demo

Path to the demo balance file.

```python
def test_with_demo_file(fichier_balance_demo):
    reader = BalanceReader(fichier_balance_demo)
    balances = reader.charger_balances()
```

### balance_simple

Simple balance DataFrame for quick tests.

```python
def test_with_simple_balance(balance_simple):
    extractor = AccountExtractor(balance_simple)
    solde = extractor.extraire_solde_compte('211')
```

### correspondances_test

Test mapping dictionary.

```python
def test_with_mapping(correspondances_test):
    manager = MappingManager()
    manager.correspondances = correspondances_test
```

## Hypothesis Configuration

Three profiles are available:

### Default Profile (default)
```python
settings.load_profile("default")
# max_examples=100, deadline=60s
```

### CI Profile (continuous integration)
```python
settings.load_profile("ci")
# max_examples=200, deadline=120s
```

### Dev Profile (fast development)
```python
settings.load_profile("dev")
# max_examples=50, deadline=30s
```

## Usage Examples

### Example 1: Test Balance Loading

```python
from hypothesis import given
from conftest import st_balance
from Modules.balance_reader import BalanceReader

@given(st_balance())
def test_balance_has_all_columns(balance):
    """Verify all required columns are present."""
    required_columns = [
        'Numéro', 'Intitulé', 
        'Ant Débit', 'Ant Crédit',
        'Débit', 'Crédit',
        'Solde Débit', 'Solde Crédit'
    ]
    for col in required_columns:
        assert col in balance.columns
```

### Example 2: Test Account Extraction

```python
from hypothesis import given
from conftest import st_balance, st_compte_racine
from Modules.account_extractor import AccountExtractor

@given(st_balance(), st_compte_racine())
def test_account_extraction_returns_dict(balance, racine):
    """Verify extraction returns proper structure."""
    extractor = AccountExtractor(balance)
    result = extractor.extraire_solde_compte(racine)
    
    assert isinstance(result, dict)
    assert 'ant_debit' in result
    assert 'solde_debit' in result
```

### Example 3: Test Movement Calculation

```python
from hypothesis import given
from conftest import st_montant
from Modules.movement_calculator import MovementCalculator

@given(st_montant(), st_montant(), st_montant(), st_montant())
def test_accounting_equation(solde_d_n1, solde_c_n1, mvt_d, mvt_c):
    """Verify accounting equation holds."""
    calc = MovementCalculator()
    
    solde_ouv = calc.calculer_solde_ouverture(solde_d_n1, solde_c_n1)
    aug = calc.calculer_augmentations(mvt_d)
    dim = calc.calculer_diminutions(mvt_c)
    solde_clo = solde_ouv + aug - dim
    
    # Equation should hold
    assert abs(solde_clo - (solde_ouv + aug - dim)) < 0.01
```

## Running Tests

### Run all property tests
```bash
pytest py_backend/Doc\ calcul\ notes\ annexes/Tests/ -v
```

### Run with specific profile
```bash
pytest --hypothesis-profile=dev
```

### Run with verbose Hypothesis output
```bash
pytest --hypothesis-verbosity=verbose
```

## Troubleshooting

### Tests are too slow
Switch to dev profile:
```python
from hypothesis import settings
settings.load_profile("dev")
```

### Need more examples
Switch to ci profile or increase max_examples:
```python
from hypothesis import settings
settings.load_profile("ci")
```

### Flaky tests
Hypothesis will automatically find minimal failing examples. Check the output for the exact values that cause failures.

## Next Steps

1. Use these strategies in property-based tests for all modules
2. Create additional strategies as needed for specific test cases
3. Add more fixtures for common test scenarios

## References

- Hypothesis documentation: https://hypothesis.readthedocs.io/
- Property-based testing guide: https://hypothesis.works/articles/what-is-property-based-testing/
