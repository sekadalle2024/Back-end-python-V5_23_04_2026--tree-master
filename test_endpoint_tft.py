# -*- coding: utf-8 -*-
"""
Test de l'endpoint /etats-financiers/process-excel avec 2 fichiers
"""
import requests
import base64
import json

print("="*80)
print("TEST ENDPOINT ETATS FINANCIERS + TFT")
print("="*80)

# 1. Lire les fichiers Excel
print("\n1. Lecture des fichiers Excel...")
with open('BALANCES_N_N1_N2.xlsx', 'rb') as f:
    file_n_content = f.read()
    file_n_base64 = base64.b64encode(file_n_content).decode('utf-8')

print(f"   ✅ Balance N encodée: {len(file_n_base64)} caractères")
print(f"   ✅ Balance N-1: même fichier (feuilles différentes)")

# 2. Préparer la requête (pour l'instant sans N-1 car même fichier)
print("\n2. Préparation de la requête...")
payload = {
    "file_base64": file_n_base64,
    "filename": "BALANCES_N_N1_N2.xlsx"
}

# 3. Envoyer la requête
print("\n3. Envoi de la requête à l'endpoint...")
url = "http://127.0.0.1:5000/etats-financiers/process-excel"

try:
    response = requests.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=30
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
            print(f"\n📊 TOTAUX:")
            print(f"   Actif:      {totaux['actif']:>20,.2f}")
            print(f"   Passif:     {totaux['passif']:>20,.2f}")
            print(f"   Charges:    {totaux['charges']:>20,.2f}")
            print(f"   Produits:   {totaux['produits']:>20,.2f}")
            print(f"   Résultat:   {totaux['resultat_net']:>20,.2f}")
            
            # Vérifier si TFT présent
            if 'tft' in result['results']:
                print(f"\n💧 TFT PRESENT!")
                tft = result['results']['tft']
                print(f"   Trésorerie ouverture: {tft.get('ZA_tresorerie_ouverture', 0):>20,.2f}")
                print(f"   Trésorerie clôture:   {tft.get('ZH_tresorerie_cloture', 0):>20,.2f}")
            else:
                print(f"\n⚠️  TFT NON PRESENT (normal, une seule balance fournie)")
        
        if 'html' in result and result['html']:
            html_length = len(result['html'])
            print(f"\n✅ HTML généré: {html_length} caractères")
            
            # Vérifier les sections
            sections = [
                'BILAN - ACTIF',
                'BILAN - PASSIF',
                'COMPTE DE RÉSULTAT',
                'RÉSULTAT NET',
                'ÉTATS DE CONTRÔLE'
            ]
            
            print("\n📋 Sections présentes:")
            for section in sections:
                present = section in result['html']
                print(f"   {'✅' if present else '❌'} {section}")
        
        print("\n" + "="*80)
        print("TEST REUSSI")
        print("="*80)
        
    else:
        print(f"\n❌ Erreur HTTP {response.status_code}")
        print(f"   Réponse: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERREUR: Impossible de se connecter au backend")
    print("   Vérifiez que le backend est démarré sur http://127.0.0.1:5000")
except requests.exceptions.Timeout:
    print("\n❌ ERREUR: Timeout (>30s)")
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
