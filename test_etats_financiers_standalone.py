# -*- coding: utf-8 -*-
"""
Script de test standalone pour les états financiers
"""
import pandas as pd
import numpy as np
import json
import sys
import io

# Forcer l'encodage UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("TEST DES ETATS FINANCIERS - VERSION STANDALONE")
print("="*80)

# Charger correspondances
print("\n1. Chargement correspondances...")
with open('correspondances_syscohada.json', 'r', encoding='utf-8') as f:
    correspondances = json.load(f)
print(f"   OK - {len(correspondances['bilan_actif'])} postes Actif")

# Charger balance
print("\n2. Chargement balance...")
balance_df = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N (2024)')
print(f"   OK - {len(balance_df)} comptes")

# Détecter colonnes
print("\n3. Detection colonnes...")
columns = balance_df.columns.tolist()
print(f"   Colonnes: {columns}")

col_map = {}
for idx, col in enumerate(columns):
    col_lower = str(col).lower().strip()
    col_clean = col_lower.replace(' ', '')
    
    if 'num' in col_clean or ('compte' in col_clean and idx == 0):
        col_map['numero'] = col
    elif 'intitul' in col_clean or 'libel' in col_clean:
        col_map['intitule'] = col
    elif 'solde' in col_clean and 'd' in col_clean and 'c' not in col_clean:
        col_map['solde_debit'] = col
    elif 'solde' in col_clean and 'c' in col_clean:
        col_map['solde_credit'] = col

print(f"   Mapping: {col_map}")

# Traiter balance
print("\n4. Traitement balance...")
results = {
    'bilan_actif': {},
    'bilan_passif': {},
    'charges': {},
    'produits': {}
}

controles = {
    'comptes_non_integres': [],
    'comptes_sens_inverse': [],
    'comptes_desequilibre': [],
    'statistiques': {
        'total_comptes_balance': 0,
        'comptes_integres': 0,
        'comptes_non_integres': 0
    }
}

def clean_number(value):
    if pd.isna(value) or value == '' or value is None:
        return 0.0
    try:
        return float(str(value).replace(' ', '').replace(',', '.'))
    except:
        return 0.0

def match_compte(numero, correspondances_section):
    for poste in correspondances_section:
        for racine in poste['racines']:
            if numero.startswith(racine):
                return poste
    return None

for _, row in balance_df.iterrows():
    numero = str(row.get(col_map['numero'], '')).strip()
    if not numero or numero == 'nan' or not numero[0].isdigit():
        continue
    
    controles['statistiques']['total_comptes_balance'] += 1
    
    intitule = str(row.get(col_map.get('intitule', ''), '')).strip()
    solde_debit = clean_number(row.get(col_map.get('solde_debit', ''), 0))
    solde_credit = clean_number(row.get(col_map.get('solde_credit', ''), 0))
    solde_net = solde_debit - solde_credit
    
    # Chercher correspondance
    compte_integre = False
    for section_name, section_correspondances in correspondances.items():
        poste = match_compte(numero, section_correspondances)
        if poste:
            ref = poste['ref']
            if ref not in results[section_name]:
                results[section_name][ref] = {
                    'ref': ref,
                    'libelle': poste['libelle'],
                    'montant': 0,
                    'comptes': []
                }
            
            montant_a_ajouter = solde_net
            if section_name == 'bilan_passif' or section_name == 'produits':
                montant_a_ajouter = -solde_net
            
            results[section_name][ref]['montant'] += montant_a_ajouter
            results[section_name][ref]['comptes'].append({
                'numero': numero,
                'intitule': intitule,
                'solde': solde_net
            })
            
            compte_integre = True
            controles['statistiques']['comptes_integres'] += 1
            break
    
    if not compte_integre and abs(solde_net) > 0.01:
        controles['comptes_non_integres'].append({
            'numero': numero,
            'intitule': intitule,
            'solde_net': solde_net
        })
        controles['statistiques']['comptes_non_integres'] += 1

# Calculer totaux
total_actif = sum(p['montant'] for p in results['bilan_actif'].values())
total_passif = sum(p['montant'] for p in results['bilan_passif'].values())
total_charges = sum(p['montant'] for p in results['charges'].values())
total_produits = sum(p['montant'] for p in results['produits'].values())
resultat_net = total_produits - total_charges

