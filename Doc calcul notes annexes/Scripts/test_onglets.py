import pandas as pd

xls = pd.ExcelFile('P000 -BALANCE DEMO N_N-1_N-2.xls')
print('Onglets disponibles:')
for i, name in enumerate(xls.sheet_names):
    print(f'{i}: [{name}] (longueur: {len(name)} caractères)')
