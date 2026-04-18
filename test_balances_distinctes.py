# -*- coding: utf-8 -*-
"""
Test pour vérifier que les balances N et N-1 sont bien distinctes
"""
import pandas as pd
import sys
import io

# Forcer UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("TEST DES BALANCES N ET N-1 DISTINCTES")
print("="*80)

# Charger les 3 balances
df_n = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N (2024)')
df_n1 = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N-1 (2023)')
df_n2 = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N-2 (2022)')

print(f"\n✅ Balance N: {len(df_n)} lignes")
print(f"✅ Balance N-1: {len(df_n1)} lignes")
print(f"✅ Balance N-2: {len(df_n2)} lignes")

# Identifier les colonnes de soldes
print(f"\nColonnes Balance N: {df_n.columns.tolist()}")

# Trouver les colonnes de soldes
solde_debit_col = None
solde_credit_col = None

for col in df_n.columns:
    col_lower = str(col).lower()
    if 'solde' in col_lower and 'débit' in col_lower:
        solde_debit_col = col
    elif 'solde' in col_lower and 'crédit' in col_lower:
        solde_credit_col = col

print(f"\nColonne Solde Débit: {solde_debit_col}")
print(f"Colonne Solde Crédit: {solde_credit_col}")

# Comparer quelques comptes clés
comptes_test = ['101000', '411000', '601000', '701000', '521000']

print("\n" + "="*80)
print("COMPARAISON DES COMPTES CLÉS")
print("="*80)

# Fonction pour convertir en float
def to_float(val):
    try:
        return float(str(val).replace(' ', '').replace(',', '.'))
    except:
        return 0.0

for compte in comptes_test:
    # Chercher dans les 3 balances
    row_n = df_n[df_n.iloc[:, 0].astype(str) == compte]
    row_n1 = df_n1[df_n1.iloc[:, 0].astype(str) == compte]
    row_n2 = df_n2[df_n2.iloc[:, 0].astype(str) == compte]
    
    if not row_n.empty and not row_n1.empty and not row_n2.empty:
        solde_n_debit = to_float(row_n[solde_debit_col].values[0]) if solde_debit_col else 0
        solde_n_credit = to_float(row_n[solde_credit_col].values[0]) if solde_credit_col else 0
        
        solde_n1_debit = to_float(row_n1[solde_debit_col].values[0]) if solde_debit_col else 0
        solde_n1_credit = to_float(row_n1[solde_credit_col].values[0]) if solde_credit_col else 0
        
        solde_n2_debit = to_float(row_n2[solde_debit_col].values[0]) if solde_debit_col else 0
        solde_n2_credit = to_float(row_n2[solde_credit_col].values[0]) if solde_credit_col else 0
        
        print(f"\nCompte {compte}:")
        print(f"  N   : Débit={solde_n_debit:>15,.2f}  Crédit={solde_n_credit:>15,.2f}")
        print(f"  N-1 : Débit={solde_n1_debit:>15,.2f}  Crédit={solde_n1_credit:>15,.2f}")
        print(f"  N-2 : Débit={solde_n2_debit:>15,.2f}  Crédit={solde_n2_credit:>15,.2f}")
        
        # Vérifier si tous différents
        n_vs_n1 = (solde_n_debit != solde_n1_debit or solde_n_credit != solde_n1_credit)
        n1_vs_n2 = (solde_n1_debit != solde_n2_debit or solde_n1_credit != solde_n2_credit)
        n_vs_n2 = (solde_n_debit != solde_n2_debit or solde_n_credit != solde_n2_credit)
        
        if n_vs_n1 and n1_vs_n2 and n_vs_n2:
            print(f"  ✅ TOUS DIFFÉRENTS")
        elif n_vs_n1 or n1_vs_n2 or n_vs_n2:
            print(f"  ⚠️ PARTIELLEMENT DIFFÉRENTS")
        else:
            print(f"  ❌ TOUS IDENTIQUES")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

# Calculer le total des soldes débiteurs pour chaque balance
total_n = df_n[solde_debit_col].apply(to_float).sum() if solde_debit_col else 0
total_n1 = df_n1[solde_debit_col].apply(to_float).sum() if solde_debit_col else 0
total_n2 = df_n2[solde_debit_col].apply(to_float).sum() if solde_debit_col else 0

print(f"\nTotal Soldes Débiteurs N: {total_n:,.2f}")
print(f"Total Soldes Débiteurs N-1: {total_n1:,.2f}")
print(f"Total Soldes Débiteurs N-2: {total_n2:,.2f}")

diff_n_n1 = abs(total_n - total_n1)
diff_n1_n2 = abs(total_n1 - total_n2)
diff_n_n2 = abs(total_n - total_n2)

print(f"\nDifférence N vs N-1: {diff_n_n1:,.2f}")
print(f"Différence N-1 vs N-2: {diff_n1_n2:,.2f}")
print(f"Différence N vs N-2: {diff_n_n2:,.2f}")

if diff_n_n1 > 1 and diff_n1_n2 > 1 and diff_n_n2 > 1:
    print("\n✅ Les 3 balances (N, N-1, N-2) sont TOUTES DISTINCTES")
elif diff_n_n1 > 1 or diff_n1_n2 > 1 or diff_n_n2 > 1:
    print("\n⚠️ Les balances sont PARTIELLEMENT DISTINCTES")
else:
    print("\n❌ Les balances sont IDENTIQUES")
