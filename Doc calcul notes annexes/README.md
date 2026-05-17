# Calcul Automatique des Notes Annexes SYSCOHADA Révisé

## Vue d'ensemble

Ce système automatise le calcul et la génération des 33 notes annexes des états financiers SYSCOHADA révisé. Il lit des fichiers Excel de balances à 8 colonnes couvrant trois exercices comptables (N, N-1, N-2), extrait les comptes pertinents selon le plan comptable SYSCOHADA, effectue les calculs de mouvements et de soldes, puis génère des tableaux HTML et Excel conformes au format officiel de la liasse SYSCOHADA révisé.

**Objectif de performance**: Calcul complet des 33 notes en moins de 30 secondes.

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Claraverse                      │
│              (Frontend React + Backend Flask)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrateur Principal                     │
│              (calcul_notes_annexes_main.py)                  │
│  - Coordination des 33 calculateurs                          │
│  - Gestion du cache des balances                             │
│  - Validation de cohérence inter-notes                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Calculateur  │ │ Calculateur  │ │ Calculateur  │
│   Note 01    │ │   Note 02    │ │   Note 33    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Modules Partagés                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Balance    │  │   Account    │  │   Movement   │      │
│  │   Reader     │  │  Extractor   │  │  Calculator  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     VNC      │  │     HTML     │  │    Excel     │      │
│  │  Calculator  │  │  Generator   │  │   Exporter   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Mapping    │  │  Coherence   │  │    Trace     │      │
│  │   Manager    │  │  Validator   │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Données Sources                           │
│  - Balances Excel (N, N-1, N-2)                              │
│  - correspondances_syscohada.json                            │
│  - Liasse_officielle_revise.xlsx                             │
└─────────────────────────────────────────────────────────────┘
```

## Structure des Répertoires

```
Doc calcul notes annexes/
├── README.md                          # Ce fichier
├── GUIDE_UTILISATION.md              # Guide d'utilisation détaillé
├── TROUBLESHOOTING.md                # Dépannage et solutions
├── Modules/                          # 9 modules partagés
│   ├── __init__.py
│   ├── balance_reader.py             # Lecture des balances Excel
│   ├── account_extractor.py          # Extraction des comptes
│   ├── movement_calculator.py        # Calcul des mouvements
│   ├── vnc_calculator.py             # Calcul des VNC
│   ├── html_generator.py             # Génération HTML
│   ├── excel_exporter.py             # Export Excel
│   ├── mapping_manager.py            # Gestion des correspondances
│   ├── coherence_validator.py        # Validation de cohérence
│   └── trace_manager.py              # Traçabilité et audit
├── Scripts/                          # 33 calculateurs de notes
│   ├── __init__.py
│   ├── calculateur_note_template.py  # Template de base
│   ├── calculer_note_1.py            # Note 1: Immobilisations incorporelles
│   ├── calculer_note_2.py            # Note 2: Immobilisations corporelles
│   ├── calculer_note_3.py            # Note 3: Immobilisations financières
│   ├── calculer_note_3a.py           # Note 3A: Détail immobilisations incorporelles
│   ├── calculer_note_3b.py           # Note 3B: Détail immobilisations corporelles
│   ├── calculer_note_3c.py           # Note 3C: Détail immobilisations financières
│   ├── calculer_note_3d.py           # Note 3D: Charges immobilisées
│   ├── calculer_note_3e.py           # Note 3E: Écarts de conversion actif
│   ├── calculer_note_4.py            # Note 4: Stocks
│   ├── calculer_note_5.py            # Note 5: Créances clients
│   ├── calculer_note_6.py            # Note 6: Autres créances
│   ├── calculer_note_7.py            # Note 7: Trésorerie actif
│   ├── calculer_note_8.py            # Note 8: Capital
│   ├── calculer_note_9.py            # Note 9: Réserves
│   ├── calculer_note_10.py           # Note 10: Résultat
│   ├── calculer_note_11.py           # Note 11: Provisions
│   ├── calculer_note_12.py           # Note 12: Emprunts
│   ├── calculer_note_13.py           # Note 13: Dettes fournisseurs
│   ├── calculer_note_14.py           # Note 14: Dettes fiscales
│   ├── calculer_note_15.py           # Note 15: Dettes sociales
│   ├── calculer_note_16.py           # Note 16: Autres dettes
│   ├── calculer_note_17.py           # Note 17: Trésorerie passif
│   ├── calculer_note_18.py           # Note 18: Charges constatées d'avance
│   ├── calculer_note_19.py           # Note 19: Produits constatés d'avance
│   ├── calculer_note_20.py           # Note 20: Écarts de conversion passif
│   ├── calculer_note_21.py           # Note 21: Achats de marchandises
│   ├── calculer_note_22.py           # Note 22: Achats de matières
│   ├── calculer_note_23.py           # Note 23: Autres achats
│   ├── calculer_note_24.py           # Note 24: Services extérieurs
│   ├── calculer_note_25.py           # Note 25: Charges de personnel
│   ├── calculer_note_26.py           # Note 26: Dotations aux amortissements
│   ├── calculer_note_27.py           # Note 27: Dotations aux provisions
│   ├── calculer_note_28.py           # Note 28: Ventes de marchandises
│   ├── calculer_note_29.py           # Note 29: Ventes de produits finis
│   ├── calculer_note_30.py           # Note 30: Production immobilisée
│   ├── calculer_note_31.py           # Note 31: Subventions d'exploitation
│   ├── calculer_note_32.py           # Note 32: Reprises de provisions
│   └── calculer_note_33.py           # Note 33: Produits financiers
├── Tests/                            # Tests et fixtures
│   ├── conftest.py                   # Configuration Hypothesis
│   ├── test_balance_reader.py        # Tests Balance_Reader
│   ├── test_account_extractor.py     # Tests Account_Extractor
│   ├── test_movement_calculator.py   # Tests Movement_Calculator
│   ├── test_vnc_calculator.py        # Tests VNC_Calculator
│   ├── test_html_generator.py        # Tests HTML_Generator
│   ├── test_excel_exporter.py        # Tests Excel_Exporter
│   ├── test_mapping_manager.py       # Tests Mapping_Manager
│   ├── test_coherence_validator.py   # Tests Coherence_Validator
│   ├── test_trace_manager.py         # Tests Trace_Manager
│   ├── test_script_structure.py      # Tests structure des calculateurs
│   ├── test_all_notes_integration.py # Test intégration 33 notes
│   ├── test_api_integration.py       # Test intégration API
│   ├── test_balance_format_flexibility.py  # Tests flexibilité format
│   ├── fixtures/                     # Fichiers de test
│   │   ├── balance_demo_n_n1_n2.xlsx
│   │   ├── balance_incomplete.xlsx
│   │   ├── balance_invalid_format.xlsx
│   │   └── correspondances_test.json
│   └── test_note_XX.html             # Fichiers HTML de test (générés)
├── Ressources/                       # Ressources et données
│   ├── correspondances_syscohada.json # Mapping comptes SYSCOHADA
│   ├── liasse_officielle_revise.xlsx # Template officiel
│   └── README.md                     # Documentation ressources
├── calcul_notes_annexes_main.py      # Orchestrateur principal
└── api_notes_annexes.py              # Endpoint Flask API
```

## Modules Partagés

### 1. Balance_Reader
Responsabilité: Lecture et chargement des balances multi-exercices depuis Excel

**Fonctionnalités**:
- Détection automatique des onglets "BALANCE N", "BALANCE N-1", "BALANCE N-2"
- Chargement des 8 colonnes (Numéro, Intitulé, Ant Débit, Ant Crédit, Débit, Crédit, Solde Débit, Solde Crédit)
- Nettoyage des noms de colonnes (suppression espaces multiples)
- Conversion des montants en float avec gestion des valeurs invalides
- Gestion gracieuse des onglets manquants

### 2. Account_Extractor
Responsabilité: Extraction des soldes des comptes par racine

**Fonctionnalités**:
- Filtrage des comptes par racine (ex: "211" pour tous les comptes 211X)
- Extraction des 6 valeurs (Ant Débit, Ant Crédit, Débit, Crédit, Solde Débit, Solde Crédit)
- Sommation des comptes multiples avec la même racine
- Retour de zéros pour les comptes manquants

### 3. Movement_Calculator
Responsabilité: Calcul des mouvements et soldes avec validation de cohérence

**Fonctionnalités**:
- Calcul du solde d'ouverture: Solde Débit N-1 - Solde Crédit N-1
- Calcul des augmentations: Mouvement Débit N
- Calcul des diminutions: Mouvement Crédit N
- Calcul du solde de clôture: Solde Débit N - Solde Crédit N
- Vérification de cohérence: Solde_Clôture = Solde_Ouverture + Augmentations - Diminutions
- Inversion des signes pour les comptes d'amortissement (classe 28, 29)

### 4. VNC_Calculator
Responsabilité: Calcul des valeurs nettes comptables

**Fonctionnalités**:
- Calcul VNC Ouverture = Brut Ouverture - Amortissement Ouverture
- Calcul VNC Clôture = Brut Clôture - Amortissement Clôture
- Extraction des dotations aux amortissements (mouvements crédit 28X)
- Extraction des reprises d'amortissements (mouvements débit 28X)
- Validation que VNC >= 0

### 5. HTML_Generator
Responsabilité: Génération des fichiers HTML de visualisation

**Fonctionnalités**:
- Génération de tableaux HTML conformes au format SYSCOHADA
- En-têtes groupés avec sous-colonnes
- Formatage des montants avec séparateur de milliers et 0 décimales
- Ligne de total avec style distinct
- CSS avec bordures, couleurs d'en-tête et alternance de lignes
- Responsive design adapté à différentes tailles d'écran

### 6. Excel_Exporter
Responsabilité: Export des notes annexes vers Excel

**Fonctionnalités**:
- Export d'une note ou de toutes les notes dans un seul fichier
- Reproduction de la structure du tableau HTML
- Formatage des cellules (bordures, couleurs, formats numériques)
- Noms de fichiers avec timestamp (Notes_Annexes_Calculees_AAAAMMJJ.xlsx)

### 7. Mapping_Manager
Responsabilité: Gestion des correspondances SYSCOHADA

**Fonctionnalités**:
- Chargement du fichier correspondances_syscohada.json
- Lookup des racines de comptes par poste
- Validation des racines (chaînes numériques)
- Ajout dynamique de nouvelles correspondances
- Gestion des 4 sections: bilan_actif, bilan_passif, charges, produits

### 8. Coherence_Validator
Responsabilité: Validation de la cohérence inter-notes

**Fonctionnalités**:
- Vérification que total immobilisations (Notes 3A-3E) = Bilan Actif
- Vérification que dotations amortissements (Notes 3A-3E) = Compte de Résultat
- Vérification que Solde Clôture N-1 = Solde Ouverture N
- Calcul du taux de cohérence global (% d'écarts < 1%)
- Génération de rapport HTML de cohérence
- Émission d'alertes si taux < 95%

### 9. Trace_Manager
Responsabilité: Traçabilité et audit des calculs

**Fonctionnalités**:
- Enregistrement des calculs avec sources (comptes et soldes)
- Enregistrement des métadonnées (fichier balance, hash MD5, date/heure)
- Sauvegarde en JSON pour traçabilité complète
- Export en CSV pour analyse Excel
- Gestion de l'historique (conservation des 10 dernières générations)

## Flux de Traitement

```
1. Chargement des balances
   ├─ Balance_Reader.charger_balances()
   └─ Retour: 3 DataFrames (N, N-1, N-2)

