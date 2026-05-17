#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 9 - RÉSERVES
Syscohada Révisé

Ce script calcule la Note 9 à partir des balances N, N-1, N-2 en utilisant
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


class CalculateurNote9(CalculateurNote):
    """
    Calculateur pour la Note 9 - Réserves.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 9 avec les mouvements des réserves:
    - Réserve légale
    - Réserves statutaires ou contractuelles
    - Réserves réglementées
    - Réserves libres
    - Report à nouveau
    - Autres réserves
    
    Mapping des comptes SYSCOHADA:
    - Comptes de réserves: 11X
      * 111: Réserve légale
      * 112: Réserves statutaires ou contractuelles
      * 113: Réserves réglementées
        - 1131: Réserves de plus-values nettes à long terme
        - 1132: Réserves de réévaluation
        - 1133: Réserves consécutives à l'octroi de subventions d'investissement
      * 114: Réserves libres
      * 115: Écarts de réévaluation
      * 116: Écarts d'équivalence
      * 117: Écarts de conversion
      * 118: Autres réserves
      * 12: Report à nouveau
        - 121: Report à nouveau créditeur
        - 129: Report à nouveau débiteur
    
    Note: Les réserves représentent les bénéfices non distribués et affectés
    à des comptes de réserves. Cette note suit les mouvements des réserves
    (dotations, prélèvements) sur les 3 exercices (N, N-1, N-2).
    Les comptes de réserves ne font pas l'objet d'amortissements.
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 9.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "9", "RÉSERVES")
        
        # Mapping des comptes pour chaque ligne de la Note 9
        self.mapping_comptes = {
            'Réserve légale': {
                'brut': ['111'],
                'amort': None  # Pas d'amortissements pour les réserves
            },
            'Réserves statutaires ou contractuelles': {
                'brut': ['112'],
                'amort': None
            },
            'Réserves réglementées': {
                'brut': ['1131', '1132', '1133'],
                'amort': None
            },
            'Réserves libres': {
                'brut': ['114'],
                'amort': None
            },
            'Écarts de réévaluation': {
                'brut': ['115'],
                'amort': None
            },
            'Écarts d\'équivalence': {
                'brut': ['116'],
                'amort': None
            },
            'Écarts de conversion': {
                'brut': ['117'],
                'amort': None
            },
            'Autres réserves': {
                'brut': ['118'],
                'amort': None
            },
            'Report à nouveau': {
                'brut': ['121', '129'],
                'amort': None
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 9 complète avec les 9 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne de réserves
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 10 lignes (9 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne de réserves
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
            'libelle': 'TOTAL RÉSERVES',
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
        description='Calcul de la Note 9 - Réserves'
    )
    parser.add_argument(
        'fichier_balance',
        nargs='?',
        default='../../../P000 -BALANCE DEMO N_N-1_N-2.xls',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='../Tests/test_note_9.html',
        help='Chemin du fichier HTML de sortie (défaut: ../Tests/test_note_9.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='../Tests/trace_note_9.json',
        help='Chemin du fichier de trace JSON (défaut: ../Tests/trace_note_9.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote9(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
