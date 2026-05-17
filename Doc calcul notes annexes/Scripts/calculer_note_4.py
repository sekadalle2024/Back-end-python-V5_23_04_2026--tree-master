#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 4 - STOCKS
Syscohada Révisé

Ce script calcule la Note 4 à partir des balances N, N-1, N-2 en utilisant
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


class CalculateurNote4(CalculateurNote):
    """
    Calculateur pour la Note 4 - Stocks.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 4 avec les 8 lignes de stocks:
    - Marchandises
    - Matières premières et fournitures liées
    - Autres approvisionnements
    - Produits en cours
    - Services en cours
    - Produits finis
    - Produits intermédiaires et résiduels
    - Stocks en cours de route, en consignation ou en dépôt
    
    Mapping des comptes SYSCOHADA:
    - Comptes stocks: 3X (Stocks et en-cours)
      * 31: Marchandises
      * 32: Matières premières et fournitures liées
      * 33: Autres approvisionnements
      * 34: Produits en cours
      * 35: Services en cours
      * 36: Produits finis
      * 37: Produits intermédiaires et résiduels
      * 38: Stocks en cours de route, en consignation ou en dépôt
    
    Note: Les stocks ne sont généralement pas amortis, mais peuvent faire l'objet
    de provisions pour dépréciation (comptes 39X).
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 4.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "4", "STOCKS")
        
        # Mapping des comptes pour chaque ligne de la Note 4
        self.mapping_comptes = {
            'Marchandises': {
                'brut': ['31'],
                'amort': ['391']  # Provisions pour dépréciation des marchandises
            },
            'Matières premières et fournitures liées': {
                'brut': ['32'],
                'amort': ['392']  # Provisions pour dépréciation des matières premières
            },
            'Autres approvisionnements': {
                'brut': ['33'],
                'amort': ['393']  # Provisions pour dépréciation des autres approvisionnements
            },
            'Produits en cours': {
                'brut': ['34'],
                'amort': ['394']  # Provisions pour dépréciation des produits en cours
            },
            'Services en cours': {
                'brut': ['35'],
                'amort': ['395']  # Provisions pour dépréciation des services en cours
            },
            'Produits finis': {
                'brut': ['36'],
                'amort': ['396']  # Provisions pour dépréciation des produits finis
            },
            'Produits intermédiaires et résiduels': {
                'brut': ['37'],
                'amort': ['397']  # Provisions pour dépréciation des produits intermédiaires
            },
            'Stocks en cours de route, en consignation ou en dépôt': {
                'brut': ['38'],
                'amort': ['398']  # Provisions pour dépréciation des stocks en cours de route
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 4 complète avec les 8 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne de stock
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 9 lignes (8 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne de stock
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
            'libelle': 'TOTAL STOCKS',
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
        description='Calcul de la Note 4 - Stocks'
    )
    parser.add_argument(
        'fichier_balance',
        nargs='?',
        default='../../P000 -BALANCE DEMO N_N-1_N-2.xls',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='../Tests/test_note_4.html',
        help='Chemin du fichier HTML de sortie (défaut: ../Tests/test_note_4.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='../Tests/trace_note_4.json',
        help='Chemin du fichier de trace JSON (défaut: ../Tests/trace_note_4.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote4(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
