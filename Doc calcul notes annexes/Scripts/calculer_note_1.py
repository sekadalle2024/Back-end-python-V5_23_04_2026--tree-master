#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 1 - DETTES GARANTIES PAR DES SURETES REELLES ET LES ENGAGEMENTS FINANCIERS
Syscohada Révisé

Ce script calcule la Note 1 à partir des balances N, N-1, N-2
"""

import pandas as pd
import openpyxl
import os
from typing import Dict, List


class CalculateurNote1:
    """Classe pour calculer la Note 1 des états financiers"""
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        self.fichier_balance = fichier_balance
        self.balance_n = None
        self.balance_n1 = None
        self.balance_n2 = None
        
        # Mapping des comptes pour la Note 1
        # Note: La Note 1 nécessite des informations sur les sûretés réelles
        # qui ne sont pas directement dans les balances
        # On va extraire les montants bruts des dettes
        self.mapping_comptes = {
            'Emprunts obligataires convertibles': {
                'comptes': ['161']
            },
            'Autres emprunts obligataires': {
                'comptes': ['162', '163', '164', '165', '166', '167', '168']
            },
            'Emprunts et dettes des établissements de crédit': {
                'comptes': ['171', '172', '173', '174', '175', '176']
            },
            'Autres dettes financières': {
                'comptes': ['178', '181', '182', '183', '184', '185', '186', '187', '188']
            },
            'Dettes de crédit-bail immobilier': {
                'comptes': ['173']
            },
            'Dettes de crédit-bail mobilier': {
                'comptes': ['174']
            },
            'Dettes sur contrats de location-vente': {
                'comptes': ['175']
            },
            'Autres dettes sur contrats de location-acquisition': {
                'comptes': ['176']
            },
            'Fournisseurs et comptes rattachés': {
                'comptes': ['401', '402', '403', '404', '405', '408']
            },
            'Clients': {
                'comptes': ['419']  # Clients créditeurs
            },
            'Personnel': {
                'comptes': ['421', '422', '423', '424', '425', '426', '427', '428']
            },
            'Sécurité sociale et organismes sociaux': {
                'comptes': ['431', '432', '433', '434', '435', '436', '437', '438']
            },
            'Etat': {
                'comptes': ['441', '442', '443', '444', '445', '446', '447', '448']
            },
            'Organismes internationaux': {
                'comptes': ['451', '452', '453', '454', '455', '456', '457', '458']
            },
            'Associés et groupe': {
                'comptes': ['461', '462', '463', '464', '465', '466', '467']
            },
            'Créditeurs divers': {
                'comptes': ['471', '472', '473', '474', '475', '476', '477', '478']
            }
        }
    
    def to_float(self, value) -> float:
        """
        Convertit une valeur en float de manière robuste
        
        Args:
            value: Valeur à convertir
        
        Returns:
            Valeur convertie en float, 0.0 si impossible
        """
        if value is None or pd.isna(value):
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            value = value.strip().replace(' ', '').replace(',', '.')
            if value == '' or value == '-':
                return 0.0
            try:
                return float(value)
            except ValueError:
                return 0.0
        
        return 0.0
    
    def charger_balances(self) -> bool:
        """
        Charge les 3 balances depuis le fichier Excel
        
        Returns:
            True si succès, False sinon
        """
        try:
            print(f"Chargement du fichier: {self.fichier_balance}")
            
            # Charger le fichier Excel
            wb = openpyxl.load_workbook(self.fichier_balance, data_only=True)
            
            # Détecter les noms d'onglets (avec ou sans espaces)
            sheet_names = wb.sheetnames
            
            # Trouver les onglets des balances
            balance_n_name = None
            balance_n1_name = None
            balance_n2_name = None
            
            for name in sheet_names:
                name_clean = name.strip().upper()
                if 'BALANCE N-2' in name_clean or 'BALANCE N - 2' in name_clean:
                    balance_n2_name = name
                elif 'BALANCE N-1' in name_clean or 'BALANCE N - 1' in name_clean:
                    balance_n1_name = name
                elif name_clean == 'BALANCE N' or name_clean.startswith('BALANCE N '):
                    balance_n_name = name
            
            if not all([balance_n_name, balance_n1_name, balance_n2_name]):
                print("❌ Erreur: Impossible de trouver tous les onglets de balances")
                print(f"   Onglets trouvés: N={balance_n_name}, N-1={balance_n1_name}, N-2={balance_n2_name}")
                return False
            
            print(f"✓ Onglets détectés:")
            print(f"  - Balance N  : '{balance_n_name}'")
            print(f"  - Balance N-1: '{balance_n1_name}'")
            print(f"  - Balance N-2: '{balance_n2_name}'")
            
            # Charger les balances
            self.balance_n = pd.read_excel(self.fichier_balance, sheet_name=balance_n_name)
            self.balance_n1 = pd.read_excel(self.fichier_balance, sheet_name=balance_n1_name)
            self.balance_n2 = pd.read_excel(self.fichier_balance, sheet_name=balance_n2_name)
            
            print(f"✓ Balances chargées avec succès")
            print(f"  - Balance N  : {len(self.balance_n)} lignes")
            print(f"  - Balance N-1: {len(self.balance_n1)} lignes")
            print(f"  - Balance N-2: {len(self.balance_n2)} lignes")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des balances: {e}")
            return False
    
    def extraire_solde_compte(self, balance: pd.DataFrame, numero_compte: str) ->