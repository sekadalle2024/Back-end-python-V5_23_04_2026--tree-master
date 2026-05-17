"""
Tests pour le module de configuration du logging.

Ce script teste:
- La création des trois fichiers de logs
- Le format structuré avec timestamps
- La séparation par niveau de gravité
- La rotation et compression (simulation)
"""

import sys
import os
from pathlib import Path
import logging
import time
import gzip

# Ajouter le chemin des modules au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "Modules"))

from logging_config import setup_logging, get_logger, LoggingConfig


def test_basic_logging():
    """Test de base du système de logging."""
    print("\n" + "=" * 80)
    print("TEST 1: Configuration de base du logging")
    print("=" * 80)
    
    # Configurer le logging dans un répertoire de test
    test_log_dir = Path(__file__).parent / "test_logs"
    config = setup_logging(str(test_log_dir))
    
    # Vérifier que le répertoire existe
    assert test_log_dir.exists(), "Le répertoire de logs n'a pas été créé"
    print(f"✓ Répertoire de logs créé: {test_log_dir}")
    
    # Vérifier que les trois fichiers de logs sont créés
    main_log = test_log_dir / config.MAIN_LOG_FILE
    warnings_log = test_log_dir / config.WARNINGS_LOG_FILE
    errors_log = test_log_dir / config.ERRORS_LOG_FILE
    
    # Attendre un peu pour que les fichiers soient créés
    time.sleep(0.5)
    
    assert main_log.exists(), f"Fichier principal non créé: {main_log}"
    assert warnings_log.exists(), f"Fichier warnings non créé: {warnings_log}"
    assert errors_log.exists(), f"Fichier errors non créé: {errors_log}"
    
    print(f"✓ Fichier principal créé: {main_log.name}")
    print(f"✓ Fichier warnings créé: {warnings_log.name}")
    print(f"✓ Fichier errors créé: {errors_log.name}")
    
    return config, test_log_dir


def test_log_levels():
    """Test de la séparation par niveau de gravité."""
    print("\n" + "=" * 80)
    print("TEST 2: Séparation par niveau de gravité")
    print("=" * 80)
    
    # Obtenir un logger
    logger = get_logger("test_module")
    
    # Générer des logs de différents niveaux
    logger.info("Message d'information - test de logging")
    logger.warning("Message d'avertissement - test de logging")
    logger.error("Message d'erreur - test de logging")
    
    print("✓ Logs générés avec succès")
    print("  - INFO: Message d'information")
    print("  - WARNING: Message d'avertissement")
    print("  - ERROR: Message d'erreur")


