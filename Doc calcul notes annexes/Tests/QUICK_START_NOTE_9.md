# Quick Start - Note 9: Réserves

## Vue d'ensemble

La Note 9 calcule automatiquement les mouvements des réserves à partir des balances SYSCOHADA sur 3 exercices (N, N-1, N-2).

## Comptes SYSCOHADA concernés

### Réserves (Comptes 11X)
- **111**: Réserve légale
- **112**: Réserves statutaires ou contractuelles
- **113**: Réserves réglementées
  - 1131: Réserves de plus-values nettes à long terme
  - 1132: Réserves de réévaluation
  - 1133: Réserves consécutives à l'octroi de subventions d'investissement
- **114**: Réserves libres
- **115**: Écarts de réévaluation
- **116**: Écarts d'équivalence
- **117**: Écarts de conversion
- **118**: Autres réserves

### Report à nouveau (Comptes 12X)
- **121**: Report à nouveau créditeur
- **129**: Report à nouveau débiteur

## Structure de la Note 9

La Note 9 contient **9 lignes de détail + 1 ligne de total**:

1. Réserve légale
2. Réserves statutaires ou contractuelles
3. Réserves réglementées
4. Réserves libres
5. Écarts de réévaluation
6. Écarts d'équivalence
7. Écarts de conversion
8. Autres réserves
9. Report à nouveau
10. **TOTAL RÉSERVES**

## Colonnes calculées

Pour chaque ligne, le système calcule:

### Valeurs brutes
- Début exercice (solde d'ouverture N)
- Augmentations (dotations aux réserves)
- Diminutions (prélèvements sur réserves)
- Fin exercice (solde de clôture N)

### Amortissements
- Non applicable (les réserves ne s'amortissent pas)

### Valeurs nettes
- Début exercice = Valeurs brutes début exercice
- Fin exercice = Valeurs brutes fin exercice

## Exécution rapide

### Option 1: Script PowerShell (Windows)
```powershell
.\test-note-9.ps1
```

### Option 2: Ligne de commande Python
```bash
cd "py_backend/Doc calcul notes annexes/Scripts"
python calculer_note_9.py
```

### Option 3: Avec paramètres personnalisés
```bash
python calculer_note_9.py "chemin/vers/balance.xlsx" \
  --output-html "sortie/note_9.html" \
  --output-trace "sortie/trace_9.json"
```

## Fichiers générés

Après exécution, vous trouverez:

1. **test_note_9.html** - Tableau HTML formaté de la Note 9
   - Localisation: `py_backend/Doc calcul notes annexes/Tests/`
   - Visualisation: Ouvrir dans un navigateur web

2. **trace_note_9.json** - Fichier de traçabilité
   - Localisation: `py_backend/Doc calcul notes annexes/Tests/`
   - Contenu: Détail des comptes sources et calculs

## Validation des résultats

### Vérifications automatiques

Le système effectue automatiquement:
- ✓ Cohérence comptable: Solde clôture = Solde ouverture + Augmentations - Diminutions
- ✓ Validation des montants (pas de valeurs négatives anormales)
- ✓ Traçabilité complète des calculs

### Contrôles manuels recommandés

1. **Vérifier le total des réserves**
   - Comparer avec le bilan passif
   - Vérifier la cohérence avec l'exercice précédent

2. **Analyser les mouvements**
   - Augmentations: Affectation du résultat, réévaluations
   - Diminutions: Distributions, incorporations au capital

3. **Contrôler le report à nouveau**
   - Vérifier la continuité avec l'exercice N-1
   - Contrôler l'affectation du résultat N-1

## Particularités de la Note 9

### Report à nouveau
- Peut être créditeur (121) ou débiteur (129)
- Le report à nouveau débiteur est généralement affiché en négatif

### Réserves réglementées
- Soumises à des règles fiscales spécifiques
- Peuvent inclure des plus-values à long terme

### Écarts de réévaluation
- Résultent de la réévaluation des actifs
- Ne peuvent être distribués qu'après réalisation

## Dépannage

### Erreur: "Balance non trouvée"
- Vérifier le chemin du fichier de balance
- S'assurer que les onglets "BALANCE N", "BALANCE N-1", "BALANCE N-2" existent

### Avertissement: "Incohérence détectée"
- Vérifier les écritures comptables dans la balance
- Contrôler les reports à nouveau

### Montants à zéro
- Normal si l'entreprise n'a pas de réserves de ce type
- Vérifier que les comptes existent dans la balance

## Exemple de résultat

```
================================================================================
  CALCULATEUR NOTE 9 - RÉSERVES
================================================================================

📂 Chargement des balances depuis: ../../../P000 -BALANCE DEMO N_N-1_N-2.xls
✓ Balance N   : 150 lignes chargées
✓ Balance N-1 : 150 lignes chargées
✓ Balance N-2 : 150 lignes chargées

🔢 Calcul de la note 9...
  Calcul: Réserve légale...
  Calcul: Réserves statutaires ou contractuelles...
  Calcul: Réserves réglementées...
  Calcul: Réserves libres...
  Calcul: Écarts de réévaluation...
  Calcul: Écarts d'équivalence...
  Calcul: Écarts de conversion...
  Calcul: Autres réserves...
  Calcul: Report à nouveau...
✓ Note calculée: 10 lignes

📄 Génération du HTML...
✓ HTML généré

✓ Fichier HTML sauvegardé: ../Tests/test_note_9.html
✓ Fichier de trace sauvegardé: ../Tests/trace_note_9.json

────────────────────────────────────────────────────────────────────────────────
  RÉSUMÉ NOTE 9
────────────────────────────────────────────────────────────────────────────────

  Nombre de lignes: 9
  VNC Ouverture:        5,000,000
  VNC Clôture:          6,500,000
  Variation:            1,500,000

================================================================================
  ✓ NOTE 9 CALCULÉE AVEC SUCCÈS EN 2.45s
================================================================================
```

## Support

Pour toute question ou problème:
1. Consulter la documentation complète dans `py_backend/Doc calcul notes annexes/`
2. Vérifier les fichiers de trace JSON pour le détail des calculs
3. Examiner les logs d'avertissement pour les incohérences

## Prochaines étapes

Après la Note 9, vous pouvez calculer:
- **Note 10**: Résultat (comptes 12X, 13X)
- **Note 11**: Provisions (comptes 19X)
- **Note 12**: Emprunts (comptes 16X)

---

**Date de création**: 25 Avril 2026  
**Version**: 1.0  
**Système**: Calcul automatique des notes annexes SYSCOHADA Révisé
