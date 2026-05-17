# Test Fixtures

Ce dossier contient les fichiers de test pour les tests unitaires et d'intégration du système de calcul des notes annexes SYSCOHADA.

## Fichiers de test

### 1. balance_demo_n_n1_n2.xlsx
Balance complète et valide avec 3 exercices (N, N-1, N-2).
- Contient tous les comptes SYSCOHADA nécessaires
- Données cohérentes entre les exercices
- Utilisé pour les tests d'intégration complets

### 2. balance_incomplete.xlsx
Balance incomplète pour tester la gestion des erreurs.
- Manque l'onglet N-2
- Utilisé pour tester la robustesse du système

### 3. balance_invalid_format.xlsx
Balance avec format invalide pour tester la validation.
- Colonnes manquantes ou mal nommées
- Utilisé pour tester la détection d'erreurs de format

### 4. correspondances_test.json
Fichier de mapping de test pour les tests unitaires.
- Contient un sous-ensemble des correspondances SYSCOHADA
- Utilisé pour les tests isolés des modules

## Utilisation

Ces fixtures sont automatiquement chargées par pytest via le fichier `conftest.py`.

```python
def test_example(fichier_balance_demo):
    # Le fixture est automatiquement injecté
    reader = BalanceReader(fichier_balance_demo)
    ...
```
