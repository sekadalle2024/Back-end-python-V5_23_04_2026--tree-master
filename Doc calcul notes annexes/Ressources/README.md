# Ressources - Calcul des Notes Annexes

Ce dossier contient les fichiers de référence pour le calcul des notes annexes des états financiers Syscohada Révisé.

## Fichiers disponibles

### 📊 Templates Excel

#### NOTE 3A.xlsx
Template vide de la Note 3A (Immobilisations incorporelles)

**Contenu:**
- Tableau avec colonnes: Libellé, Valeur brute (4 cols), Amortissements (4 cols), VNC (2 cols)
- Lignes pour chaque type d'immobilisation incorporelle
- Format conforme Syscohada Révisé

#### Liasse_officielle_revise.xlsx
Template complet de la liasse fiscale Syscohada Révisé

**Contenu:**
- Tous les états financiers (Bilan, Compte de résultat, TFT, etc.)
- Toutes les notes annexes (Note 3A à Note 27)
- Format officiel pour export

**Utilisation:**
- Sert de référence pour la structure des notes
- Utilisé pour l'export final des états financiers

### 🖼️ Captures d'écran

#### NOTE 3A renseignee.png
Exemple visuel d'une Note 3A remplie avec des données réelles

**Utilité:**
- Comprendre le format attendu
- Vérifier la mise en forme
- Référence pour le développement

### 📚 Documentation comptable

#### Syscohada revise plan compte.pdf
Plan comptable officiel Syscohada Révisé

**Contenu:**
- Liste complète des comptes (Classe 1 à Classe 9)
- Description de chaque compte
- Règles de fonctionnement

**Utilisation:**
- Identifier les comptes pour chaque note annexe
- Comprendre la logique comptable
- Référence pour les correspondances

## Fichiers de test

### Balance de démonstration
**Fichier:** `P000 -BALANCE DEMO N_N-1_N-2.xls` (racine du projet)

**Structure:**
- 3 onglets: BALANCE N, BALANCE N-1, BALANCE N-2
- Format 8 colonnes standard
- Données réelles d'une entité

**Utilisation:**
```python
fichier_balance = "../../../P000 -BALANCE DEMO N_N-1_N-2.xls"
calculateur = CalculateurNote3A(fichier_balance)
```

## Correspondances comptes

### Fichier de mapping
**Fichier:** `py_backend/correspondances_syscohada.json`

**Contenu:**
- Mapping entre postes des états financiers et comptes
- Utilisé pour tous les calculs automatiques

**Exemple:**
```json
{
  "bilan_actif": {
    "immobilisations_incorporelles_brut": ["211", "212", "213", "214", "215", "216", "217", "218"],
    "immobilisations_incorporelles_amort": ["2811", "2812", "2813", "2814", "2815", "2816", "2817", "2818"]
  }
}
```

## Notes annexes à développer

### ✅ Note 3A - Immobilisations incorporelles
**Comptes:**
- Brut: 211-218
- Amortissements: 2811-2818, 2911-2918

### ⏳ Note 3B - Immobilisations corporelles
**Comptes:**
- Brut: 221-229
- Amortissements: 2821-2829, 2921-2929

### ⏳ Note 3C - Immobilisations financières
**Comptes:**
- Brut: 231-279
- Provisions: 291-297

### ⏳ Note 4 - Stocks
**Comptes:**
- Brut: 31-38
- Provisions: 391-398

### ⏳ Note 5 - Créances
**Comptes:**
- Brut: 40-48
- Provisions: 490-498

### ⏳ Note 6 - Trésorerie
**Comptes:**
- Disponibilités: 51-58
- Concours bancaires: 56-57

### ⏳ Note 7 - Capitaux propres
**Comptes:**
- Capital: 101-109
- Réserves: 11-13
- Résultat: 12-13

### ⏳ Note 8 - Dettes financières
**Comptes:**
- Emprunts: 16-17
- Dettes financières diverses: 18

### ⏳ Note 9 - Provisions
**Comptes:**
- Provisions pour risques: 19
- Provisions réglementées: 15

### ⏳ Note 10 - Dettes fournisseurs
**Comptes:**
- Fournisseurs: 40-48
- Autres dettes: 42-48

## Utilisation des ressources

### Pour développer un nouveau script

1. Consulter le plan comptable (Syscohada revise plan compte.pdf)
2. Identifier les comptes concernés
3. Voir le template Excel correspondant
4. Utiliser la balance démo pour tester
5. Générer un HTML de test

### Pour vérifier un calcul

1. Ouvrir le template Excel (NOTE XX.xlsx)
2. Comparer avec la capture d'écran (NOTE XX renseignee.png)
3. Vérifier les comptes dans le plan comptable
4. Tester avec la balance démo

## Maintenance

### Mise à jour des templates

Si les templates officiels changent:
1. Remplacer Liasse_officielle_revise.xlsx
2. Mettre à jour les captures d'écran
3. Adapter les scripts si nécessaire

### Ajout de nouvelles notes

Pour chaque nouvelle note:
1. Ajouter le template Excel (NOTE XX.xlsx)
2. Ajouter une capture d'écran (NOTE XX renseignee.png)
3. Documenter les comptes concernés
4. Créer le script de calcul

---

**Dernière mise à jour:** 08 Avril 2026
