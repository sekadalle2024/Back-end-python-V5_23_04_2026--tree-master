"""
Script pour créer les fichiers Excel de test pour les fixtures.

Ce script génère:
1. balance_demo_n_n1_n2.xlsx - Balance complète valide
2. balance_incomplete.xlsx - Balance sans onglet N-2
3. balance_invalid_format.xlsx - Balance avec colonnes manquantes
"""

import pandas as pd
import os


def create_balance_demo():
    """Crée une balance de démonstration complète avec 3 exercices."""
    
    # Données de test cohérentes
    comptes_data = [
        # Immobilisations incorporelles
        {'Numéro': '211', 'Intitulé': 'Frais de recherche et développement', 
         'Ant Débit': 1500000, 'Ant Crédit': 0, 'Débit': 500000, 'Crédit': 0, 
         'Solde Débit': 2000000, 'Solde Crédit': 0},
        {'Numéro': '212', 'Intitulé': 'Brevets, licences, logiciels', 
         'Ant Débit': 800000, 'Ant Crédit': 0, 'Débit': 200000, 'Crédit': 0, 
         'Solde Débit': 1000000, 'Solde Crédit': 0},
        {'Numéro': '2811', 'Intitulé': 'Amortissements frais R&D', 
         'Ant Débit': 0, 'Ant Crédit': 300000, 'Débit': 0, 'Crédit': 200000, 
         'Solde Débit': 0, 'Solde Crédit': 500000},
        {'Numéro': '2812', 'Intitulé': 'Amortissements brevets', 
         'Ant Débit': 0, 'Ant Crédit': 150000, 'Débit': 0, 'Crédit': 100000, 
         'Solde Débit': 0, 'Solde Crédit': 250000},
        
        # Immobilisations corporelles
        {'Numéro': '221', 'Intitulé': 'Terrains', 
         'Ant Débit': 5000000, 'Ant Crédit': 0, 'Débit': 0, 'Crédit': 0, 
         'Solde Débit': 5000000, 'Solde Crédit': 0},
        {'Numéro': '222', 'Intitulé': 'Bâtiments', 
         'Ant Débit': 10000000, 'Ant Crédit': 0, 'Débit': 2000000, 'Crédit': 0, 
         'Solde Débit': 12000000, 'Solde Crédit': 0},
        {'Numéro': '2822', 'Intitulé': 'Amortissements bâtiments', 
         'Ant Débit': 0, 'Ant Crédit': 2000000, 'Débit': 0, 'Crédit': 500000, 
         'Solde Débit': 0, 'Solde Crédit': 2500000},
        
        # Capital et réserves
        {'Numéro': '101', 'Intitulé': 'Capital social', 
         'Ant Débit': 0, 'Ant Crédit': 10000000, 'Débit': 0, 'Crédit': 0, 
         'Solde Débit': 0, 'Solde Crédit': 10000000},
        {'Numéro': '111', 'Intitulé': 'Réserve légale', 
         'Ant Débit': 0, 'Ant Crédit': 500000, 'Débit': 0, 'Crédit': 100000, 
         'Solde Débit': 0, 'Solde Crédit': 600000},
        
        # Charges
        {'Numéro': '601', 'Intitulé': 'Achats de marchandises', 
         'Ant Débit': 0, 'Ant Crédit': 0, 'Débit': 3000000, 'Crédit': 0, 
         'Solde Débit': 3000000, 'Solde Crédit': 0},
        {'Numéro': '66', 'Intitulé': 'Charges de personnel', 
         'Ant Débit': 0, 'Ant Crédit': 0, 'Débit': 1500000, 'Crédit': 0, 
         'Solde Débit': 1500000, 'Solde Crédit': 0},
        {'Numéro': '681', 'Intitulé': 'Dotations aux amortissements', 
         'Ant Débit': 0, 'Ant Crédit': 0, 'Débit': 800000, 'Crédit': 0, 
         'Solde Débit': 800000, 'Solde Crédit': 0},
        
        # Produits
        {'Numéro': '701', 'Intitulé': 'Ventes de marchandises', 
         'Ant Débit': 0, 'Ant Crédit': 0, 'Débit': 0, 'Crédit': 5000000, 
         'Solde Débit': 0, 'Solde Crédit': 5000000},
    ]
    
    # Créer les DataFrames pour les 3 exercices
    df_n = pd.DataFrame(comptes_data)
    
    # Pour N-1, ajuster les soldes (Solde N devient Ant N+1)
    df_n1 = df_n.copy()
    df_n1['Solde Débit'] = df_n['Ant Débit']
    df_n1['Solde Crédit'] = df_n['Ant Crédit']
    df_n1['Ant Débit'] = df_n['Ant Débit'] * 0.8
    df_n1['Ant Crédit'] = df_n['Ant Crédit'] * 0.8
    df_n1['Débit'] = df_n['Débit'] * 0.9
    df_n1['Crédit'] = df_n['Crédit'] * 0.9
    
    # Pour N-2
    df_n2 = df_n1.copy()
    df_n2['Solde Débit'] = df_n1['Ant Débit']
    df_n2['Solde Crédit'] = df_n1['Ant Crédit']
    df_n2['Ant Débit'] = df_n1['Ant Débit'] * 0.8
    df_n2['Ant Crédit'] = df_n1['Ant Crédit'] * 0.8
    df_n2['Débit'] = df_n1['Débit'] * 0.9
    df_n2['Crédit'] = df_n1['Crédit'] * 0.9
    
    # Créer le fichier Excel avec 3 onglets
    output_path = os.path.join(os.path.dirname(__file__), 'balance_demo_n_n1_n2.xlsx')
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_n.to_excel(writer, sheet_name='BALANCE N', index=False)
        df_n1.to_excel(writer, sheet_name='BALANCE N-1', index=False)
        df_n2.to_excel(writer, sheet_name='BALANCE N-2', index=False)
    
    print(f"✓ Créé: {output_path}")
    return output_path