# Taux de couverture
if controles['statistiques']['total_comptes_balance'] > 0:
    controles['statistiques']['taux_couverture'] = (
        controles['statistiques']['comptes_integres'] / 
        controles['statistiques']['total_comptes_balance'] * 100
    )

# Equilibres
controles['equilibre_bilan'] = {
    'actif': total_actif,
    'passif': total_passif,
    'difference': total_actif - total_passif,
    'equilibre': abs(total_actif - total_passif) < 0.01
}

controles['equilibre_resultat'] = {
    'resultat_cr': resultat_net,
    'resultat_bilan': total_actif - total_passif,
    'difference': resultat_net - (total_actif - total_passif),
    'equilibre': abs(resultat_net - (total_actif - total_passif)) < 0.01
}

# Contrôle spécifique : Hypothèse d'affectation du résultat
passif_avec_resultat = total_passif + resultat_net
difference_apres_affectation = total_actif - passif_avec_resultat

controles['hypothese_affectation_resultat'] = {
    'resultat_net': resultat_net,
    'passif_avant_affectation': total_passif,
    'passif_apres_affectation': passif_avec_resultat,
    'actif': total_actif,
    'difference_avant': total_actif - total_passif,
    'difference_apres': difference_apres_affectation,
    'equilibre_apres_affectation': abs(difference_apres_affectation) < 0.01,
    'recommandation': 'Affecter le resultat au passif (compte 13)' if abs(difference_apres_affectation) < 0.01 else 'Verifier les ecritures comptables',
    'type_resultat': 'Benefice' if resultat_net > 0 else 'Perte' if resultat_net < 0 else 'Nul'
}

# Contrôle spécifique : Comptes avec sens anormal par nature
# Définir les règles de sens normal par nature de compte
regles_sens_normal = {
    # Classe 1 : Capitaux (normalement créditeurs)
    '101': {'sens': 'credit', 'nature': 'Capital social', 'gravite': 'critique'},
    '10': {'sens': 'credit', 'nature': 'Capital', 'gravite': 'critique'},
    '11': {'sens': 'credit', 'nature': 'Reserves', 'gravite': 'elevee'},
    '12': {'sens': 'credit', 'nature': 'Report a nouveau', 'gravite': 'moyenne'},
    '13': {'sens': 'variable', 'nature': 'Resultat', 'gravite': 'faible'},
    '14': {'sens': 'credit', 'nature': 'Subventions', 'gravite': 'elevee'},
    '16': {'sens': 'credit', 'nature': 'Emprunts', 'gravite': 'elevee'},
    
    # Classe 2 : Immobilisations (normalement débitrices)
    '21': {'sens': 'debit', 'nature': 'Immobilisations incorporelles', 'gravite': 'elevee'},
    '22': {'sens': 'debit', 'nature': 'Terrains', 'gravite': 'elevee'},
    '23': {'sens': 'debit', 'nature': 'Batiments', 'gravite': 'elevee'},
    '24': {'sens': 'debit', 'nature': 'Materiel', 'gravite': 'elevee'},
    '28': {'sens': 'credit', 'nature': 'Amortissements', 'gravite': 'moyenne'},
    '29': {'sens': 'credit', 'nature': 'Provisions', 'gravite': 'moyenne'},
    
    # Classe 3 : Stocks (normalement débiteurs)
    '31': {'sens': 'debit', 'nature': 'Marchandises', 'gravite': 'elevee'},
    '32': {'sens': 'debit', 'nature': 'Matieres premieres', 'gravite': 'elevee'},
    '33': {'sens': 'debit', 'nature': 'Autres approvisionnements', 'gravite': 'moyenne'},
    
    # Classe 4 : Tiers (sens variable selon le compte)
    '401': {'sens': 'credit', 'nature': 'Fournisseurs', 'gravite': 'moyenne'},
    '411': {'sens': 'debit', 'nature': 'Clients', 'gravite': 'moyenne'},
    '421': {'sens': 'credit', 'nature': 'Personnel', 'gravite': 'moyenne'},
    '43': {'sens': 'credit', 'nature': 'Organismes sociaux', 'gravite': 'elevee'},
    '44': {'sens': 'credit', 'nature': 'Etat', 'gravite': 'elevee'},
    
    # Classe 5 : Trésorerie (normalement débiteurs sauf banques créditrices)
    '52': {'sens': 'debit', 'nature': 'Banques', 'gravite': 'critique'},
    '53': {'sens': 'debit', 'nature': 'Etablissements financiers', 'gravite': 'critique'},
    '54': {'sens': 'debit', 'nature': 'Caisse', 'gravite': 'critique'},
    '57': {'sens': 'debit', 'nature': 'Regies d\'avances', 'gravite': 'elevee'},
    
    # Classe 6 : Charges (normalement débitrices)
    '60': {'sens': 'debit', 'nature': 'Achats', 'gravite': 'moyenne'},
    '61': {'sens': 'debit', 'nature': 'Transports', 'gravite': 'faible'},
    '62': {'sens': 'debit', 'nature': 'Services exterieurs', 'gravite': 'faible'},
    '63': {'sens': 'debit', 'nature': 'Autres services', 'gravite': 'faible'},
    '64': {'sens': 'debit', 'nature': 'Impots et taxes', 'gravite': 'moyenne'},
    '66': {'sens': 'debit', 'nature': 'Charges de personnel', 'gravite': 'elevee'},
    
    # Classe 7 : Produits (normalement créditeurs)
    '70': {'sens': 'credit', 'nature': 'Ventes', 'gravite': 'elevee'},
    '71': {'sens': 'credit', 'nature': 'Subventions d\'exploitation', 'gravite': 'moyenne'},
    '72': {'sens': 'credit', 'nature': 'Production immobilisee', 'gravite': 'faible'},
    '75': {'sens': 'credit', 'nature': 'Autres produits', 'gravite': 'faible'},
}

