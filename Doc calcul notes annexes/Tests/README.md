# Tests - Calcul des Notes Annexes

Ce dossier contient les fichiers HTML de test générés pour chaque note annexe calculée.

## 📋 Fichiers de test disponibles

### ✅ test_note_3a.html
**Note 3A - Immobilisations incorporelles**

Tableau HTML généré automatiquement montrant:
- Valeurs brutes (ouverture, augmentations, diminutions, clôture)
- Amortissements (ouverture, dotations, reprises, clôture)
- Valeurs nettes comptables (N-1 et N)

**Généré par:** `../Scripts/calculer_note_3a.py`

### ⏳ test_note_3b.html (À CRÉER)
**Note 3B - Immobilisations corporelles**

### ⏳ test_note_3c.html (À CRÉER)
**Note 3C - Immobilisations financières**

### ⏳ test_note_4.html (À CRÉER)
**Note 4 - Stocks**

### ⏳ test_note_5.html (À CRÉER)
**Note 5 - Créances**

### ⏳ test_note_6.html (À CRÉER)
**Note 6 - Trésorerie**

### ⏳ test_note_7.html (À CRÉER)
**Note 7 - Capitaux propres**

### ⏳ test_note_8.html (À CRÉER)
**Note 8 - Dettes financières**

### ⏳ test_note_9.html (À CRÉER)
**Note 9 - Provisions**

### ⏳ test_note_10.html (À CRÉER)
**Note 10 - Dettes fournisseurs**

## 🎯 Objectif des tests

Chaque fichier HTML de test permet de:
1. **Vérifier visuellement** le calcul de la note annexe
2. **Valider le format** du tableau généré
3. **Contrôler les données** extraites des balances
4. **Tester rapidement** sans lancer l'application complète

## 🚀 Comment générer un test

### Méthode 1: Script PowerShell (Recommandé)
```bash
# Depuis la racine du projet
.\test-note-3a.ps1
```

### Méthode 2: Script Python direct
```bash
cd "py_backend/Doc calcul notes annexes/Scripts"
python calculer_note_3a.py
```

Le fichier HTML sera généré dans `py_backend/Doc calcul notes annexes/Tests/`

## 📊 Structure d'un fichier de test

Chaque fichier HTML contient:
- **En-tête** avec le titre de la note
- **Tableau formaté** avec CSS professionnel
- **Données calculées** à partir des balances N, N-1, N-2
- **Mise en forme** conforme au Syscohada Révisé

## 🔍 Vérification des tests

Pour vérifier un test:
1. Ouvrir le fichier HTML dans un navigateur
2. Comparer avec le template dans `../Ressources/`
3. Vérifier les totaux et sous-totaux
4. Contrôler la cohérence des données

## 📝 Convention de nommage

Les fichiers de test suivent cette convention:
- `test_note_3a.html` - Note 3A (Immobilisations incorporelles)
- `test_note_3b.html` - Note 3B (Immobilisations corporelles)
- `test_note_3c.html` - Note 3C (Immobilisations financières)
- `test_note_4.html` - Note 4 (Stocks)
- etc.

## 🔄 Workflow de développement

Pour chaque nouvelle note annexe:

1. **Créer le script** dans `../Scripts/calculer_note_xx.py`
2. **Générer le test** en exécutant le script
3. **Vérifier le HTML** dans ce dossier
4. **Valider les calculs** en comparant avec les données sources
5. **Documenter** dans `../Documentation/`
6. **Passer** à la note suivante

## 🛠️ Modification des tests

Si vous devez modifier un test:
1. Modifier le script Python correspondant dans `../Scripts/`
2. Régénérer le fichier HTML
3. Vérifier les changements dans le navigateur

## 📚 Fichiers de référence

### Balance de test
`P000 -BALANCE DEMO N_N-1_N-2.xls` (racine du projet)

### Templates Excel
`../Ressources/NOTE XX.xlsx`

### Exemples visuels
`../Ressources/NOTE XX renseignee.png`

## ⚠️ Notes importantes

- Les fichiers HTML sont générés automatiquement
- Ne pas modifier manuellement les fichiers HTML
- Toujours régénérer après modification du script
- Les tests utilisent les vraies données de la balance démo

## 🎨 Style des tableaux

Les tableaux HTML utilisent:
- CSS inline pour la portabilité
- Bordures et couleurs professionnelles
- Format conforme aux états financiers
- Mise en page responsive

## 📈 Statistiques

- Tests disponibles: 1 (Note 3A)
- Tests à créer: 9+ notes annexes
- Format: HTML avec CSS inline
- Source de données: Balance démo N, N-1, N-2

## 💡 Conseils

1. **Toujours tester** après modification d'un script
2. **Comparer** avec le template Excel officiel
3. **Vérifier** les totaux et sous-totaux
4. **Documenter** les anomalies détectées
5. **Archiver** les versions de test si nécessaire

## 🔗 Liens utiles

- Scripts de calcul: `../Scripts/`
- Documentation: `../Documentation/`
- Ressources: `../Ressources/`
- Guide principal: `../00_COMMENCER_ICI.txt`

---

**Dernière mise à jour:** 08 Avril 2026  
**Tests disponibles:** 1/10+  
**Prochaine note:** Note 3B (Immobilisations corporelles)
