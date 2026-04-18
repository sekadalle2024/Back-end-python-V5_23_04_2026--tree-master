#!/usr/bin/env python3
"""
Script de création de fichier Excel de test pour Lead Balance
Version: 1.0.0
Date: 2026-03-22
"""

import pandas as pd
import sys
from pathlib import Path

def create_test_balance(filename="TEST_BALANCE.xlsx"):
    """
    Crée un fichier Excel de test pour Lead Balance avec des données réalistes
    """
    print(f"📊 Création du fichier de test : {filename}")
    print("")
    
    # Données Balance N (année actuelle)
    data_n = {
        'Numéro': [
            # Classe 1 - Capitaux
            '101', '106', '12', '13',
            # Classe 2 - Immobilisations
            '211', '213', '215', '218', '241', '244',
            # Classe 3 - Stocks
            '31', '32', '37',
            # Classe 4 - Tiers
            '401', '411', '421', '431', '441', '445', '471',
            # Classe 5 - Trésorerie
            '512', '521', '531',
            # Classe 6 - Charges
            '601', '605', '621', '622', '631', '641', '661', '671',
            # Classe 7 - Produits
            '701', '706', '707', '771', '781'
        ],
        'Intitulé': [
            # Classe 1
            'Capital social', 'Réserves', 'Résultat de l\'exercice', 'Subventions d\'investissement',
            # Classe 2
            'Terrains', 'Constructions', 'Matériel et outillage', 'Amortissements des immobilisations',
            'Matériel de transport', 'Mobilier de bureau',
            # Classe 3
            'Marchandises', 'Matières premières', 'Stocks de produits finis',
            # Classe 4
            'Fournisseurs', 'Clients', 'Personnel', 'Sécurité sociale', 'État - Impôts sur les bénéfices',
            'État - TVA', 'Comptes transitoires',
            # Classe 5
            'Banque', 'Chèques postaux', 'Caisse',
            # Classe 6
            'Achats de marchandises', 'Achats de matières premières', 'Locations', 'Entretien et réparations',
            'Publicité', 'Impôts et taxes', 'Charges de personnel', 'Charges financières',
            # Classe 7
            'Ventes de marchandises', 'Prestations de services', 'Produits accessoires',
            'Produits financiers', 'Transferts de charges'
        ],
        'Solde Débit': [
            # Classe 1
            0, 0, 0, 0,
            # Classe 2
            15000000, 25000000, 8000000, 0, 5000000, 2000000,
            # Classe 3
            3500000, 2800000, 4200000,
            # Classe 4
            0, 8500000, 0, 0, 0, 0, 500000,
            # Classe 5
            12000000, 3500000, 850000,
            # Classe 6
            45000000, 18000000, 2400000, 1800000, 3200000, 2500000, 28000000, 1200000,
            # Classe 7
            0, 0, 0, 0, 0
        ],
        'Solde Crédit': [
            # Classe 1
            50000000, 8000000, 15000000, 2000000,
            # Classe 2
            0, 0, 0, 12000000, 0, 0,
            # Classe 3
            0, 0, 0,
            # Classe 4
            6500000, 0, 3200000, 1800000, 2500000, 1200000, 0,
            # Classe 5
            0, 0, 0,
            # Classe 6
            0, 0, 0, 0, 0, 0, 0, 0,
            # Classe 7
            95000000, 12000000, 1500000, 450000, 800000
        ]
    }
    
    # Données Balance N-1 (année précédente)
    # Quelques comptes en moins, quelques montants différents
    data_n_1 = {
        'Numéro': [
            # Classe 1
            '101', '106', '12',
            # Classe 2
            '211', '213', '215', '218', '241',
            # Classe 3
            '31', '32',
            # Classe 4
            '401', '411', '421', '431', '441', '445',
            # Classe 5
            '512', '521', '531',
            # Classe 6
            '601', '605', '621', '622', '631', '641', '661', '671',
            # Classe 7
            '701', '706', '707', '771'
        ],
        'Intitulé': [
            # Classe 1
            'Capital social', 'Réserves', 'Résultat de l\'exercice',
            # Classe 2
            'Terrains', 'Constructions', 'Matériel et outillage', 'Amortissements des immobilisations',
            'Matériel de transport',
            # Classe 3
            'Marchandises', 'Matières premières',
            # Classe 4
            'Fournisseurs', 'Clients', 'Personnel', 'Sécurité sociale', 'État - Impôts sur les bénéfices',
            'État - TVA',
            # Classe 5
            'Banque', 'Chèques postaux', 'Caisse',
            # Classe 6
            'Achats de marchandises', 'Achats de matières premières', 'Locations', 'Entretien et réparations',
            'Publicité', 'Impôts et taxes', 'Charges de personnel', 'Charges financières',
            # Classe 7
            'Ventes de marchandises', 'Prestations de services', 'Produits accessoires',
            'Produits financiers'
        ],
        'Solde Débit': [
            # Classe 1
            0, 0, 0,
            # Classe 2
            15000000, 20000000, 6000000, 0, 4000000,
            # Classe 3
            2800000, 2200000,
            # Classe 4
            0, 7200000, 0, 0, 0, 0,
            # Classe 5
            9500000, 2800000, 650000,
            # Classe 6
            38000000, 15000000, 2200000, 1500000, 2800000, 2200000, 24000000, 950000,
            # Classe 7
            0, 0, 0, 0
        ],
        'Solde Crédit': [
            # Classe 1
            50000000, 5000000, 12000000,
            # Classe 2
            0, 0, 0, 10000000, 0,
            # Classe 3
            0, 0,
            # Classe 4
            5800000, 0, 2900000, 1600000, 2200000, 1000000,
            # Classe 5
            0, 0, 0,
            # Classe 6
            0, 0, 0, 0, 0, 0, 0, 0,
            # Classe 7
            82000000, 10000000, 1200000, 380000
        ]
    }
    
    # Créer les DataFrames
    df_n = pd.DataFrame(data_n)
    df_n_1 = pd.DataFrame(data_n_1)
    
    # Statistiques
    print("📈 Statistiques Balance N:")
    print(f"   Nombre de comptes: {len(df_n)}")
    print(f"   Total Débit: {df_n['Solde Débit'].sum():,.0f}")
    print(f"   Total Crédit: {df_n['Solde Crédit'].sum():,.0f}")
    print("")
    
    print("📉 Statistiques Balance N-1:")
    print(f"   Nombre de comptes: {len(df_n_1)}")
    print(f"   Total Débit: {df_n_1['Solde Débit'].sum():,.0f}")
    print(f"   Total Crédit: {df_n_1['Solde Crédit'].sum():,.0f}")
    print("")
    
    # Comptes nouveaux et supprimés
    comptes_n = set(df_n['Numéro'])
    comptes_n_1 = set(df_n_1['Numéro'])
    nouveaux = comptes_n - comptes_n_1
    supprimes = comptes_n_1 - comptes_n
    
    print(f"🆕 Comptes nouveaux en N: {len(nouveaux)}")
    if nouveaux:
        print(f"   {', '.join(sorted(nouveaux))}")
    print("")
    
    print(f"🗑️  Comptes supprimés en N: {len(supprimes)}")
    if supprimes:
        print(f"   {', '.join(sorted(supprimes))}")
    print("")
    
    # Créer le fichier Excel
    filepath = Path(__file__).parent / filename
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df_n.to_excel(writer, sheet_name='Balance N', index=False)
        df_n_1.to_excel(writer, sheet_name='Balance N-1', index=False)
    
    print(f"✅ Fichier créé : {filepath}")
    print(f"   Taille : {filepath.stat().st_size / 1024:.2f} KB")
    print("")
    
    print("🧪 Pour tester:")
    print("   1. Démarrer le backend: python main.py")
    print("   2. Démarrer le frontend: npm run dev")
    print("   3. Dans le chat: Lead_balance")
    print(f"   4. Sélectionner: {filename}")
    print("")
    
    return filepath

def main():
    """Point d'entrée principal"""
    print("=" * 70)
    print("CRÉATION DE FICHIER EXCEL DE TEST - LEAD BALANCE")
    print("=" * 70)
    print("")
    
    # Nom du fichier
    filename = "TEST_BALANCE.xlsx"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    try:
        filepath = create_test_balance(filename)
        print("=" * 70)
        print("✅ SUCCÈS")
        print("=" * 70)
        return 0
    except Exception as e:
        print("=" * 70)
        print("❌ ERREUR")
        print("=" * 70)
        print(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
