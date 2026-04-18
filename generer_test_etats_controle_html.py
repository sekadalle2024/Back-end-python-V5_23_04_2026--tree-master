# -*- coding: utf-8 -*-
"""
Script de génération du fichier HTML de test des états de contrôle
À partir de la balance démo P000 -BALANCE DEMO N_N-1_N-2.xls
Utilise le nouveau module etats_controle_exhaustifs_html.py pour générer les 16 états
"""

import pandas as pd
import os
from datetime import datetime
from etats_controle_exhaustifs_html import generate_all_16_etats_controle_html


def charger_balance_demo():
    """Charge la balance démo depuis le fichier Excel"""
    # Chemin relatif depuis la racine du projet
    fichier = os.path.join("py_backend", "P000 -BALANCE DEMO N_N-1_N-2.xls")
    
    if not os.path.exists(fichier):
        print(f"❌ Fichier non trouvé: {fichier}")
        return None, None
    
    # Charger les onglets avec gestion des espaces
    # Les onglets actuels sont: "BALANCE N ", "BALANCE N-1 ", "BALANCE N-2"
    balance_n = pd.read_excel(fichier, sheet_name="BALANCE N ")
    balance_n1 = pd.read_excel(fichier, sheet_name="BALANCE N-1 ")
    
    print(f"✅ Balance N chargée: {len(balance_n)} comptes")
    print(f"✅ Balance N-1 chargée: {len(balance_n1)} comptes")
    
    return balance_n, balance_n1


def preparer_donnees_balance(balance_df):
    """Prépare les données de la balance pour les calculs"""
    # Mapper les colonnes
    balance_data = []
    
    for _, row in balance_df.iterrows():
        numero = str(row.get('Numéro', '')).strip()
        if not numero or numero == 'nan':
            continue
            
        compte = {
            'numero': numero,
            'intitule': str(row.get('Intitulé', '')).strip(),
            'solde_debit': float(row.get('Solde  Débit', 0) or 0),
            'solde_credit': float(row.get('Solde Crédit', 0) or 0)
        }
        balance_data.append(compte)
    
    return balance_data


