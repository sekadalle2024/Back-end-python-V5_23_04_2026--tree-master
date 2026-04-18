# -*- coding: utf-8 -*-
"""
Test de l'endpoint /etats-financiers/process-excel avec 2 fichiers (N et N-1)
Pour tester le calcul du TFT
"""
import requests
import base64
import json

print("="*80)
print("TEST ENDPOINT ETATS FINANCIERS + TFT (2 FICHIERS)")
print("="*80)

# 1. Lire les 2 fichiers Excel
print("\n1. Lecture des fichiers Excel...")
with open('BALANCE_N_2024.xlsx', 'rb') as f:
    file_n_content = f.read()
    file_n_base64 = base64.b64encode(file_n_content).decode('utf-8')

with open('BALANCE_N1_2023.xlsx', 'rb') as f:
    file_n1_content = f.read()
    file_n1_base64 = base64.b64encode(file_n1_content).decode('utf-8')

print(f"   ✅ Balance N encodée: {len(file_n_base64)} caractères")
print(f"   ✅ Balance N-1 encodée: {len(file_n1_base64)} caractères")

# 2. Préparer la requête avec les 2 fichiers
print("\n2. Préparation de la requête avec 2 fichiers...")
payload = {
    "file_base64": file_n_base64,
    "filename": "BALANCE_N_2024.xlsx",
    "file_n1_base64": file_n1_base64,
    "filename_n1": "BALANCE_N1_2023.xlsx"
}

# 3. Envoyer la requête
print("\n3. Envoi de la requête à l'endpoint...")
url = "http://127.0.0.1:5000/etats-financiers/process-excel"

try:
    response = requests.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=60
    )
    
    print(f"   Statut: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "="*80)
        print("RESULTATS")
        print("="*80)
        
        print(f"\n✅ Success: {result['success']}")
        print(f"✅ Message: {result['message']}")
        
        if 'results' in result and result['results']:
            totaux = result['results']['totaux']
            print(f"\n📊 ETATS FINANCIERS:")
            print(f"   Actif:      {totaux['actif']:>20,.2f}")
            print(f"   Passif:     {totaux['passif']:>20,.2f}")
            print(f"   Charges:    {totaux['charges']:>20,.2f}")
            print(f"   Produits:   {totaux['produits']:>20,.2f}")
            print(f"   Résultat:   {totaux['resultat_net']:>20,.2f}")
            
            # Vérifier si TFT présent
            if 'tft' in result['results']:
                print(f"\n💧 TFT CALCULE AVEC SUCCES!")
                tft = result['results']['tft']
                print(f"\n   Trésorerie ouverture:  {tft.get('ZA_tresorerie_ouverture', 0):>20,.2f}")
                print(f"   CAFG:                  {tft.get('FA_cafg', 0):>20,.2f}")
                print(f"   Flux opérationnels:    {tft.get('ZB_flux_operationnels', 0):>20,.2f}")
                print(f"   Flux investissement:   {tft.get('ZC_flux_investissement', 0):>20,.2f}")
                print(f"   Flux financement:      {tft.get('ZF_flux_financement', 0):>20,.2f}")
                print(f"   Variation trésorerie:  {tft.get('ZG_variation_tresorerie', 0):>20,.2f}")
                print(f"   Trésorerie clôture:    {tft.get('ZH_tresorerie_cloture', 0):>20,.2f}")
                
                # Contrôles TFT
                if 'controles' in tft:
                    print(f"\n🔍 CONTROLES TFT:")
                    controles = tft['controles']
                    
                    coh_tres = controles.get('coherence_tresorerie', {})
                    print(f"   Cohérence trésorerie: {'✅ OUI' if coh_tres.get('coherent') else '❌ NON'}")
                    if not coh_tres.get('coherent'):
                        print(f"   Différence: {coh_tres.get('difference', 0):,.2f}")
                    
                    eq_flux = controles.get('equilibre_flux', {})
                    print(f"   Équilibre flux:       {'✅ OUI' if eq_flux.get('equilibre') else '❌ NON'}")
                    if not eq_flux.get('equilibre'):
                        print(f"   Différence: {eq_flux.get('difference', 0):,.2f}")
            else:
                print(f"\n❌ TFT NON PRESENT!")
        
        if 'html' in result and result['html']:
            html_length = len(result['html'])
            print(f"\n✅ HTML généré: {html_length} caractères")
            
            # Vérifier les sections
            sections = [
                'BILAN - ACTIF',
                'BILAN - PASSIF',
                'COMPTE DE RÉSULTAT',
                'RÉSULTAT NET',
                'TABLEAU DES FLUX DE TRÉSORERIE',
                'ÉTATS DE CONTRÔLE',
                'CONTRÔLES TFT'
            ]
            
            print("\n📋 Sections présentes:")
            sections_trouvees = 0
            for section in sections:
                present = section in result['html']
                if present:
                    sections_trouvees += 1
                print(f"   {'✅' if present else '❌'} {section}")
            
            print(f"\n📊 Total: {sections_trouvees}/{len(sections)} sections présentes")
        
        print("\n" + "="*80)
        if 'tft' in result.get('results', {}):
            print("🎉 TEST REUSSI - TFT INTEGRE!")
        else:
            print("⚠️  TEST PARTIEL - TFT NON INTEGRE")
        print("="*80)
        
    else:
        print(f"\n❌ Erreur HTTP {response.status_code}")
        print(f"   Réponse: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERREUR: Impossible de se connecter au backend")
    print("   Vérifiez que le backend est démarré sur http://127.0.0.1:5000")
except requests.exceptions.Timeout:
    print("\n❌ ERREUR: Timeout (>60s)")
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
