# Guide d'Utilisation - Calcul Automatique des Notes Annexes SYSCOHADA Révisé

## Table des Matières

1. [Introduction](#introduction)
2. [Installation et Configuration](#installation-et-configuration)
3. [Utilisation des Calculateurs Individuels](#utilisation-des-calculateurs-individuels)
4. [Utilisation de l'Orchestrateur Principal](#utilisation-de-lorchestrator-principal)
5. [Utilisation de l'API REST](#utilisation-de-lapi-rest)
6. [Exemples Pratiques](#exemples-pratiques)
7. [Dépannage](#dépannage)
8. [Bonnes Pratiques](#bonnes-pratiques)

---

## Introduction

Ce guide explique comment utiliser le système d'automatisation du calcul des 33 notes annexes SYSCOHADA révisé. Le système offre trois niveaux d'utilisation :

1. **Calculateurs individuels** : Calculer une note annexe spécifique
2. **Orchestrateur principal** : Calculer les 33 notes en une seule exécution
3. **API REST** : Intégration avec l'application Claraverse

---

## Installation et Configuration

### Prérequis

- Python 3.8+
- pandas >= 1.3.0
- openpyxl >= 3.6.0
- flask >= 2.0.0
- hypothesis >= 6.0.0 (pour les tests)
- pytest >= 6.0.0 (pour les tests)

### Installation des Dépendances

```bash
cd py_backend
pip install -r requirements.txt
```

### Structure des Fichiers

```
py_backend/
├── Doc calcul notes annexes/
│   ├── Modules/                    # Modules partagés
│   │   ├── balance_reader.py
│   │   ├── account_extractor.py
│   │   ├── movement_calculator.py
│   │   ├── vnc_calculator.py
│   │   ├── html_generator.py
│   │   ├── excel_exporter.py
│   │   ├── mapping_manager.py
│   │   ├── coherence_validator.py
│   │   └── trace_manager.py
│   ├── Scripts/                    # Calculateurs des 33 notes
│   │   ├── calculer_note_1.py
│   │   ├── calculer_note_3a.py
│   │   ├── calculer_note_3b.py
│   │   └── ... (jusqu'à calculer_note_33.py)
│   ├── Tests/                      # Tests et fixtures
│   │   ├── conftest.py
│   │   ├── test_balance_reader.py
│   │   └── ... (tests des modules)
│   ├── Ressources/                 # Fichiers de configuration
│   │   └── correspondances_syscohada.json
│   ├── calcul_notes_annexes_main.py  # Orchestrateur principal
│   └── api_notes_annexes.py           # Endpoint API
├── correspondances_syscohada.json
└── P000 -BALANCE DEMO N_N-1_N-2.xlsx  # Fichier de balance de test
```

### Configuration des Chemins

Les calculateurs utilisent des chemins relatifs. Assurez-vous que le fichier de balance est situé à :

```
py_backend/P000 -BALANCE DEMO N_N-1_N-2.xlsx
```

---

## Utilisation des Calculateurs Individuels

### Exécuter un Calculateur Spécifique

Chaque note annexe dispose d'un script Python dédié. Pour exécuter le calculateur de la Note 3A (Immobilisations Incorporelles) :

```bash
cd py_backend/Doc\ calcul\ notes\ annexes/Scripts
python calculer_note_3a.py
```

### Résultat de l'Exécution

Le calculateur génère :

1. **Fichier HTML** : `../Tests/test_note_3a.html`
   - Tableau formaté avec les données de la note
   - Styles CSS SYSCOHADA
   - Prêt pour visualisation dans un navigateur

2. **Affichage Console** : Résumé des calculs avec indicateurs visuels
   ```
   ✓ Balance chargée avec succès
   ✓ Comptes extraits
   ✓ Mouvements calculés
   ✓ VNC calculées
   ✓ HTML généré
   ```

### Exemple : Exécuter la Note 3B (Immobilisations Corporelles)

```bash
python calculer_note_3b.py
```

Résultat : `../Tests/test_note_3b.html`

### Exemple : Exécuter la Note 8 (Capital)

```bash
python calculer_note_8.py
```

Résultat : `../Tests/test_note_8.html`

### Gestion des Erreurs

Si une erreur survient :

1. **Balance non trouvée** : Vérifiez que le fichier `P000 -BALANCE DEMO N_N-1_N-2.xlsx` existe
2. **Onglets manquants** : Assurez-vous que les onglets "BALANCE N", "BALANCE N-1", "BALANCE N-2" existent
3. **Comptes manquants** : Le système utilise des valeurs nulles (0.0) pour les comptes inexistants

---

## Utilisation de l'Orchestrateur Principal

### Exécuter Toutes les 33 Notes

L'orchestrateur principal calcule les 33 notes en une seule exécution, avec validation de cohérence inter-notes :

```bash
cd py_backend/Doc\ calcul\ notes\ annexes
python calcul_notes_annexes_main.py
```

### Résultat de l'Exécution

L'orchestrateur génère :

1. **Fichiers HTML** : 33 fichiers dans `Tests/`
   - `test_note_01.html` à `test_note_33.html`
   - Chacun contient le tableau formaté de la note

2. **Fichier Excel** : `Notes_Annexes_Calculees_AAAAMMJJ.xlsx`
   - 33 onglets (un par note)
   - Formatage SYSCOHADA
   - Prêt pour intégration dans la liasse fiscale

3. **Rapport de Cohérence** : `rapport_coherence.html`
   - Validation inter-notes
   - Taux de cohérence global
   - Alertes si cohérence < 95%

4. **Fichiers de Trace** : `trace_note_XX.json` (33 fichiers)
   - Détail des calculs pour chaque note
   - Métadonnées de génération
   - Traçabilité complète

5. **Affichage Console** : Barre de progression et résumé
   ```
   Calcul des 33 notes annexes...
   [████████████████████] 100% (33/33)
   
   Résumé :
   ✓ Note 01 : Succès
   ✓ Note 02 : Succès
   ...
   ✓ Note 33 : Succès
   
   Taux de cohérence : 98.5%
   Temps total : 12.3 secondes
   ```

### Options de Configuration

Modifiez `calcul_notes_annexes_main.py` pour :

- **Charger une balance personnalisée** :
  ```python
  orchestrator = CalculNotesAnnexesMain(
      fichier_balance="chemin/vers/votre/balance.xlsx"
  )
  ```

- **Générer uniquement les HTML** (sans Excel) :
  ```python
  orchestrator.calculer_toutes_notes(generer_excel=False)
  ```

- **Générer uniquement les fichiers de trace** :
  ```python
  orchestrator.calculer_toutes_notes(generer_traces=True)
  ```

---

## Utilisation de l'API REST

### Démarrer le Serveur Flask

```bash
cd py_backend
python main.py
```

Le serveur démarre sur `http://localhost:5000`

### Endpoint : POST /api/calculer_notes_annexes

**URL** : `http://localhost:5000/api/calculer_notes_annexes`

**Méthode** : POST

**Content-Type** : multipart/form-data

**Paramètres** :
- `file` (required) : Fichier Excel de balance (multipart file upload)

**Réponse** : JSON contenant les 33 notes

### Exemple avec cURL

```bash
curl -X POST \
  -F "file=@P000 -BALANCE DEMO N_N-1_N-2.xlsx" \
  http://localhost:5000/api/calculer_notes_annexes
```

### Exemple avec Python

```python
import requests

with open('P000 -BALANCE DEMO N_N-1_N-2.xlsx', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:5000/api/calculer_notes_annexes',
        files=files
    )

# Réponse JSON
data = response.json()
print(f"Statut : {data['status']}")
print(f"Nombre de notes : {len(data['notes'])}")

# Accéder à une note spécifique
note_3a = data['notes']['Note 3A']
print(f"Note 3A HTML : {note_3a['html']}")
```

### Exemple avec JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/api/calculer_notes_annexes', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Statut:', data.status);
  console.log('Nombre de notes:', data.notes.length);
  
  // Afficher la Note 3A
  const note3a = data.notes.find(n => n.numero === '3A');
  document.getElementById('note-container').innerHTML = note3a.html;
})
.catch(error => console.error('Erreur:', error));
```

### Codes de Réponse HTTP

| Code | Signification |
|------|---------------|
| 200 | Succès - Calcul complété |
| 400 | Erreur - Fichier invalide ou manquant |
| 404 | Erreur - Endpoint non trouvé |
| 500 | Erreur - Erreur serveur interne |
| 503 | Erreur - Service temporairement indisponible |

### Format de Réponse JSON

```json
{
  "status": "success",
  "timestamp": "2026-04-28T14:30:00",
  "coherence_rate": 98.5,
  "notes": [
    {
      "numero": "3A",
      "titre": "Immobilisations incorporelles",
      "html": "<table>...</table>",
      "data": {
        "lignes": [
          {
            "libelle": "Frais de R&D",
            "brut_ouverture": 1500000.0,
            "augmentations": 500000.0,
            ...
          }
        ]
      }
    },
    ...
  ]
}
```

---

## Exemples Pratiques

### Exemple 1 : Calculer une Note Spécifique et Visualiser le Résultat

```bash
# Calculer la Note 3A
cd py_backend/Doc\ calcul\ notes\ annexes/Scripts
python calculer_note_3a.py

# Ouvrir le fichier HTML dans le navigateur
open ../Tests/test_note_3a.html  # macOS
# ou
start ../Tests/test_note_3a.html  # Windows
# ou
xdg-open ../Tests/test_note_3a.html  # Linux
```

### Exemple 2 : Calculer Toutes les Notes et Exporter en Excel

```bash
cd py_backend/Doc\ calcul\ notes\ annexes
python calcul_notes_annexes_main.py

# Le fichier Excel est généré automatiquement
# Vérifier le fichier créé
ls -la Notes_Annexes_Calculees_*.xlsx
```

### Exemple 3 : Utiliser l'API depuis Claraverse

1. **Démarrer le serveur backend** :
   ```bash
   cd py_backend
   python main.py
   ```

2. **Dans l'interface Claraverse** :
   - Aller à "Etat fin"
   - Cliquer sur "Calculer Notes Annexes"
   - Sélectionner le fichier de balance
   - Les 33 notes s'affichent dans des accordéons cliquables

3. **Exporter les résultats** :
   - Cliquer sur "Exporter en Excel"
   - Le fichier est téléchargé automatiquement

### Exemple 4 : Tracer les Calculs d'une Note

```python
# Dans un script Python
from py_backend.Doc_calcul_notes_annexes.Scripts.calculer_note_3a import CalculateurNote3A

calculateur = CalculateurNote3A('P000 -BALANCE DEMO N_N-1_N-2.xlsx')
calculateur.charger_balances()
note_df = calculateur.generer_note()

# Accéder aux traces
traces = calculateur.trace_manager.traces
for trace in traces:
    print(f"Ligne : {trace['libelle']}")
    print(f"Montant : {trace['montant']}")
    print(f"Comptes sources : {trace['comptes_sources']}")
```

### Exemple 5 : Valider la Cohérence Inter-Notes

```python
from py_backend.Doc_calcul_notes_annexes.Modules.coherence_validator import CoherenceValidator

# Après avoir calculé toutes les notes
validator = CoherenceValidator(notes_dict)
coherent, ecart = validator.valider_total_immobilisations()
print(f"Total immobilisations cohérent : {coherent}")
print(f"Écart : {ecart}")

taux = validator.calculer_taux_coherence()
print(f"Taux de cohérence global : {taux}%")

rapport = validator.generer_rapport_coherence()
with open('rapport_coherence.html', 'w') as f:
    f.write(rapport)
```

---

## Dépannage

### Problème : "Balance not found"

**Cause** : Le fichier de balance n'existe pas au chemin attendu

**Solution** :
1. Vérifiez que `P000 -BALANCE DEMO N_N-1_N-2.xlsx` existe dans `py_backend/`
2. Vérifiez le chemin relatif dans le calculateur
3. Utilisez un chemin absolu si nécessaire

### Problème : "Missing worksheet"

**Cause** : Les onglets "BALANCE N", "BALANCE N-1", "BALANCE N-2" n'existent pas

**Solution** :
1. Ouvrez le fichier Excel
2. Vérifiez les noms des onglets
3. Renommez-les si nécessaire
4. Assurez-vous que les 8 colonnes requises existent

### Problème : "Invalid column names"

**Cause** : Les noms de colonnes ne correspondent pas au format attendu

**Solution** :
1. Vérifiez que les colonnes sont : Numéro, Intitulé, Ant Débit, Ant Crédit, Débit, Crédit, Solde Débit, Solde Crédit
2. Supprimez les espaces superflus
3. Utilisez la normalisation automatique du Balance_Reader

### Problème : "Coherence rate < 95%"

**Cause** : Les données ne sont pas cohérentes entre les notes

**Solution** :
1. Vérifiez les données source dans la balance
2. Consultez le rapport de cohérence (`rapport_coherence.html`)
3. Vérifiez les alertes spécifiques
4. Corrigez les données source et recalculez

### Problème : "API endpoint returns 500 error"

**Cause** : Erreur serveur interne

**Solution** :
1. Vérifiez les logs du serveur Flask
2. Assurez-vous que le fichier de balance est valide
3. Vérifiez que tous les modules sont importés correctement
4. Redémarrez le serveur

### Problème : "HTML file is empty"

**Cause** : Aucune donnée n'a été calculée

**Solution** :
1. Vérifiez que la balance contient des données
2. Vérifiez que les comptes mappés existent dans la balance
3. Consultez les logs pour les avertissements
4. Vérifiez le fichier de correspondances JSON

---

## Bonnes Pratiques

### 1. Validation des Données Source

Avant de calculer les notes :

```python
from py_backend.Doc_calcul_notes_annexes.Modules.balance_reader import BalanceReader

reader = BalanceReader('P000 -BALANCE DEMO N_N-1_N-2.xlsx')
balance_n, balance_n1, balance_n2 = reader.charger_balances()

# Vérifier les dimensions
print(f"Balance N : {len(balance_n)} comptes")
print(f"Balance N-1 : {len(balance_n1)} comptes")
print(f"Balance N-2 : {len(balance_n2)} comptes")

# Vérifier les colonnes
print(f"Colonnes : {balance_n.columns.tolist()}")
```

### 2. Gestion des Erreurs

Toujours encapsuler les appels dans des blocs try-except :

```python
try:
    calculateur = CalculateurNote3A('balance.xlsx')
    calculateur.charger_balances()
    note_df = calculateur.generer_note()
    html = calculateur.generer_html(note_df)
    calculateur.sauvegarder_html(html, 'test_note_3a.html')
except FileNotFoundError as e:
    print(f"Erreur : Fichier non trouvé - {e}")
except ValueError as e:
    print(f"Erreur : Données invalides - {e}")
except Exception as e:
    print(f"Erreur inattendue : {e}")
```

### 3. Performance

Pour optimiser la performance :

- **Charger les balances une seule fois** : Utilisez l'orchestrateur principal
- **Utiliser le cache** : Les résultats intermédiaires sont mis en cache
- **Paralléliser si possible** : Les notes indépendantes peuvent être calculées en parallèle

### 4. Traçabilité

Toujours générer les fichiers de trace :

```python
orchestrator = CalculNotesAnnexesMain('balance.xlsx')
orchestrator.calculer_toutes_notes(generer_traces=True)

# Les fichiers trace_note_XX.json sont générés automatiquement
# Consultez-les pour auditer les calculs
```

### 5. Validation de Cohérence

Toujours valider la cohérence après le calcul :

```python
validator = CoherenceValidator(notes_dict)
taux = validator.calculer_taux_coherence()

if taux < 95:
    print("⚠️ Attention : Cohérence faible")
    rapport = validator.generer_rapport_coherence()
    # Analyser le rapport
else:
    print("✓ Cohérence validée")
```

### 6. Logging

Activez le logging pour le débogage :

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calcul_notes_annexes.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Démarrage du calcul des notes annexes")
```

---

## Résumé des Commandes Principales

| Tâche | Commande |
|-------|----------|
| Calculer Note 3A | `python Scripts/calculer_note_3a.py` |
| Calculer toutes les notes | `python calcul_notes_annexes_main.py` |
| Démarrer l'API | `python main.py` |
| Exécuter les tests | `pytest Tests/` |
| Générer la documentation | `python -m pydoc -w Modules` |

---

## Support et Ressources

- **Documentation technique** : Voir `design.md`
- **Spécifications** : Voir `requirements.md`
- **Tests** : Voir `Tests/README.md`
- **Modules** : Voir `Modules/README.md`
- **Scripts** : Voir `Scripts/README.md`

---

**Dernière mise à jour** : 28 avril 2026
**Version** : 1.0
