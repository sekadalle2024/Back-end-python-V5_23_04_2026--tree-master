# -*- coding: utf-8 -*-
"""
Test standalone du module annexes
"""
import pandas as pd
import json
from annexes_liasse import calculer_annexes
from annexes_html import generate_annexes_html


def test_annexes():
    """Test du calcul des annexes"""
    print("=" * 80)
    print("TEST MODULE ANNEXES")
    print("=" * 80)
    
    # Données de test simulées
    results = {
        'bilan_actif': {
            'AD': {'ref': 'AD', 'libelle': 'Immobilisations incorporelles', 'montant': 50000},
            'AI': {'ref': 'AI', 'libelle': 'Terrains', 'montant': 200000},
            'AJ': {'ref': 'AJ', 'libelle': 'Bâtiments', 'montant': 500000},
            'BB': {'ref': 'BB', 'libelle': 'Stocks de marchandises', 'montant': 150000},
            'BF': {'ref': 'BF', 'libelle': 'Clients et comptes rattachés', 'montant': 300000},
        },
        'bilan_passif': {
            'DA': {'ref': 'DA', 'libelle': 'Capital social', 'montant': 1000000},
            'DH': {'ref': 'DH', 'libelle': 'Réserves légales', 'montant': 100000},
            'DI': {'ref': 'DI', 'libelle': 'Réserves statutaires', 'montant': 50000},
            'DZ': {'ref': 'DZ', 'libelle': 'Emprunts et dettes financières', 'montant': 400000},
            'EB': {'ref': 'EB', 'libelle': 'Fournisseurs et comptes rattachés', 'montant': 250000},
        },
        'charges': {
            'RA': {'ref': 'RA', 'libelle': 'Achats de marchandises', 'montant': 800000},
            'TK': {'ref': 'TK', 'libelle': 'Charges de personnel', 'montant': 300000},
            'TL': {'ref': 'TL', 'libelle': 'Impôts et taxes', 'montant': 50000},
        },
        'produits': {
            'TA': {'ref': 'TA', 'libelle': 'Ventes de marchandises', 'montant': 1500000},
            'TB': {'ref': 'TB', 'libelle': 'Ventes de produits fabriqués', 'montant': 200000},
        },
        'totaux': {
            'actif': 1200000,
            'passif': 1800000,
            'charges': 1150000,
            'produits': 1700000,
            'resultat_net': 550000
        }
    }
    
    print("\n📊 Données de test:")
    print(f"   - Actif: {results['totaux']['actif']:,.0f}")
    print(f"   - Passif: {results['totaux']['passif']:,.0f}")
    print(f"   - Charges: {results['totaux']['charges']:,.0f}")
    print(f"   - Produits: {results['totaux']['produits']:,.0f}")
    print(f"   - Résultat net: {results['totaux']['resultat_net']:,.0f}")
    
    # Calculer les annexes
    print("\n📋 Calcul des annexes...")
    annexes = calculer_annexes(results)
    
    print(f"\n✅ {len(annexes)} annexes calculées:")
    for note_key, note_data in annexes.items():
        titre = note_data.get('titre', '')
        
        if note_key == 'note_13':
            print(f"   - {titre}: {note_data.get('type', '')} de {note_data.get('montant_absolu', 0):,.0f}")
        else:
            nb_postes = len(note_data.get('postes', {}))
            total = note_data.get('total', 0)
            if nb_postes > 0:
                print(f"   - {titre}: {nb_postes} postes, total {total:,.0f}")
    
    # Générer le HTML
    print("\n🎨 Génération du HTML...")
    html = generate_annexes_html(annexes)
    
    print(f"✅ HTML généré: {len(html)} caractères")
    
    # Sauvegarder le HTML pour inspection
    with open('test_annexes_output.html', 'w', encoding='utf-8') as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Annexes</title>
    <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
    .etats-fin-section {
        margin: 16px 0;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        overflow: hidden;
        background: white;
    }
    .section-header-ef {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px;
        background: #f8f9fa;
        cursor: pointer;
        font-weight: 600;
        font-size: 17px;
    }
    .section-content-ef {
        padding: 10px;
    }
    </style>
</head>
<body>
    <h1>Test Module Annexes</h1>
""")
        f.write(html)
        f.write("""
</body>
</html>
""")
    
    print("✅ HTML sauvegardé dans: test_annexes_output.html")
    
    print("\n" + "=" * 80)
    print("TEST TERMINÉ AVEC SUCCÈS")
    print("=" * 80)


if __name__ == "__main__":
    test_annexes()
