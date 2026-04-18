"""
Orchestrateur principal pour le calcul des 33 notes annexes SYSCOHADA révisé.

Ce script coordonne le calcul de toutes les notes annexes et gère la validation de cohérence.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Dict
import pandas as pd

# Ajouter le dossier Modules au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Modules'))

from balance_reader import BalanceReader
from coherence_validator import CoherenceValidator
from excel_exporter import ExcelExporter


def configurer_logging():
    """Configure le système de logging avec rotation quotidienne."""
    # Créer le dossier Logs s'il n'existe pas
    logs_dir = os.path.join(os.path.dirname(__file__), 'Logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configuration du logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Format des logs
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour le fichier principal (INFO et plus)
    main_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(logs_dir, 'calcul_notes_annexes.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(formatter)
    logger.addHandler(main_handler)
    
    # Handler pour les warnings uniquement
    warning_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(logs_dir, 'calcul_notes_warnings.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)
    logger.addHandler(warning_handler)
    
    # Handler pour les erreurs uniquement
    error_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(logs_dir, 'calcul_notes_errors.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logging.info("=" * 80)
    logging.info("Système de logging configuré avec succès")
    logging.info(f"Logs sauvegardés dans: {logs_dir}")
    logging.info("=" * 80)


class CalculNotesAnnexesMain:
    """Orchestrateur principal pour le calcul des notes annexes."""
    
    def __init__(self, fichier_balance: str):
        """
        Initialise l'orchestrateur.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel de balances
        """
        self.fichier_balance = fichier_balance
        self.balance_reader = BalanceReader(fichier_balance)
        self.balances = None
        self.notes_calculees = {}
        
        logging.info(f"Orchestrateur initialisé avec: {fichier_balance}")
    
    def charger_balances(self) -> bool:
        """
        Charge les balances en mémoire (une seule fois).
        
        Returns:
            True si le chargement a réussi
        """
        try:
            logging.info("Chargement des balances...")
            self.balances = self.balance_reader.charger_balances()
            logging.info("✓ Balances chargées avec succès")
            return True
        except Exception as e:
            logging.error(f"✗ Erreur lors du chargement des balances: {e}")
            return False
    
    def calculer_toutes_notes(self) -> Dict[str, pd.DataFrame]:
        """
        Calcule toutes les 33 notes annexes.
        
        Returns:
            Dict mappant nom_note -> DataFrame
        """
        if self.balances is None:
            if not self.charger_balances():
                return {}
        
        logging.info("=" * 80)
        logging.info("DÉBUT DU CALCUL DES 33 NOTES ANNEXES")
        logging.info("=" * 80)
        
        debut = datetime.now()
        
        # TODO: Implémenter le calcul de chaque note
        # Pour l'instant, structure de base
        
        # Exemple: Calculer la Note 3A (si le script existe)
        try:
            from Scripts.calculer_note_3a import CalculateurNote3A
            calc_3a = CalculateurNote3A(self.fichier_balance)
            if calc_3a.charger_balances():
                df_3a = calc_3a.generer_note()
                self.notes_calculees['Note_3A'] = df_3a
                logging.info("✓ Note 3A calculée")
        except ImportError:
            logging.warning("Script calculer_note_3a.py non trouvé")
        except Exception as e:
            logging.error(f"✗ Erreur lors du calcul de la Note 3A: {e}")
        
        fin = datetime.now()
        duree = (fin - debut).total_seconds()
        
        logging.info("=" * 80)
        logging.info(f"CALCUL TERMINÉ - Durée: {duree:.2f}s")
        logging.info(f"Notes calculées: {len(self.notes_calculees)}/33")
        logging.info("=" * 80)
        
        return self.notes_calculees
    
    def valider_coherence(self) -> float:
        """
        Valide la cohérence inter-notes.
        
        Returns:
            Taux de cohérence global (0-100)
        """
        if not self.notes_calculees:
            logging.warning("Aucune note calculée pour la validation")
            return 0.0
        
        logging.info("Validation de la cohérence inter-notes...")
        validator = CoherenceValidator(self.notes_calculees)
        taux = validator.calculer_taux_coherence()
        
        # Générer le rapport
        rapport_html = validator.generer_rapport_coherence()
        fichier_rapport = os.path.join(
            os.path.dirname(__file__),
            'Tests',
            'rapport_coherence.html'
        )
        
        with open(fichier_rapport, 'w', encoding='utf-8') as f:
            f.write(rapport_html)
        
        logging.info(f"✓ Taux de cohérence: {taux:.1f}%")
        logging.info(f"✓ Rapport sauvegardé: {fichier_rapport}")
        
        return taux
    
    def exporter_excel(self, fichier_sortie: str = None) -> bool:
        """
        Exporte toutes les notes vers Excel.
        
        Args:
            fichier_sortie: Nom du fichier Excel (optionnel)
            
        Returns:
            True si l'export a réussi
        """
        if not self.notes_calculees:
            logging.warning("Aucune note à exporter")
            return False
        
        logging.info("Export des notes vers Excel...")
        exporter = ExcelExporter(fichier_sortie)
        exporter.exporter_toutes_notes(self.notes_calculees)
        
        return exporter.sauvegarder()


def main():
    """Point d'entrée principal."""
    # Configurer le logging
    configurer_logging()
    
    # Chemin vers le fichier de balance
    fichier_balance = os.path.join(
        os.path.dirname(__file__),
        '..',
        'P000 -BALANCE DEMO N_N-1_N-2.xls'
    )
    
    # Créer l'orchestrateur
    orchestrateur = CalculNotesAnnexesMain(fichier_balance)
    
    # Calculer toutes les notes
    notes = orchestrateur.calculer_toutes_notes()
    
    if notes:
        # Valider la cohérence
        taux_coherence = orchestrateur.valider_coherence()
        
        # Exporter vers Excel
        orchestrateur.exporter_excel()
        
        # Résumé final
        logging.info("=" * 80)
        logging.info("RÉSUMÉ FINAL")
        logging.info(f"Notes calculées: {len(notes)}/33")
        logging.info(f"Taux de cohérence: {taux_coherence:.1f}%")
        logging.info("=" * 80)
    else:
        logging.error("Aucune note n'a pu être calculée")


if __name__ == "__main__":
    main()
