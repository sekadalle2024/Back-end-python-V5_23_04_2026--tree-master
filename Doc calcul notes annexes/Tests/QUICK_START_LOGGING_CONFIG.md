# Quick Start: Configuration du Logging

## Vue d'ensemble

Le système de logging pour le calcul des notes annexes SYSCOHADA est maintenant configuré avec:

- **3 fichiers de logs** séparés par niveau de gravité
- **Rotation quotidienne** à minuit
- **Rétention de 30 jours** d'historique
- **Compression automatique** des anciens logs (.gz)
- **Format structuré** avec timestamps

## Fichiers de logs

### 1. calcul_notes_annexes.log
Contient **tous les logs** (INFO, WARNING, ERROR)
- Utilisé pour le suivi général de l'application
- Permet de voir l'historique complet des opérations

### 2. calcul_notes_warnings.log
Contient **uniquement les avertissements** (WARNING)
- Utilisé pour identifier les situations anormales non critiques
- Exemples: soldes incohérents, VNC négatives, comptes manquants

### 3. calcul_notes_errors.log
Contient **uniquement les erreurs** (ERROR)
- Utilisé pour identifier les problèmes critiques
- Exemples: fichiers manquants, erreurs de calcul, exceptions

## Utilisation dans le code

### Configuration initiale (une seule fois au démarrage)

```python
from Modules.logging_config import setup_logging

# Configurer le logging au démarrage de l'application
setup_logging(log_directory="logs")
```

### Utilisation dans un module

```python
from Modules.logging_config import get_logger

# Obtenir un logger pour le module
logger = get_logger(__name__)

# Utiliser le logger
logger.info("Chargement des balances...")
logger.warning("Compte 211 manquant dans la balance N-2")
logger.error("Impossible de lire le fichier Excel")
```

### Exemple complet

```python
from Modules.logging_config import setup_logging, get_logger

# Configuration au démarrage
setup_logging()

# Dans votre module
logger = get_logger(__name__)

def calculer_note():
    logger.info("Début du calcul de la note 3A")
    
    try:
        # Votre code ici
        logger.info("Note 3A calculée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du calcul: {e}")
        raise
```

## Format des logs

Chaque ligne de log suit ce format structuré:

```
2026-04-28 14:30:15 | INFO     | balance_reader | charger_balances:45 | Chargement de la balance N
2026-04-28 14:30:16 | WARNING  | account_extractor | extraire_solde:78 | Compte 211 non trouvé
2026-04-28 14:30:17 | ERROR    | balance_reader | charger_balances:52 | Fichier Excel introuvable
```

**Éléments du format:**
- `2026-04-28 14:30:15` - Timestamp (YYYY-MM-DD HH:MM:SS)
- `INFO` - Niveau de log (INFO, WARNING, ERROR)
- `balance_reader` - Nom du module
- `charger_balances:45` - Fonction et numéro de ligne
- `Message` - Message descriptif

## Rotation et compression

### Rotation quotidienne
- Les logs sont automatiquement archivés chaque jour à minuit
- Format: `calcul_notes_annexes.log.2026-04-27`

### Compression automatique
- Les logs archivés sont compressés en `.gz`
- Format: `calcul_notes_annexes.log.2026-04-27.gz`
- Économie d'espace: ~70-90% de réduction

### Rétention
- Les logs de plus de 30 jours sont automatiquement supprimés
- Configurable via `BACKUP_COUNT` dans `LoggingConfig`

## Statistiques des logs

```python
from Modules.logging_config import setup_logging

config = setup_logging()
stats = config.get_log_statistics()

print(f"Nombre de fichiers: {stats['total_files']}")
print(f"Taille totale: {stats['total_size_mb']} MB")

for file_info in stats['files']:
    print(f"{file_info['name']}: {file_info['size_mb']} MB")
```

## Nettoyage manuel

```python
from Modules.logging_config import setup_logging

config = setup_logging()

# Supprimer les logs de plus de 15 jours
deleted = config.cleanup_old_logs(days=15)
print(f"{deleted} fichiers supprimés")
```

## Tests

### Exécuter les tests

```bash
# Windows PowerShell
.\test-logging-config.ps1

# Python direct
python "py_backend/Doc calcul notes annexes/Tests/test_logging_config.py"
```

### Tests inclus

1. ✓ Configuration de base du logging
2. ✓ Séparation par niveau de gravité
3. ✓ Format structuré avec timestamps
4. ✓ Séparation des logs par fichier
5. ✓ Statistiques des logs
6. ✓ Simulation de compression

## Bonnes pratiques

### 1. Niveaux de log appropriés

```python
# INFO: Opérations normales
logger.info("Calcul de la note 3A démarré")
logger.info("Balance N chargée: 1250 comptes")

# WARNING: Situations anormales non critiques
logger.warning("Compte 211 manquant, utilisation de 0.0")
logger.warning("VNC négative détectée: -15000.00")

# ERROR: Erreurs critiques
logger.error("Impossible de lire le fichier Excel")
logger.error("Format de balance invalide")
```

### 2. Messages descriptifs

```python
# ✗ Mauvais
logger.error("Erreur")

# ✓ Bon
logger.error("Impossible de charger la balance N: fichier introuvable")
```

### 3. Contexte dans les messages

```python
# ✓ Inclure les valeurs importantes
logger.warning(f"Solde incohérent pour le compte {numero_compte}: "
               f"attendu {solde_attendu}, trouvé {solde_reel}")
```

### 4. Exceptions avec traceback

```python
try:
    # Code qui peut échouer
    pass
except Exception as e:
    logger.error(f"Erreur lors du calcul: {e}", exc_info=True)
    # exc_info=True ajoute le traceback complet
```

## Dépannage

### Les logs ne sont pas créés

Vérifier que:
1. Le répertoire `logs/` existe et est accessible en écriture
2. `setup_logging()` a été appelé au démarrage
3. Aucune erreur de permission

### Les logs ne sont pas séparés correctement

Vérifier que:
1. Les niveaux de log sont corrects (INFO, WARNING, ERROR)
2. La configuration n'a pas été modifiée
3. Les handlers sont bien configurés

### La compression ne fonctionne pas

Vérifier que:
1. Le module `gzip` est disponible (inclus dans Python standard)
2. Les permissions d'écriture sont correctes
3. L'espace disque est suffisant

## Configuration avancée

### Changer le répertoire des logs

```python
setup_logging(log_directory="/var/log/calcul_notes")
```

### Modifier la rétention

```python
from Modules.logging_config import LoggingConfig

config = LoggingConfig()
config.BACKUP_COUNT = 60  # 60 jours au lieu de 30
config.configure()
```

### Désactiver la console

Modifier `logging_config.py` et commenter la section du console handler.

## Validation

✓ Task 28.1 complétée avec succès:
- [x] Trois fichiers de logs configurés
- [x] Rotation quotidienne à minuit
- [x] Rétention de 30 jours
- [x] Compression automatique (.gz)
- [x] Format structuré avec timestamps
- [x] Tests de validation créés
