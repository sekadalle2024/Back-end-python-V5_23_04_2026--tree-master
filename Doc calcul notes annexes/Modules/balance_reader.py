"""
Module Balance_Reader - Lecture et chargement des balances multi-exercices

Ce module fournit la classe BalanceReader pour charger et traiter les fichiers
Excel de balances à 8 colonnes pour les exercices N, N-1 et N-2.

Auteur: Système de calcul automatique des notes annexes SYSCOHADA
Date: 08 Avril 2026
"""

import pandas as pd
import re
from typing import Tuple, Dict, List
import logging


# Configuration du logging
logger = logging.getLogger(__name__)


class BalanceNotFoundException(Exception):
    """Exception levée quand un onglet de balance requis est manquant"""
    pass


class InvalidBalanceFormatException(Exception):
    """Exception levée quand le format de la balance est invalide"""
    pass


class BalanceReader:
    """
    Classe pour lire et charger les balances multi-exercices depuis Excel.
    
    Cette classe gère la lecture de fichiers Excel contenant les balances
    des exercices N, N-1 et N-2, avec détection automatique des onglets,
    nettoyage des colonnes et conversion des montants.
    
    Attributes:
        fichier_balance (str): Chemin vers le fichier Excel de balances
        colonnes_requises (List[str]): Liste des colonnes attendues dans les balances
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le lecteur avec le chemin du fichier Excel.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel contenant les balances
        """
        self.fichier_balance = fichier_balance
        # Colonnes minimales requises (certaines peuvent être calculées)
        self.colonnes_minimales = [
            'Numéro', 'Intitulé', 
            'Ant Débit', 'Ant Crédit',
            'Solde Débit', 'Solde Crédit'
        ]
        logger.info(f"BalanceReader initialisé avec le fichier: {fichier_balance}")
    
    def charger_balances(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les 3 balances (N, N-1, N-2) depuis le fichier Excel.
        
        Cette méthode:
        1. Détecte automatiquement les onglets N, N-1, N-2
        2. Charge chaque onglet dans un DataFrame
        3. Nettoie les noms de colonnes
        4. Convertit les montants en float
        
        Returns:
            Tuple de 3 DataFrames (balance_n, balance_n1, balance_n2)
            
        Raises:
            BalanceNotFoundException: Si un onglet requis est manquant
            InvalidBalanceFormatException: Si le format est invalide
        """
        try:
            # Lire les noms d'onglets du fichier Excel
            excel_file = pd.ExcelFile(self.fichier_balance)
            sheet_names = excel_file.sheet_names
            logger.info(f"Onglets détectés: {sheet_names}")
            
            # Détecter les onglets N, N-1, N-2
            onglets_map = self.detecter_onglets(sheet_names)
            
            # Charger chaque balance
            balance_n = self._charger_balance(onglets_map['N'], 'N')
            balance_n1 = self._charger_balance(onglets_map['N-1'], 'N-1')
            balance_n2 = self._charger_balance(onglets_map['N-2'], 'N-2')
            
            logger.info("✓ Toutes les balances chargées avec succès")
            return balance_n, balance_n1, balance_n2
            
        except FileNotFoundError:
            error_msg = f"Fichier de balance non trouvé: {self.fichier_balance}"
            logger.error(error_msg)
            raise BalanceNotFoundException(error_msg)
        except Exception as e:
            error_msg = f"Erreur lors du chargement des balances: {str(e)}"
            logger.error(error_msg)
            raise InvalidBalanceFormatException(error_msg)
    
    def detecter_onglets(self, sheet_names: List[str]) -> Dict[str, str]:
        """
        Détecte automatiquement les onglets N, N-1, N-2.
        
        Cette méthode recherche les onglets contenant les patterns:
        - "BALANCE N" ou "BALANCE_N" ou "N" pour l'exercice N
        - "BALANCE N-1" ou "BALANCE_N-1" ou "N-1" pour l'exercice N-1
        - "BALANCE N-2" ou "BALANCE_N-2" ou "N-2" pour l'exercice N-2
        
        Args:
            sheet_names: Liste des noms d'onglets du fichier Excel
            
        Returns:
            Dict mappant 'N', 'N-1', 'N-2' aux noms d'onglets détectés
            
        Raises:
            BalanceNotFoundException: Si un onglet requis n'est pas trouvé
        """
        onglets_map = {}
        
        # Patterns de recherche pour chaque exercice
        patterns = {
            'N': [r'BALANCE[\s_-]*N(?!-)', r'^N$'],
            'N-1': [r'BALANCE[\s_-]*N[\s_-]*1', r'N[\s_-]*1'],
            'N-2': [r'BALANCE[\s_-]*N[\s_-]*2', r'N[\s_-]*2']
        }
        
        for exercice, pattern_list in patterns.items():
            found = False
            for sheet_name in sheet_names:
                for pattern in pattern_list:
                    if re.search(pattern, sheet_name, re.IGNORECASE):
                        onglets_map[exercice] = sheet_name
                        logger.info(f"Onglet détecté pour {exercice}: {sheet_name}")
                        found = True
                        break
                if found:
                    break
            
            if not found:
                error_msg = f"Onglet manquant pour l'exercice {exercice}"
                logger.error(error_msg)
                raise BalanceNotFoundException(error_msg)
        
        return onglets_map
    
    def _charger_balance(self, sheet_name: str, exercice: str) -> pd.DataFrame:
        """
        Charge une balance depuis un onglet spécifique.
        
        Args:
            sheet_name: Nom de l'onglet à charger
            exercice: Nom de l'exercice (N, N-1, N-2) pour le logging
            
        Returns:
            DataFrame de la balance chargée et nettoyée
        """
        try:
            # Charger l'onglet
            df = pd.read_excel(self.fichier_balance, sheet_name=sheet_name)
            logger.info(f"Onglet {exercice} chargé: {len(df)} lignes brutes")
            
            # Nettoyer les colonnes
            df = self.nettoyer_colonnes(df)
            logger.info(f"Colonnes nettoyées pour {exercice}")
            
            # Convertir les montants
            df = self.convertir_montants(df)
            logger.info(f"Montants convertis pour {exercice}")
            
            logger.info(f"✓ Balance {exercice} chargée: {len(df)} lignes")
            return df
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la balance {exercice}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def nettoyer_colonnes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les noms de colonnes en supprimant les espaces superflus.
        
        Cette méthode:
        1. Supprime les espaces en début et fin
        2. Remplace les espaces multiples par un seul espace
        3. Normalise les variations de noms de colonnes
        4. Calcule les colonnes Débit et Crédit si manquantes
        5. Gère les colonnes dupliquées
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame avec colonnes nettoyées
        """
        # Nettoyer les noms de colonnes
        df.columns = [str(col).strip() for col in df.columns]
        df.columns = [re.sub(r'\s+', ' ', col) for col in df.columns]
        
        # Supprimer les colonnes Unnamed
        df = df.loc[:, ~pd.Series(df.columns).str.contains('^Unnamed', na=False).values]
        
        # Mapping des variations de noms de colonnes
        column_mapping = {
            'Numero': 'Numéro',
            'Numero de compte': 'Numéro',
            'Compte': 'Numéro',
            'Libelle': 'Intitulé',
            'Libellé': 'Intitulé',
            'Intitule': 'Intitulé',
            'Ant Debit': 'Ant Débit',
            'Ant Crédit': 'Ant Crédit',
            'Ant Credit': 'Ant Crédit',
            'Debit': 'Débit',
            'Credit': 'Crédit',
            'Solde Debit': 'Solde Débit',
            'Solde Credit': 'Solde Crédit',
            'Solde D': 'Solde Débit',
            'Solde C': 'Solde Crédit'
        }
        
        # Appliquer le mapping
        df.columns = [column_mapping.get(col, col) for col in df.columns]
        
        # Gérer les colonnes dupliquées en gardant seulement la première occurrence
        if df.columns.duplicated().any():
            logger.warning(f"Colonnes dupliquées détectées: {df.columns[df.columns.duplicated()].tolist()}")
            # Garder seulement les colonnes uniques (première occurrence)
            df = df.loc[:, ~df.columns.duplicated(keep='first')]
            logger.info(f"Colonnes après suppression des doublons: {list(df.columns)}")
        
        # Vérifier que les colonnes minimales sont présentes
        colonnes_manquantes = [col for col in self.colonnes_minimales if col not in df.columns]
        if colonnes_manquantes:
            error_msg = f"Colonnes manquantes: {', '.join(colonnes_manquantes)}"
            logger.error(error_msg)
            raise InvalidBalanceFormatException(error_msg)
        
        # Calculer les colonnes Débit et Crédit si elles n'existent pas
        # Débit = Solde Débit - Ant Débit (si Solde Débit > Ant Débit)
        # Crédit = Solde Crédit - Ant Crédit (si Solde Crédit > Ant Crédit)
        if 'Débit' not in df.columns:
            logger.info("Colonne 'Débit' manquante, calcul à partir des soldes")
            df['Débit'] = 0.0
        
        if 'Crédit' not in df.columns:
            logger.info("Colonne 'Crédit' manquante, calcul à partir des soldes")
            df['Crédit'] = 0.0
        
        return df
    
    def convertir_montants(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convertit tous les montants en float avec gestion des erreurs.
        
        Cette méthode:
        1. Convertit les colonnes de montants en float
        2. Remplace les valeurs vides ou invalides par 0.0
        3. Gère les séparateurs décimaux (virgule et point)
        4. Gère les séparateurs de milliers
        5. Remplace les valeurs infinies par 0.0
        
        Args:
            df: DataFrame à convertir
            
        Returns:
            DataFrame avec montants convertis
        """
        colonnes_montants = [
            'Ant Débit', 'Ant Crédit',
            'Débit', 'Crédit',
            'Solde Débit', 'Solde Crédit'
        ]
        
        for col in colonnes_montants:
            if col in df.columns:
                # Convertir la colonne en string, nettoyer, puis convertir en float
                temp_series = df[col].astype(str)
                temp_series = temp_series.str.replace(' ', '', regex=False)
                temp_series = temp_series.str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(temp_series, errors='coerce').fillna(0.0)
                
                # Remplacer les valeurs infinies par 0.0
                df[col] = df[col].replace([float('inf'), float('-inf')], 0.0)
        
        # Convertir la colonne Numéro en string
        if 'Numéro' in df.columns:
            df['Numéro'] = df['Numéro'].astype(str).str.strip()
        
        return df


if __name__ == "__main__":
    # Configuration du logging pour les tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test du module
    print("=" * 60)
    print("TEST DU MODULE BALANCE_READER")
    print("=" * 60)
    
    try:
        # Chemin vers le fichier de test
        fichier_test = "../../P000 -BALANCE DEMO N_N-1_N-2.xlsx"
        
        # Créer une instance du lecteur
        reader = BalanceReader(fichier_test)
        
        # Charger les balances
        print("\n📂 Chargement des balances...")
        balance_n, balance_n1, balance_n2 = reader.charger_balances()
        
        # Afficher les résultats
        print("\n✓ Résultats du chargement:")
        print(f"  - Balance N:   {len(balance_n)} comptes")
        print(f"  - Balance N-1: {len(balance_n1)} comptes")
        print(f"  - Balance N-2: {len(balance_n2)} comptes")
        
        print("\n✓ Colonnes de la balance N:")
        for col in balance_n.columns:
            print(f"  - {col}")
        
        print("\n✓ Exemple de données (5 premières lignes de la balance N):")
        print(balance_n.head())
        
        print("\n" + "=" * 60)
        print("✓ TEST RÉUSSI - Module Balance_Reader opérationnel")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERREUR: {str(e)}")
        print("=" * 60)