comptes_sens_anormal = []

for _, row in balance_df.iterrows():
    numero = str(row.get(col_map['numero'], '')).strip()
    if not numero or numero == 'nan' or not numero[0].isdigit():
        continue
    
    intitule = str(row.get(col_map.get('intitule', ''), '')).strip()
    solde_debit = clean_number(row.get(col_map.get('solde_debit', ''), 0))
    solde_credit = clean_number(row.get(col_map.get('solde_credit', ''), 0))
    solde_net = solde_debit - solde_credit
    
    if abs(solde_net) < 0.01:
        continue
    
    # Déterminer le sens réel
    sens_reel = 'debit' if solde_net > 0 else 'credit'
    
    # Chercher la règle applicable (du plus spécifique au plus général)
    regle = None
    for longueur in [6, 5, 4, 3, 2, 1]:
        racine = numero[:longueur]
        if racine in regles_sens_normal:
            regle = regles_sens_normal[racine]
            break
    
    if regle and regle['sens'] != 'variable' and regle['sens'] != sens_reel:
        comptes_sens_anormal.append({
            'numero': numero,
            'intitule': intitule,
            'nature': regle['nature'],
            'sens_attendu': regle['sens'],
            'sens_reel': sens_reel,
            'solde_net': solde_net,
            'solde_debit': solde_debit,
            'solde_credit': solde_credit,
            'gravite': regle['gravite'],
            'impact_potentiel': 'Desequilibre majeur' if regle['gravite'] == 'critique' else 'Anomalie comptable'
        })

controles['comptes_sens_anormal_par_nature'] = comptes_sens_anormal

# Afficher résultats
print("\n" + "="*80)
print("RESULTATS")
print("="*80)

print(f"\nTOTAUX:")
print(f"  Total Actif:    {total_actif:>20,.2f}")
print(f"  Total Passif:   {total_passif:>20,.2f}")
print(f"  Total Charges:  {total_charges:>20,.2f}")
print(f"  Total Produits: {total_produits:>20,.2f}")
print(f"  Resultat Net:   {resultat_net:>20,.2f}")

print("\n" + "="*80)
print("ETATS DE CONTROLE")
print("="*80)

stats = controles['statistiques']
print(f"\nSTATISTIQUES:")
print(f"  Total comptes:      {stats['total_comptes_balance']}")
print(f"  Comptes integres:   {stats['comptes_integres']}")
print(f"  Comptes non integres: {stats['comptes_non_integres']}")
print(f"  Taux couverture:    {stats.get('taux_couverture', 0):.2f}%")

