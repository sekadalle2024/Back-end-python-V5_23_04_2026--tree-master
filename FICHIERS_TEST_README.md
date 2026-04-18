# 📁 FICHIERS DE TEST - BACKEND PYTHON

**Date** : 22 Mars 2026  
**Dossier** : `py_backend/`

---

## 📊 Fichiers Excel de Test Disponibles

### 1. P000 -BALANCE DEMO.xls

**Type** : Balance comptable (format ancien Excel .xls)  
**Taille** : ~150 KB  
**Usage** : Test Lead Balance

**Description** :
- Fichier de démonstration pour tester la fonctionnalité Lead Balance
- Contient 2 onglets minimum (Balance N et Balance N-1)
- Format attendu : Numéro, Intitulé, Solde Débit, Solde Crédit

**Endpoint** : `/lead-balance/process-excel`

**Test** :
```powershell
# Dans le navigateur
1. Taper : Lead_balance
2. Sélectionner : py_backend/P000 -BALANCE DEMO.xls
3. Observer les résultats
```

---

### 2. Balance excel.xlsx

**Type** : Balance comptable (format Excel moderne .xlsx)  
**Usage** : Test alternatif Lead Balance

**Description** :
- Fichier Excel au format moderne
- Peut être utilisé comme alternative à P000 -BALANCE DEMO.xls

---

### 3. LIASSE.xlsx

**Type** : Liasse fiscale  
**Usage** : Test États Financiers SYSCOHADA

**Description** :
- Fichier pour tester les états financiers
- Format SYSCOHADA

**Endpoint** : `/etats-financiers/generate`

---

### 4. Tableau correspondance.xlsx

**Type** : Table de correspondance  
**Usage** : Mapping de comptes

**Description** :
- Table de correspondance entre différents plans comptables
- Utilisé pour les conversions

---

## 🧪 TESTS RECOMMANDÉS

### Test 1 : Lead Balance avec P000 -BALANCE DEMO.xls

**Commande** :
```
Lead_balance
```

**Fichier** : `py_backend/P000 -BALANCE DEMO.xls`

**Résultat attendu** :
- Accordéons par section SYSCOHADA
- Comptes communs aux deux périodes
- Comptes uniquement en N (nouveaux)
- Comptes uniquement en N-1 (supprimés)
- Calcul des variations

---

### Test 2 : Lead Balance avec Balance excel.xlsx

**Commande** :
```
Lead_balance
```

**Fichier** : `py_backend/Balance excel.xlsx`

**Résultat attendu** :
- Même traitement que P000 -BALANCE DEMO.xls
- Vérification du support .xlsx

---

### Test 3 : États Financiers avec LIASSE.xlsx

**Commande** :
```
Etats_financiers
```

**Fichier** : `py_backend/LIASSE.xlsx`

**Résultat attendu** :
- Génération des états financiers SYSCOHADA
- Bilan, Compte de résultat, etc.

---

## 📋 FORMAT ATTENDU DES FICHIERS

### Lead Balance (P000 -BALANCE DEMO.xls)

**Structure** :
```
Onglet 1 : Balance N (période actuelle)
Onglet 2 : Balance N-1 (période précédente)
```

**Colonnes attendues** :
- Numéro / Compte
- Intitulé / Libellé
- Solde Débit
- Solde Crédit

**Exemple** :
```
| Numéro | Intitulé          | Solde Débit | Solde Crédit |
|--------|-------------------|-------------|--------------|
| 101    | Capital social    | 0           | 10000000     |
| 211    | Terrains          | 5000000     | 0            |
| 401    | Fournisseurs      | 0           | 2500000      |
```

---

## 🔧 CRÉATION DE NOUVEAUX FICHIERS DE TEST

### Créer un fichier Lead Balance

**Étapes** :
1. Créer un fichier Excel (.xlsx ou .xls)
2. Créer 2 onglets : "Balance N" et "Balance N-1"
3. Ajouter les colonnes : Numéro, Intitulé, Solde Débit, Solde Crédit
4. Remplir avec des données de test
5. Sauvegarder dans `py_backend/`

