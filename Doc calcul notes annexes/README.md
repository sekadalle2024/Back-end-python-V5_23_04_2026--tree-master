# Calcul des Notes Annexes - Syscohada Révisé

Ce dossier contient tout le nécessaire pour calculer automatiquement les notes annexes des états financiers Syscohada Révisé à partir des balances comptables.

## 🚀 Démarrage rapide

**Lire en premier:** `00_COMMENCER_ICI.txt`

## 📁 Structure du dossier

```
Doc calcul notes annexes/
├── 00_COMMENCER_ICI.txt          # Guide de démarrage
├── README.md                      # Ce fichier
│
├── Documentation/                 # 📚 Guides et documentation
│   ├── README.md
│   ├── 00_CALCUL_NOTE_3A_REUSSI_08_AVRIL_2026.txt
│   └── QUICK_START_NOTE_3A.txt
│
├── Scripts/                       # 🐍 Scripts Python de calcul
│   ├── README.md
│   ├── calculer_note_3a.py       # ✅ Note 3A (Immobilisations incorporelles)
│   └── test_onglets.py           # Tests de lecture des balances
│
├── Tests/                         # 🧪 Fichiers HTML de test
│   ├── README.md
│   └── test_note_3a.html         # ✅ Test Note 3A
│
└── Ressources/                    # 📊 Fichiers de référence
    ├── README.md
    ├── NOTE 3A.xlsx              # Template vide
    ├── NOTE 3A renseignee.png    # Exemple rempli
    ├── Liasse_officielle_revise.xlsx  # Template complet
    └── Syscohada revise plan compte.pdf  # Plan comptable
```

## ✅ Notes annexes disponibles

- **Note 3A** - Immobilisations incorporelles (TERMINÉ)

## ⏳ Notes annexes à développer

- Note 3B - Immobilisations corporelles
- Note 3C - Immobilisations financières
- Note 4 - Stocks
- Note 5 - Créances
- Note 6 - Trésorerie
- Note 7 - Capitaux propres
- Note 8 - Dettes financières
- Note 9 - Provisions
- Note 10 - Dettes fournisseurs
- ... (autres notes)

## 🎯 Méthodologie

Pour chaque note annexe:

1. **Analyser** le template Excel dans `Ressources/`
2. **Identifier** les comptes concernés dans le plan comptable
3. **Créer** le script Python dans `Scripts/`
4. **Tester** avec la balance démo (`P000 -BALANCE DEMO N_N-1_N-2.xls`)
5. **Générer** un HTML de test
6. **Documenter** dans `Documentation/`
7. **Passer** à la note suivante

## 📝 Exemple: Note 3A

### Test rapide
```bash
# Depuis la racine du projet
.\test-note-3a.ps1
```

### Utilisation du script
```bash
cd "py_backend/Doc calcul notes annexes/Scripts"
python calculer_note_3a.py
```

### Résultat
Génère `py_backend/Doc calcul notes annexes/Tests/test_note_3a.html` avec le tableau formaté

## 📚 Documentation

Chaque sous-dossier contient son propre README.md avec des détails spécifiques:

- `Documentation/README.md` - Guide complet de la documentation
- `Scripts/README.md` - Guide des scripts Python
- `Tests/README.md` - Guide des fichiers HTML de test
- `Ressources/README.md` - Guide des fichiers de référence

## 🔗 Fichiers externes

### Balance de test
`P000 -BALANCE DEMO N_N-1_N-2.xls` (racine du projet)
- 3 onglets: BALANCE N, BALANCE N-1, BALANCE N-2
- Format 8 colonnes standard

### Correspondances comptes
`py_backend/correspondances_syscohada.json`
- Mapping entre postes et comptes
- Utilisé pour tous les calculs

## 💡 Besoin d'aide ?

1. Lire `00_COMMENCER_ICI.txt`
2. Consulter `Documentation/QUICK_START_NOTE_3A.txt`
3. Voir les exemples dans `Ressources/`
4. Lancer les tests avec `test-note-3a.ps1`

## 🔄 Prochaines étapes

1. Développer le script pour la Note 3B (Immobilisations corporelles)
2. Générer un HTML de test pour la Note 3B
3. Continuer avec les autres notes annexes
4. Intégrer dans le backend API
5. Créer les composants React pour l'affichage frontend

---

**Date:** 08 Avril 2026  
**Version:** 1.0  
**Statut:** Note 3A terminée, autres notes en cours de développement


---

## 🏗️ Infrastructure du Projet (Mise à jour)

### Structure Complète