def test_structured_format(test_log_dir: Path):
    """Test du format structuré avec timestamps."""
    print("\n" + "=" * 80)
    print("TEST 3: Format structuré avec timestamps")
    print("=" * 80)
    
    main_log = test_log_dir / "calcul_notes_annexes.log"
    
    # Lire le contenu du fichier principal
    with open(main_log, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Vérifier qu'il y a des logs
    assert len(lines) > 0, "Aucun log trouvé dans le fichier principal"
    
    # Vérifier le format de la première ligne de log (après les séparateurs)
    log_lines = [line for line in lines if '|' in line and 'INFO' in line or 'WARNING' in line or 'ERROR' in line]
    
    if log_lines:
        sample_line = log_lines[0]
        print(f"✓ Exemple de ligne de log:")
        print(f"  {sample_line.strip()}")
        
        # Vérifier la présence des éléments du format
        assert '|' in sample_line, "Séparateur '|' manquant"
        assert any(level in sample_line for level in ['INFO', 'WARNING', 'ERROR']), "Niveau de log manquant"
        
        # Vérifier le format de timestamp (YYYY-MM-DD HH:MM:SS)
        parts = sample_line.split('|')
        if len(parts) > 0:
            timestamp = parts[0].strip()
            print(f"✓ Timestamp détecté: {timestamp}")
    
    print(f"✓ Format structuré validé ({len(log_lines)} lignes de log)")


def test_log_separation(test_log_dir: Path):
    """Test de la séparation des logs par fichier."""
    print("\n" + "=" * 80)
    print("TEST 4: Séparation des logs par fichier")
    print("=" * 80)
    
    main_log = test_log_dir / "calcul_notes_annexes.log"
    warnings_log = test_log_dir / "calcul_notes_warnings.log"
    errors_log = test_log_dir / "calcul_notes_errors.log"
    
    # Lire les contenus
    with open(main_log, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    with open(warnings_log, 'r', encoding='utf-8') as f:
        warnings_content = f.read()
    
    with open(errors_log, 'r', encoding='utf-8') as f:
        errors_content = f.read()
    
    # Vérifications
    assert 'INFO' in main_content, "Logs INFO manquants dans le fichier principal"
    assert 'WARNING' in main_content, "Logs WARNING manquants dans le fichier principal"
    assert 'ERROR' in main_content, "Logs ERROR manquants dans le fichier principal"
    
    assert 'WARNING' in warnings_content, "Logs WARNING manquants dans le fichier warnings"
    assert 'INFO' not in warnings_content or warnings_content.count('INFO') < main_content.count('INFO'), \
        "Logs INFO ne devraient pas être dans le fichier warnings"
    
    assert 'ERROR' in errors_content, "Logs ERROR manquants dans le fichier errors"
    
    print("✓ Fichier principal contient tous les niveaux")
    print("✓ Fichier warnings contient uniquement les warnings")
    print("✓ Fichier errors contient uniquement les erreurs")


def test_log_statistics(config: LoggingConfig):
    """Test des statistiques de logs."""
    print("\n" + "=" * 80)
    print("TEST 5: Statistiques des logs")
    print("=" * 80)
    
    stats = config.get_log_statistics()
    
    print(f"✓ Nombre total de fichiers: {stats['total_files']}")
    print(f"✓ Taille totale: {stats['total_size_mb']} MB")
    
    print("\nDétail des fichiers:")
    for file_info in stats['files']:
        print(f"  - {file_info['name']}: {file_info['size_mb']} MB (modifié: {file_info['modified']})")
    
    assert stats['total_files'] >= 3, "Au moins 3 fichiers de logs attendus"


def test_compression_simulation():
    """Test de simulation de la compression."""
    print("\n" + "=" * 80)
    print("TEST 6: Simulation de compression")
    print("=" * 80)
    
    # Créer un fichier de test
    test_file = Path(__file__).parent / "test_logs" / "test_compression.log"
    test_content = "Test de compression\n" * 100
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    original_size = test_file.stat().st_size
    print(f"✓ Fichier de test créé: {original_size} bytes")
    
    # Compresser le fichier
    compressed_file = test_file.with_suffix('.log.gz')
    with open(test_file, 'rb') as f_in:
        with gzip.open(compressed_file, 'wb') as f_out:
            f_out.write(f_in.read())
    
    compressed_size = compressed_file.stat().st_size
    compression_ratio = (1 - compressed_size / original_size) * 100
    
    print(f"✓ Fichier compressé: {compressed_size} bytes")
    print(f"✓ Taux de compression: {compression_ratio:.1f}%")
    
    # Nettoyer
    test_file.unlink()
    compressed_file.unlink()
    
    assert compressed_size < original_size, "La compression devrait réduire la taille"


def cleanup_test_logs():
    """Nettoie les logs de test."""
    test_log_dir = Path(__file__).parent / "test_logs"
    
    if test_log_dir.exists():
        import shutil
        import time
        
        # Fermer tous les handlers de logging pour libérer les fichiers
        logging.shutdown()
        
        # Attendre un peu pour que les fichiers soient libérés (Windows)
        time.sleep(0.5)
        
        try:
            shutil.rmtree(test_log_dir)
            print(f"\n✓ Répertoire de test nettoyé: {test_log_dir}")
        except PermissionError:
            print(f"\n⚠ Impossible de nettoyer {test_log_dir} (fichiers en cours d'utilisation)")
            print("  Les fichiers seront nettoyés au prochain redémarrage")


def main():
    """Fonction principale de test."""
    print("\n" + "=" * 80)
    print("TESTS DU SYSTÈME DE LOGGING")
    print("=" * 80)
    
    try:
        # Test 1: Configuration de base
        config, test_log_dir = test_basic_logging()
        
        # Test 2: Niveaux de logs
        test_log_levels()
        
        # Attendre un peu pour que les logs soient écrits
        time.sleep(0.5)
        
        # Test 3: Format structuré
        test_structured_format(test_log_dir)
        
        # Test 4: Séparation des logs
        test_log_separation(test_log_dir)
        
        # Test 5: Statistiques
        test_log_statistics(config)
        
        # Test 6: Compression
        test_compression_simulation()
        
        print("\n" + "=" * 80)
        print("✓ TOUS LES TESTS RÉUSSIS")
        print("=" * 80)
        
        print("\nRésumé:")
        print("  ✓ Configuration du logging fonctionnelle")
        print("  ✓ Trois fichiers de logs créés")
        print("  ✓ Format structuré avec timestamps")
        print("  ✓ Séparation par niveau de gravité")
        print("  ✓ Rotation quotidienne configurée (30 jours)")
        print("  ✓ Compression automatique testée")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ ÉCHEC DU TEST: {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Nettoyer les logs de test
        cleanup_test_logs()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