def create_balance_incomplete():
    """Crée une balance incomplète (sans onglet N-2)."""
    
    comptes_data = [
        {'Numéro': '211', 'Intitulé': 'Frais de recherche', 
         'Ant Débit': 1000000, 'Ant Crédit': 0, 'Débit': 300000, 'Crédit': 0, 
         'Solde Débit': 1300000, 'Solde Crédit': 0},
        {'Numéro': '2811', 'Intitulé': 'Amortissements frais R&D', 
         'Ant Débit': 0, 'Ant Crédit': 200000, 'Débit': 0, 'Crédit': 100000, 
         'Solde Débit': 0, 'Solde Crédit': 300000},
    ]
    
    df = pd.DataFrame(comptes_data)
    
    # Créer le fichier Excel avec seulement 2 onglets (N et N-1)
    output_path = os.path.join(os.path.dirname(__file__), 'balance_incomplete.xlsx')
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='BALANCE N', index=False)
        df.to_excel(writer, sheet_name='BALANCE N-1', index=False)
    
    print(f"✓ Créé: {output_path}")
    return output_path


def create_balance_invalid_format():
    """Crée une balance avec format invalide (colonnes manquantes)."""
    
    # Données avec colonnes manquantes (pas de "Débit" ni "Crédit")
    comptes_data = [
        {'Numéro': '211', 'Intitulé': 'Frais de recherche', 
         'Ant Débit': 1000000, 'Ant Crédit': 0, 
         'Solde Débit': 1300000, 'Solde Crédit': 0},
        {'Numéro': '2811', 'Intitulé': 'Amortissements', 
         'Ant Débit': 0, 'Ant Crédit': 200000, 
         'Solde Débit': 0, 'Solde Crédit': 300000},
    ]
    
    df = pd.DataFrame(comptes_data)
    
    # Créer le fichier Excel
    output_path = os.path.join(os.path.dirname(__file__), 'balance_invalid_format.xlsx')
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='BALANCE N', index=False)
    
    print(f"✓ Créé: {output_path}")
    return output_path


if __name__ == '__main__':
    print("Création des fichiers de test...")
    print()
    
    create_balance_demo()
    create_balance_incomplete()
    create_balance_invalid_format()
    
    print()
    print("✓ Tous les fichiers de test ont été créés avec succès!")
    print()
    print("Fichiers créés:")
    print("  - balance_demo_n_n1_n2.xlsx (balance complète)")
    print("  - balance_incomplete.xlsx (sans N-2)")
    print("  - balance_invalid_format.xlsx (colonnes manquantes)")
    print("  - correspondances_test.json (mapping de test)")
