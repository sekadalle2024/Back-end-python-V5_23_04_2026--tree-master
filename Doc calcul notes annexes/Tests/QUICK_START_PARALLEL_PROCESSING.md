# Quick Start - Traitement Parallèle Optionnel

## Vue d'ensemble

Le système de calcul des notes annexes SYSCOHADA supporte le **traitement parallèle optionnel** pour améliorer les performances. Le mode parallèle calcule les notes indépendantes en parallèle tout en gérant automatiquement les contraintes de mémoire.

## Utilisation

### Mode Séquentiel (Par défaut)

```bash
# Calcul séquentiel standard
python calcul_notes_annexes_main.py
```

### Mode Parallèle

```bash
# Activer le mode parallèle avec configuration automatique
python calcul_notes_annexes_main.py --parallel

# Spécifier le nombre de workers
python calcul_notes_annexes_main.py --parallel --workers 4

# Avec un fichier de balance personnalisé
python calcul_notes_annexes_main.py --parallel --balance "chemin/vers/balance.xlsx"
```

## Utilisation Programmatique

```python
from calcul_notes_annexes_main import CalculNotesAnnexesMain

# Mode séquentiel
orchestrateur_seq = CalculNotesAnnexesMain(
    "balance.xlsx",
    mode_parallele=False
)

# Mode parallèle avec 4 workers
orchestrateur_par = CalculNotesAnnexesMain(
    "balance.xlsx",
    mode_parallele=True,
    max_workers=4
)

# Calculer toutes les notes
notes = orchestrateur_par.calculer_toutes_notes()
```

## Fonctionnalités Clés

### 1. Groupes de Notes Indépendantes

Le système identifie automatiquement 8 groupes de notes qui peuvent être calculées en parallèle:

- **Groupe 1**: Immobilisations (3a, 3b, 3c, 3d, 3e)
- **Groupe 2**: Actif circulant (4, 5, 6, 7)
- **Groupe 3**: Capitaux propres (8, 9, 10)
- **Groupe 4**: Provisions et emprunts (11, 12)
- **Groupe 5**: Dettes (13-20)
- **Groupe 6**: Charges d'exploitation (21-25)
- **Groupe 7**: Dotations (26, 27)
- **Groupe 8**: Produits (28-33)

### 2. Vérification Automatique de la Mémoire

Le système vérifie la mémoire disponible avant et pendant le calcul parallèle:

```python
# Vérifier la mémoire disponible (seuil: 500 MB)
if orchestrateur.verifier_memoire_disponible(seuil_mb=500.0):
    print("Mémoire suffisante pour le mode parallèle")
else:
    print("Basculement en mode séquentiel")
```

### 3. Fallback Automatique

Si la mémoire devient insuffisante pendant le calcul:
- Le système bascule automatiquement en mode séquentiel
- Les notes déjà calculées sont préservées
- Le calcul continue sans interruption

## Tests

### Exécuter les Tests

```bash
# Tous les tests de traitement parallèle
pytest test_parallel_processing.py -v

# Test spécifique
pytest test_parallel_processing.py::TestParallelProcessing::test_performance_parallele_vs_sequentiel -v

# Avec sortie détaillée
pytest test_parallel_processing.py -v -s
```

### Tests Disponibles

1. **test_groupes_independants_definis**: Vérifie la définition des groupes
2. **test_verification_memoire_disponible**: Teste la vérification mémoire
3. **test_mode_parallele_active**: Vérifie l'activation du mode parallèle
4. **test_fallback_sequentiel_memoire_insuffisante**: Teste le fallback
5. **test_calcul_parallele_par_groupes**: Vérifie le calcul par groupes
6. **test_performance_parallele_vs_sequentiel**: Compare les performances
7. **test_gestion_erreurs_parallele**: Teste la gestion des erreurs
8. **test_configuration_workers**: Vérifie la configuration des workers
9. **test_integration_complete_parallele**: Test d'intégration complet

## Performances Attendues

### Mode Séquentiel
- **Durée**: ~15-25 secondes (33 notes)
- **Mémoire**: ~200-300 MB
- **CPUs**: 1 core utilisé

### Mode Parallèle (4 workers)
- **Durée**: ~8-15 secondes (33 notes)
- **Mémoire**: ~400-600 MB
- **CPUs**: 4 cores utilisés
- **Gain**: 30-50% plus rapide

## Configuration Recommandée

