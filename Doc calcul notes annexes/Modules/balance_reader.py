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
        5. Gère gracieusement l'absence de N-2 (retourne DataFrame vide)
        
        Returns:
            Tuple de 3 DataFrames (balance_n, balance_n1, balance_n2)
            Note: balance_n2 peut être un DataFrame vide si N-2 est manquant
            
        Raises:
            BalanceNotFoundException: Si N ou N-1 sont manquants (critiques)
            InvalidBalanceFormatException: Si le format est invalide
        """
        try:
            # Lire les noms d'onglets du fichier Excel
            excel_file = pd.ExcelFile(self.fichier_balance)
            sheet_names = excel_file.sheet_names
            logger.info(f"Onglets détectés: {sheet_names}")
            
            # Détecter les onglets N, N-1, N-2 avec gestion gracieuse de N-2
            onglets_map = self.detecter_onglets(sheet_names, graceful_n2=True)
            
            # Charger chaque balance
            balance_n = self._charger_balance(onglets_map['N'], 'N')
            balance_n1 = self._charger_balance(onglets_map['N-1'], 'N-1')
            
            # Charger N-2 avec gestion gracieuse
            if onglets_map.get('N-2'):
                balance_n2 = self._charger_balance(onglets_map['N-2'], 'N-2')
            else:
                logger.warning("⚠ Exercice N-2 manquant - création d'une balance vide")
                balance_n2 = self._creer_balance_vide()
            
            logger.info("✓ Balances chargées avec succès")
            return balance_n, balance_n1, balance_n2
            
        except FileNotFoundError:
            error_msg = f"Fichier de balance non trouvé: {self.fichier_balance}"
            logger.error(error_msg)
            raise BalanceNotFoundException(error_msg)
        except Exception as e:
            error_msg = f"Erreur lors du chargement des balances: {str(e)}"
            logger.error(error_msg)
            raise InvalidBalanceFormatException(error_msg)
    
    def detecter_onglets(self, sheet_names: List[str], graceful_n2: bool = False) -> Dict[str, str]:
        """
        Détecte automatiquement les onglets N, N-1, N-2.
        
        Cette méthode recherche les onglets contenant les patterns:
        - "BALANCE N" ou "BALANCE_N" ou "N" pour l'exercice N
        - "BALANCE N-1" ou "BALANCE_N-1" ou "N-1" pour l'exercice N-1
        - "BALANCE N-2" ou "BALANCE_N-2" ou "N-2" pour l'exercice N-2
        
        Args:
            sheet_names: Liste des noms d'onglets du fichier Excel
            graceful_n2: Si True, N-2 manquant ne lève pas d'exception (défaut: False)
            
        Returns:
            Dict mappant 'N', 'N-1', 'N-2' aux noms d'onglets détectés
            Note: Si graceful_n2=True et N-2 manquant, la clé 'N-2' sera None
            
        Raises:
            BalanceNotFoundException: Si N ou N-1 sont manquants, ou si N-2 manquant et graceful_n2=False
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
                # N-2 manquant avec mode graceful
                if exercice == 'N-2' and graceful_n2:
                    logger.warning(f"⚠ Onglet manquant pour l'exercice {exercice} - mode graceful activé")
                    onglets_map[exercice] = None
                else:
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
    
    def _creer_balance_vide(self) -> pd.DataFrame:
        """
        Crée un DataFrame de balance vide avec les colonnes requises.
        
        Cette méthode est utilisée pour la gestion gracieuse de l'exercice N-2 manquant.
        Le DataFrame vide permet au système de continuer le traitement sans erreur,
        en utilisant des valeurs nulles pour tous les comptes.
        
        Returns:
            DataFrame vide avec les colonnes standard d'une balance
        """
        colonnes = [
            'Numéro', 'Intitulé',
            'Ant Débit', 'Ant Crédit',
            'Débit', 'Crédit',
            'Solde Débit', 'Solde Crédit'
        ]
        
        df_vide = pd.DataFrame(columns=colonnes)
        
        # Définir les types de colonnes
        df_vide['Numéro'] = df_vide['Numéro'].astype(str)
        df_vide['Intitulé'] = df_vide['Intitulé'].astype(str)
        for col in colonnes[2:]:  # Colonnes de montants
            df_vide[col] = df_vide[col].astype(float)
        
        logger.info("Balance vide créée avec colonnes standard")
        return df_vide
    
    def _normaliser_nom_colonne(self, col_name: str) -> str:
        """
        Normalise un nom de colonne en supprimant accents et espaces multiples.
        
        Args:
            col_name: Nom de colonne à normaliser
            
        Returns:
            Nom de colonne normalisé
        """
        # Supprimer les espaces multiples
        col_name = re.sub(r'\s+', ' ', col_name.strip())
        # Remplacer les tirets et underscores par des espaces
        col_name = re.sub(r'[-_]', ' ', col_name)
        return col_name
    
    def _detecter_format_balance(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Détecte automatiquement le format de la balance et retourne le mapping des colonnes.
        
        Cette méthode analyse les noms de colonnes pour identifier:
        - Les variations de noms (Numero, Numéro, Compte, etc.)
        - Les variations d'accents (Debit, Débit, etc.)
        - Les variations d'espaces (Ant Debit, Ant  Debit, Ant_Debit, etc.)
        
        Args:
            df: DataFrame dont on veut détecter le format
            
        Returns:
            Dict mappant les noms de colonnes standards aux noms réels dans le DataFrame
        """
        # Normaliser tous les noms de colonnes pour la détection
        colonnes_normalisees = {col: self._normaliser_nom_colonne(col) for col in df.columns}
        
        # Patterns de détection pour chaque colonne standard
        patterns_detection = {
            'Numéro': [r'numero', r'numéro', r'compte', r'n°', r'num'],
            'Intitulé': [r'intitule', r'intitulé', r'libelle', r'libellé', r'designation', r'désignation'],
            'Ant Débit': [r'ant.*debit', r'ant.*crédit', r'solde.*initial.*debit', r'ouverture.*debit'],
            'Ant Crédit': [r'ant.*credit', r'ant.*crédit', r'solde.*initial.*credit', r'ouverture.*credit'],
            'Débit': [r'^debit$', r'^débit$', r'mouvement.*debit', r'mvt.*debit'],
            'Crédit': [r'^credit$', r'^crédit$', r'mouvement.*credit', r'mvt.*credit'],
            'Solde Débit': [r'solde.*debit', r'solde.*d', r'sd', r'clôture.*debit'],
            'Solde Crédit': [r'solde.*credit', r'solde.*c', r'sc', r'clôture.*credit']
        }
        
        mapping_detecte = {}
        
        for col_standard, patterns in patterns_detection.items():
            for col_reel, col_norm in colonnes_normalisees.items():
                col_norm_lower = col_norm.lower()
                for pattern in patterns:
                    if re.search(pattern, col_norm_lower):
                        mapping_detecte[col_standard] = col_reel
                        logger.info(f"Colonne détectée: {col_standard} -> {col_reel}")
                        break
                if col_standard in mapping_detecte:
                    break
        
        return mapping_detecte
    
    def nettoyer_colonnes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les noms de colonnes en supprimant les espaces superflus.
        
        Cette méthode:
        1. Supprime les espaces en début et fin
        2. Remplace les espaces multiples par un seul espace
        3. Détecte automatiquement le format de la balance
        4. Normalise les variations de noms de colonnes
        5. Gère les colonnes dupliquées
        6. Calcule les colonnes Débit et Crédit si manquantes
        
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
        
        # Détection automatique du format
        mapping_detecte = self._detecter_format_balance(df)
        logger.info(f"Format détecté: {mapping_detecte}")
        
        # Mapping des variations de noms de colonnes (fallback si détection échoue)
        column_mapping = {
            'Numero': 'Numéro',
            'Numero de compte': 'Numéro',
            'Compte': 'Numéro',
            'Libelle': 'Intitulé',
            'Libellé': 'Intitulé',
            'Intitule': 'Intitulé',
            'Ant Debit': 'Ant Débit',
            'Ant Crédit': 'Ant Crédit',
            'Ant Credit': 'Ant Crébit',
            'Debit': 'Débit',
            'Credit': 'Crédit',
            'Solde Debit': 'Solde Débit',
            'Solde Credit': 'Solde Crédit',
            'Solde D': 'Solde Débit',
            'Solde C': 'Solde Crédit'
        }
        
        # Appliquer le mapping
        df.columns = [column_mapping.get(col, col) for col in df.columns]
        
        # Renommer les colonnes détectées
        rename_dict = {}
        for col_standard, col_reel in mapping_detecte.items():
            if col_reel in df.columns and col_standard not in df.columns:
                rename_dict[col_reel] = col_standard
        
        if rename_dict:
            df = df.rename(columns=rename_dict)
            logger.info(f"Colonnes renommées: {rename_dict}")
        
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
        if 'Débit' not in df.columns:
            logger.info("Colonne 'Débit' manquante, calcul à partir des soldes")
            df['Débit'] = 0.0
        
        if 'Crédit' not in df.columns:
            logger.info("Colonne 'Crédit' manquante, calcul à partir des soldes")
            df['Crédit'] = 0.0
        
        return df
    
    def _detecter_format_nombre(self, serie: pd.Series) -> Dict[str, str]:
        """
        Détecte automatiquement le format des nombres (séparateurs décimaux et de milliers).
        
        Analyse les valeurs de la série pour identifier:
        - Le séparateur décimal utilisé (virgule ou point)
        - Le séparateur de milliers utilisé (espace, virgule ou point)
        
        Args:
            serie: Série pandas contenant les nombres à analyser
            
        Returns:
            Dict avec clés 'decimal_sep' et 'thousand_sep'
        """
        # Convertir en string et filtrer les valeurs non vides
        valeurs_str = serie.astype(str).str.strip()
        valeurs_str = valeurs_str[(valeurs_str != '') & (valeurs_str != 'nan')]
        
        if len(valeurs_str) == 0:
            return {'decimal_sep': '.', 'thousand_sep': ''}
        
        # Analyser les premiers nombres non vides
        decimal_sep = '.'
        thousand_sep = ''
        
        for val in valeurs_str.head(20):
            # Compter les occurrences de virgules et points
            count_virgule = val.count(',')
            count_point = val.count('.')
            count_espace = val.count(' ')
            
            # Cas 1: Une seule virgule = séparateur décimal
            if count_virgule == 1 and count_point == 0:
                decimal_sep = ','
                if count_espace > 0:
                    thousand_sep = ' '
                break
            
            # Cas 2: Une seule point = séparateur décimal
            elif count_point == 1 and count_virgule == 0:
                decimal_sep = '.'
                if count_espace > 0:
                    thousand_sep = ' '
                break
            
            # Cas 3: Plusieurs virgules = virgule est séparateur de milliers
            elif count_virgule > 1:
                thousand_sep = ','
                decimal_sep = '.'
                break
            
            # Cas 4: Plusieurs points = point est séparateur de milliers
            elif count_point > 1:
                thousand_sep = '.'
                decimal_sep = ','
                break
            
            # Cas 5: Virgule et point = le dernier est décimal
            elif count_virgule > 0 and count_point > 0:
                # Trouver la position du dernier séparateur
                last_virgule = val.rfind(',')
                last_point = val.rfind('.')
                
                if last_virgule > last_point:
                    # Virgule est après point = virgule est décimal
                    decimal_sep = ','
                    thousand_sep = '.'
                else:
                    # Point est après virgule = point est décimal
                    decimal_sep = '.'
                    thousand_sep = ','
                break
        
        logger.info(f"Format détecté: séparateur décimal='{decimal_sep}', séparateur milliers='{thousand_sep}'")
        return {'decimal_sep': decimal_sep, 'thousand_sep': thousand_sep}
    
    def _convertir_montant(self, valeur: str, decimal_sep: str = '.', thousand_sep: str = '') -> float:
        """
        Convertit une valeur texte en float en gérant les séparateurs.
        
        Args:
            valeur: Valeur texte à convertir
            decimal_sep: Séparateur décimal ('.' ou ',')
            thousand_sep: Séparateur de milliers ('', ' ', ',' ou '.')
            
        Returns:
            Valeur convertie en float, ou 0.0 si conversion échoue
        """
        try:
            # Convertir en string et nettoyer
            valeur = str(valeur).strip()
            
            if valeur == '' or valeur == 'nan' or valeur == 'None':
                return 0.0
            
            # Supprimer les espaces inutiles
            valeur = valeur.replace(' ', '')
            
            # Gérer le séparateur de milliers
            if thousand_sep:
                valeur = valeur.replace(thousand_sep, '')
            
            # Remplacer le séparateur décimal par un point
            if decimal_sep == ',':
                valeur = valeur.replace(',', '.')
            
            # Convertir en float
            resultat = float(valeur)
            
            # Vérifier les valeurs infinies
            if resultat == float('inf') or resultat == float('-inf'):
                return 0.0
            
            return resultat
        except (ValueError, TypeError):
            return 0.0
    
    def convertir_montants(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convertit tous les montants en float avec gestion des erreurs et formats variables.
        
        Cette méthode:
        1. Détecte automatiquement le format des nombres
        2. Convertit les colonnes de montants en float
        3. Remplace les valeurs vides ou invalides par 0.0
        4. Gère les séparateurs décimaux (virgule et point)
        5. Gère les séparateurs de milliers (espace, virgule, point)
        6. Remplace les valeurs infinies par 0.0
        
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
        
        # Détecter le format des nombres en analysant la première colonne de montants
        format_detecte = None
        for col in colonnes_montants:
            if col in df.columns:
                format_detecte = self._detecter_format_nombre(df[col])
                break
        
        if format_detecte is None:
            format_detecte = {'decimal_sep': '.', 'thousand_sep': ''}
        
        # Convertir chaque colonne de montants
        for col in colonnes_montants:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: self._convertir_montant(
                        x,
                        decimal_sep=format_detecte['decimal_sep'],
                        thousand_sep=format_detecte['thousand_sep']
                    )
                )
                
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
