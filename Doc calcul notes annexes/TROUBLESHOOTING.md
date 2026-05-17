# Guide de Dépannage - Calcul Automatique des Notes Annexes SYSCOHADA Révisé

## Table des Matières

1. [Erreurs Courantes](#erreurs-courantes)
2. [Problèmes de Format de Balance](#problèmes-de-format-de-balance)
3. [Problèmes de Performance](#problèmes-de-performance)
4. [Techniques de Débogage](#techniques-de-débogage)
5. [Optimisation des Performances](#optimisation-des-performances)
6. [Problèmes d'API](#problèmes-dapi)
7. [Problèmes de Cohérence](#problèmes-de-cohérence)
8. [FAQ](#faq)

---

## Erreurs Courantes

### Erreur 1: "FileNotFoundError: Balance file not found"

**Symptôme** :
```
FileNotFoundError: [Errno 2] No such file or directory: '../../P000 -BALANCE DEMO N_N-1_N-2.xlsx'
```

**Causes possibles** :
- Le fichier de balance n'existe pas au chemin spécifié
- Le chemin relatif est incorrect
- Le fichier a été déplacé ou renommé

**Solutions** :

1. **Vérifier l'existence du fichier** :
   ```bash
   ls -la py_backend/P000\ -BALANCE\ DEMO\ N_N-1_N-2.xlsx
   ```

2. **Utiliser un chemin absolu** :
   ```python
   import os
   chemin_absolu = os.path.abspath('P000 -BALANCE DEMO N_N-1_N-2.xlsx')
   calculateur = CalculateurNote3A(chemin_absolu)
   ```

3. **Vérifier le répertoire de travail** :
   ```python
   import os
   print(f"Répertoire actuel : {os.getcwd()}")
   ```

4. **Copier le fichier au bon emplacement** :
   ```bash
   cp /chemin/source/balance.xlsx py_backend/P000\ -BALANCE\ DEMO\ N_N-1_N-2.xlsx
   ```

---

### Erreur 2: "BalanceNotFoundException: Missing worksheet"

**Symptôme** :
```
BalanceNotFoundException: Worksheet 'BALANCE N' not found in Excel file
```

**Causes possibles** :
- Les onglets n'ont pas les noms attendus
- Les onglets sont mal orthographiés
- Le fichier Excel est corrompu

**Solutions** :

1. **Vérifier les noms des onglets** :
   ```python
   import openpyxl
   wb = openpyxl.load_workbook('balance.xlsx')
   print(f"Onglets disponibles : {wb.sheetnames}")
   ```

2. **Renommer les onglets manuellement** :
   - Ouvrir le fichier Excel
   - Renommer les onglets en : "BALANCE N", "BALANCE N-1", "BALANCE N-2"
   - Sauvegarder le fichier

3. **Utiliser un script de renommage** :
   ```python
   import openpyxl
   
   wb = openpyxl.load_workbook('balance.xlsx')
   
   # Mapper les anciens noms aux nouveaux
   mapping = {
       'Balance 2024': 'BALANCE N',
       'Balance 2023': 'BALANCE N-1',
       'Balance 2022': 'BALANCE N-2'
   }
   
   for old_name, new_name in mapping.items():
       if old_name in wb.sheetnames:
           ws = wb[old_name]
           ws.title = new_name
   
   wb.save('balance_corrigee.xlsx')
   ```



---

### Erreur 3: "InvalidBalanceFormatException: Missing required columns"

**Symptôme** :
```
InvalidBalanceFormatException: Missing columns: ['Ant Débit', 'Solde Crédit']
```

**Causes possibles** :
- Les colonnes n'ont pas les noms attendus
- Les colonnes ont des espaces multiples
- Les colonnes sont dans un ordre différent

**Solutions** :

1. **Vérifier les noms de colonnes** :
   ```python
   import pandas as pd
   df = pd.read_excel('balance.xlsx', sheet_name='BALANCE N')
   print(f"Colonnes actuelles : {df.columns.tolist()}")
   ```

2. **Colonnes attendues** :
   - Numéro
   - Intitulé
   - Ant Débit
   - Ant Crédit
   - Débit
   - Crédit
   - Solde Débit
   - Solde Crédit

3. **Renommer les colonnes** :
   ```python
   import pandas as pd
   
   df = pd.read_excel('balance.xlsx', sheet_name='BALANCE N')
   
   # Mapper les anciens noms aux nouveaux
   mapping = {
       'Numero': 'Numéro',
       'Libelle': 'Intitulé',
       'Ant_Debit': 'Ant Débit',
       'Ant_Credit': 'Ant Crédit',
       'Solde_Debit': 'Solde Débit',
       'Solde_Credit': 'Solde Crédit'
   }
   
   df.rename(columns=mapping, inplace=True)
   df.to_excel('balance_corrigee.xlsx', sheet_name='BALANCE N', index=False)
   ```

4. **Utiliser la normalisation automatique** :
   Le Balance_Reader normalise automatiquement les espaces multiples :
   ```python
   from Modules.balance_reader import BalanceReader
   
   reader = BalanceReader('balance.xlsx')
   # La normalisation est automatique
   balance_n, balance_n1, balance_n2 = reader.charger_balances()
   ```

---

### Erreur 4: "ValueError: Invalid numeric value"

**Symptôme** :
```
ValueError: could not convert string to float: '1 500 000,00'
```

**Causes possibles** :
- Les montants contiennent des séparateurs de milliers
- Les montants utilisent la virgule comme séparateur décimal
- Les montants contiennent des caractères non numériques

**Solutions** :

1. **Le Balance_Reader gère automatiquement** :
   - Séparateurs de milliers (espace, virgule, point)
   - Séparateurs décimaux (virgule, point)
   - Valeurs vides (remplacées par 0.0)

2. **Nettoyer manuellement si nécessaire** :
   ```python
   import pandas as pd
   
   def nettoyer_montant(valeur):
       if pd.isna(valeur):
           return 0.0
       if isinstance(valeur, (int, float)):
           return float(valeur)
       
       # Supprimer les espaces et remplacer virgule par point
       valeur_str = str(valeur).replace(' ', '').replace(',', '.')
       try:
           return float(valeur_str)
       except ValueError:
           return 0.0
   
   df['Débit'] = df['Débit'].apply(nettoyer_montant)
   ```

3. **Vérifier les formats dans Excel** :
   - Sélectionner les colonnes de montants
   - Format → Nombre → Décimales : 2
   - Supprimer les formats personnalisés

---

### Erreur 5: "KeyError: Account root not found in mapping"

**Symptôme** :
```
KeyError: 'Immobilisations incorporelles' not found in correspondances_syscohada.json
```

**Causes possibles** :
- Le fichier correspondances_syscohada.json est manquant
- Le fichier JSON est mal formaté
- Le poste recherché n'existe pas dans le mapping

**Solutions** :

1. **Vérifier l'existence du fichier** :
   ```bash
   ls -la py_backend/correspondances_syscohada.json
   ```

2. **Valider le format JSON** :
   ```python
   import json
   
   with open('correspondances_syscohada.json', 'r', encoding='utf-8') as f:
       try:
           data = json.load(f)
           print("✓ JSON valide")
       except json.JSONDecodeError as e:
           print(f"✗ JSON invalide : {e}")
   ```

3. **Vérifier la structure** :
   ```python
   import json
   
   with open('correspondances_syscohada.json', 'r', encoding='utf-8') as f:
       data = json.load(f)
   
   # Vérifier les sections
   sections = ['bilan_actif', 'bilan_passif', 'charges', 'produits']
   for section in sections:
       if section in data:
           print(f"✓ Section {section} présente")
           print(f"  Postes : {list(data[section].keys())}")
       else:
           print(f"✗ Section {section} manquante")
   ```

4. **Ajouter un poste manquant** :
   ```python
   import json
   
   with open('correspondances_syscohada.json', 'r', encoding='utf-8') as f:
       data = json.load(f)
   
   # Ajouter un nouveau poste
   data['bilan_actif']['Nouveau poste'] = {
       'brut': ['2XX'],
       'amort': ['28XX']
   }
   
   with open('correspondances_syscohada.json', 'w', encoding='utf-8') as f:
       json.dump(data, f, indent=2, ensure_ascii=False)
   ```



---

## Problèmes de Format de Balance

### Format de Balance Requis

**Structure attendue** :

| Numéro | Intitulé | Ant Débit | Ant Crédit | Débit | Crédit | Solde Débit | Solde Crédit |
|--------|----------|-----------|------------|-------|--------|-------------|--------------|
| 211 | Frais R&D | 1500000 | 0 | 500000 | 0 | 2000000 | 0 |
| 2811 | Amort Frais R&D | 0 | 300000 | 0 | 200000 | 0 | 500000 |

**Règles** :
- 8 colonnes obligatoires
- Numéro de compte : chaîne de caractères (ex: "211", "2811")
- Montants : numériques (float)
- Valeurs vides : remplacées par 0.0

### Problème : Formats de Nombres Variables

**Symptôme** : Les montants sont formatés différemment selon les logiciels comptables

**Formats supportés** :

| Format | Exemple | Support |
|--------|---------|---------|
| Espace comme séparateur de milliers | 1 500 000 | ✓ |
| Virgule comme séparateur de milliers | 1,500,000 | ✓ |
| Point comme séparateur de milliers | 1.500.000 | ✓ |
| Virgule comme séparateur décimal | 1500000,50 | ✓ |
| Point comme séparateur décimal | 1500000.50 | ✓ |
| Mixte | 1 500 000,50 | ✓ |

**Solution automatique** :
Le Balance_Reader détecte et convertit automatiquement tous ces formats.

**Test de compatibilité** :
```python
from Modules.balance_reader import BalanceReader

reader = BalanceReader('votre_balance.xlsx')
try:
    balance_n, balance_n1, balance_n2 = reader.charger_balances()
    print("✓ Format de balance compatible")
except Exception as e:
    print(f"✗ Format incompatible : {e}")
```

### Problème : Colonnes avec Espaces Multiples

**Symptôme** : Les noms de colonnes contiennent des espaces multiples

**Exemple** :
```
"Ant  Débit"  (2 espaces)
"Solde    Crédit"  (4 espaces)
```

**Solution automatique** :
Le Balance_Reader normalise automatiquement les espaces :
```python
# Avant normalisation : "Ant  Débit"
# Après normalisation : "Ant Débit"
```

**Vérification manuelle** :
```python
import pandas as pd

df = pd.read_excel('balance.xlsx', sheet_name='BALANCE N')
print("Colonnes avant normalisation :")
for col in df.columns:
    print(f"  '{col}' (longueur: {len(col)})")

# Normaliser
df.columns = [' '.join(col.split()) for col in df.columns]

print("\nColonnes après normalisation :")
for col in df.columns:
    print(f"  '{col}' (longueur: {len(col)})")
```

### Problème : Exercice N-2 Manquant

**Symptôme** : Le fichier ne contient que les exercices N et N-1

**Solution** :
Le système gère gracieusement l'absence de N-2 :
- Les calculs continuent avec N et N-1
- Les colonnes N-2 affichent des valeurs nulles
- Un avertissement est émis dans les logs

**Vérification** :
```python
from Modules.balance_reader import BalanceReader

reader = BalanceReader('balance.xlsx')
try:
    balance_n, balance_n1, balance_n2 = reader.charger_balances()
    
    if balance_n2 is None or len(balance_n2) == 0:
        print("⚠️ Exercice N-2 manquant - Calcul avec N et N-1 uniquement")
    else:
        print(f"✓ Exercice N-2 présent ({len(balance_n2)} comptes)")
except Exception as e:
    print(f"✗ Erreur : {e}")
```

### Problème : Comptes Manquants dans la Balance

**Symptôme** : Certains comptes mappés n'existent pas dans la balance

**Comportement** :
Le système retourne des valeurs nulles (0.0) pour les comptes manquants sans interrompre le traitement.

**Exemple** :
```python
from Modules.account_extractor import AccountExtractor

extractor = AccountExtractor(balance_n)

# Compte existant
solde_211 = extractor.extraire_solde_compte('211')
print(f"Compte 211 : {solde_211}")  # {'ant_debit': 1500000, ...}

# Compte manquant
solde_999 = extractor.extraire_solde_compte('999')
print(f"Compte 999 : {solde_999}")  # {'ant_debit': 0.0, 'ant_credit': 0.0, ...}
```

**Vérification des comptes manquants** :
```python
import logging

# Activer le logging des avertissements
logging.basicConfig(level=logging.WARNING)

# Les comptes manquants sont loggés automatiquement
calculateur = CalculateurNote3A('balance.xlsx')
calculateur.charger_balances()
note_df = calculateur.generer_note()

# Consulter calcul_notes_warnings.log
with open('calcul_notes_warnings.log', 'r') as f:
    warnings = f.read()
    if 'Missing account' in warnings:
        print("⚠️ Comptes manquants détectés")
        print(warnings)
```

---

## Problèmes de Performance

### Problème : Calcul Trop Lent (> 30 secondes)

**Symptôme** : Le calcul des 33 notes prend plus de 30 secondes

**Causes possibles** :
- Fichier de balance très volumineux (> 10 000 comptes)
- Disque dur lent (HDD vs SSD)
- Mémoire insuffisante
- Antivirus bloquant les accès fichiers

**Solutions** :

1. **Utiliser l'orchestrateur avec cache** :
   ```python
   from calcul_notes_annexes_main import CalculNotesAnnexesMain
   
   # L'orchestrateur charge les balances une seule fois
   orchestrator = CalculNotesAnnexesMain('balance.xlsx')
   resultats = orchestrator.calculer_toutes_notes()
   ```

2. **Profiler les performances** :
   ```python
   import time
   
   start = time.time()
   
   # Charger les balances
   t1 = time.time()
   reader = BalanceReader('balance.xlsx')
   balance_n, balance_n1, balance_n2 = reader.charger_balances()
   print(f"Chargement balances : {time.time() - t1:.2f}s")
   
   # Calculer une note
   t2 = time.time()
   calculateur = CalculateurNote3A('balance.xlsx')
   note_df = calculateur.generer_note()
   print(f"Calcul note : {time.time() - t2:.2f}s")
   
   # Générer HTML
   t3 = time.time()
   html = calculateur.generer_html(note_df)
   print(f"Génération HTML : {time.time() - t3:.2f}s")
   
   print(f"Total : {time.time() - start:.2f}s")
   ```

3. **Optimiser le fichier de balance** :
   - Supprimer les comptes inutilisés (soldes à zéro)
   - Compresser le fichier Excel
   - Utiliser le format XLSX au lieu de XLS

4. **Augmenter la mémoire disponible** :
   ```python
   import pandas as pd
   
   # Optimiser l'utilisation mémoire
   pd.set_option('mode.chained_assignment', None)
   pd.set_option('compute.use_numexpr', True)
   ```



### Problème : Mémoire Insuffisante

**Symptôme** :
```
MemoryError: Unable to allocate array
```

**Causes possibles** :
- Fichier de balance très volumineux
- Calcul de toutes les notes simultanément
- Mémoire RAM insuffisante

**Solutions** :

1. **Calculer les notes séquentiellement** :
   ```python
   # Au lieu de calculer toutes les notes en mémoire
   for i in range(1, 34):
       calculateur = eval(f'CalculateurNote{i}')('balance.xlsx')
       note_df = calculateur.generer_note()
       html = calculateur.generer_html(note_df)
       calculateur.sauvegarder_html(html, f'test_note_{i}.html')
       
       # Libérer la mémoire
       del calculateur, note_df, html
       import gc
       gc.collect()
   ```

2. **Réduire la taille des DataFrames** :
   ```python
   import pandas as pd
   
   # Utiliser des types de données optimisés
   df = pd.read_excel('balance.xlsx', dtype={
       'Numéro': 'str',
       'Intitulé': 'str',
       'Ant Débit': 'float32',
       'Ant Crédit': 'float32',
       'Débit': 'float32',
       'Crédit': 'float32',
       'Solde Débit': 'float32',
       'Solde Crédit': 'float32'
   })
   ```

3. **Augmenter la mémoire virtuelle** (Windows) :
   - Panneau de configuration → Système → Paramètres système avancés
   - Onglet Avancé → Performances → Paramètres
   - Onglet Avancé → Mémoire virtuelle → Modifier
   - Augmenter la taille du fichier d'échange

---

## Techniques de Débogage

### Activer le Logging Détaillé

```python
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calcul_notes_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Utiliser le logger
logger.debug("Démarrage du calcul")
logger.info("Balance chargée avec succès")
logger.warning("Compte manquant : 211")
logger.error("Erreur lors du calcul")
```

### Inspecter les Données Intermédiaires

```python
from Modules.balance_reader import BalanceReader
from Modules.account_extractor import AccountExtractor

# Charger la balance
reader = BalanceReader('balance.xlsx')
balance_n, balance_n1, balance_n2 = reader.charger_balances()

# Inspecter la balance N
print(f"Nombre de comptes : {len(balance_n)}")
print(f"Colonnes : {balance_n.columns.tolist()}")
print(f"Premiers comptes :")
print(balance_n.head())

# Extraire un compte spécifique
extractor = AccountExtractor(balance_n)
solde = extractor.extraire_solde_compte('211')
print(f"\nCompte 211 :")
for key, value in solde.items():
    print(f"  {key}: {value}")

# Vérifier les comptes par racine
comptes_21x = extractor.filtrer_par_racine('21')
print(f"\nComptes 21X : {len(comptes_21x)}")
print(comptes_21x[['Numéro', 'Intitulé', 'Solde Débit', 'Solde Crédit']])
```

### Valider la Cohérence des Calculs

```python
from Modules.movement_calculator import MovementCalculator

calculator = MovementCalculator()

# Exemple de calcul
solde_ouverture = 1500000
augmentations = 500000
diminutions = 0
solde_cloture = 2000000

# Vérifier la cohérence
coherent, ecart = calculator.verifier_coherence(
    solde_ouverture, augmentations, diminutions, solde_cloture
)

if coherent:
    print("✓ Calcul cohérent")
else:
    print(f"✗ Incohérence détectée : écart de {ecart}")
```

### Tracer les Calculs

```python
from Modules.trace_manager import TraceManager

trace_manager = TraceManager('3A')

# Enregistrer un calcul
trace_manager.enregistrer_calcul(
    libelle='Frais de R&D',
    montant=2000000,
    comptes_sources=[
        {'compte': '211', 'solde_debit': 2000000, 'solde_credit': 0}
    ]
)

# Enregistrer les métadonnées
trace_manager.enregistrer_metadata(
    fichier_balance='balance.xlsx',
    hash_md5='a1b2c3d4e5f6...'
)

# Sauvegarder la trace
trace_manager.sauvegarder_trace('trace_note_3a.json')

# Consulter la trace
import json
with open('trace_note_3a.json', 'r') as f:
    trace = json.load(f)
    print(json.dumps(trace, indent=2, ensure_ascii=False))
```

### Tester avec des Données Minimales

```python
import pandas as pd

# Créer une balance de test minimale
data = {
    'Numéro': ['211', '2811'],
    'Intitulé': ['Frais R&D', 'Amort Frais R&D'],
    'Ant Débit': [1500000, 0],
    'Ant Crédit': [0, 300000],
    'Débit': [500000, 0],
    'Crédit': [0, 200000],
    'Solde Débit': [2000000, 0],
    'Solde Crédit': [0, 500000]
}

balance_test = pd.DataFrame(data)

# Sauvegarder en Excel
with pd.ExcelWriter('balance_test.xlsx') as writer:
    balance_test.to_excel(writer, sheet_name='BALANCE N', index=False)
    balance_test.to_excel(writer, sheet_name='BALANCE N-1', index=False)
    balance_test.to_excel(writer, sheet_name='BALANCE N-2', index=False)

# Tester avec cette balance
calculateur = CalculateurNote3A('balance_test.xlsx')
calculateur.charger_balances()
note_df = calculateur.generer_note()
print(note_df)
```

---

## Optimisation des Performances

### Recommandations Générales

1. **Utiliser l'orchestrateur principal** :
   - Charge les balances une seule fois
   - Met en cache les résultats intermédiaires
   - Optimise l'ordre d'exécution

2. **Désactiver les sorties non nécessaires** :
   ```python
   orchestrator = CalculNotesAnnexesMain('balance.xlsx')
   resultats = orchestrator.calculer_toutes_notes(
       generer_html=True,
       generer_excel=False,  # Désactiver Excel si non nécessaire
       generer_traces=False  # Désactiver traces si non nécessaire
   )
   ```

3. **Utiliser un SSD** :
   - Les accès disque sont plus rapides
   - Réduction du temps de chargement des balances

4. **Fermer les applications gourmandes** :
   - Libérer de la mémoire RAM
   - Réduire la charge CPU

### Benchmarks de Performance

**Configuration de test** :
- CPU: Intel Core i5 (4 cœurs)
- RAM: 8 GB
- Disque: SSD
- Balance: 5000 comptes

**Résultats** :

| Opération | Temps (s) | % Total |
|-----------|-----------|---------|
| Chargement balances | 1.2 | 5% |
| Calcul 33 notes | 16.5 | 69% |
| Validation cohérence | 2.1 | 9% |
| Génération HTML | 3.8 | 16% |
| Génération Excel | 0.4 | 1% |
| **Total** | **24.0** | **100%** |

**Optimisations possibles** :

1. **Parallélisation** (gain: 30-40%) :
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def calculer_note(numero):
       calculateur = eval(f'CalculateurNote{numero}')('balance.xlsx')
       return calculateur.generer_note()
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       notes = list(executor.map(calculer_note, range(1, 34)))
   ```

2. **Cache des comptes** (gain: 10-15%) :
   ```python
   # Déjà implémenté dans l'orchestrateur
   # Les comptes extraits sont mis en cache
   ```

3. **Génération HTML optimisée** (gain: 5-10%) :
   ```python
   # Utiliser des templates pré-compilés
   from jinja2 import Template
   
   template = Template(html_template_string)
   html = template.render(data=note_df.to_dict('records'))
   ```



---

## Problèmes d'API

### Erreur : "Failed to fetch" ou "Network error"

**Symptôme** : L'appel API échoue avec une erreur réseau

**Causes possibles** :
- Le serveur Flask n'est pas démarré
- Le port 5000 est déjà utilisé
- Problème de CORS
- Timeout dépassé

**Solutions** :

1. **Vérifier que le serveur est démarré** :
   ```bash
   # Démarrer le serveur
   cd py_backend
   python main.py
   
   # Vérifier que le serveur écoute
   curl http://localhost:5000/health
   ```

2. **Changer le port si nécessaire** :
   ```python
   # Dans main.py
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5001, debug=True)
   ```

3. **Configurer CORS** :
   ```python
   from flask_cors import CORS
   
   app = Flask(__name__)
   CORS(app, resources={r"/api/*": {"origins": "*"}})
   ```

4. **Augmenter le timeout** :
   ```javascript
   // Côté frontend
   const controller = new AbortController();
   const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes
   
   fetch('http://localhost:5000/api/calculer_notes_annexes', {
     method: 'POST',
     body: formData,
     signal: controller.signal
   })
   .then(response => {
     clearTimeout(timeoutId);
     return response.json();
   })
   .catch(error => {
     if (error.name === 'AbortError') {
       console.error('Timeout dépassé');
     }
   });
   ```

### Erreur : "400 Bad Request - No file provided"

**Symptôme** :
```json
{
  "error": "No file provided",
  "status": 400
}
```

**Causes possibles** :
- Le fichier n'est pas envoyé dans la requête
- Le nom du champ n'est pas "file"
- Le Content-Type n'est pas multipart/form-data

**Solutions** :

1. **Vérifier le nom du champ** :
   ```javascript
   const formData = new FormData();
   formData.append('file', fileInput.files[0]); // Nom doit être "file"
   ```

2. **Vérifier le Content-Type** :
   ```bash
   curl -X POST \
     -H "Content-Type: multipart/form-data" \
     -F "file=@balance.xlsx" \
     http://localhost:5000/api/calculer_notes_annexes
   ```

3. **Vérifier que le fichier existe** :
   ```javascript
   if (fileInput.files.length === 0) {
     alert('Veuillez sélectionner un fichier');
     return;
   }
   ```

### Erreur : "500 Internal Server Error"

**Symptôme** :
```json
{
  "error": "Internal server error",
  "status": 500
}
```

**Causes possibles** :
- Erreur dans le code Python
- Fichier de balance invalide
- Module manquant

**Solutions** :

1. **Consulter les logs du serveur** :
   ```bash
   # Les logs s'affichent dans le terminal où le serveur est démarré
   # Rechercher les tracebacks Python
   ```

2. **Activer le mode debug** :
   ```python
   # Dans main.py
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=True)
   ```

3. **Tester le fichier localement** :
   ```python
   # Tester le fichier avant de l'envoyer à l'API
   from Modules.balance_reader import BalanceReader
   
   try:
       reader = BalanceReader('balance.xlsx')
       balance_n, balance_n1, balance_n2 = reader.charger_balances()
       print("✓ Fichier valide")
   except Exception as e:
       print(f"✗ Fichier invalide : {e}")
   ```

4. **Vérifier les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

### Erreur : "503 Service Unavailable"

**Symptôme** :
```json
{
  "error": "Service temporarily unavailable",
  "status": 503
}
```

**Causes possibles** :
- Le serveur est surchargé
- Calcul en cours pour un autre utilisateur
- Ressources insuffisantes

**Solutions** :

1. **Réessayer après quelques secondes** :
   ```javascript
   async function calculerNotesAvecRetry(file, maxRetries = 3) {
     for (let i = 0; i < maxRetries; i++) {
       try {
         const response = await fetch('/api/calculer_notes_annexes', {
           method: 'POST',
           body: formData
         });
         
         if (response.ok) {
           return await response.json();
         }
         
         if (response.status === 503 && i < maxRetries - 1) {
           await new Promise(resolve => setTimeout(resolve, 5000)); // Attendre 5s
           continue;
         }
         
         throw new Error(`HTTP ${response.status}`);
       } catch (error) {
         if (i === maxRetries - 1) throw error;
       }
     }
   }
   ```

2. **Augmenter les ressources serveur** :
   - Augmenter la RAM
   - Utiliser un serveur plus puissant
   - Implémenter une file d'attente

3. **Implémenter un système de file d'attente** :
   ```python
   from queue import Queue
   from threading import Thread
   
   calcul_queue = Queue()
   
   def worker():
       while True:
           task = calcul_queue.get()
           try:
               # Effectuer le calcul
               resultats = calculer_notes(task['fichier'])
               task['callback'](resultats)
           finally:
               calcul_queue.task_done()
   
   # Démarrer le worker
   Thread(target=worker, daemon=True).start()
   ```

---

## Problèmes de Cohérence

### Problème : Taux de Cohérence < 95%

**Symptôme** :
```
⚠️ Taux de cohérence : 87.3% (< 95%)
```

**Causes possibles** :
- Données source incohérentes
- Erreurs de saisie dans la balance
- Comptes mal mappés
- Calculs incorrects

**Solutions** :

1. **Consulter le rapport de cohérence** :
   ```bash
   open Tests/rapport_coherence.html
   ```

2. **Identifier les écarts** :
   ```python
   from Modules.coherence_validator import CoherenceValidator
   
   validator = CoherenceValidator(notes_dict)
   
   # Vérifier les immobilisations
   coherent, ecart = validator.valider_total_immobilisations()
   if not coherent:
       print(f"Écart immobilisations : {ecart}")
   
   # Vérifier les dotations
   coherent, ecart = validator.valider_dotations_amortissements()
   if not coherent:
       print(f"Écart dotations : {ecart}")
   
   # Vérifier la continuité temporelle
   ecarts = validator.valider_continuite_temporelle()
   for note, (coherent, ecart) in ecarts.items():
       if not coherent:
           print(f"Écart {note} : {ecart}")
   ```

3. **Corriger les données source** :
   - Vérifier les soldes d'ouverture = soldes de clôture N-1
   - Vérifier l'équation comptable : Solde Clôture = Solde Ouverture + Débit - Crédit
   - Vérifier les totaux par classe de comptes

4. **Vérifier le mapping des comptes** :
   ```python
   import json
   
   with open('correspondances_syscohada.json', 'r') as f:
       mapping = json.load(f)
   
   # Vérifier que tous les comptes mappés existent dans la balance
   from Modules.account_extractor import AccountExtractor
   
   extractor = AccountExtractor(balance_n)
   
   for section in mapping.values():
       for poste, comptes in section.items():
           if 'brut' in comptes:
               for racine in comptes['brut']:
                   solde = extractor.extraire_solde_compte(racine)
                   if all(v == 0.0 for v in solde.values()):
                       print(f"⚠️ Compte {racine} ({poste}) absent de la balance")
   ```

### Problème : VNC Négative

**Symptôme** :
```
⚠️ VNC négative détectée : Frais R&D = -50000
```

**Causes possibles** :
- Amortissements > Valeur brute
- Erreur de saisie
- Compte d'amortissement mal mappé

**Solutions** :

1. **Identifier les VNC négatives** :
   ```python
   from Modules.vnc_calculator import VNCCalculator
   
   vnc_calc = VNCCalculator()
   
   brut_cloture = 1000000
   amort_cloture = 1050000  # Erreur : amort > brut
   
   vnc = vnc_calc.calculer_vnc_cloture(brut_cloture, amort_cloture)
   valide, message = vnc_calc.valider_vnc(vnc)
   
   if not valide:
       print(f"✗ {message}")
       print(f"  Brut : {brut_cloture}")
       print(f"  Amort : {amort_cloture}")
       print(f"  VNC : {vnc}")
   ```

2. **Corriger les données** :
   - Vérifier que Amortissements ≤ Valeur brute
   - Vérifier les comptes d'amortissement (28X, 29X)
   - Vérifier les reprises d'amortissements

3. **Consulter les logs** :
   ```bash
   grep "VNC négative" calcul_notes_warnings.log
   ```



### Problème : Soldes Incohérents

**Symptôme** :
```
⚠️ Incohérence détectée : Solde Clôture ≠ Solde Ouverture + Augmentations - Diminutions
Écart : 10000
```

**Causes possibles** :
- Erreur de saisie dans la balance
- Mouvements non enregistrés
- Soldes d'ouverture incorrects

**Solutions** :

1. **Vérifier l'équation comptable** :
   ```python
   from Modules.movement_calculator import MovementCalculator
   
   calc = MovementCalculator()
   
   solde_ouverture = 1500000
   augmentations = 500000
   diminutions = 0
   solde_cloture = 2010000  # Devrait être 2000000
   
   coherent, ecart = calc.verifier_coherence(
       solde_ouverture, augmentations, diminutions, solde_cloture
   )
   
   if not coherent:
       print(f"✗ Incohérence : écart de {ecart}")
       print(f"  Solde attendu : {solde_ouverture + augmentations - diminutions}")
       print(f"  Solde réel : {solde_cloture}")
   ```

2. **Recalculer les soldes** :
   ```python
   # Vérifier dans Excel
   # Solde Clôture = Solde Ouverture + Débit - Crédit
   # Solde Ouverture = Ant Débit - Ant Crédit
   ```

3. **Consulter les avertissements** :
   ```bash
   grep "Incohérence" calcul_notes_warnings.log
   ```

---

## FAQ

### Q1 : Puis-je utiliser un fichier de balance avec un format différent ?

**R** : Oui, le système supporte plusieurs variations de format :
- Noms de colonnes avec espaces multiples
- Séparateurs de milliers (espace, virgule, point)
- Séparateurs décimaux (virgule, point)
- Noms d'onglets différents (avec détection automatique)

Cependant, les 8 colonnes obligatoires doivent être présentes.

### Q2 : Que faire si certains comptes n'existent pas dans ma balance ?

**R** : Le système gère gracieusement les comptes manquants :
- Les valeurs sont remplacées par 0.0
- Un avertissement est émis dans les logs
- Le calcul continue normalement

### Q3 : Puis-je calculer uniquement certaines notes au lieu des 33 ?

**R** : Oui, vous pouvez exécuter les calculateurs individuellement :
```python
# Calculer uniquement la Note 3A
from Scripts.calculer_note_3a import CalculateurNote3A

calculateur = CalculateurNote3A('balance.xlsx')
calculateur.charger_balances()
note_df = calculateur.generer_note()
```

### Q4 : Comment ajouter une nouvelle note annexe ?

**R** : Suivez ces étapes :

1. Créer un nouveau calculateur basé sur le template :
   ```python
   # Scripts/calculer_note_34.py
   from calculateur_note_template import CalculateurNote
   
   class CalculateurNote34(CalculateurNote):
       def __init__(self, fichier_balance):
           super().__init__(fichier_balance, '34', 'Titre de la note')
           self.mapping_comptes = {
               'Ligne 1': {'brut': ['XXX'], 'amort': ['XXXX']}
           }
   ```

2. Ajouter le mapping dans correspondances_syscohada.json

3. Mettre à jour l'orchestrateur principal

### Q5 : Comment exporter les notes en PDF ?

**R** : Utilisez une bibliothèque de conversion HTML vers PDF :

```python
import pdfkit

# Générer le HTML
html = calculateur.generer_html(note_df)

# Convertir en PDF
pdfkit.from_string(html, 'note_3a.pdf')
```

Ou utilisez wkhtmltopdf :
```bash
wkhtmltopdf test_note_3a.html note_3a.pdf
```

### Q6 : Puis-je personnaliser le style CSS des tableaux HTML ?

**R** : Oui, modifiez la méthode `appliquer_style_css()` dans `html_generator.py` :

```python
def appliquer_style_css(self):
    return """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
        }
        th {
            background-color: #4CAF50;  /* Personnaliser la couleur */
            color: white;
            padding: 12px;
        }
        /* ... autres styles ... */
    </style>
    """
```

### Q7 : Comment gérer plusieurs sociétés avec des balances différentes ?

**R** : Créez une structure de dossiers par société :

```
balances/
├── societe_a/
│   └── balance.xlsx
├── societe_b/
│   └── balance.xlsx
└── societe_c/
    └── balance.xlsx

resultats/
├── societe_a/
│   ├── Notes_Annexes_*.xlsx
│   └── Tests/
├── societe_b/
│   └── ...
└── societe_c/
    └── ...
```

Script de traitement :
```python
import os

societes = ['societe_a', 'societe_b', 'societe_c']

for societe in societes:
    balance_path = f'balances/{societe}/balance.xlsx'
    output_dir = f'resultats/{societe}'
    
    os.makedirs(output_dir, exist_ok=True)
    
    orchestrator = CalculNotesAnnexesMain(balance_path)
    orchestrator.calculer_toutes_notes(output_dir=output_dir)
```

### Q8 : Comment automatiser le calcul quotidien des notes ?

**R** : Utilisez un planificateur de tâches :

**Windows (Task Scheduler)** :
```powershell
# Créer une tâche planifiée
$action = New-ScheduledTaskAction -Execute "python" -Argument "calcul_notes_annexes_main.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "Calcul Notes Annexes" -Action $action -Trigger $trigger
```

**Linux (cron)** :
```bash
# Ajouter au crontab
0 2 * * * cd /path/to/py_backend/Doc\ calcul\ notes\ annexes && python calcul_notes_annexes_main.py
```

**Python (APScheduler)** :
```python
from apscheduler.schedulers.blocking import BlockingScheduler

def job():
    orchestrator = CalculNotesAnnexesMain('balance.xlsx')
    orchestrator.calculer_toutes_notes()

scheduler = BlockingScheduler()
scheduler.add_job(job, 'cron', hour=2)
scheduler.start()
```

### Q9 : Comment intégrer le système avec un ERP ?

**R** : Utilisez l'API REST :

1. **Export depuis l'ERP** :
   - Exporter la balance au format Excel
   - Respecter le format des 8 colonnes

2. **Appel API** :
   ```python
   import requests
   
   # Exporter depuis l'ERP
   balance_file = erp.export_balance('2024-12-31')
   
   # Envoyer à l'API
   with open(balance_file, 'rb') as f:
       files = {'file': f}
       response = requests.post(
           'http://localhost:5000/api/calculer_notes_annexes',
           files=files
       )
   
   # Récupérer les résultats
   notes = response.json()['notes']
   
   # Importer dans l'ERP
   erp.import_notes_annexes(notes)
   ```

3. **Webhook** (optionnel) :
   ```python
   # Notifier l'ERP quand le calcul est terminé
   @app.route('/api/calculer_notes_annexes', methods=['POST'])
   def calculer_notes_annexes():
       # ... calcul ...
       
       # Notifier l'ERP
       requests.post(
           'http://erp.example.com/webhook/notes_annexes',
           json={'status': 'completed', 'notes': notes}
       )
       
       return jsonify(notes)
   ```

### Q10 : Comment sauvegarder l'historique des calculs ?

**R** : Utilisez le Trace_Manager :

```python
from Modules.trace_manager import TraceManager

trace_manager = TraceManager('3A')

# Enregistrer les calculs
trace_manager.enregistrer_calcul(...)
trace_manager.enregistrer_metadata(...)

# Sauvegarder avec timestamp
import datetime
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
trace_manager.sauvegarder_trace(f'historique/trace_note_3a_{timestamp}.json')

# Gérer l'historique (garder les 10 derniers)
trace_manager.gerer_historique(max_historique=10)
```

---

## Ressources Supplémentaires

### Documentation

- **README.md** : Vue d'ensemble du système
- **GUIDE_UTILISATION.md** : Guide d'utilisation détaillé
- **design.md** : Conception technique
- **requirements.md** : Spécifications fonctionnelles

### Logs

- **calcul_notes_annexes.log** : Log principal
- **calcul_notes_warnings.log** : Avertissements
- **calcul_notes_errors.log** : Erreurs critiques

### Fichiers de Trace

- **trace_note_XX.json** : Détail des calculs pour chaque note
- **rapport_coherence.html** : Rapport de cohérence inter-notes

### Support

Pour toute question ou problème non résolu :

1. Consulter les logs
2. Activer le mode debug
3. Tester avec une balance minimale
4. Consulter la documentation technique

---

**Dernière mise à jour** : 28 avril 2026  
**Version** : 1.0

