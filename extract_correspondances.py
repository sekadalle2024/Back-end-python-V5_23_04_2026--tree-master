"""
Script pour extraire les correspondances du fichier Excel vers JSON
"""
import pandas as pd
import json
import re

def parse_racines_comptes(comptes_str: str) -> list:
    """Parse une chaîne de racines de comptes"""
    racines = []
    comptes_str = comptes_str.replace('–', ',').replace('-', ',')
    comptes_str = comptes_str.replace(' p', '').replace('p', '')
    comptes_str = comptes_str.replace('(sauf', ',').replace(')', '')
    
    parts = comptes_str.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        match = re.match(r'(\d+)', part)
        if match:
            racine = match.group(1)
            if 1 <= len(racine) <= 4:
                racines.append(racine)
    return racines

# Charger le fichier Excel
df = pd.read_excel('Tableau correspondance.xlsx', sheet_name=0, header=None)

correspondances = {
    'bilan_actif': [],
    'bilan_passif': [],
    'charges': [],
    'produits': []
}

current_section = None

for idx, row in df.iterrows():
    ref = str(row[0]).strip() if pd.notna(row[0]) else ''
    libelle = str(row[1]).strip() if pd.notna(row[1]) else ''
    comptes = str(row[2]).strip() if pd.notna(row[2]) else ''
    
    # Détecter les sections
    if 'BILAN' in libelle.upper() and 'ACTIF' in libelle.upper():
        current_section = 'bilan_actif'
        print(f"Section: BILAN ACTIF (ligne {idx})")
        continue
    elif 'BILAN' in libelle.upper() and 'PASSIF' in libelle.upper():
        current_section = 'bilan_passif'
        print(f"Section: BILAN PASSIF (ligne {idx})")
        continue
    elif 'COMPTE DE RÉSULTAT' in libelle.upper() or 'COMPTE DE RESULTAT' in libelle.upper():
        if 'CHARGE' in libelle.upper():
            current_section = 'charges'
            print(f"Section: CHARGES (ligne {idx})")
        elif 'PRODUIT' in libelle.upper():
            current_section = 'produits'
            print(f"Section: PRODUITS (ligne {idx})")
        continue
    
    # Ignorer les lignes d'en-tête et vides
    if not ref or ref == 'nan' or 'Réf' in ref or len(ref) > 3:
        continue
    
    # Ignorer si pas de comptes
    if not comptes or comptes == 'nan':
        continue
    
    # Parser les racines
    racines = parse_racines_comptes(comptes)
    
    if racines and current_section:
        correspondances[current_section].append({
            'ref': ref,
            'libelle': libelle,
            'racines': racines
        })
        print(f"  {ref} - {libelle}: {racines}")

# Sauvegarder en JSON
with open('correspondances_syscohada.json', 'w', encoding='utf-8') as f:
    json.dump(correspondances, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fichier JSON créé avec succès!")
print(f"   - Bilan Actif: {len(correspondances['bilan_actif'])} postes")
print(f"   - Bilan Passif: {len(correspondances['bilan_passif'])} postes")
print(f"   - Charges: {len(correspondances['charges'])} postes")
print(f"   - Produits: {len(correspondances['produits'])} postes")