```
py_backend/Doc calcul notes annexes/
├── Modules/                    # ✅ Modules partagés (NOUVEAU)
│   ├── __init__.py
│   ├── balance_reader.py       # Lecture des balances Excel
│   ├── account_extractor.py    # Extraction des comptes par racine
│   ├── movement_calculator.py  # Calcul des mouvements et soldes
│   ├── vnc_calculator.py       # Calcul des VNC
│   ├── html_generator.py       # Génération HTML
│   ├── excel_exporter.py       # Export Excel
│   ├── mapping_manager.py      # Gestion des correspondances
│   ├── coherence_validator.py  # Validation de cohérence
│   └── trace_manager.py        # Traçabilité et audit
├── Scripts/                    # Scripts de calcul
│   ├── __init__.py
│   ├── calculateur_note_template.py  # ✅ Template (NOUVEAU)
│   ├── calculer_note_1.py
│   └── calculer_note_3a.py
├── Tests/                      # Tests et fixtures
│   ├── __init__.py
│   ├── conftest.py            # ✅ Config pytest + Hypothesis (NOUVEAU)
│   ├── fixtures/              # ✅ Données de test (NOUVEAU)
│   │   └── __init__.py
│   └── README.md
├── Ressources/                 # Ressources
│   ├── correspondances_syscohada.json  # ✅ Mapping (NOUVEAU)
│   └── README.md
├── Logs/                       # ✅ Fichiers de log (NOUVEAU)
│   └── .gitkeep
├── calcul_notes_annexes_main.py  # ✅ Orchestrateur (NOUVEAU)
├── requirements.txt            # ✅ Dépendances (NOUVEAU)
└── README.md
```

### Installation des Dépendances

```bash
cd "py_backend/Doc calcul notes annexes"
pip install -r requirements.txt
```

**Dépendances installées:**
- pandas ≥2.0.0 (manipulation de données)
- openpyxl ≥3.1.0 (lecture/écriture Excel)
- pytest ≥7.4.0 (tests unitaires)
- pytest-cov ≥4.1.0 (couverture de code)
- hypothesis ≥6.82.0 (tests basés sur les propriétés)
- flask ≥2.3.0 (API web)
- flask-cors ≥4.0.0 (support CORS)

### Orchestrateur Principal

**Calcul de toutes les notes:**
```bash
python calcul_notes_annexes_main.py
```

Cette commande:
1. ✅ Charge les balances N, N-1, N-2
2. ✅ Calcule les 33 notes annexes
3. ✅ Valide la cohérence inter-notes
4. ✅ Génère HTML et Excel
5. ✅ Crée les logs dans Logs/

### Système de Logging

Trois fichiers de log dans `Logs/`:
- **calcul_notes_annexes.log**: Log principal (INFO+)
- **calcul_notes_warnings.log**: Avertissements uniquement
- **calcul_notes_errors.log**: Erreurs uniquement

Rotation quotidienne, conservation 30 jours.

### Tests

```bash
# Tous les tests
pytest Tests/ -v

# Tests unitaires
pytest Tests/unit/ -v

# Tests de propriétés (Hypothesis)
pytest Tests/property/ -v --hypothesis-show-statistics

# Avec couverture
pytest Tests/ -v --cov=. --cov-report=html
```

### Modules Partagés

**BalanceReader**: Charge les balances Excel multi-exercices
```python
from Modules.balance_reader import BalanceReader
reader = BalanceReader("balance.xlsx")
balance_n, balance_n1, balance_n2 = reader.charger_balances()
```

**AccountExtractor**: Extrait les soldes par racine
```python
from Modules.account_extractor import AccountExtractor
extractor = AccountExtractor(balance_n)
soldes = extractor.extraire_solde_compte("211")
```

**MovementCalculator**: Calcule mouvements et soldes
```python
from Modules.movement_calculator import MovementCalculator
solde_ouv = MovementCalculator.calculer_solde_ouverture(sd_n1, sc_n1)
```

**VNCCalculator**: Calcule les VNC
```python
from Modules.vnc_calculator import VNCCalculator
vnc = VNCCalculator.calculer_vnc_cloture(brut, amort)
```

**HTMLGenerator**: Génère les tableaux HTML
```python
from Modules.html_generator import HTMLGenerator
generator = HTMLGenerator("IMMOBILISATIONS", "3A")
html = generator.generer_html(df)
```

### Créer une Nouvelle Note

1. **Copier le template:**
```bash
cp Scripts/calculateur_note_template.py Scripts/calculer_note_XX.py
```

2. **Adapter le mapping:**
```python
self.mapping_comptes = {
    'Ligne 1': {
        'brut': ['211', '2111'],
        'amort': ['2811', '28111']
    },
    # ...
}
```

3. **Modifier titre et numéro:**
```python
generator = HTMLGenerator('TITRE DE LA NOTE', 'XX')
```

4. **Tester:**
```bash
python Scripts/calculer_note_XX.py
```

### Correspondances SYSCOHADA

Le fichier `Ressources/correspondances_syscohada.json` contient le mapping entre postes et comptes:

```json
{
  "bilan_actif": {
    "Immobilisations incorporelles": {
      "brut": ["211", "212", "213", ...],
      "amort": ["2811", "2812", "2813", ...]
    }
  }
}
```

Utilisé par `MappingManager` pour extraire les comptes.

---

**Mise à jour:** 08 Avril 2026  
**Infrastructure:** Task 1 complétée - Structure et modules de base créés