eq_bilan = controles['equilibre_bilan']
print(f"\nEQUILIBRE BILAN:")
print(f"  Actif:      {eq_bilan['actif']:>20,.2f}")
print(f"  Passif:     {eq_bilan['passif']:>20,.2f}")
print(f"  Difference: {eq_bilan['difference']:>20,.2f}")
print(f"  Equilibre:  {'OUI' if eq_bilan['equilibre'] else 'NON'}")

eq_res = controles['equilibre_resultat']
print(f"\nCOHERENCE RESULTAT:")
print(f"  Resultat CR:    {eq_res['resultat_cr']:>20,.2f}")
print(f"  Resultat Bilan: {eq_res['resultat_bilan']:>20,.2f}")
print(f"  Difference:     {eq_res['difference']:>20,.2f}")
print(f"  Coherent:       {'OUI' if eq_res['equilibre'] else 'NON'}")

# Hypothèse d'affectation
hyp_affect = controles.get('hypothese_affectation_resultat', {})
if hyp_affect:
    print(f"\nHYPOTHESE D'AFFECTATION DU RESULTAT:")
    print(f"  Type resultat:  {hyp_affect['type_resultat']}")
    print(f"  Montant:        {hyp_affect['resultat_net']:>20,.2f}")
    print(f"\n  SITUATION ACTUELLE:")
    print(f"    Actif:        {hyp_affect['actif']:>20,.2f}")
    print(f"    Passif:       {hyp_affect['passif_avant_affectation']:>20,.2f}")
    print(f"    Difference:   {hyp_affect['difference_avant']:>20,.2f}")
    print(f"\n  HYPOTHESE (si resultat affecte au passif):")
    print(f"    Passif+Res:   {hyp_affect['passif_apres_affectation']:>20,.2f}")
    print(f"    Difference:   {hyp_affect['difference_apres']:>20,.2f}")
    print(f"    Equilibre:    {'OUI' if hyp_affect['equilibre_apres_affectation'] else 'NON'}")
    print(f"\n  RECOMMANDATION: {hyp_affect['recommandation']}")

if controles['comptes_non_integres']:
    print(f"\nCOMPTES NON INTEGRES: {len(controles['comptes_non_integres'])}")
    print("  Top 10:")
    for i, c in enumerate(controles['comptes_non_integres'][:10], 1):
        print(f"    {i}. {c['numero']:10} {c['intitule'][:40]:40} {c['solde_net']:>15,.2f}")

# Comptes avec sens anormal par nature
comptes_anormaux = controles.get('comptes_sens_anormal_par_nature', [])
if comptes_anormaux:
    print(f"\nCOMPTES AVEC SENS ANORMAL PAR NATURE: {len(comptes_anormaux)}")
    
    # Grouper par gravité
    critiques = [c for c in comptes_anormaux if c['gravite'] == 'critique']
    eleves = [c for c in comptes_anormaux if c['gravite'] == 'elevee']
    moyens = [c for c in comptes_anormaux if c['gravite'] == 'moyenne']
    
    if critiques:
        print(f"\n  CRITIQUES ({len(critiques)}) - Desequilibre majeur:")
        for i, c in enumerate(critiques[:5], 1):
            print(f"    {i}. {c['numero']:10} {c['nature']:30} Attendu: {c['sens_attendu']:6} Reel: {c['sens_reel']:6} Solde: {c['solde_net']:>15,.2f}")
    
    if eleves:
        print(f"\n  ELEVES ({len(eleves)}) - Anomalie comptable:")
        for i, c in enumerate(eleves[:5], 1):
            print(f"    {i}. {c['numero']:10} {c['nature']:30} Attendu: {c['sens_attendu']:6} Reel: {c['sens_reel']:6} Solde: {c['solde_net']:>15,.2f}")
    
    if moyens:
        print(f"\n  MOYENS ({len(moyens)}) - A verifier:")
        for i, c in enumerate(moyens[:5], 1):
            print(f"    {i}. {c['numero']:10} {c['nature']:30} Attendu: {c['sens_attendu']:6} Reel: {c['sens_reel']:6} Solde: {c['solde_net']:>15,.2f}")

print("\n" + "="*80)
print("TEST TERMINE")
print("="*80)
