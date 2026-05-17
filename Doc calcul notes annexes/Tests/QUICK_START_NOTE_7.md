# Quick Start Guide - Note 7: Trésorerie Actif

## Vue d'ensemble

La **Note 7 - Trésorerie Actif** calcule automatiquement les disponibilités de l'entreprise (cash and cash equivalents) à partir des balances comptables SYSCOHADA.

## Comptes concernés

### Comptes de trésorerie actif (5X)

| Compte | Libellé | Description |
|--------|---------|-------------|
| **51X** | **Banques et établissements financiers** | |
| 511 | Valeurs à l'encaissement | Chèques et effets en cours d'encaissement |
| 512 | Banques | Comptes bancaires courants |
| 513 | Établissements financiers | Comptes dans les établissements financiers |
| 514 | Chèques postaux | Comptes chèques postaux |
| **52X** | **Caisse** | |
| 521-528 | Caisses diverses | Caisse siège, succursales, etc. |
| **53X** | **Régies d'avances** | |
| 531 | Régies d'avances | Avances pour dépenses courantes |
| 532 | Accréditifs | Lettres de crédit |
| **54X** | **Instruments de trésorerie** | |
| 541 | Bons de caisse et du Trésor | Placements à court terme |
| 542 | Titres de placement | Valeurs mobilières de placement |
| **57X** | **Virements internes** | |
| 571 | Virements de fonds | Transferts entre comptes |
| 572 | Virements d'exploitation | Virements liés à l'exploitation |

### Comptes de provisions (59X)

| Compte | Libellé | Description |
|--------|---------|-------------|
| 5941 | Provisions sur bons de caisse | Dépréciation des bons de caisse |
| 5942 | Provisions sur titres de placement | Dépréciation des titres |

## Structure de la Note 7

La Note 7 comprend **6 lignes de détail + 1 ligne de total**:

1. Banques, établissements financiers et assimilés
2. Chèques postaux, caisse nationale d'épargne
3. Caisse
4. Régies d'avances et accréditifs
5. Instruments de trésorerie
6. Virements internes
7. **TOTAL TRÉSORERIE ACTIF**

## Colonnes calculées

Pour chaque ligne, 11 colonnes sont calculées:

### Valeurs brutes
- **Début exercice**: Solde d'ouverture N
- **Augmentations**: Mouvements débiteurs N (encaissements)
- **Diminutions**: Mouvements créditeurs N (décaissements)
- **Fin exercice**: Solde de clôture N

### Provisions (si applicable)
- **Début exercice**: Provisions d'ouverture
- **Dotations**: Provisions constituées
- **Reprises**: Provisions reprises
- **Fin exercice**: Provisions de clôture

### Valeurs nettes
- **Début exercice**: Brut - Provisions (ouverture)
- **Fin exercice**: Brut - Provisions (clôture)

## Utilisation

### Méthode 1: Ligne de commande

```bash
# Avec le fichier de balance par défaut
python py_backend/Doc\ calcul\ notes\ annexes/Scripts/calculer_note_7.py

# Avec un fichier de balance spécifique
python py_backend/Doc\ calcul\ notes\ annexes/Scripts/calculer_note_7.py "chemin/vers/balance.xlsx"

# Avec des chemins de sortie personnalisés
python py_backend/Doc\ calcul\ notes\ annexes/Scripts/calculer_note_7.py \
    --output-html "mon_rapport.html" \
    --output-trace "ma_trace.json"
```

### Méthode 2: Script PowerShell (Windows)

```powershell
# Exécuter le test complet
.\test-note-7.ps1
```

### Méthode 3: Import Python

```python
from calculer_note_7 import CalculateurNote7

# Créer le calculateur
calculateur = CalculateurNote7("chemin/vers/balance.xlsx")

# Exécuter le calcul complet
calculateur.executer(
    fichier_html="output/note_7.html",
    fichier_trace="output/trace_7.json"
)
```

## Fichiers générés

### 1. Fichier HTML (test_note_7.html)

Tableau formaté avec:
- En-têtes conformes au format SYSCOHADA
- Montants formatés avec séparateurs de milliers
- Ligne de total en gras
- Style CSS professionnel

### 2. Fichier de trace JSON (trace_note_7.json)

Contient:
- Détail de tous les calculs
- Comptes sources utilisés
- Métadonnées (date, fichier, hash MD5)
- Traçabilité complète pour audit

## Exemple de sortie

