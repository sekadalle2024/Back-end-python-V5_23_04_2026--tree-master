#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 8 - CAPITAL
Syscohada Révisé

Ce script calcule la Note 8 à partir des balances N, N-1, N-2 en utilisant
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


class CalculateurNote8(CalculateurNote):
    """
    Calculateur pour la Note 8 - Capital.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 8 avec les mouvements du capital social:
    - Capital social
    - Capital souscrit non appelé
    - Capital souscrit appelé non versé
    - Capital souscrit appelé versé
    - Actionnaires, capital souscrit non appelé
    
    Mapping des comptes SYSCOHADA:
    - Comptes de capital: 10X (Capital et réserves)
      * 101: Capital social
        - 1011: Capital souscrit non appelé
        - 1012: Capital souscrit appelé non versé
        - 1013: Capital souscrit appelé versé
      * 102: Capital par dotation
      * 103: Capital personnel
      * 104: Compte de l'exploitant
      * 105: Primes liées au capital social
        - 1051: Primes d'émission
        - 1052: Primes d'apport
        - 1053: Primes de fusion
        - 1054: Primes de conversion d'obligations en actions
    
    Note: Le capital représente les apports des associés ou actionnaires.
    Cette note suit les mouvements du capital (augmentations, réductions)
    sur les 3 exercices (N, N-1, N-2).
    Les comptes de capital ne font pas l'objet d'amortissements.
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 8.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "8", "CAPITAL")
        
        # Mapping des comptes pour chaque ligne de la Note 8
        self.mapping_comptes = {
            'Capital social': {
                'brut': ['1011', '1012', '1013'],
                'amort': None  # Pas d'amortissements pour le capital
            },
            'Capital par dotation': {
                'brut': ['102'],
                'amort': None
            },
            'Capital personnel': {
                'brut': ['103'],
                'amort': None
            },
            'Compte de l\'exploitant': {
                'brut': ['104'],
                'amort': None
            },
            'Primes liées au capital social': {
                'brut': ['1051', '1052', '1053', '1054'],
                'amort': None
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 8 complète avec les 5 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne de capital
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 6 lignes (5 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne de capital
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
            'libelle': 'TOTAL CAPITAL',
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
        description='Calcul de la Note 8 - Capital'
    )
    parser.add_argument(
        'fichier_balance',
        nargs='?',
        default='../../../P000 -BALANCE DEMO N_N-1_N-2.xls',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='../Tests/test_note_8.html',
        help='Chemin du fichier HTML de sortie (défaut: ../Tests/test_note_8.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='../Tests/trace_note_8.json',
        help='Chemin du fichier de trace JSON (défaut: ../Tests/trace_note_8.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote8(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
