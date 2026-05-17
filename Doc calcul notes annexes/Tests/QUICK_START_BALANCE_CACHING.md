# Quick Start - Balance Caching

## Vue d'ensemble

Le système de mise en cache des balances optimise les performances en:
1. **Chargement unique**: Les balances sont chargées une seule fois en mémoire
2. **Accès O(1)**: Index par dictionnaire pour accès instantané aux comptes
3. **Cache de résultats**: Réutilisation des calculs répétés

## Fonctionnalités implémentées

### 1. Cache des balances (Requirements 12.2, 12.4)

```python
orchestrateur = CalculNotesAnnexesMain(fichier_balance)

# Premier chargement: lit le fichier Excel
orchestrateur.charger_balances()  # ~2-3 secondes

# Chargements suivants: utilise le cache
orchestrateur.charger_balances()  # ~0.001 secondes (instantané)
```

### 2. Index dictionnaire pour O(1) (Requirements 12.3, 12.4)

```python
# Accès direct à un compte (O(1))
compte = orchestrateur.obtenir_compte_cache('211', exercice=0)
# Retourne: {'Numéro': '211', 'Intitulé': '...', 'Débit': ..., ...}

# Recherche par racine (optimisée)
comptes_21 = orchestrateur.obtenir_comptes_par_racine_cache('21', exercice=0)
# Retourne: liste de tous les comptes commençant par '21'
```

### 3. Cache de résultats (Requirement 12.4)

```python
# Mettre un résultat en cache
cle = "calcul_note_3a_ligne_1"
resultat = {"brut_ouverture": 1500000, "vnc_cloture": 1200000}
orchestrateur.mettre_en_cache_resultat(cle, resultat)

# Récupérer du cache
resultat_cache = orchestrateur.obtenir_resultat_cache(cle)
if resultat_cache:
    print("Résultat trouvé en cache!")
```

### 4. Statistiques du cache

```python
stats = orchestrateur.obtenir_stats_cache()
print(f"Balances en cache: {stats['balances_en_cache']}")
print(f"Comptes indexés: {stats['nombre_comptes_indexes']}")
print(f"Résultats en cache: {stats['nombre_resultats_caches']}")
print(f"Taille cache: {stats['taille_cache_resultats_mb']:.2f} MB")
```

## Exécuter les tests

### Test complet

```bash
cd "py_backend/Doc calcul notes annexes/Tests"
python test_balance_caching.py
```

### Test rapide avec PowerShell

```powershell
cd "py_backend/Doc calcul notes annexes/Tests"
.\test-balance-caching.ps1
```

## Résultats attendus

### Test 1: Chargement unique
- ✓ Premier chargement: ~2-3 secondes
- ✓ Deuxième chargement (cache): ~0.001 secondes
- ✓ Gain de performance: >1000x plus rapide

### Test 2: Index O(1)
- ✓ Balance N: ~500+ comptes indexés
- ✓ Balance N-1: ~500+ comptes indexés
- ✓ Balance N-2: ~500+ comptes indexés
- ✓ Accès à un compte: <1ms

### Test 3: Recherche par racine
- ✓ Comptes trouvés avec racine '21': plusieurs comptes
- ✓ Temps de recherche: <10ms

### Test 4: Cache de résultats
- ✓ Résultat mis en cache et récupéré avec succès
- ✓ Clé inexistante retourne None

### Test 5: Statistiques
- ✓ Balances en cache: True
- ✓ Comptes indexés: >1500
- ✓ Résultats en cache: 5
- ✓ Taille cache: <1 MB

### Test 6: Performance globale
- ✓ 100 accès aux comptes: <1 seconde
- ✓ Temps moyen par accès: <10ms

## Architecture du cache

```
CalculNotesAnnexesMain
├── balances (DataFrames)          # Cache des balances brutes
│   ├── balance_n
│   ├── balance_n1
│   └── balance_n2
│
├── balances_dict (Dictionnaires)  # Index pour O(1)
│   ├── {numero_compte: données}   # Balance N
│   ├── {numero_compte: données}   # Balance N-1
│   └── {numero_compte: données}   # Balance N-2
│
└── cache_resultats                # Cache des calculs
    └── {cle_calcul: resultat}
```

## Avantages

1. **Performance**: Chargement unique des balances (gain >1000x)
2. **Efficacité**: Accès O(1) aux comptes via dictionnaire
3. **Réutilisation**: Cache des résultats de calculs répétés
4. **Mémoire**: Optimisation de l'utilisation mémoire
5. **Scalabilité**: Support de calculs parallèles

## Utilisation dans les calculateurs

Les calculateurs individuels peuvent utiliser le cache:

```python
class CalculateurNote3A:
    def __init__(self, fichier_balance: str):
        self.fichier_balance = fichier_balance
        # Les balances seront fournies par l'orchestrateur
        self.balance_n = None
        self.balance_n1 = None
        self.balance_n2 = None
    
    def charger_balances(self):
        # Si les balances sont déjà fournies (cache), ne pas recharger
        if self.balance_n is not None:
            return True
        
        # Sinon, charger normalement
        reader = BalanceReader(self.fichier_balance)
        self.balance_n, self.balance_n1, self.balance_n2 = reader.charger_balances()
        return True
```

## Contraintes de performance

- **Objectif**: Calcul des 33 notes en <30 secondes
- **Avec cache**: Chargement unique des balances économise ~2-3s par note
- **Gain total**: ~60-90 secondes économisées sur 33 notes
- **Résultat**: Performance largement améliorée

## Prochaines étapes

1. ✓ Implémentation du cache de balances
2. ✓ Index dictionnaire pour O(1)
3. ✓ Cache de résultats
4. ✓ Tests de validation
5. → Intégration dans tous les calculateurs
6. → Tests de performance globale

## Support

Pour toute question ou problème:
- Consulter les logs: `Logs/calcul_notes_annexes.log`
- Vérifier les tests: `test_balance_caching.py`
- Voir la documentation: `README.md`
