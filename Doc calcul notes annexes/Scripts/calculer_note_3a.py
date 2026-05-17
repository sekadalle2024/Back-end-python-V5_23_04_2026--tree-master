#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 3A - IMMOBILISATIONS INCORPORELLES
Syscohada Révisé

Ce script calcule la Note 3A à partir des balances N, N-1, N-2 en utilisant
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


class CalculateurNote3A(CalculateurNote):
    """
    Calculateur pour la Note 3A - Immobilisations Incorporelles.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 3A avec les 4 lignes d'immobilisations incorporelles:
    - Frais de recherche et de développement
    - Brevets, licences, logiciels et droits similaires
    - Fonds commercial et droit au bail
    - Autres immobilisations incorporelles
    
    Mapping des comptes SYSCOHADA:
    - Comptes bruts: 21X (Immobilisations incorporelles)
    - Comptes amortissements: 281X (Amortissements des immobilisations incorporelles)
    - Comptes provisions: 291X (Provisions pour dépréciation des immobilisations incorporelles)
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 3A.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "3A", "IMMOBILISATIONS INCORPORELLES")
        
        # Mapping des comptes pour chaque ligne de la Note 3A
        self.mapping_comptes = {
            'Frais de recherche et de développement': {
                'brut': ['211'],
                'amort': ['2811', '2911']
            },
            'Brevets, licences, logiciels et droits similaires': {
                'brut': ['212', '213'],
                'amort': ['2812', '2813', '2912', '2913']
            },
            'Fonds commercial et droit au bail': {
                'brut': ['214', '215'],
                'amort': ['2814', '2815', '2914', '2915']
            },
            'Autres immobilisations incorporelles': {
                'brut': ['216', '217', '218'],
                'amort': ['2816', '2817', '2818', '2916', '2917', '2918']
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 3A complète avec les 4 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne d'immobilisation incorporelle
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 5 lignes (4 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne d'immobilisation incorporelle
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
            'libelle': 'TOTAL IMMOBILISATIONS INCORPORELLES',
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
        description='Calcul de la Note 3A - Immobilisations Incorporelles'
    )
    parser.add_argument(
        'fichier_balance',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='note_3a_immobilisations_incorporelles.html',
        help='Chemin du fichier HTML de sortie (défaut: note_3a_immobilisations_incorporelles.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='note_3a_trace.json',
        help='Chemin du fichier de trace JSON (défaut: note_3a_trace.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote3A(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
