"""
Module de traçabilité et audit des calculs.

Ce module gère l'enregistrement des traces de calcul pour l'audit.
"""

import json
import csv
import logging
from typing import List, Dict
from datetime import datetime
import hashlib
import os

logger = logging.getLogger(__name__)


class TraceManager:
    """Gestionnaire de traces pour l'audit."""
    
    def __init__(self, numero_note: str):
        """
        Initialise le gestionnaire de traces pour une note.
        
        Args:
            numero_note: Numéro de la note (ex: "3A")
        """
        self.numero_note = numero_note
        self.trace = {
            'note': numero_note,
            'date_generation': datetime.now().isoformat(),
            'lignes': [],
            'metadata': {}
        }
        logger.debug(f"TraceManager initialisé pour Note {numero_note}")
    
    def enregistrer_calcul(self, libelle: str, montant: float, 
                          comptes_sources: List[Dict]):
        """
        Enregistre un calcul avec ses sources.
        
        Args:
            libelle: Libellé de la ligne
            montant: Montant calculé
            comptes_sources: Liste des comptes sources avec leurs soldes
        """
        self.trace['lignes'].append({
            'libelle': libelle,
            'montant': montant,
            'comptes_sources': comptes_sources,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.debug(f"Calcul enregistré: {libelle} = {montant:.2f}")
    
    def enregistrer_metadata(self, fichier_balance: str, hash_md5: str = None):
        """
        Enregistre les métadonnées de génération.
        
        Args:
            fichier_balance: Chemin du fichier de balance
            hash_md5: Hash MD5 du fichier (calculé automatiquement si None)
        """
        if hash_md5 is None and os.path.exists(fichier_balance):
            hash_md5 = self._calculer_md5(fichier_balance)
        
        self.trace['metadata'] = {
            'fichier_balance': fichier_balance,
            'hash_md5': hash_md5,
            'date_generation': datetime.now().isoformat()
        }
        
        logger.info(f"Métadonnées enregistrées: {fichier_balance}")
    
    def _calculer_md5(self, fichier: str) -> str:
        """Calcule le hash MD5 d'un fichier."""
        hash_md5 = hashlib.md5()
        try:
            with open(fichier, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Impossible de calculer le MD5: {e}")
            return ""
    
    def sauvegarder_trace(self, fichier_sortie: str = None):
        """
        Sauvegarde la trace en JSON.
        
        Args:
            fichier_sortie: Chemin du fichier de sortie (optionnel)
        """
        if fichier_sortie is None:
            fichier_sortie = f"../Tests/trace_note_{self.numero_note}.json"
        
        try:
            with open(fichier_sortie, 'w', encoding='utf-8') as f:
                json.dump(self.trace, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Trace sauvegardée: {fichier_sortie}")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur lors de la sauvegarde de la trace: {e}")
            return False
    
    def exporter_csv(self, fichier_sortie: str = None):
        """
        Exporte la trace en CSV pour analyse Excel.
        
        Args:
            fichier_sortie: Chemin du fichier CSV (optionnel)
        """
        if fichier_sortie is None:
            fichier_sortie = f"../Tests/trace_note_{self.numero_note}.csv"
        
        try:
            with open(fichier_sortie, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # En-têtes
                writer.writerow(['Libellé', 'Montant', 'Comptes Sources', 'Timestamp'])
                
                # Données
                for ligne in self.trace['lignes']:
                    comptes_str = '; '.join([
                        f"{c.get('compte', '')}: {c.get('solde', 0):.2f}"
                        for c in ligne.get('comptes_sources', [])
                    ])
                    
                    writer.writerow([
                        ligne.get('libelle', ''),
                        ligne.get('montant', 0),
                        comptes_str,
                        ligne.get('timestamp', '')
                    ])
            
            logger.info(f"✓ Trace exportée en CSV: {fichier_sortie}")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'export CSV: {e}")
            return False
    
    def gerer_historique(self, max_historique: int = 10):
        """
        Conserve les N dernières générations.
        
        Args:
            max_historique: Nombre maximum de traces à conserver
        """
        dossier_traces = "../Tests/"
        pattern = f"trace_note_{self.numero_note}_*.json"
        
        try:
            # Lister les fichiers de trace
            fichiers = [f for f in os.listdir(dossier_traces) 
                       if f.startswith(f"trace_note_{self.numero_note}_")]
            
            # Trier par date de modification
            fichiers.sort(key=lambda x: os.path.getmtime(os.path.join(dossier_traces, x)))
            
            # Supprimer les plus anciens si nécessaire
            while len(fichiers) > max_historique:
                fichier_a_supprimer = os.path.join(dossier_traces, fichiers[0])
                os.remove(fichier_a_supprimer)
                logger.info(f"Trace ancienne supprimée: {fichiers[0]}")
                fichiers.pop(0)
            
        except Exception as e:
            logger.warning(f"Erreur lors de la gestion de l'historique: {e}")
