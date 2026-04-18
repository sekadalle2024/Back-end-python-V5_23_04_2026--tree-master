# -*- coding: utf-8 -*-
"""
Script pour créer des balances cohérentes sur 3 exercices
avec une évolution réaliste d'une entreprise
"""
import pandas as pd
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("CRÉATION DE BALANCES COHÉRENTES SUR 3 EXERCICES")
print("="*80)

# Charger la balance démo (exercice N)
balance_n = pd.read_excel('P000 -BALANCE DEMO.xls')
print(f"\n✅ Balance N (2024) chargée: {len(balance_n)} comptes")

# Identifier les colonnes
col_numero = balance_n.columns[0]
col_intitule = balance_n.columns[1]
col_solde_debit = ' Solde  Débit  '
col_solde_credit = '  Solde Crédit'

def to_float(val):
    """Convertit une valeur en float"""
    try:
        return float(str(val).replace(' ', '').replace(',', '.'))
    except:
        return 0.0

def to_string(val):
    """Convertit un float en string formaté"""
    if abs(val) < 0.01:
        return '0'
    return f"{val:,.2f}".replace(',', ' ')

# Créer Balance N-1 (2023) avec croissance cohérente de -5%
print("\n📊 Création Balance N-1 (2023) - Croissance -5%")
balance_n1 = balance_n.copy()

for idx, row in balance_n1.iterrows():
    numero = str(row[col_numero]).strip()
    
    if not numero or numero == 'nan' or not numero[0].isdigit():
        continue
    
    classe = numero[0]
    
    # Récupérer les soldes N
    solde_d_n = to_float(row[col_solde_debit])
    solde_c_n = to_float(row[col_solde_credit])
    
    # Appliquer une décroissance de 5% pour N-1
    # Les comptes de structure (capital, immobilisations) varient moins
    if classe in ['1', '2']:  # Capitaux et immobilisations: -2%
        facteur = 0.98
    elif classe in ['3']:  # Stocks: -5%
        facteur = 0.95
    elif classe in ['4']:  # Tiers: -5%
        facteur = 0.95
    elif classe in ['5']:  # Trésorerie: -8%
        facteur = 0.92
    elif classe in ['6', '7']:  # Charges et produits: -5%
        facteur = 0.95
    else:
        facteur = 0.95
    
    solde_d_n1 = solde_d_n * facteur
    solde_c_n1 = solde_c_n * facteur
    
    balance_n1.at[idx, col_solde_debit] = to_string(solde_d_n1)
    balance_n1.at[idx, col_solde_credit] = to_string(solde_c_n1)

# Créer Balance N-2 (2022) avec croissance cohérente de -10% par rapport à N
print("📊 Création Balance N-2 (2022) - Croissance -10% par rapport à N")
balance_n2 = balance_n.copy()

for idx, row in balance_n2.iterrows():
    numero = str(row[col_numero]).strip()
    
    if not numero or numero == 'nan' or not numero[0].isdigit():
        continue
    
    classe = numero[0]
    
    # Récupérer les soldes N
    solde_d_n = to_float(row[col_solde_debit])
    solde_c_n = to_float(row[col_solde_credit])
    
    # Appliquer une décroissance de 10% pour N-2
    if classe in ['1', '2']:  # Capitaux et immobilisations: -5%
        facteur = 0.95
    elif classe in ['3']:  # Stocks: -10%
        facteur = 0.90
    elif classe in ['4']:  # Tiers: -10%
        facteur = 0.90
    elif classe in ['5']:  # Trésorerie: -15%
        facteur = 0.85
    elif classe in ['6', '7']:  # Charges et produits: -10%
        facteur = 0.90
    else:
        facteur = 0.90
    
    solde_d_n2 = solde_d_n * facteur
    solde_c_n2 = solde_c_n * facteur
    
    balance_n2.at[idx, col_solde_debit] = to_string(solde_d_n2)
    balance_n2.at[idx, col_solde_credit] = to_string(solde_c_n2)

# Créer le fichier Excel avec 3 onglets
output_file = 'BALANCES_N_N1_N2.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    balance_n.to_excel(writer, sheet_name='Balance N (2024)', index=False)
    balance_n1.to_excel(writer, sheet_name='Balance N-1 (2023)', index=False)
    balance_n2.to_excel(writer, sheet_name='Balance N-2 (2022)', index=False)

print(f"\n✅ Fichier créé: {output_file}")
print(f"   - Onglet 1: Balance N (2024) - {len(balance_n)} comptes")
print(f"   - Onglet 2: Balance N-1 (2023) - {len(balance_n1)} comptes (croissance -5%)")
print(f"   - Onglet 3: Balance N-2 (2022) - {len(balance_n2)} comptes (croissance -10%)")

# Vérifier quelques comptes clés
print("\n" + "="*80)
print("VÉRIFICATION DES COMPTES CLÉS")
print("="*80)

comptes_test = ['101000', '411000', '521000', '601000', '701000']

for compte in comptes_test:
    row_n = balance_n[balance_n[col_numero].astype(str).str.strip() == compte]
    row_n1 = balance_n1[balance_n1[col_numero].astype(str).str.strip() == compte]
    row_n2 = balance_n2[balance_n2[col_numero].astype(str).str.strip() == compte]
    
    if not row_n.empty and not row_n1.empty and not row_n2.empty:
        intitule = str(row_n[col_intitule].values[0])
        
        # Soldes débiteurs
        sd_n = to_float(row_n[col_solde_debit].values[0])
        sd_n1 = to_float(row_n1[col_solde_debit].values[0])
        sd_n2 = to_float(row_n2[col_solde_debit].values[0])
        
        # Soldes créditeurs
        sc_n = to_float(row_n[col_solde_credit].values[0])
        sc_n1 = to_float(row_n1[col_solde_credit].values[0])
        sc_n2 = to_float(row_n2[col_solde_credit].values[0])
        
        print(f"\n{compte} - {intitule}")
        
        if sd_n > 0 or sd_n1 > 0 or sd_n2 > 0:
            print(f"  Solde Débit:")
            print(f"    N-2 (2022): {sd_n2:>15,.2f}")
            print(f"    N-1 (2023): {sd_n1:>15,.2f}  ({((sd_n1/sd_n2-1)*100) if sd_n2 > 0 else 0:+.1f}%)")
            print(f"    N   (2024): {sd_n:>15,.2f}  ({((sd_n/sd_n1-1)*100) if sd_n1 > 0 else 0:+.1f}%)")
        
        if sc_n > 0 or sc_n1 > 0 or sc_n2 > 0:
            print(f"  Solde Crédit:")
            print(f"    N-2 (2022): {sc_n2:>15,.2f}")
            print(f"    N-1 (2023): {sc_n1:>15,.2f}  ({((sc_n1/sc_n2-1)*100) if sc_n2 > 0 else 0:+.1f}%)")
            print(f"    N   (2024): {sc_n:>15,.2f}  ({((sc_n/sc_n1-1)*100) if sc_n1 > 0 else 0:+.1f}%)")

print("\n" + "="*80)
print("✅ BALANCES COHÉRENTES CRÉÉES")
print("="*80)
print("\nÉvolution de l'entreprise:")
print("  2022 (N-2): Année de référence (100%)")
print("  2023 (N-1): Croissance +5.3% (facteur 1.053)")
print("  2024 (N):   Croissance +11.1% par rapport à N-2 (facteur 1.111)")
print("\nCette évolution reflète une entreprise en croissance régulière.")
