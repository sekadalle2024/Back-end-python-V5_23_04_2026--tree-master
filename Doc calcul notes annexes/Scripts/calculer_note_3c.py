#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 3C - IMMOBILISATIONS FINANCIÈRES
Syscohada Révisé

Ce script calcule la Note 3C à partir des balances N, N-1, N-2 en utilisant
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


class CalculateurNote3C(CalculateurNote):
    """
    Calculateur pour la Note 3C - Immobilisations Financières.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 3C avec les lignes d'immobilisations financières:
    - Titres de participation
    - Autres immobilisations financières
    - Prêts et créances
    - Dépôts et cautionnements versés
    
    Mapping des comptes SYSCOHADA:
    - Comptes bruts: 26X (Immobilisations financières)
    - Comptes provisions: 27X (Provisions pour dépréciation des immobilisations financières)
    
    Note: Les immobilisations financières ne sont généralement pas amorties,
    mais peuvent faire l'objet de provisions pour dépréciation (comptes 27X).
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 3C.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "3C", "IMMOBILISATIONS FINANCIÈRES")
        
        # Mapping des comptes pour chaque ligne de la Note 3C
        self.mapping_comptes = {
            'Titres de participation': {
                'brut': ['261'],
                'amort': ['271']  # Provisions pour dépréciation
            },
            'Autres titres immobilisés': {
                'brut': ['262', '263'],
                'amort': ['272', '273']
            },
            'Prêts et créances': {
                'brut': ['264', '265'],
                'amort': ['274', '275']
            },
            'Dépôts et cautionnements versés': {
                'brut': ['266', '267'],
                'amort': ['276', '277']
            },
            'Autres immobilisations financières': {
                'brut': ['268'],
                'amort': ['278']
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 3C complète avec les 5 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne d'immobilisation financière
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 6 lignes (5 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne d'immobilisation financière
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
            'libelle': 'TOTAL IMMOBILISATIONS FINANCIÈRES',
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
        description='Calcul de la Note 3C - Immobilisations Financières'
    )
    parser.add_argument(
        'fichier_balance',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='note_3c_immobilisations_financieres.html',
        help='Chemin du fichier HTML de sortie (défaut: note_3c_immobilisations_financieres.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='note_3c_trace.json',
        help='Chemin du fichier de trace JSON (défaut: note_3c_trace.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote3C(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
