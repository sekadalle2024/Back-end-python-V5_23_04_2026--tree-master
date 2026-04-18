"""
Module Account_Extractor - Extraction des soldes des comptes par racine

Ce module fournit la classe AccountExtractor pour extraire les soldes des comptes
depuis une balance chargée, en filtrant par numéro de racine et en gérant
gracieusement les comptes manquants.

Auteur: Système de calcul automatique des notes annexes SYSCOHADA
Date: 12 Avril 2026
"""

import pandas as pd
from typing import Dict, List
import logging


# Configuration du logging
logger = logging.getLogger(__name__)


class AccountExtractor:
    """
    Classe pour extraire les soldes des comptes par racine depuis une balance.
    
    Cette classe permet de:
    - Filtrer les comptes par numéro de racine
    - Extraire les 6 valeurs d'un compte (Ant Débit, Ant Crédit, Débit, Crédit, Solde Débit, Solde Crédit)
    - Sommer les soldes de plusieurs racines de comptes
    - Gérer gracieusement les comptes manquants en retournant des zéros
    
    Attributes:
        balance (pd.DataFrame): DataFrame de la balance chargée
        colonnes_montants (List[str]): Liste des colonnes de montants à extraire
    """
    
    def __init__(self, balance: pd.DataFrame):
        """
        Initialise l'extracteur avec une balance.
        
        Args:
            balance: DataFrame de la balance avec colonnes:
                    Numéro, Intitulé, Ant Débit, Ant Crédit, Débit, Crédit,
                    Solde Débit, Solde Crédit
        """
        self.balance = balance
        self.colonnes_montants = [
            'Ant Débit', 'Ant Crédit',
            'Débit', 'Crédit',
            'Solde Débit', 'Solde Crédit'
        ]
        
        # Vérifier que les colonnes requises sont présentes
        colonnes_manquantes = [col for col in self.colonnes_montants if col not in balance.columns]
        if colonnes_manquantes:
            logger.warning(f"Colonnes manquantes dans la balance: {colonnes_manquantes}")
        
        logger.info(f"AccountExtractor initialisé avec {len(balance)} comptes")
    
    def extraire_solde_compte(self, numero_compte: str) -> Dict[str, float]:
        """
        Extrait les 6 valeurs d'un compte par sa racine.
        
        Cette méthode filtre tous les comptes commençant par le numéro de racine
        fourni et somme leurs valeurs. Si aucun compte ne correspond, retourne
        des valeurs nulles (0.0) pour toutes les colonnes.
        
        Args:
            numero_compte: Racine du compte (ex: "211", "2811")
            
        Returns:
            Dict avec clés: ant_debit, ant_credit, mvt_debit, mvt_credit,
                           solde_debit, solde_credit
                           
        Example:
            >>> extractor = AccountExtractor(balance_n)
            >>> soldes = extractor.extraire_solde_compte("211")
            >>> print(soldes['solde_debit'])
            1500000.0
        """
        # Filtrer les comptes par racine
        comptes_filtres = self.filtrer_par_racine(numero_compte)
        
        # Si aucun compte trouvé, retourner des zéros
        if comptes_filtres.empty:
            logger.debug(f"Aucun compte trouvé pour la racine {numero_compte}, retour de zéros")
            return {
                'ant_debit': 0.0,
                'ant_credit': 0.0,
                'mvt_debit': 0.0,
                'mvt_credit': 0.0,
                'solde_debit': 0.0,
                'solde_credit': 0.0
            }
        
        # Sommer les valeurs de tous les comptes correspondants
        resultat = {
            'ant_debit': comptes_filtres['Ant Débit'].sum() if 'Ant Débit' in comptes_filtres.columns else 0.0,
            'ant_credit': comptes_filtres['Ant Crédit'].sum() if 'Ant Crédit' in comptes_filtres.columns else 0.0,
            'mvt_debit': comptes_filtres['Débit'].sum() if 'Débit' in comptes_filtres.columns else 0.0,
            'mvt_credit': comptes_filtres['Crédit'].sum() if 'Crédit' in comptes_filtres.columns else 0.0,
            'solde_debit': comptes_filtres['Solde Débit'].sum() if 'Solde Débit' in comptes_filtres.columns else 0.0,
            'solde_credit': comptes_filtres['Solde Crédit'].sum() if 'Solde Crédit' in comptes_filtres.columns else 0.0
        }
        
        logger.debug(f"Compte {numero_compte}: {len(comptes_filtres)} ligne(s) trouvée(s), "
                    f"Solde Débit={resultat['solde_debit']:.2f}, "
                    f"Solde Crédit={resultat['solde_credit']:.2f}")
        
        return resultat
    
    def extraire_comptes_multiples(self, racines: List[str]) -> Dict[str, float]:
        """
        Extrait et somme les soldes de plusieurs racines de comptes.
        
        Cette méthode permet d'extraire et de sommer les soldes de plusieurs
        racines de comptes en une seule opération. Utile pour regrouper
        plusieurs sous-comptes (ex: 211, 212, 213 pour les immobilisations
        incorporelles).
        
        Args:
            racines: Liste de racines de comptes (ex: ["211", "212", "213"])
            
        Returns:
            Dict avec les sommes des 6 valeurs pour toutes les racines
            
        Example:
            >>> extractor = AccountExtractor(balance_n)
            >>> soldes = extractor.extraire_comptes_multiples(["211", "212", "213"])
            >>> print(soldes['solde_debit'])
            5000000.0
        """
        # Initialiser le résultat avec des zéros
        resultat_total = {
            'ant_debit': 0.0,
            'ant_credit': 0.0,
            'mvt_debit': 0.0,
            'mvt_credit': 0.0,
            'solde_debit': 0.0,
            'solde_credit': 0.0
        }
        
        # Extraire et sommer chaque racine
        for racine in racines:
            soldes = self.extraire_solde_compte(racine)
            for cle in resultat_total.keys():
                resultat_total[cle] += soldes[cle]
        
        logger.debug(f"Extraction multiple de {len(racines)} racines: "
                    f"Solde Débit total={resultat_total['solde_debit']:.2f}, "
                    f"Solde Crédit total={resultat_total['solde_credit']:.2f}")
        
        return resultat_total
    
    def filtrer_par_racine(self, racine: str) -> pd.DataFrame:
        """
        Filtre les comptes commençant par une racine.
        
        Cette méthode retourne un DataFrame contenant tous les comptes dont
        le numéro commence par la racine spécifiée. Gère les comptes avec
        plusieurs niveaux (ex: "2811", "28111").
        
        Args:
            racine: Racine de compte (ex: "211", "28")
            
        Returns:
            DataFrame des comptes filtrés
            
        Example:
            >>> extractor = AccountExtractor(balance_n)
            >>> comptes_211 = extractor.filtrer_par_racine("211")
            >>> print(len(comptes_211))
            5
        """
        # Vérifier que la colonne Numéro existe
        if 'Numéro' not in self.balance.columns:
            logger.error("Colonne 'Numéro' manquante dans la balance")
            return pd.DataFrame()
        
        # Convertir la colonne Numéro en string pour la comparaison
        balance_copy = self.balance.copy()
        balance_copy['Numéro'] = balance_copy['Numéro'].astype(str).str.strip()
        
        # Filtrer les comptes commençant par la racine
        comptes_filtres = balance_copy[balance_copy['Numéro'].str.startswith(racine)]
        
        logger.debug(f"Filtrage par racine '{racine}': {len(comptes_filtres)} compte(s) trouvé(s)")
        
        return comptes_filtres


