# Scripts - Calcul des Notes Annexes

Ce dossier contient les scripts Python pour calculer automatiquement les notes annexes des états financiers Syscohada Révisé.

## Scripts disponibles

### ✅ calculer_note_3a.py
**Note 3A - Immobilisations incorporelles**

Calcule automatiquement la Note 3A à partir des balances N, N-1, N-2.

**Fonctionnalités:**
- Lecture des 3 balances depuis un fichier Excel
- Extraction des soldes des comptes d'immobilisations incorporelles
- Calcul des valeurs brutes (ouverture, augmentations, diminutions, clôture)
- Calcul des amortissements (ouverture, dotations, reprises, clôture)
- Calcul des valeurs nettes comptables
- Génération d'un tableau HTML formaté

**Utilisation:**
```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Scripts
python calculer_note_3a.py
```

**Résultat:** Génère `../../test_note_3a.html`

### test_onglets.py
**Script de test pour la lecture des balances**

Teste la lecture des onglets Excel et l'extraction des données.

**Utilisation:**
```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Scripts
python test_onglets.py
```

## Structure d'un script de calcul

Chaque script de calcul de note annexe suit cette structure:

```python
import pandas as pd
import openpyxl

class CalculateurNoteXX:
    def __init__(self, fichier_balance):
        self.fichier_balance = fichier_balance
        self.balance_n = None
        self.balance_n1 = None
        self.balance_n2 = None
    
    def charger_balances(self):
        """Charge les 3 balances depuis le fichier Excel"""
        pass
    
    def extraire_solde(self, balance, numero_compte):
        """Extrait le solde d'un compte"""
        pass
    
    def calculer_note(self):
        """Calcule les valeurs de la note annexe"""
        pass
    
    def generer_html(self):
        """Génère le tableau HTML"""
        pass
```

## Comptes Syscohada Révisé

### Note 3A - Immobilisations incorporelles
- **Brut:** 211-218
- **Amortissements:** 2811-2818, 2911-2918

### Note 3B - Immobilisations corporelles (À FAIRE)
- **Brut:** 221-229
- **Amortissements:** 2821-2829, 2921-2929

### Note 3C - Immobilisations financières (À FAIRE)
- **Brut:** 231-279
- **Provisions:** 291-297

## Format des balances

Les balances doivent avoir 8 colonnes:
1. Numéro (compte)
2. Intitulé
3. Ant Débit (solde d'ouverture débit)
4. Ant Crédit (solde d'ouverture crédit)
5. Mvt Débit (mouvements de l'exercice débit)
6. Mvt Crédit (mouvements de l'exercice crédit)
7. Solde Débit (solde de clôture débit)
8. Solde Crédit (solde de clôture crédit)

## Fichier de référence

Balance de test: `P000 -BALANCE DEMO N_N-1_N-2.xls` (racine du projet)

## Prochains scripts à créer

- [ ] calculer_note_3b.py (Immobilisations corporelles)
- [ ] calculer_note_3c.py (Immobilisations financières)
- [ ] calculer_note_4.py (Stocks)
- [ ] calculer_note_5.py (Créances)
- [ ] calculer_note_6.py (Trésorerie)
- [ ] calculer_note_7.py (Capitaux propres)
- [ ] calculer_note_8.py (Dettes financières)
- [ ] calculer_note_9.py (Provisions)
- [ ] calculer_note_10.py (Dettes fournisseurs)

## Tests

Pour tester un script:
```bash
# Depuis la racine du projet
.\test-note-3a.ps1

# Ou directement
cd py_backend/Doc\ calcul\ notes\ annexes/Scripts
python calculer_note_3a.py
```

---

**Dernière mise à jour:** 08 Avril 2026