**Template Python** :
```python
import pandas as pd

# Données Balance N
data_n = {
    'Numéro': ['101', '211', '401', '512'],
    'Intitulé': ['Capital social', 'Terrains', 'Fournisseurs', 'Banque'],
    'Solde Débit': [0, 5000000, 0, 1500000],
    'Solde Crédit': [10000000, 0, 2500000, 0]
}

# Données Balance N-1
data_n_1 = {
    'Numéro': ['101', '211', '401'],
    'Intitulé': ['Capital social', 'Terrains', 'Fournisseurs'],
    'Solde Débit': [0, 4000000, 0],
    'Solde Crédit': [8000000, 0, 2000000]
}

# Créer le fichier Excel
with pd.ExcelWriter('py_backend/TEST_BALANCE.xlsx') as writer:
    pd.DataFrame(data_n).to_excel(writer, sheet_name='Balance N', index=False)
    pd.DataFrame(data_n_1).to_excel(writer, sheet_name='Balance N-1', index=False)
```

---

## 📊 VALIDATION DES FICHIERS

### Script de validation

```python
import pandas as pd

def validate_lead_balance_file(filepath):
    """Valide un fichier Excel pour Lead Balance"""
    try:
        # Lire le fichier
        xl = pd.ExcelFile(filepath)
        
        # Vérifier le nombre d'onglets
        if len(xl.sheet_names) < 2:
            return False, "Le fichier doit contenir au moins 2 onglets"
        
        # Lire les deux premiers onglets
        df_n = pd.read_excel(xl, sheet_name=xl.sheet_names[0])
        df_n_1 = pd.read_excel(xl, sheet_name=xl.sheet_names[1])
        
        # Vérifier les colonnes
        required_cols = ['numéro', 'intitulé', 'solde', 'débit', 'crédit']
        
        for df, name in [(df_n, 'N'), (df_n_1, 'N-1')]:
            cols_lower = [str(c).lower() for c in df.columns]
            has_numero = any('numéro' in c or 'numero' in c or 'compte' in c for c in cols_lower)
            has_intitule = any('intitulé' in c or 'intitule' in c or 'libellé' in c for c in cols_lower)
            has_solde = any('solde' in c for c in cols_lower)
            
            if not (has_numero and has_intitule and has_solde):
                return False, f"Onglet {name} : colonnes manquantes"
        
        return True, "Fichier valide"
        
    except Exception as e:
        return False, f"Erreur : {str(e)}"

# Test
is_valid, message = validate_lead_balance_file('py_backend/P000 -BALANCE DEMO.xls')
print(f"Validation : {message}")
```

---

## 🚀 UTILISATION

### Test rapide

```powershell
# 1. Démarrer le backend
conda activate claraverse_backend
cd py_backend
python main.py

# 2. Démarrer le frontend
npm run dev

# 3. Tester
# Navigateur : http://localhost:5173
# Chat : Lead_balance
# Fichier : py_backend/P000 -BALANCE DEMO.xls
```

---

## 📚 DOCUMENTATION

### Endpoints disponibles

- **POST** `/lead-balance/process-excel` - Lead Balance
- **POST** `/etats-financiers/generate` - États Financiers
- **POST** `/pandas/analyze` - Analyse Pandas
- **POST** `/word-export` - Export Word

### Fichiers de code

- `pandas_lead.py` - Traitement Lead Balance
- `etats_financiers.py` - États Financiers SYSCOHADA
- `pandas_api.py` - API Pandas générique
- `word_export.py` - Export Word

---

## ✅ CHECKLIST

### Avant de tester

- [x] Fichier `P000 -BALANCE DEMO.xls` présent
- [x] Fichier `Balance excel.xlsx` présent
- [x] Fichier `LIASSE.xlsx` présent
- [x] Backend démarré
- [x] Frontend démarré

### Pendant le test

- [ ] Commande `Lead_balance` tapée
- [ ] Fichier sélectionné
- [ ] Upload réussi
- [ ] Résultats affichés
- [ ] Pas d'erreur

---

## 🔍 DÉPANNAGE

### Erreur : "Fichier non trouvé"

**Solution** : Vérifier que le fichier est bien dans `py_backend/`

```powershell
Get-ChildItem py_backend/*.xls*
```

### Erreur : "Format non supporté"

**Solution** : Vérifier que le fichier a l'extension .xlsx ou .xls

### Erreur : "Colonnes manquantes"

**Solution** : Vérifier que le fichier contient les colonnes requises

---

**Version** : 1.0.0  
**Date** : 22 Mars 2026  
**Statut** : ✅ Fichiers de test disponibles
