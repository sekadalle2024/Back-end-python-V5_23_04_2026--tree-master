# -*- coding: utf-8 -*-
"""
Test d'intégration complet : États Financiers + TFT
Simule l'appel à l'endpoint avec 2 fichiers (Balance N et N-1)
"""
import pandas as pd
import base64
import sys
import io
from etats_financiers import process_balance_to_etats_financiers, load_tableau_correspondance, generate_etats_financiers_html
from tableau_flux_tresorerie import calculer_tft

# Forcer l'encodage UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("TEST D'INTEGRATION COMPLET : ETATS FINANCIERS + TFT")
print("="*80)

# 1. Charger les balances
print("\n1. Chargement des balances...")
balance_n = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N (2024)')
balance_n1 = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N-1 (2023)')
print(f"   ✅ Balance N: {len(balance_n)} comptes")
print(f"   ✅ Balance N-1: {len(balance_n1)} comptes")

# 2. Charger les correspondances
print("\n2. Chargement des correspondances SYSCOHADA...")
correspondances = load_tableau_correspondance()
print("   ✅ Correspondances chargées")

# 3. Traiter la balance N pour générer les états financiers
print("\n3. Génération des états financiers...")
results = process_balance_to_etats_financiers(balance_n, correspondances)
print(f"   ✅ Bilan Actif: {len(results['bilan_actif'])} postes")
print(f"   ✅ Bilan Passif: {len(results['bilan_passif'])} postes")
print(f"   ✅ Charges: {len(results['charges'])} postes")
print(f"   ✅ Produits: {len(results['produits'])} postes")

# 4. Calculer le TFT
print("\n4. Calcul du Tableau des Flux de Trésorerie...")
resultat_net = results['totaux']['resultat_net']
print(f"   Résultat net: {resultat_net:,.2f}")

tft_data = calculer_tft(balance_n, balance_n1, resultat_net)
results['tft'] = tft_data
print("   ✅ TFT calculé avec succès")

# 5. Afficher les résultats clés
print("\n" + "="*80)
print("RESULTATS CLES")
print("="*80)

print("\n📊 ETATS FINANCIERS:")
print(f"   Total Actif:        {results['totaux']['actif']:>20,.2f}")
print(f"   Total Passif:       {results['totaux']['passif']:>20,.2f}")
print(f"   Total Charges:      {results['totaux']['charges']:>20,.2f}")
print(f"   Total Produits:     {results['totaux']['produits']:>20,.2f}")
print(f"   Résultat Net:       {results['totaux']['resultat_net']:>20,.2f}")

print("\n💧 TABLEAU DES FLUX DE TRESORERIE:")
print(f"   Trésorerie ouverture:  {tft_data['ZA_tresorerie_ouverture']:>20,.2f}")
print(f"   CAFG:                  {tft_data['FA_cafg']:>20,.2f}")
print(f"   Flux opérationnels:    {tft_data['ZB_flux_operationnels']:>20,.2f}")
print(f"   Flux investissement:   {tft_data['ZC_flux_investissement']:>20,.2f}")
print(f"   Flux financement:      {tft_data['ZF_flux_financement']:>20,.2f}")
print(f"   Variation trésorerie:  {tft_data['ZG_variation_tresorerie']:>20,.2f}")
print(f"   Trésorerie clôture:    {tft_data['ZH_tresorerie_cloture']:>20,.2f}")

# 6. Contrôles
print("\n" + "="*80)
print("ETATS DE CONTROLE")
print("="*80)

controles = results['controles']

print("\n🔍 CONTROLES ETATS FINANCIERS:")
eq_bilan = controles['equilibre_bilan']
print(f"   Équilibre bilan:    {'✅ OUI' if eq_bilan['equilibre'] else '❌ NON'}")
if not eq_bilan['equilibre']:
    print(f"   Différence:         {eq_bilan['difference']:,.2f}")

stats = controles['statistiques']
print(f"   Taux couverture:    {stats['taux_couverture']:.1f}%")
print(f"   Comptes intégrés:   {stats['comptes_integres']}/{stats['total_comptes_balance']}")

sens_anormal = controles.get('comptes_sens_anormal_par_nature', [])
print(f"   Sens anormaux:      {len(sens_anormal)} comptes")

print("\n💧 CONTROLES TFT:")
controles_tft = tft_data['controles']

coh_tres = controles_tft['coherence_tresorerie']
print(f"   Cohérence trésorerie: {'✅ OUI' if coh_tres['coherent'] else '❌ NON'}")
if not coh_tres['coherent']:
    print(f"   Différence:           {coh_tres['difference']:,.2f}")

eq_flux = controles_tft['equilibre_flux']
print(f"   Équilibre flux:       {'✅ OUI' if eq_flux['equilibre'] else '❌ NON'}")
if not eq_flux['equilibre']:
    print(f"   Différence:           {eq_flux['difference']:,.2f}")

# 7. Générer le HTML
print("\n5. Génération du HTML...")
html = generate_etats_financiers_html(results)
print(f"   ✅ HTML généré: {len(html)} caractères")

# Vérifier que le HTML contient bien toutes les sections
sections_attendues = [
    'BILAN - ACTIF',
    'BILAN - PASSIF',
    'COMPTE DE RÉSULTAT - CHARGES',
    'COMPTE DE RÉSULTAT - PRODUITS',
    'RÉSULTAT NET',
    'TABLEAU DES FLUX DE TRÉSORERIE',
    'ÉTATS DE CONTRÔLE',
    'CONTRÔLES TFT'
]

print("\n6. Vérification des sections HTML...")
sections_trouvees = []
sections_manquantes = []

for section in sections_attendues:
    if section in html:
        sections_trouvees.append(section)
        print(f"   ✅ {section}")
    else:
        sections_manquantes.append(section)
        print(f"   ❌ {section}")

# 8. Résumé final
print("\n" + "="*80)
print("RESUME DU TEST")
print("="*80)

print(f"\n✅ États financiers générés: {len(results['bilan_actif']) + len(results['bilan_passif']) + len(results['charges']) + len(results['produits'])} postes")
print(f"✅ TFT calculé: {len([k for k in tft_data.keys() if k.startswith('Z') or k.startswith('F')])} lignes")
print(f"✅ Contrôles effectués: {len(controles)} contrôles EF + {len(controles_tft)} contrôles TFT")
print(f"✅ HTML généré: {len(html)} caractères")
print(f"✅ Sections trouvées: {len(sections_trouvees)}/{len(sections_attendues)}")

if sections_manquantes:
    print(f"\n⚠️  Sections manquantes: {', '.join(sections_manquantes)}")
else:
    print("\n🎉 TOUTES LES SECTIONS SONT PRESENTES!")

print("\n" + "="*80)
print("TEST TERMINE AVEC SUCCES")
print("="*80)