2. Calcul de chaque note (33 fois)
   ├─ CalculateurNoteXX.charger_balances()
   ├─ Pour chaque ligne de la note:
   │  ├─ Account_Extractor.extraire_solde_compte()
   │  ├─ Movement_Calculator.calculer_*()
   │  ├─ VNC_Calculator.calculer_vnc_*()
   │  └─ Trace_Manager.enregistrer_calcul()
   ├─ CalculateurNoteXX.generer_note()
   ├─ HTML_Generator.generer_html()
   ├─ Excel_Exporter.exporter_note()
   └─ Retour: DataFrame de la note

3. Validation de cohérence inter-notes
   ├─ Coherence_Validator.valider_total_immobilisations()
   ├─ Coherence_Validator.valider_dotations_amortissements()
   ├─ Coherence_Validator.valider_continuite_temporelle()
   ├─ Coherence_Validator.calculer_taux_coherence()
   └─ Coherence_Validator.generer_rapport_coherence()

4. Génération des sorties
   ├─ Fichiers HTML: Tests/test_note_XX.html (33 fichiers)
   ├─ Fichier Excel: Notes_Annexes_Calculees_AAAAMMJJ.xlsx
   ├─ Fichiers de trace: Tests/trace_note_XX.json (33 fichiers)
   ├─ Rapport de cohérence: Tests/rapport_coherence.html
   └─ Fichiers de log: calcul_notes_annexes.log, calcul_notes_warnings.log
