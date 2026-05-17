#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de calcul de la NOTE 7 - TRÉSORERIE ACTIF
Syscohada Révisé

Ce script calcule la Note 7 à partir des balances N, N-1, N-2 en utilisant
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


class CalculateurNote7(CalculateurNote):
    """
    Calculateur pour la Note 7 - Trésorerie Actif.
    
    Cette classe hérite de CalculateurNote et implémente le calcul spécifique
    de la Note 7 avec les lignes de trésorerie actif (disponibilités):
    - Banques, établissements financiers et assimilés
    - Chèques postaux, caisse nationale d'épargne
    - Caisse
    - Régies d'avances et accréditifs
    
    Mapping des comptes SYSCOHADA:
    - Comptes de trésorerie actif: 5X (Comptes de trésorerie)
      * 51: Banques, établissements financiers et assimilés
        - 511: Valeurs à l'encaissement
        - 512: Banques
        - 513: Établissements financiers et assimilés
        - 514: Chèques postaux
      * 52: Caisse
        - 521: Caisse siège social
        - 522: Caisse succursale (ou usine) A
        - 523: Caisse succursale (ou usine) B
      * 53: Régies d'avances et accréditifs
        - 531: Régies d'avances
        - 532: Accréditifs
      * 54: Instruments de trésorerie
        - 541: Bons de caisse et bons du Trésor à court terme
        - 542: Titres de placement à court terme
      * 57: Virements internes
        - 571: Virements de fonds
        - 572: Virements d'exploitation
    
    Note: La trésorerie actif représente les disponibilités immédiates de l'entreprise.
    Ces comptes ne font généralement pas l'objet d'amortissements ou de provisions,
    sauf cas exceptionnels (provisions pour dépréciation de titres de placement).
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur de la Note 7.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        super().__init__(fichier_balance, "7", "TRÉSORERIE ACTIF")
        
        # Mapping des comptes pour chaque ligne de la Note 7
        self.mapping_comptes = {
            'Banques, établissements financiers et assimilés': {
                'brut': ['511', '512', '513', '514'],
                'amort': None  # Pas de provisions pour les comptes bancaires
            },
            'Chèques postaux, caisse nationale d\'épargne': {
                'brut': ['514'],  # Chèques postaux
                'amort': None
            },
            'Caisse': {
                'brut': ['521', '522', '523', '524', '525', '526', '527', '528'],
                'amort': None  # Pas de provisions pour la caisse
            },
            'Régies d\'avances et accréditifs': {
                'brut': ['531', '532'],
                'amort': None  # Pas de provisions pour les régies
            },
            'Instruments de trésorerie': {
                'brut': ['541', '542'],
                'amort': ['5941', '5942']  # Provisions pour dépréciation des titres de placement
            },
            'Virements internes': {
                'brut': ['571', '572'],
                'amort': None  # Pas de provisions pour les virements internes
            }
        }
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la Note 7 complète avec les 6 lignes et le total.
        
        Cette méthode:
        1. Calcule chaque ligne de trésorerie actif
        2. Calcule la ligne de total
        3. Retourne un DataFrame avec toutes les lignes
        
        Returns:
            DataFrame contenant les 7 lignes (6 lignes + total)
        """
        lignes = []
        
        # Calculer chaque ligne de trésorerie actif
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
            'libelle': 'TOTAL TRÉSORERIE ACTIF',
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
        description='Calcul de la Note 7 - Trésorerie Actif'
    )
    parser.add_argument(
        'fichier_balance',
        nargs='?',
        default='../../P000 -BALANCE DEMO N_N-1_N-2.xls',
        help='Chemin vers le fichier Excel des balances (N, N-1, N-2)'
    )
    parser.add_argument(
        '--output-html',
        default='../Tests/test_note_7.html',
        help='Chemin du fichier HTML de sortie (défaut: ../Tests/test_note_7.html)'
    )
    parser.add_argument(
        '--output-trace',
        default='../Tests/trace_note_7.json',
        help='Chemin du fichier de trace JSON (défaut: ../Tests/trace_note_7.json)'
    )
    
    args = parser.parse_args()
    
    # Créer le calculateur
    calculateur = CalculateurNote7(args.fichier_balance)
    
    # Exécuter le calcul complet
    calculateur.executer(
        fichier_html=args.output_html,
        fichier_trace=args.output_trace
    )
