#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 3B - IMMOBILISATIONS CORPORELLES
Syscohada Révisé

Ce script calcule la Note 3B à partir des balances N, N-1, N-2 en utilisant
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


class CalculateurNote3B(CalculateurNote):
    """
    Calculateur pour la Note 3B - Immobilisations Corporelles.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 3B avec les 9 lignes d'immobilisations corporelles:
    - Terrains
    - Bâtiments
    - Installations et agencements
    - Matériel
    - Matériel de transport
    - Avances et acomptes versés sur immobilisations
    - Immobilisations corporelles en cours
    - Autres immobilisations corporelles
    - Immobilisations corporelles hors exploitation
    
    Mapping des comptes SYSCOHADA:
    - Comptes bruts: 22X (Immobilisations corporelles)
    - Comptes amortissements: 282X (Amortissements des immobilisations corporelles)
    - Comptes provisions: 292X (Provisions pour dépréciation des immobilisations corporelles)
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 3B.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "3B", "IMMOBILISATIONS CORPORELLES")
        
        # Mapping des comptes pour chaque ligne de la Note 3B
        self.mapping_comptes = {
            'Terrains': {
                'brut': ['221'],
                'amort': ['2821', '2921']
            },
            'Bâtiments': {
                'brut': ['222', '223'],
                'amort': ['2822', '2823', '2922', '2923']
            },
            'Installations et agencements': {
                'brut': ['224'],
                'amort': ['2824', '2924']
            },
            'Matériel': {
                'brut': ['225', '226'],
                'amort': ['2825', '2826', '2925', '2926']
            },
            'Matériel de transport': {
                'brut': ['227'],
                'amort': ['2827', '2927']
            },
            'Avances et acomptes versés sur immobilisations': {
                'brut': ['228'],
                'amort': ['2828', '2928']
            },
            'Immobilisations corporelles en cours': {
                'brut': ['229'],
                'amort': ['2829', '2929']
            },
            'Autres immobilisations corporelles': {
                'brut': ['2281', '2282', '2283', '2284', '2285', '2286', '2287'],
                'amort': ['28281', '28282', '28283', '28284', '28285', '28286', '28287',
                         '29281', '29282', '29283', '29284', '29285', '29286', '29287']
            },
            'Immobilisations corporelles hors exploitation': {
                'brut': ['2288'],
                'amort': ['28288', '29288']
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 3B complète avec les 9 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne d'immobilisation corporelle
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 10 lignes (9 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne d'immobilisation corporelle
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
            'libelle': 'TOTAL IMMOBILISATIONS CORPORELLES',
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
        description='Calcul de la Note 3B - Immobilisations Corporelles'
    )
    parser.add_argument(
        'fichier_balance',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='note_3b_immobilisations_corporelles.html',
        help='Chemin du fichier HTML de sortie (défaut: note_3b_immobilisations_corporelles.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='note_3b_trace.json',
        help='Chemin du fichier de trace JSON (défaut: note_3b_trace.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote3B(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