```

## Utilisation

### Exécution d'une note individuelle

```python
from Scripts.calculer_note_3a import CalculateurNote3A

calculateur = CalculateurNote3A("../../P000 -BALANCE DEMO N_N-1_N-2.xlsx")
calculateur.charger_balances()
note_df = calculateur.generer_note()
html = calculateur.generer_html(note_df)
calculateur.sauvegarder_html(html, "Tests/test_note_3a.html")
```

### Exécution de toutes les 33 notes

```python
from calcul_notes_annexes_main import CalculNotesAnnexesMain

orchestrateur = CalculNotesAnnexesMain("../../P000 -BALANCE DEMO N_N-1_N-2.xlsx")
resultats = orchestrateur.calculer_toutes_notes()
print(f"Taux de cohérence: {resultats['taux_coherence']}%")
```

### Utilisation via API Flask

```bash
curl -X POST http://localhost:5000/api/calculer_notes_annexes \
  -F "file=@balance.xlsx"
```

## Fichiers de Configuration

### correspondances_syscohada.json

Mappe les postes des états financiers aux racines de comptes SYSCOHADA:

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

## Logs et Traçabilité

### calcul_notes_annexes.log
Log principal avec tous les événements du système

### calcul_notes_warnings.log
Avertissements spécifiques (balances incohérentes, VNC négatif, etc.)

### trace_note_XX.json
Détail complet des calculs pour chaque note avec sources

## Performance

- **Chargement des balances**: ~1 seconde
- **Calcul d'une note**: ~0.5 secondes
- **Calcul des 33 notes**: ~16 secondes
- **Validation de cohérence**: ~2 secondes
- **Génération HTML/Excel**: ~5 secondes
- **Total**: ~24 secondes (< 30 secondes requis)

## Propriétés de Correctness Validées

Le système valide 21 propriétés de correctness via tests property-based:

1. Balance Loading Completeness
2. Column Name Normalization
3. Numeric Conversion Robustness
4. Account Filtering by Root
5. Account Extraction Completeness
6. Missing Account Handling
7. Accounting Equation Coherence
8. Depreciation Account Sign Inversion
9. VNC Calculation Formula
10. Script Structure Conformity
11. HTML Generation Conformity
12. Mapping Lookup Consistency
13. Graceful Degradation with Missing Data
14. Warning Logging Completeness
15. Excel Export Structure Preservation
16. Inter-Note Coherence Validation
17. Coherence Rate Calculation
18. Performance Constraint
19. Calculation Caching
20. API Integration Round-Trip
21. Balance Format Flexibility

## Dépannage

Voir le fichier TROUBLESHOOTING.md pour les solutions aux problèmes courants.

## Support

Pour toute question ou problème, consultez:
- GUIDE_UTILISATION.md pour les exemples d'utilisation
- TROUBLESHOOTING.md pour les solutions
- Les docstrings Python pour les détails techniques
- Les fichiers de log pour les diagnostics