def generer_html_complet(html_etats_16):
    """Génère le fichier HTML complet avec les 16 états de contrôle"""
    
    date_generation = datetime.now().strftime("%d %B %Y à %H:%M")
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test États de Contrôle - États Financiers SYSCOHADA</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .section:hover {{
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .section-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        .section-header:hover {{
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }}
        
        .section-header .arrow {{
            transition: transform 0.3s ease;
            font-size: 1.5em;
        }}
        
        .section.active .arrow {{
            transform: rotate(90deg);
        }}
        
        .section-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        
        .section.active .section-content {{
            max-height: 5000px;
        }}
        
        .section-body {{
            padding: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tbody tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .total-row {{
            background-color: #f0f0f0;
            font-weight: bold;
            border-top: 2px solid #667eea;
        }}
        
        .ref-cell {{
            font-weight: bold;
            color: #667eea;
            width: 80px;
        }}
        
        .montant-cell {{
            text-align: right;
            font-family: 'Courier New', monospace;
            font-weight: 500;
        }}
        
        .controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 1em;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 2px solid #e0e0e0;
        }}
        
        .info-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .success-box {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .warning-box {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .danger-box {{
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            background: #9e9e9e;
            color: white;
        }}
        
        .badge-success {{
            background: #4caf50;
        }}
        
        .badge-warning {{
            background: #ff9800;
        }}
        
        .badge-danger {{
            background: #f44336;
        }}
        
        .badge-info {{
            background: #2196f3;
        }}
        
        .badge-critical {{
            background: #d32f2f;
            animation: pulse 1.5s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Test États de Contrôle - 16 États Exhaustifs</h1>
            <p>États Financiers SYSCOHADA Révisé - Module de Contrôle Exhaustif</p>
            <p style="font-size: 0.9em; margin-top: 10px;">📅 Généré le: {date_generation}</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h2 style="margin-bottom: 15px;">📊 Vue d'Ensemble - 16 États de Contrôle</h2>
                <p>Ce fichier a été généré automatiquement à partir de la balance démo.</p>
                <p style="margin-top: 10px;"><strong>8 états pour l'exercice N + 8 états pour l'exercice N-1</strong></p>
                <p style="margin-top: 10px;">Les contrôles couvrent : statistiques de couverture, équilibre du bilan, cohérence du résultat, comptes non intégrés, sens inversés, déséquilibres, hypothèse d'affectation, et sens anormaux par nature.</p>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="expandAll()">📂 Tout Ouvrir</button>
                <button class="btn" onclick="collapseAll()">📁 Tout Fermer</button>
                <button class="btn" onclick="window.print()">🖨️ Imprimer</button>
            </div>

{html_etats_16}

        </div>
        
        <div class="footer">
            <p><strong>États de Contrôle - États Financiers SYSCOHADA Révisé</strong></p>
            <p style="margin-top: 10px;">Module développé pour ClaraVerse - Projet Open Source</p>
            <p style="margin-top: 5px;">📅 Date de génération: {date_generation}</p>
        </div>
    </div>
    
    <script>
        function toggleSection(header) {{
            const section = header.parentElement;
            section.classList.toggle('active');
        }}
        
        function expandAll() {{
            const sections = document.querySelectorAll('.section');
            sections.forEach(section => {{
                section.classList.add('active');
            }});
        }}
        
        function collapseAll() {{
            const sections = document.querySelectorAll('.section');
            sections.forEach(section => {{
                section.classList.remove('active');
            }});
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('✅ Test États de Contrôle chargé avec succès - 16 états');
        }});
    </script>
</body>
</html>
"""
    
    return html


def main():
    """Fonction principale"""
    print("═══════════════════════════════════════════════════════════════")
    print("  🔍 GÉNÉRATION DU FICHIER HTML DE TEST - 16 ÉTATS DE CONTRÔLE")
    print("═══════════════════════════════════════════════════════════════")
    print()
    
    # Charger les balances
    balance_n, balance_n1 = charger_balance_demo()
    
    if balance_n is None or balance_n1 is None:
        print("❌ Impossible de charger les balances")
        return
    
    # Préparer les données
    print("\n📊 Préparation des données...")
    donnees_n = preparer_donnees_balance(balance_n)
    donnees_n1 = preparer_donnees_balance(balance_n1)
    
    # Calculer les contrôles (données minimales pour le test)
    print("\n🔄 Calcul des états de contrôle...")
    
    controles_n = {
        'statistiques': {
            'total_comptes_balance': len(donnees_n),
            'comptes_integres': len(donnees_n) - 5,
            'comptes_non_integres': 5,
            'taux_couverture': ((len(donnees_n) - 5) / len(donnees_n) * 100) if len(donnees_n) > 0 else 0
        },
        'equilibre_bilan': {
            'actif': 1000000,
            'passif': 1000000,
            'difference': 0,
            'pourcentage_ecart': 0,
            'equilibre': True
        },
        'equilibre_resultat': {
            'resultat_cr': 50000,
            'resultat_bilan': 50000,
            'difference': 0,
            'equilibre': True
        },
        'comptes_non_integres': [],
        'comptes_sens_inverse': [],
        'comptes_desequilibre': [],
        'hypothese_affectation': {
            'resultat_net': 50000,
            'actif': 1000000,
            'passif_sans_resultat': 950000,
            'difference_avant': 50000,
            'passif_avec_resultat': 1000000,
            'difference_apres': 0,
            'equilibre_apres': True
        },
        'comptes_sens_anormal': {
            'critiques': [],
            'eleves': [],
            'moyens': [],
            'faibles': []
        }
    }
    
    controles_n1 = {
        'statistiques': {
            'total_comptes_balance': len(donnees_n1),
            'comptes_integres': len(donnees_n1) - 5,
            'comptes_non_integres': 5,
            'taux_couverture': ((len(donnees_n1) - 5) / len(donnees_n1) * 100) if len(donnees_n1) > 0 else 0
        },
        'equilibre_bilan': {
            'actif': 950000,
            'passif': 950000,
            'difference': 0,
            'pourcentage_ecart': 0,
            'equilibre': True
        },
        'equilibre_resultat': {
            'resultat_cr': 45000,
            'resultat_bilan': 45000,
            'difference': 0,
            'equilibre': True
        },
        'comptes_non_integres': [],
        'comptes_sens_inverse': [],
        'comptes_desequilibre': [],
        'hypothese_affectation': {
            'resultat_net': 45000,
            'actif': 950000,
            'passif_sans_resultat': 905000,
            'difference_avant': 45000,
            'passif_avec_resultat': 950000,
            'difference_apres': 0,
            'equilibre_apres': True
        },
        'comptes_sens_anormal': {
            'critiques': [],
            'eleves': [],
            'moyens': [],
            'faibles': []
        }
    }
    
    totaux_n = {
        'actif': 1000000,
        'passif': 1000000,
        'resultat': 50000
    }
    
    totaux_n1 = {
        'actif': 950000,
        'passif': 950000,
        'resultat': 45000
    }
    
    # Générer les 16 états de contrôle
    print("\n📝 Génération des 16 états de contrôle HTML...")
    html_etats_16 = generate_all_16_etats_controle_html(controles_n, controles_n1, totaux_n, totaux_n1)
    
    # Générer le HTML complet
    html_content = generer_html_complet(html_etats_16)
    
    # Sauvegarder sur le bureau
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop, "test_etats_controle_html.html")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Fichier généré avec succès!")
    print(f"📁 Emplacement: {output_file}")
    print(f"📊 Nombre d'états générés: 16 (8 pour N + 8 pour N-1)")
    print()
    print("═══════════════════════════════════════════════════════════════")
    print("  ✅ GÉNÉRATION TERMINÉE")
    print("═══════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
