# -*- coding: utf-8 -*-
"""
Crée 2 fichiers Excel séparés à partir du fichier multi-feuilles
"""
import pandas as pd

print("Création de fichiers Excel séparés...")

# Lire les 2 feuilles
balance_n = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N (2024)')
balance_n1 = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N-1 (2023)')

# Sauvegarder en fichiers séparés
balance_n.to_excel('BALANCE_N_2024.xlsx', index=False)
balance_n1.to_excel('BALANCE_N1_2023.xlsx', index=False)

print(f"✅ BALANCE_N_2024.xlsx créé: {len(balance_n)} lignes")
print(f"✅ BALANCE_N1_2023.xlsx créé: {len(balance_n1)} lignes")
