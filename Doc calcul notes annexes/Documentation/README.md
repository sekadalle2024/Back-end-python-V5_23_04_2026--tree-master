# Documentation - Calcul des Notes Annexes

## Vue d'ensemble

Ce dossier contient la documentation et les fichiers de référence pour le calcul automatique des notes annexes des états financiers syscohada révisé.

## Fichiers de référence

Les fichiers de référence sont maintenant dans le dossier `../Ressources/`

### Fichiers Excel
- **NOTE 3A.xlsx** : Modèle de la Note 3A (Immobilisations incorporelles)
- **NOTE 3A renseignee.png** : Capture d'écran d'une Note 3A remplie
- **Liasse_officielle_revise.xlsx** : Template complet de la liasse officielle

### Plan de comptes
- **Syscohada revise plan compte.pdf** : Plan de comptes officiel syscohada révisé

## Scripts de calcul

Les scripts Python sont maintenant dans le dossier `../Scripts/`

### Note 3A - Immobilisations incorporelles
**Script** : `../Scripts/calculer_note_3a.py`

**Fonctionnalités** :
- Lecture automatique des balances N, N-1, N-2
- Calcul des valeurs brutes (ouverture, augmentations, diminutions, clôture)
- Calcul des amortissements (ouverture, dotations, reprises, clôture)
- Calcul des valeurs nettes comptables
- Génération HTML du tableau

**Comptes traités** :
- Frais de recherche et de développement (211, 2811, 2919)
- Brevets, licences, logiciels (212, 213, 214, 2812-2814, 2912-2914)
- Fonds commercial (215, 216, 2815, 2816, 2915, 2916)
- Autres immobilisations incorporelles (217, 218, 2817, 2818, 2917, 2918)

**Utilisation** :
```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Scripts
python calculer_note_3a.py
```

**Résultat** : Fichier `test_note_3a.html` généré

## Structure des notes annexes

### Note 3A - Immobilisations incorporelles
Tableau avec les colonnes suivantes :
- Libellé
- Valeur brute (4 colonnes)
- Amortissements (4 colonnes)
- Valeur nette comptable (2 colonnes)

### Notes à développer
- **Note 3B** : Immobilisations corporelles
- **Note 3C** : Immobilisations financières
- **Note 4** : Stocks
- **Note 5** : Créances
- **Note 6** : Trésorerie
- **Note 7** : Capitaux propres
- **Note 8** : Dettes
- Etc.

## Méthodologie

### 1. Lecture des balances
Les balances sont au format 8 colonnes :
- Numéro
- Intitulé
- Ant Débit
- Ant Crédit
- Mvt Débit (mouvements de l'exercice)
- Mvt Crédit (mouvements de l'exercice)
- Solde Débit
- Solde Crédit

### 2. Extraction des données
Pour chaque ligne de la note annexe :
- Identifier les comptes concernés (brut et amortissements)
- Extraire les soldes de N-1 (ouverture)
- Extraire les mouvements de N (augmentations/diminutions)
- Extraire les soldes de N (clôture)

### 3. Calculs
- **Augmentations** = Mouvements débit N des comptes de brut
- **Diminutions** = Mouvements crédit N des comptes de brut
- **Dotations** = Mouvements crédit N des comptes d'amortissement
- **Reprises** = Mouvements débit N des comptes d'amortissement
- **VNC** = Valeur brute - Amortissements

### 4. Génération du tableau
- Format HTML avec CSS
- Mise en forme professionnelle
- Conforme au modèle syscohada révisé

## Problèmes résolus

### Espaces dans les noms d'onglets
Les onglets Excel peuvent avoir des espaces à la fin :
- 'BALANCE N ' (10 caractères)
- 'BALANCE N-1 ' (12 caractères)
- 'BALANCE N-2' (11 caractères)

**Solution** : Détection automatique avec `strip()` et recherche intelligente

### Conversion des données
Les colonnes Excel peuvent contenir des strings au lieu de nombres.

**Solution** : Fonction `to_float()` robuste qui :
- Gère les valeurs None, NaN, chaînes vides
- Nettoie les espaces
- Remplace les virgules par des points
- Retourne 0.0 en cas d'erreur

## Documentation

- **00_CALCUL_NOTE_3A_REUSSI_08_AVRIL_2026.txt** : Documentation complète de la Note 3A
- **QUICK_START_NOTE_3A.txt** : Guide rapide d'utilisation

## Tests

Script de test rapide :
```bash
./test-note-3a.ps1
```

## Prochaines étapes

1. Développer les scripts pour les autres notes annexes
2. Intégrer dans le backend API
3. Créer les composants React pour l'affichage frontend
4. Permettre l'export Excel des notes annexes

## Références

- Plan de comptes syscohada révisé
- Liasse officielle syscohada révisé
- Balances demo : `P000 -BALANCE DEMO N_N-1_N-2.xls`

---

**Dernière mise à jour** : 08 Avril 2026
