# -*- coding: utf-8 -*-
"""
Script de test standalone pour le Tableau des Flux de Trésorerie (TFT)
"""
import pandas as pd
import sys
import io
from tableau_flux_tresorerie import calculer_tft, format_number

# Forcer l'encodage UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("TEST DU TABLEAU DES FLUX DE TRESORERIE (TFT)")
print("="*80)

# Charger les balances
print("\n1. Chargement des balances...")
balance_n = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N (2024)')
balance_n1 = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N-1 (2023)')
print(f"   Balance N: {len(balance_n)} comptes")
print(f"   Balance N-1: {len(balance_n1)} comptes")

# Résultat net (à calculer depuis le compte de résultat)
# Pour le test, on utilise une valeur fictive
resultat_net = -189540500.0  # Perte de l'exercice
print(f"\n2. Résultat net: {format_number(resultat_net)}")

# Calculer le TFT
print("\n3. Calcul du TFT...")
tft = calculer_tft(balance_n, balance_n1, resultat_net)

# Afficher les résultats
print("\n" + "="*80)
print("TABLEAU DES FLUX DE TRESORERIE")
print("="*80)

print("\nA. TRESORERIE D'OUVERTURE")
print(f"   ZA - Trésorerie au 1er janvier:  {format_number(tft['ZA_tresorerie_ouverture']):>20}")

print("\nB. FLUX DE TRESORERIE PROVENANT DES ACTIVITES OPERATIONNELLES")
print(f"   FA - CAFG:                        {format_number(tft['FA_cafg']):>20}")
print(f"   FB - Variation actif HAO:         {format_number(tft['FB_variation_actif_hao']):>20}")
print(f"   FC - Variation stocks:            {format_number(tft['FC_variation_stocks']):>20}")
print(f"   FD - Variation créances:          {format_number(tft['FD_variation_creances']):>20}")
print(f"   FE - Variation dettes:            {format_number(tft['FE_variation_dettes']):>20}")
print(f"   ZB - FLUX OPERATIONNELS:          {format_number(tft['ZB_flux_operationnels']):>20}")

print("\nC. FLUX DE TRESORERIE PROVENANT DES ACTIVITES D'INVESTISSEMENT")
print(f"   FF - Décaiss. immob. incorp.:     {format_number(tft['FF_decaissement_incorp']):>20}")
print(f"   FG - Décaiss. immob. corp.:       {format_number(tft['FG_decaissement_corp']):>20}")
print(f"   FH - Décaiss. immob. fin.:        {format_number(tft['FH_decaissement_fin']):>20}")
print(f"   FI - Encaiss. cessions immob.:    {format_number(tft['FI_encaissement_cessions_immob']):>20}")
print(f"   FJ - Encaiss. cessions fin.:      {format_number(tft['FJ_encaissement_cessions_fin']):>20}")
print(f"   ZC - FLUX INVESTISSEMENT:         {format_number(tft['ZC_flux_investissement']):>20}")

print("\nD. FLUX DE TRESORERIE PROVENANT DU FINANCEMENT PAR CAPITAUX PROPRES")
print(f"   FK - Augmentation capital:        {format_number(tft['FK_augmentation_capital']):>20}")
print(f"   FL - Subventions reçues:          {format_number(tft['FL_subventions_recues']):>20}")
print(f"   FM - Prélèvement capital:         {format_number(tft['FM_prelevement_capital']):>20}")
print(f"   FN - Dividendes versés:           {format_number(tft['FN_dividendes_verses']):>20}")
print(f"   ZD - FLUX CAPITAUX PROPRES:       {format_number(tft['ZD_flux_capitaux_propres']):>20}")

print("\nE. FLUX DE TRESORERIE PROVENANT DU FINANCEMENT PAR CAPITAUX ETRANGERS")
print(f"   FO - Nouveaux emprunts:           {format_number(tft['FO_nouveaux_emprunts']):>20}")
print(f"   FP - Nouvelles dettes fin.:       {format_number(tft['FP_nouvelles_dettes']):>20}")
print(f"   FQ - Remboursements:              {format_number(tft['FQ_remboursements']):>20}")
print(f"   ZE - FLUX CAPITAUX ETRANGERS:     {format_number(tft['ZE_flux_capitaux_etrangers']):>20}")

print("\nF. TOTAL FLUX DE FINANCEMENT")
print(f"   ZF - Flux financement (D+E):      {format_number(tft['ZF_flux_financement']):>20}")

print("\nG. VARIATION ET TRESORERIE FINALE")
print(f"   ZG - Variation trésorerie (B+C+F):{format_number(tft['ZG_variation_tresorerie']):>20}")
print(f"   ZH - Trésorerie au 31 décembre:   {format_number(tft['ZH_tresorerie_cloture']):>20}")

# Contrôles
print("\n" + "="*80)
print("ETATS DE CONTROLE TFT")
print("="*80)

controles = tft['controles']

print("\n1. COHERENCE TRESORERIE")
coh_tres = controles['coherence_tresorerie']
print(f"   Trésorerie calculée (ZH):  {format_number(coh_tres['tresorerie_calculee']):>20}")
print(f"   Trésorerie bilan N:        {format_number(coh_tres['tresorerie_bilan']):>20}")
print(f"   Différence:                {format_number(coh_tres['difference']):>20}")
print(f"   Cohérent:                  {'OUI' if coh_tres['coherent'] else 'NON'}")

print("\n2. EQUILIBRE DES FLUX")
eq_flux = controles['equilibre_flux']
print(f"   Flux opérationnels:        {format_number(eq_flux['flux_operationnels']):>20}")
print(f"   Flux investissement:       {format_number(eq_flux['flux_investissement']):>20}")
print(f"   Flux financement:          {format_number(eq_flux['flux_financement']):>20}")
print(f"   Total:                     {format_number(eq_flux['total']):>20}")
print(f"   Variation trésorerie:      {format_number(eq_flux['variation_tresorerie']):>20}")
print(f"   Différence:                {format_number(eq_flux['difference']):>20}")
print(f"   Équilibré:                 {'OUI' if eq_flux['equilibre'] else 'NON'}")

print("\n3. COHERENCE CAFG")
cafg_data = controles['coherence_cafg']
print(f"   Résultat net:              {format_number(cafg_data['resultat_net']):>20}")
print(f"   + Dotations:               {format_number(cafg_data['dotations']):>20}")
print(f"   - Reprises:                {format_number(cafg_data['reprises']):>20}")
print(f"   + Valeur compt. cessions:  {format_number(cafg_data['valeur_comptable_cessions']):>20}")
print(f"   - Produits cessions:       {format_number(cafg_data['produits_cessions']):>20}")
print(f"   - Subventions virées:      {format_number(cafg_data['subventions_virees']):>20}")
print(f"   = CAFG:                    {format_number(cafg_data['cafg']):>20}")

print("\n" + "="*80)
print("TEST TERMINE")
print("="*80)