```
================================================================================
  CALCULATEUR NOTE 7 - TRÉSORERIE ACTIF
================================================================================

📂 Chargement des balances depuis: P000 -BALANCE DEMO N_N-1_N-2.xlsx
✓ Balance N   : 245 lignes chargées
✓ Balance N-1 : 245 lignes chargées
✓ Balance N-2 : 245 lignes chargées

🔢 Calcul de la note 7...
  Calcul: Banques, établissements financiers et assimilés...
  Calcul: Chèques postaux, caisse nationale d'épargne...
  Calcul: Caisse...
  Calcul: Régies d'avances et accréditifs...
  Calcul: Instruments de trésorerie...
  Calcul: Virements internes...
✓ Note calculée: 7 lignes

📄 Génération du HTML...
✓ HTML généré

✓ Fichier HTML sauvegardé: ../Tests/test_note_7.html
✓ Fichier de trace sauvegardé: ../Tests/trace_note_7.json

────────────────────────────────────────────────────────────────────────────────
  RÉSUMÉ NOTE 7
────────────────────────────────────────────────────────────────────────────────

  Nombre de lignes: 6
  VNC Ouverture:        5,250,000
  VNC Clôture:          6,180,000
  Variation:              930,000

================================================================================
  ✓ NOTE 7 CALCULÉE AVEC SUCCÈS EN 1.23s
================================================================================
```

## Particularités de la Note 7

### 1. Pas d'amortissements

Les comptes de trésorerie ne sont généralement **pas amortis**. Seuls les instruments de trésorerie (titres de placement) peuvent faire l'objet de provisions pour dépréciation.

### 2. Mouvements importants

La trésorerie a généralement des **mouvements très importants** (encaissements et décaissements quotidiens), ce qui peut générer des montants élevés dans les colonnes "Augmentations" et "Diminutions".

### 3. Virements internes

Les **virements internes** (compte 57X) doivent normalement se solder à zéro en fin d'exercice, car ils représentent des transferts entre comptes de l'entreprise.

### 4. Cohérence avec le tableau de flux de trésorerie

Le total de la Note 7 doit être **cohérent** avec:
- Le poste "Trésorerie Actif" du bilan
- Le tableau de flux de trésorerie (TFT)

## Vérifications automatiques

Le calculateur effectue automatiquement:

✓ Vérification de l'équation comptable pour chaque ligne  
✓ Détection des VNC négatives (anormales)  
✓ Validation des soldes de clôture  
✓ Traçabilité complète des calculs  
✓ Logging des avertissements  

## Dépannage

### Erreur: "Balance non trouvée"

```
✗ Erreur lors du chargement des balances: Impossible de trouver l'onglet 'BALANCE N'
```

**Solution**: Vérifiez que le fichier Excel contient bien les onglets "BALANCE N", "BALANCE N-1" et "BALANCE N-2".

### Avertissement: "Incohérence détectée"

```
⚠ Incohérence détectée pour 'Banques': écart de 1500.00
```

**Cause**: L'équation comptable n'est pas respectée (Solde clôture ≠ Solde ouverture + Augmentations - Diminutions).

**Action**: Vérifier les données de la balance pour ce compte.

### Avertissement: "VNC négative"

```
⚠ VNC négative détectée pour 'Instruments de trésorerie': -50000.00
```

**Cause**: Les provisions dépassent la valeur brute (situation anormale).

**Action**: Vérifier les comptes de provisions 5941/5942.

## Intégration avec Claraverse

La Note 7 s'intègre automatiquement dans l'interface Claraverse:

1. Upload du fichier de balance via l'interface "Etat fin"
2. Clic sur "Calculer Notes Annexes"
3. Affichage de la Note 7 dans un accordéon cliquable
4. Export possible en HTML ou Excel

## Références

- **Requirement 5.1**: Génération des scripts de calcul
- **Requirement 5.2**: Structure des calculateurs
- **Requirement 5.3**: Mapping des comptes
- **Requirement 5.4**: Conformité SYSCOHADA

## Support

Pour toute question ou problème:
1. Consulter le fichier `TROUBLESHOOTING.md`
2. Vérifier les logs dans `calcul_notes_warnings.log`
3. Examiner le fichier de trace JSON pour le détail des calculs

---

**Date de création**: 25 Avril 2026  
**Version**: 1.0  
**Auteur**: Système de calcul automatique des notes annexes SYSCOHADA
