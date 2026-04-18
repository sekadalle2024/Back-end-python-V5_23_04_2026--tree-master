# -*- coding: utf-8 -*-
"""
Script de test pour les états financiers avec contrôles
"""
import pandas as pd
import json
import sys
import io

# Forcer l'encodage UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Importer les fonctions du module
from etats_financiers import (
    load_tableau_correspondance,
    process_balance_to_etats_financiers,
    generate_etats_financiers_html
)

print("="*80)
print("TEST DES ETATS FINANCIERS AVEC CONTROLES")
print("="*80)

# 1. Charger le tableau de correspondance
print("\n1. Chargement du tableau de correspondance...")
try:
    correspondances = load_tableau_correspondance()
    print(f"   OK - {len(correspondances['bilan_actif'])} postes Actif")
    print(f"   OK - {len(correspondances['bilan_passif'])} postes Passif")
    print(f"   OK - {len(correspondances['charges'])} postes Charges")
    print(f"   OK - {len(correspondances['produits'])} postes Produits")
except Exception as e:
    print(f"   ERREUR: {e}")
    sys.exit(1)

# 2. Charger la balance démo
print("\n2. Chargement de la balance demo...")
try:
    balance_df = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N (2024)')
    print(f"   OK - {len(balance_df)} comptes charges")
    print(f"   Colonnes: {balance_df.columns.tolist()}")
except Exception as e:
    print(f"   ERREUR: {e}")
    sys.exit(1)

# 3. Traiter la balance
print("\n3. Traitement de la balance...")
try:
    results = process_balance_to_etats_financiers(balance_df, correspondances)
    print(f"   OK - Traitement termine")
except Exception as e:
    print(f"   ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Afficher les résultats
print("\n4. RESULTATS")
print("="*80)

totaux = results['totaux']
print(f"\nTOTAUX:")
print(f"  Total Actif:    {totaux['actif']:>20,.2f}")
print(f"  Total Passif:   {totaux['passif']:>20,.2f}")
print(f"  Total Charges:  {totaux['charges']:>20,.2f}")
print(f"  Total Produits: {totaux['produits']:>20,.2f}")
print(f"  Resultat Net:   {totaux['resultat_net']:>20,.2f}")

# 5. Afficher les contrôles
if 'controles' in results:
    controles = results['controles']
    
    print("\n" + "="*80)
    print("ETATS DE CONTROLE")
    print("="*80)
    
    # Statistiques
    stats = controles.get('statistiques', {})
    print(f"\nSTATISTIQUES DE COUVERTURE:")
    print(f"  Total comptes balance:  {stats.get('total_comptes_balance', 0)}")
    print(f"  Comptes integres:       {stats.get('comptes_integres', 0)}")
    print(f"  Comptes non integres:   {stats.get('comptes_non_integres', 0)}")
    print(f"  Taux de couverture:     {stats.get('taux_couverture', 0):.2f}%")
    
    # Équilibre bilan
    eq_bilan = controles.get('equilibre_bilan', {})
    print(f"\nEQUILIBRE DU BILAN:")
    print(f"  Actif:       {eq_bilan.get('actif', 0):>20,.2f}")
    print(f"  Passif:      {eq_bilan.get('passif', 0):>20,.2f}")
    print(f"  Difference:  {eq_bilan.get('difference', 0):>20,.2f}")
    print(f"  Equilibre:   {'OUI' if eq_bilan.get('equilibre', False) else 'NON'}")
    if not eq_bilan.get('equilibre', False):
        print(f"  Ecart:       {eq_bilan.get('pourcentage_ecart', 0):.4f}%")
    
    # Cohérence résultat
    eq_res = controles.get('equilibre_resultat', {})
    print(f"\nCOHERENCE RESULTAT:")
    print(f"  Resultat CR:     {eq_res.get('resultat_cr', 0):>20,.2f}")
    print(f"  Resultat Bilan:  {eq_res.get('resultat_bilan', 0):>20,.2f}")
    print(f"  Difference:      {eq_res.get('difference', 0):>20,.2f}")
    print(f"  Coherent:        {'OUI' if eq_res.get('equilibre', False) else 'NON'}")
    
    # Comptes non intégrés
    comptes_ni = controles.get('comptes_non_integres', [])
    if comptes_ni:
        print(f"\nCOMPTES NON INTEGRES: {len(comptes_ni)}")
        impact = controles.get('impact_non_integres', {})
        print(f"  Impact total:        {impact.get('montant_total', 0):>20,.2f}")
        print(f"  % de l'actif:        {impact.get('pourcentage_actif', 0):.2f}%")
        print(f"\n  Top 10:")
        for i, compte in enumerate(comptes_ni[:10], 1):
            print(f"    {i}. {compte['numero']:10} {compte['intitule'][:40]:40} {compte['solde_net']:>15,.2f}")
    
    # Comptes sens inversé
    comptes_si = controles.get('comptes_sens_inverse', [])
    if comptes_si:
        print(f"\nCOMPTES AVEC SENS INVERSE: {len(comptes_si)}")
        print(f"  Top 10:")
        for i, compte in enumerate(comptes_si[:10], 1):
            print(f"    {i}. {compte['numero']:10} Classe {compte['classe']} - Attendu: {compte['sens_attendu']:6} Reel: {compte['sens_reel']:6} Solde: {compte['solde_net']:>15,.2f}")
    
    # Comptes en déséquilibre
    comptes_deseq = controles.get('comptes_desequilibre', [])
    if comptes_deseq:
        print(f"\nCOMPTES EN DESEQUILIBRE: {len(comptes_deseq)}")
        print(f"  Top 10:")
        for i, compte in enumerate(comptes_deseq[:10], 1):
            print(f"    {i}. {compte['numero']:10} {compte['section']:30} {compte['probleme'][:40]:40}")

# 6. Générer le HTML
print("\n" + "="*80)
print("GENERATION HTML")
print("="*80)

try:
    html = generate_etats_financiers_html(results)
    html_file = 'test_etats_financiers_output.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\nHTML genere: {html_file}")
    print(f"Taille: {len(html)} caracteres")
except Exception as e:
    print(f"ERREUR lors de la generation HTML: {e}")
    import traceback
    traceback.print_exc()

# 7. Sauvegarder les résultats en JSON
print("\n" + "="*80)
print("SAUVEGARDE JSON")
print("="*80)

try:
    # Convertir les résultats en format sérialisable
    results_json = {
        'totaux': totaux,
        'controles': {
            'statistiques': controles.get('statistiques', {}),
            'equilibre_bilan': controles.get('equilibre_bilan', {}),
            'equilibre_resultat': controles.get('equilibre_resultat', {}),
            'nb_comptes_non_integres': len(controles.get('comptes_non_integres', [])),
            'nb_comptes_sens_inverse': len(controles.get('comptes_sens_inverse', [])),
            'nb_comptes_desequilibre': len(controles.get('comptes_desequilibre', []))
        }
    }
    
    json_file = 'test_etats_financiers_results.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False)
    print(f"\nResultats sauvegardes: {json_file}")
except Exception as e:
    print(f"ERREUR lors de la sauvegarde JSON: {e}")

print("\n" + "="*80)
print("TEST TERMINE")
print("="*80)
