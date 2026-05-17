#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 5 - CRÉANCES CLIENTS
Syscohada Révisé

Ce script calcule la Note 5 à partir des balances N, N-1, N-2 en utilisant
l'architecture modulaire du système de calcul automatique des notes annexes.

Auteur: Système de calcul automatique des notes annexes SYSCOHADA
Date: 25 Avril 2026
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Ajouter le chemin du template au PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from calculateur_note_template import CalculateurNote


class CalculateurNote5(CalculateurNote):
    """
    Calculateur pour la Note 5 - Créances Clients.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 5 avec les lignes de créances clients:
    - Clients
    - Clients - Effets à recevoir
    - Clients douteux ou litigieux
    - Clients - Retenues de garantie
    - Clients - Créances sur travaux non encore facturables
    - Clients - Factures à établir
    
    Mapping des comptes SYSCOHADA:
    - Comptes créances clients: 41X (Clients et comptes rattachés)
      * 411: Clients
      * 412: Clients - Effets à recevoir
      * 413: Clients douteux ou litigieux
      * 414: Clients - Retenues de garantie
      * 415: Clients - Créances sur travaux non encore facturables
      * 416: Clients - Factures à établir
      * 417: Clients - Créances sur cessions d'immobilisations
      * 418: Clients - Produits à recevoir
    - Comptes provisions: 491X (Provisions pour dépréciation des comptes clients)
    
    Note: Les créances clients peuvent faire l'objet de provisions pour dépréciation
    (comptes 491X) en cas de risque de non-recouvrement.
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 5.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "5", "CRÉANCES CLIENTS")
        
        # Mapping des comptes pour chaque ligne de la Note 5
        self.mapping_comptes = {
            'Clients': {
                'brut': ['411'],
                'amort': ['4911']  # Provisions pour dépréciation des comptes clients
            },
            'Clients - Effets à recevoir': {
                'brut': ['412'],
                'amort': ['4912']  # Provisions pour dépréciation des effets à recevoir
            },
            'Clients douteux ou litigieux': {
                'brut': ['413'],
                'amort': ['4913']  # Provisions pour dépréciation des clients douteux
            },
            'Clients - Retenues de garantie': {
                'brut': ['414'],
                'amort': ['4914']  # Provisions pour dépréciation des retenues de garantie
            },
            'Clients - Créances sur travaux non encore facturables': {
                'brut': ['415'],
                'amort': ['4915']  # Provisions pour dépréciation des créances sur travaux
            },
            'Clients - Factures à établir': {
                'brut': ['416'],
                'amort': ['4916']  # Provisions pour dépréciation des factures à établir
            },
            'Autres créances clients': {
                'brut': ['417', '418'],
                'amort': ['4917', '4918']  # Provisions pour dépréciation des autres créances
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 5 complète avec les 7 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne de créances clients
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 8 lignes (7 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne de créances clients
        for libelle, comptes in self.mapping_comptes.items():
            print(f"  Calcul: {libelle}...")
            
            ligne = self.calculer_ligne_note(
                libelle=libelle,
                comptes_brut=comptes['brut'],
                comptes_amort=comptes.get('amort')
            )
            
            lignes.append(ligne)
        
        # Créer le DataFrame
        df = pd.DataFrame(lignes)
        
        # Calculer la ligne de total
        total = self.calculer_total(df)
        df = pd.concat([df, pd.DataFrame([total])], ignore_index=True)
        
        return df
    
    def calculer_total(self, df: pd.DataFrame) -> dict:
        """
        Calcule la ligne de total en sommant toutes les colonnes.
        
        Args:
            df: DataFrame contenant les lignes de détail
            
        Returns:
            Dict représentant la ligne de total
        """
        total = {
            'libelle': 'TOTAL CRÉANCES CLIENTS',
            'brut_ouverture': df['brut_ouverture'].sum(),
            'augmentations': df['augmentations'].sum(),
            'diminutions': df['diminutions'].sum(),
            'brut_cloture': df['brut_cloture'].sum(),
            'amort_ouverture': df['amort_ouverture'].sum(),
            'dotations': df['dotations'].sum(),
            'reprises': df['reprises'].sum(),
            'amort_cloture': df['amort_cloture'].sum(),
            'vnc_ouverture': df['vnc_ouverture'].sum(),
            'vnc_cloture': df['vnc_cloture'].sum()
        }
        
        return total


# Point d'entrée principal
if __name__ == "__main__":
    import argparse
    
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(
        description='Calcul de la Note 5 - Créances Clients'
    )
    parser.add_argument(
        'fichier_balance',
        nargs='?',
        default='../../P000 -BALANCE DEMO N_N-1_N-2.xls',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='../Tests/test_note_5.html',
        help='Chemin du fichier HTML de sortie (défaut: ../Tests/test_note_5.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='../Tests/trace_note_5.json',
        help='Chemin du fichier de trace JSON (défaut: ../Tests/trace_note_5.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote5(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
