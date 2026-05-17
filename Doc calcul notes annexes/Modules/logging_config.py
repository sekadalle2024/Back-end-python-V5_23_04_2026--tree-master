"""
Module de configuration du système de logging pour le calcul des notes annexes SYSCOHADA.

Ce module configure trois fichiers de logs avec rotation quotidienne et compression:
- calcul_notes_annexes.log: Tous les logs (INFO et supérieur)
- calcul_notes_warnings.log: Avertissements uniquement
- calcul_notes_errors.log: Erreurs uniquement

Fonctionnalités:
- Rotation quotidienne des logs
- Rétention de 30 jours
- Compression automatique des anciens logs
- Format structuré avec timestamps
- Séparation par niveau de gravité
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class LoggingConfig:
    """Gestionnaire de configuration du système de logging."""
    
    # Noms des fichiers de logs
    MAIN_LOG_FILE = "calcul_notes_annexes.log"
    WARNINGS_LOG_FILE = "calcul_notes_warnings.log"
    ERRORS_LOG_FILE = "calcul_notes_errors.log"
    
    # Configuration de rotation
    ROTATION_WHEN = "midnight"  # Rotation quotidienne à minuit
    ROTATION_INTERVAL = 1  # Tous les jours
    BACKUP_COUNT = 30  # Conserver 30 jours d'historique
    
    # Format de logging structuré
    LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, log_directory: str = "logs"):
        """
        Initialise la configuration du logging.
        
        Args:
            log_directory: Répertoire où stocker les fichiers de logs
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        self._configured = False
        self._loggers = {}
    
    def configure(self) -> None:
        """
        Configure le système de logging avec les trois fichiers de logs.
        
        Cette méthode doit être appelée une seule fois au démarrage de l'application.
        """
        if self._configured:
            return
        
        # Configuration du logger racine
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Supprimer les handlers existants
        root_logger.handlers.clear()
        
        # Créer le formateur
        formatter = logging.Formatter(
            fmt=self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT
        )
        
        # 1. Handler pour le fichier principal (tous les logs)
        main_handler = self._create_rotating_handler(
            filename=self.MAIN_LOG_FILE,
            level=logging.INFO
        )
        main_handler.setFormatter(formatter)
        root_logger.addHandler(main_handler)
        
        # 2. Handler pour les avertissements uniquement
        warnings_handler = self._create_rotating_handler(
            filename=self.WARNINGS_LOG_FILE,
            level=logging.WARNING
        )
        warnings_handler.setFormatter(formatter)
        warnings_handler.addFilter(self._create_level_filter(logging.WARNING))
        root_logger.addHandler(warnings_handler)
        
        # 3. Handler pour les erreurs uniquement
        errors_handler = self._create_rotating_handler(
            filename=self.ERRORS_LOG_FILE,
            level=logging.ERROR
        )
        errors_handler.setFormatter(formatter)
        root_logger.addHandler(errors_handler)
        
        # 4. Handler console pour le développement (optionnel)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        self._configured = True
        
        # Log de démarrage
        logging.info("=" * 80)
        logging.info("Système de logging configuré avec succès")
        logging.info(f"Répertoire des logs: {self.log_directory.absolute()}")
        logging.info(f"Rotation: {self.ROTATION_WHEN}, Rétention: {self.BACKUP_COUNT} jours")
        logging.info("=" * 80)
    
    def _create_rotating_handler(
        self, 
        filename: str, 
        level: int
    ) -> logging.handlers.TimedRotatingFileHandler:
        """
        Crée un handler avec rotation quotidienne et compression.
        
        Args:
            filename: Nom du fichier de log
            level: Niveau de logging minimum
            
        Returns:
            Handler configuré avec rotation
        """
        filepath = self.log_directory / filename
        
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=str(filepath),
            when=self.ROTATION_WHEN,
            interval=self.ROTATION_INTERVAL,
            backupCount=self.BACKUP_COUNT,
            encoding='utf-8',
            delay=False,
            utc=False
        )
        
        handler.setLevel(level)
        
        # Activer la compression des anciens logs
        handler.namer = self._compressed_log_namer
        handler.rotator = self._compressed_log_rotator
        
        return handler
    
    @staticmethod
    def _compressed_log_namer(default_name: str) -> str:
        """
        Génère le nom du fichier de log compressé.
        
        Args:
            default_name: Nom par défaut généré par le handler
            
        Returns:
            Nom avec extension .gz
        """
        return default_name + ".gz"
    
    @staticmethod
    def _compressed_log_rotator(source: str, dest: str) -> None:
        """
        Compresse le fichier de log lors de la rotation.
        
        Args:
            source: Chemin du fichier source
            dest: Chemin du fichier destination
        """
        import gzip
        import shutil
        
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(source)
    
    @staticmethod
    def _create_level_filter(level: int):
        """
        Crée un filtre pour capturer uniquement un niveau spécifique.
        
        Args:
            level: Niveau de logging à filtrer
            
        Returns:
            Fonction de filtrage
        """
        def level_filter(record):
            return record.levelno == level
        
        return level_filter
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Récupère ou crée un logger nommé.
        
        Args:
            name: Nom du logger (généralement __name__ du module)
            
        Returns:
            Logger configuré
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        
        return self._loggers[name]
    
    def cleanup_old_logs(self, days: Optional[int] = None) -> int:
        """
        Nettoie les logs plus anciens que le nombre de jours spécifié.
        
        Args:
            days: Nombre de jours à conserver (par défaut: BACKUP_COUNT)
            
        Returns:
            Nombre de fichiers supprimés
        """
        if days is None:
            days = self.BACKUP_COUNT
        
        cutoff_time = datetime.now().timestamp() - (days * 86400)
        deleted_count = 0
        
        for log_file in self.log_directory.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    deleted_count += 1
                    logging.info(f"Log ancien supprimé: {log_file.name}")
                except Exception as e:
                    logging.error(f"Erreur lors de la suppression de {log_file.name}: {e}")
        
        return deleted_count
    
    def get_log_statistics(self) -> dict:
        """
        Récupère des statistiques sur les fichiers de logs.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {
            'total_files': 0,
            'total_size_mb': 0.0,
            'files': []
        }
        
        for log_file in sorted(self.log_directory.glob("*.log*")):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            stats['files'].append({
                'name': log_file.name,
                'size_mb': round(size_mb, 2),
                'modified': modified.strftime(self.DATE_FORMAT)
            })
            
            stats['total_files'] += 1
            stats['total_size_mb'] += size_mb
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        
        return stats


# Instance globale de configuration
_logging_config: Optional[LoggingConfig] = None


def setup_logging(log_directory: str = "logs") -> LoggingConfig:
    """
    Configure le système de logging (fonction utilitaire).
    
    Args:
        log_directory: Répertoire où stocker les logs
        
    Returns:
        Instance de LoggingConfig configurée
    """
    global _logging_config
    
    if _logging_config is None:
        _logging_config = LoggingConfig(log_directory)
        _logging_config.configure()
    
    return _logging_config


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger configuré (fonction utilitaire).
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    if _logging_config is None:
        setup_logging()
    
    return _logging_config.get_logger(name)