### Pour Machines Standard (4-8 GB RAM)
```bash
python calcul_notes_annexes_main.py --parallel --workers 2
```

### Pour Machines Puissantes (16+ GB RAM)
```bash
python calcul_notes_annexes_main.py --parallel --workers 4
```

### Pour Serveurs
```bash
python calcul_notes_annexes_main.py --parallel --workers 8
```

## Logs et Monitoring

Le système génère des logs détaillés:

```
[2026-04-29 10:00:00] [INFO] MODE PARALLÈLE ACTIVÉ
[2026-04-29 10:00:00] [INFO] Nombre de workers: 4
[2026-04-29 10:00:00] [INFO] Groupes indépendants identifiés: 8
[2026-04-29 10:00:01] [INFO] Mémoire disponible: 8192 MB / 16384 MB (50.0% libre)
[2026-04-29 10:00:01] [INFO] ✓ Mémoire suffisante pour le mode parallèle
[2026-04-29 10:00:02] [INFO] Traitement du groupe 1/8: 5 notes
[2026-04-29 10:00:03] [INFO] ✓ Note_3A calculée (groupe 1)
...
[2026-04-29 10:00:15] [INFO] MODE PARALLÈLE TERMINÉ
[2026-04-29 10:00:15] [INFO] ✓ Contrainte de performance respectée: 12.5s < 30s
```

## Dépannage

### Problème: Mode parallèle plus lent que séquentiel

**Cause**: Overhead de ProcessPoolExecutor sur petits calculs

**Solution**: Utiliser le mode séquentiel ou augmenter la complexité des calculs

### Problème: Erreur "Mémoire insuffisante"

**Cause**: Pas assez de RAM disponible

**Solution**: 
- Fermer d'autres applications
- Réduire le nombre de workers
- Utiliser le mode séquentiel

### Problème: Certaines notes échouent en mode parallèle

**Cause**: Erreurs de calcul ou dépendances manquantes

**Solution**:
- Vérifier les logs d'erreur
- Tester la note individuellement en mode séquentiel
- Vérifier les dépendances entre notes

## Exemples Complets

### Exemple 1: Calcul Parallèle Simple

```python
from calcul_notes_annexes_main import CalculNotesAnnexesMain

# Créer l'orchestrateur
orch = CalculNotesAnnexesMain(
    "balance.xlsx",
    mode_parallele=True,
    max_workers=4
)

# Calculer toutes les notes
notes = orch.calculer_toutes_notes()

# Afficher les résultats
print(f"Notes calculées: {len(notes)}")
for nom, df in notes.items():
    print(f"  {nom}: {len(df)} lignes")
```

### Exemple 2: Avec Vérification Mémoire

```python
from calcul_notes_annexes_main import CalculNotesAnnexesMain

orch = CalculNotesAnnexesMain(
    "balance.xlsx",
    mode_parallele=True
)

# Vérifier la mémoire avant de commencer
if orch.verifier_memoire_disponible(seuil_mb=500.0):
    print("✓ Mémoire suffisante, calcul parallèle activé")
    notes = orch.calculer_toutes_notes()
else:
    print("⚠ Mémoire insuffisante, utilisation du mode séquentiel")
    orch.mode_parallele = False
    notes = orch.calculer_toutes_notes()
```

### Exemple 3: Comparaison de Performances

```python
import time
from calcul_notes_annexes_main import CalculNotesAnnexesMain

# Mode séquentiel
orch_seq = CalculNotesAnnexesMain("balance.xlsx", mode_parallele=False)
debut = time.time()
notes_seq = orch_seq.calculer_toutes_notes()
duree_seq = time.time() - debut

# Mode parallèle
orch_par = CalculNotesAnnexesMain("balance.xlsx", mode_parallele=True, max_workers=4)
debut = time.time()
notes_par = orch_par.calculer_toutes_notes()
duree_par = time.time() - debut

# Comparaison
gain = ((duree_seq - duree_par) / duree_seq) * 100
print(f"Séquentiel: {duree_seq:.2f}s")
print(f"Parallèle:  {duree_par:.2f}s")
print(f"Gain:       {gain:+.1f}%")
```

## Références

- **Requirements**: 12.6, 12.7
- **Design Document**: Section "Parallel Processing"
- **Tests**: `test_parallel_processing.py`
- **Code Source**: `calcul_notes_annexes_main.py`