if __name__ == "__main__":
    # Configuration du logging pour les tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test du module
    print("=" * 60)
    print("TEST DU MODULE ACCOUNT_EXTRACTOR")
    print("=" * 60)
    
    try:
        # Importer le module Balance_Reader pour charger une balance de test
        from balance_reader import BalanceReader
        
        # Chemin vers le fichier de test
        fichier_test = "../../P000 -BALANCE DEMO N_N-1_N-2.xls"
        
        # Charger la balance N
        print("\n📂 Chargement de la balance N...")
        reader = BalanceReader(fichier_test)
        balance_n, _, _ = reader.charger_balances()
        
        # Créer une instance de l'extracteur
        print("\n🔍 Création de l'extracteur...")
        extractor = AccountExtractor(balance_n)
        
        # Test 1: Extraire un compte simple
        print("\n" + "=" * 60)
        print("TEST 1: Extraction d'un compte simple (racine 211)")
        print("=" * 60)
        soldes_211 = extractor.extraire_solde_compte("211")
        print(f"Résultats pour le compte 211:")
        print(f"  - Ant Débit:    {soldes_211['ant_debit']:>15,.2f}")
        print(f"  - Ant Crédit:   {soldes_211['ant_credit']:>15,.2f}")
        print(f"  - Mvt Débit:    {soldes_211['mvt_debit']:>15,.2f}")
        print(f"  - Mvt Crédit:   {soldes_211['mvt_credit']:>15,.2f}")
        print(f"  - Solde Débit:  {soldes_211['solde_debit']:>15,.2f}")
        print(f"  - Solde Crédit: {soldes_211['solde_credit']:>15,.2f}")
        
        # Test 2: Extraire un compte inexistant
        print("\n" + "=" * 60)
        print("TEST 2: Extraction d'un compte inexistant (racine 999)")
        print("=" * 60)
        soldes_999 = extractor.extraire_solde_compte("999")
        print(f"Résultats pour le compte 999 (devrait être des zéros):")
        print(f"  - Solde Débit:  {soldes_999['solde_debit']:>15,.2f}")
        print(f"  - Solde Crédit: {soldes_999['solde_credit']:>15,.2f}")
        
        # Test 3: Extraire plusieurs comptes
        print("\n" + "=" * 60)
        print("TEST 3: Extraction de plusieurs comptes (211, 212, 213)")
        print("=" * 60)
        soldes_multiples = extractor.extraire_comptes_multiples(["211", "212", "213"])
        print(f"Résultats pour les comptes 211+212+213:")
        print(f"  - Solde Débit total:  {soldes_multiples['solde_debit']:>15,.2f}")
        print(f"  - Solde Crédit total: {soldes_multiples['solde_credit']:>15,.2f}")
        
        # Test 4: Filtrer par racine
        print("\n" + "=" * 60)
        print("TEST 4: Filtrage par racine (21)")
        print("=" * 60)
        comptes_21 = extractor.filtrer_par_racine("21")
        print(f"Nombre de comptes commençant par 21: {len(comptes_21)}")
        if not comptes_21.empty:
            print(f"\nPremiers comptes trouvés:")
            for idx, row in comptes_21.head().iterrows():
                print(f"  - {row['Numéro']}: {row['Intitulé']}")
        
        print("\n" + "=" * 60)
        print("✓ TEST RÉUSSI - Module Account_Extractor opérationnel")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
