# Quick Start - Validation de Cohérence (Tâche 30.4)

## Vue d'ensemble

Ce guide explique comment exécuter les tests de validation de cohérence pour la tâche 30.4 du projet de calcul automatique des notes annexes SYSCOHADA.

## Objectifs de la validation

La tâche 30.4 vérifie que:

1. ✅ **Taux de cohérence inter-notes >= 95%**
2. ✅ **Total immobilisations correspond au bilan**
3. ✅ **Dotations amortissements correspondent au compte de résultat**
4. ✅ **Continuité temporelle (N-1 clôture = N ouverture)**
5. ✅ **Rapport HTML de cohérence généré**

## Prérequis

- Python 3.8 ou supérieur
- Modules Python: pandas, logging

## Exécution rapide

### Option 1: Script PowerShell (Windows)

```powershell
./test-coherence-validation-30-4.ps1
```

### Option 2: Python direct

```bash
cd "py_backend/Doc calcul notes annexes/Tests"
python test_coherence_validation_complete.py
```

## Résultats attendus

### Tests exécutés

Le script exécute 5 tests de validation:

1. **Test 1: Taux de cohérence >= 95%**
   - Vérifie que le taux global de cohérence est supérieur ou égal à 95%
   - Requirements: 10.5, 10.6

2. **Test 2: Total immobilisations**
   - Vérifie que la somme des Notes 3A-3E correspond au bilan actif
   - Requirements: 10.1, 10.2

3. **Test 3: Dotations amortissements**
   - Vérifie que les dotations des Notes 3A-3E correspondent au compte de résultat
   - Requirements: 10.1, 10.2

4. **Test 4: Continuité temporelle**
   - Vérifie que Solde Clôture N-1 = Solde Ouverture N pour toutes les notes
   - Requirements: 10.3

5. **Test 5: Génération rapport**
   - Vérifie que le rapport HTML est généré avec tous les éléments requis
   - Requirements: 10.7

### Sortie attendue

```
================================================================================
VALIDATION DE COHÉRENCE - TÂCHE 30.4
================================================================================

Date: 29/04/2026 17:38:44

[Tests détaillés...]

================================================================================
RÉSUMÉ DES TESTS
================================================================================

📊 Résultats:
   ✓ RÉUSSI - Test 1 - Taux cohérence >= 95%
   ✓ RÉUSSI - Test 2 - Total immobilisations
   ✓ RÉUSSI - Test 3 - Dotations amortissements
   ✓ RÉUSSI - Test 4 - Continuité temporelle
   ✓ RÉUSSI - Test 5 - Génération rapport

   Total: 5/5 tests réussis (100%)

================================================================================
✓ VALIDATION COMPLÈTE RÉUSSIE
================================================================================

Tous les critères de la tâche 30.4 sont satisfaits:
  ✓ Taux de cohérence inter-notes >= 95%
  ✓ Total immobilisations correspond au bilan
  ✓ Dotations amortissements correspondent au compte de résultat
  ✓ Continuité temporelle vérifiée (N-1 clôture = N ouverture)
  ✓ Rapport HTML de cohérence généré
```

## Rapport HTML généré

Le test génère un rapport HTML détaillé:

**Emplacement**: `py_backend/Doc calcul notes annexes/Tests/rapport_coherence_validation_30_4.html`

**Contenu du rapport**:
- Taux de cohérence global avec code couleur
- Alertes (warnings et critiques)
- Validation du total des immobilisations avec détail par note
- Validation des dotations aux amortissements avec détail par note
- Validation de la continuité temporelle pour chaque note
- Métadonnées (date, nombre de notes, nombre d'alertes)

## Interprétation des résultats

### Taux de cohérence

- **100%**: Toutes les validations sont cohérentes (écart < 1%)
- **95-99%**: Cohérence acceptable, quelques écarts mineurs
- **< 95%**: Cohérence insuffisante, alerte critique émise

### Codes couleur du rapport

- 🟢 **Vert** (>= 95%): Cohérence excellente
- 🟡 **Jaune** (90-94%): Cohérence acceptable
- 🔴 **Rouge** (< 90%): Cohérence insuffisante

### Alertes

- **WARNING**: Écart détecté mais non critique
- **CRITICAL**: Taux de cohérence < 95%, action requise

## Données de test

Le script utilise des données de test cohérentes comprenant:

- **Note 3A**: Immobilisations Incorporelles (4 lignes + total)
- **Note 3B**: Immobilisations Corporelles (4 lignes + total)
- **Note 3C**: Immobilisations Financières (2 lignes + total)
- **Note 3D**: Charges Immobilisées (2 lignes + total)
- **Note 3E**: Écarts de Conversion Actif (1 ligne + total)
- **Note 26**: Dotations aux Amortissements (compte de résultat)

**Totaux attendus**:
- Total immobilisations: 10,857,000.00
- Total dotations: 648,000.00
- Continuité temporelle: 100% (5/5 notes)

## Dépannage

### Erreur: Module non trouvé

```bash
# Vérifier que vous êtes dans le bon répertoire
cd "py_backend/Doc calcul notes annexes/Tests"

# Vérifier que le module coherence_validator.py existe
ls ../Modules/coherence_validator.py
```

### Erreur: Python non trouvé

```bash
# Vérifier l'installation de Python
python --version

# Ou essayer avec python3
python3 --version
```

### Tests échoués

Si des tests échouent:

1. Consultez les logs détaillés dans la sortie console
2. Vérifiez les alertes émises par le validateur
3. Ouvrez le rapport HTML pour voir les détails des écarts
4. Vérifiez que les données de test sont correctes

## Fichiers générés

Après l'exécution, les fichiers suivants sont créés:

```
py_backend/Doc calcul notes annexes/Tests/
├── rapport_coherence_validation_30_4.html  # Rapport HTML détaillé
└── [logs dans la console]                   # Logs d'exécution
```

## Prochaines étapes

Une fois la validation réussie:

1. ✅ Marquer la tâche 30.4 comme complète
2. ✅ Archiver le rapport HTML pour référence
3. ✅ Passer à la tâche 31 (Checkpoint final)

## Références

- **Requirements**: 10.1, 10.2, 10.3, 10.5, 10.6
- **Module**: `coherence_validator.py`
- **Tests**: `test_coherence_validation_complete.py`
- **Documentation**: `README.md` dans le dossier principal

## Support

Pour toute question ou problème:

1. Consultez la documentation complète dans `py_backend/Doc calcul notes annexes/`
2. Vérifiez les logs d'exécution pour les détails des erreurs
3. Ouvrez le rapport HTML pour une analyse visuelle

---

**Date de création**: 29/04/2026  
**Version**: 1.0  
**Statut**: ✅ Validation complète réussie
