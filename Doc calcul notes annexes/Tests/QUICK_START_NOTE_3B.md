# Quick Start - Note 3B Immobilisations Corporelles

## Vue d'ensemble

La Note 3B calcule automatiquement le tableau des immobilisations corporelles selon le format SYSCOHADA Révisé. Elle couvre 9 catégories d'immobilisations corporelles.

## Catégories d'immobilisations corporelles

1. **Terrains** (compte 221)
2. **Bâtiments** (comptes 222, 223)
3. **Installations et agencements** (compte 224)
4. **Matériel** (comptes 225, 226)
5. **Matériel de transport** (compte 227)
6. **Avances et acomptes versés sur immobilisations** (compte 228)
7. **Immobilisations corporelles en cours** (compte 229)
8. **Autres immobilisations corporelles** (comptes 2281-2287)
9. **Immobilisations corporelles hors exploitation** (compte 2288)

## Mapping des comptes SYSCOHADA

### Comptes bruts (classe 22X)
- 221: Terrains
- 222-223: Bâtiments
- 224: Installations et agencements
- 225-226: Matériel
- 227: Matériel de transport
- 228: Avances et acomptes
- 229: Immobilisations en cours
- 2281-2287: Autres immobilisations corporelles
- 2288: Immobilisations hors exploitation

### Comptes amortissements (classe 282X et 292X)
- 282X: Amortissements des immobilisations corporelles
- 292X: Provisions pour dépréciation des immobilisations corporelles

## Exécution rapide

### Méthode 1: Script PowerShell (recommandé)
```powershell
.\test-note-3b.ps1
```

### Méthode 2: Ligne de commande Python
```bash
python "py_backend\Doc calcul notes annexes\Scripts\calculer_note_3b.py" "P000 -BALANCE DEMO N_N-1_N-2.xlsx"
```

### Méthode 3: Avec options personnalisées
```bash
python "py_backend\Doc calcul notes annexes\Scripts\calculer_note_3b.py" ^
    "P000 -BALANCE DEMO N_N-1_N-2.xlsx" ^
    --output-html "mon_rapport_3b.html" ^
    --output-trace "ma_trace_3b.json"
```

## Colonnes calculées

Pour chaque ligne d'immobilisation corporelle, le système calcule:

1. **Valeur brute**:
   - Brut ouverture (N-1)
   - Augmentations (exercice N)
   - Diminutions (exercice N)
   - Brut clôture (N)

2. **Amortissements**:
   - Amortissements ouverture (N-1)
   - Dotations (exercice N)
   - Reprises (exercice N)
   - Amortissements clôture (N)

3. **Valeur nette comptable (VNC)**:
   - VNC ouverture = Brut ouverture - Amortissements ouverture
   - VNC clôture = Brut clôture - Amortissements clôture

## Fichiers générés

### 1. Fichier HTML
- **Nom**: `note_3b_immobilisations_corporelles.html`
- **Contenu**: Tableau formaté conforme au format SYSCOHADA
- **Usage**: Visualisation et impression

### 2. Fichier de trace JSON
- **Nom**: `note_3b_trace.json`
- **Contenu**: Détail des calculs avec comptes sources
- **Usage**: Audit et traçabilité

## Vérification des résultats

### Contrôles automatiques
Le système effectue automatiquement:
- ✓ Vérification de l'équation comptable pour chaque ligne
- ✓ Validation que VNC ≥ 0
- ✓ Cohérence temporelle (clôture N-1 = ouverture N)
- ✓ Calcul du total des immobilisations corporelles

### Contrôles manuels recommandés
1. Vérifier que le total correspond au bilan actif
2. Comparer les dotations avec le compte de résultat
3. Valider les mouvements importants (acquisitions, cessions)

## Différences avec Note 3A

| Aspect | Note 3A (Incorporelles) | Note 3B (Corporelles) |
|--------|------------------------|----------------------|
| Nombre de lignes | 4 lignes | 9 lignes |
| Comptes bruts | 21X | 22X |
| Comptes amortissements | 281X, 291X | 282X, 292X |
| Particularités | Fonds commercial | Terrains (non amortissables) |

## Dépannage

### Erreur: "Fichier de balance non trouvé"
**Solution**: Vérifiez que le fichier `P000 -BALANCE DEMO N_N-1_N-2.xlsx` est à la racine du projet.

### Erreur: "Module calculateur_note_template not found"
**Solution**: Assurez-vous que le fichier `calculateur_note_template.py` existe dans le même dossier.

### Avertissement: "VNC négative détectée"
**Cause**: Amortissements supérieurs à la valeur brute
**Action**: Vérifier les comptes d'amortissement dans la balance

### Avertissement: "Incohérence comptable détectée"
**Cause**: L'équation Clôture = Ouverture + Augmentations - Diminutions n'est pas respectée
**Action**: Vérifier les mouvements dans la balance

## Prochaines étapes

Après avoir généré la Note 3B, vous pouvez:
1. Générer la Note 3C (Immobilisations Financières)
2. Générer la Note 3D (Charges Immobilisées)
3. Générer la Note 3E (Écarts de Conversion Actif)
4. Exécuter la validation de cohérence inter-notes

## Support

Pour plus d'informations:
- Consultez le fichier `README.md` dans le dossier principal
- Consultez la documentation complète dans `.kiro/specs/calcul-notes-annexes-syscohada/`
- Examinez le fichier de trace JSON pour comprendre les calculs détaillés

---

**Date de création**: 25 Avril 2026  
**Version**: 1.0  
**Statut**: ✓ Opérationnel
