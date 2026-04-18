import requests
import json
import base64
import os
import pandas as pd
import io

print("=== TEST EXPORT LIASSE OFFICIELLE ===")

# 1. Préparer une balance factice minimale pour le test
print("1. Création balance démo...")
balance_data = [
    {"Compte": "211000", "Intitulé": "Frais de R&D", "Solde Débit": 1500000, "Solde Crédit": 0},
    {"Compte": "281100", "Intitulé": "Amort R&D", "Solde Débit": 0, "Solde Crédit": 500000},
    {"Compte": "101000", "Intitulé": "Capital", "Solde Débit": 0, "Solde Crédit": 1000000},
    {"Compte": "701000", "Intitulé": "Ventes", "Solde Débit": 0, "Solde Crédit": 2500000},
    {"Compte": "601000", "Intitulé": "Achats", "Solde Débit": 1500000, "Solde Crédit": 0},
]
df = pd.DataFrame(balance_data)
buffer = io.BytesIO()
df.to_excel(buffer, index=False)
buffer.seek(0)
file_base64 = base64.b64encode(buffer.read()).decode('utf-8')

# 2. Obtenir les résultats du backend (calcul)
print("2. Appel API /etats-financiers/calculer-excel...")
# This will start the py_backend on an alternative port if needed, but we'll try the main one first.
api_url = "http://localhost:8000"

try:
    calc_response = requests.post(f"{api_url}/etats-financiers/calculer-excel", json={
        "file_base64": file_base64,
        "filename": "balance_test.xlsx"
    })
    
    if calc_response.status_code != 200:
        print(f"Erreur API Calcul: {calc_response.status_code}")
        print(calc_response.text)
        exit(1)
        
    calc_data = calc_response.json()
    print("✓ Calcul réussi")
    results = calc_data.get("results")
    
    # Validation du brut/amort
    print("Contrôle structure des données calculées:")
    actif_det = results.get("actif_detaille", {})
    if 'AE' in actif_det: # AE = Frais recherche et developpement
        print(f"  Poste AE Brut: {actif_det['AE'].get('brut')}")
        print(f"  Poste AE Amort: {actif_det['AE'].get('amort_deprec')}")
        print(f"  Poste AE Net: {actif_det['AE'].get('net')}")
    else:
        print("  Poste AE non trouvé dans actif_detaille!")
        

    # 3. Exporter la liasse
    print("\n3. Appel API /export-liasse/generer...")
    export_response = requests.post(f"{api_url}/export-liasse/generer", json={
        "results": results,
        "nom_entreprise": "TEST ENTREPRISE",
        "exercice": "2026"
    })
    
    if export_response.status_code != 200:
        print(f"Erreur API Export: {export_response.status_code}")
        print(export_response.text)
        exit(1)
        
    export_data = export_response.json()
    print(f"✓ Export réussi: {export_data.get('filename')}")
    
    # 4. Sauvegarder le fichier généré
    output_filename = "test_liasse_generee.xlsx"
    with open(output_filename, "wb") as f:
        f.write(base64.b64decode(export_data['file_base64']))
    
    print(f"Fichier sauvegardé: {output_filename}")
    print("Test terminé avec succès. Veuillez ouvrir ce fichier et vérifier les cellules.")
    
except Exception as e:
    print(f"Erreur d'exécution du test: {e}")
