# Quick Start - Test Fixtures

## Vue d'ensemble

Les fixtures de test sont des fichiers de données pré-configurés utilisés pour tester le système de calcul des notes annexes SYSCOHADA.

## Fichiers disponibles

### 1. balance_demo_n_n1_n2.xlsx ✓
**Balance complète et valide avec 3 exercices**

- **Contenu**: 13 comptes représentatifs couvrant:
  - Immobilisations incorporelles (211, 212, 2811, 2812)
  - Immobilisations corporelles (221, 222, 2822)
  - Capital et réserves (101, 111)
  - Charges (601, 66, 681)
  - Produits (701)

- **Structure**: 3 onglets
  - BALANCE N (exercice en cours)
  - BALANCE N-1 (exercice précédent)
  - BALANCE N-2 (exercice antérieur)

- **Utilisation**: Tests d'intégration complets
  ```python
  from Modules.balance_reader import BalanceReader
  
  reader = BalanceReader('Tests/fixtures/balance_demo_n_n1_n2.xlsx')
  balance_n, balance_n1, balance_n2 = reader.charger_balances()
  ```

### 2. balance_incomplete.xlsx ✓
**Balance incomplète pour tester la gestion d'erreurs**

- **Contenu**: 2 comptes seulement
- **Structure**: 2 onglets (BALANCE N et BALANCE N-1, **manque N-2**)
- **Utilisation**: Tester la robustesse du système face aux données manquantes
  ```python
  # Doit gérer gracieusement l'absence de N-2
  reader = BalanceReader('Tests/fixtures/balance_incomplete.xlsx')
  # Le système doit continuer sans crasher
  ```

### 3. balance_invalid_format.xlsx ✓
**Balance avec format invalide**

- **Contenu**: 2 comptes
- **Structure**: Colonnes manquantes (pas de "Débit" ni "Crédit")
- **Utilisation**: Tester la validation du format
  ```python
  # Doit détecter le format invalide
  reader = BalanceReader('Tests/fixtures/balance_invalid_format.xlsx')
  # Doit lever InvalidBalanceFormatException
  ```

### 4. correspondances_test.json ✓
**Fichier de mapping de test**

- **Contenu**: Sous-ensemble des correspondances SYSCOHADA
  - Bilan actif: Immobilisations incorporelles, corporelles, financières
  - Bilan passif: Capital, Réserves, Provisions
  - Charges: Achats, Services, Personnel, Dotations
  - Produits: Ventes, Subventions, Reprises

- **Utilisation**: Tests unitaires des modules
  ```python
  from Modules.mapping_manager import MappingManager
  
  manager = MappingManager('Tests/fixtures/correspondances_test.json')
  racines = manager.obtenir_racines_compte('Immobilisations incorporelles', 'bilan_actif')
  ```

## Utilisation dans les tests

### Avec pytest fixtures

Les fixtures sont automatiquement disponibles via `conftest.py`:

```python
def test_balance_loading(fichier_balance_demo):
    """Le fixture est injecté automatiquement."""
    reader = BalanceReader(fichier_balance_demo)
    balance_n, balance_n1, balance_n2 = reader.charger_balances()
    assert len(balance_n) > 0
```

### Avec Hypothesis

Les stratégies de génération sont également disponibles:

```python
from hypothesis import given
from conftest import st_balance

@given(balance=st_balance())
def test_property(balance):
    """Test avec balance générée aléatoirement."""
    assert len(balance) >= 10
```

## Régénération des fixtures

Si vous devez régénérer les fichiers Excel:

```bash
python py_backend/Doc\ calcul\ notes\ annexes/Tests/fixtures/create_test_balances.py
```

## Structure des données

### Format balance Excel

| Colonne | Type | Description |
|---------|------|-------------|
| Numéro | str | Numéro de compte SYSCOHADA |
| Intitulé | str | Libellé du compte |
| Ant Débit | float | Solde débiteur d'ouverture |
| Ant Crédit | float | Solde créditeur d'ouverture |
| Débit | float | Mouvements débiteurs |
| Crédit | float | Mouvements créditeurs |
| Solde Débit | float | Solde débiteur de clôture |
| Solde Crédit | float | Solde créditeur de clôture |

### Format correspondances JSON

```json
{
  "section": {
    "Poste": {
      "brut": ["racine1", "racine2"],
      "amort": ["racine3", "racine4"]
    }
  }
}
```

## Validation des fixtures

Pour vérifier que les fixtures sont valides:

```python
import os
import pandas as pd

# Vérifier balance_demo_n_n1_n2.xlsx
path = 'Tests/fixtures/balance_demo_n_n1_n2.xlsx'
assert os.path.exists(path), "Fichier manquant"

xl = pd.ExcelFile(path)
assert 'BALANCE N' in xl.sheet_names
assert 'BALANCE N-1' in xl.sheet_names
assert 'BALANCE N-2' in xl.sheet_names

df = pd.read_excel(path, sheet_name='BALANCE N')
assert 'Numéro' in df.columns
assert 'Débit' in df.columns
assert len(df) > 0
```

## Prochaines étapes

1. ✓ Fixtures créées
2. Utiliser dans les tests unitaires
3. Utiliser dans les tests d'intégration
4. Ajouter plus de comptes si nécessaire

## Références

- **Requirements**: 11.7
- **Task**: 27.2
- **Related**: conftest.py, test_balance_reader.py
