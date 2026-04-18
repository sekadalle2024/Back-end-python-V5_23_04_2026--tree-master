"""
Script pour générer les états financiers au format liasse officielle
À partir du fichier BALANCES_N_N1_N2.xlsx
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(__file__))

from etats_financiers import load_tableau_correspondance
from etats_financiers_v2 import (
    process_balance_to_liasse_format,
    generate_section_html_liasse,
    generate_css_liasse
)
from tableau_flux_tresorerie import calculer_tft
from annexes_liasse import calculer_annexes
from annexes_html import generate_annexes_html


def generer_etats_complets(fichier_excel="BALANCES_N_N1_N2.xlsx", output_dir=None):
    """
    Génère les états financiers complets au format liasse officielle
    
    Args:
        fichier_excel: Chemin vers le fichier Excel avec les 3 balances
        output_dir: Répertoire de sortie (par défaut: Bureau)
    """
    print("=" * 80)
    print("GÉNÉRATION ÉTATS FINANCIERS - FORMAT LIASSE OFFICIELLE")
    print("=" * 80)
    print()
    
    # Déterminer le répertoire de sortie
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # 1. Charger les balances
    print("1. Chargement des balances...")
    try:
        balance_n = pd.read_excel(fichier_excel, sheet_name="Balance N (2024)")
        balance_n1 = pd.read_excel(fichier_excel, sheet_name="Balance N-1 (2023)")
        print(f"   ✅ Balance N (2024): {len(balance_n)} comptes")
        print(f"   ✅ Balance N-1 (2023): {len(balance_n1)} comptes")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None
    
    # 2. Charger les correspondances
    print("\n2. Chargement des correspondances SYSCOHADA...")
    try:
        correspondances = load_tableau_correspondance()
        print(f"   ✅ Correspondances chargées")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None
    
    # 3. Traiter les balances au format liasse
    print("\n3. Traitement des balances au format liasse officielle...")
    try:
        # Chercher Balance N-2
        try:
            balance_n2 = pd.read_excel(fichier_excel, sheet_name="Balance N-2 (2022)")
            print(f"   ✅ Balance N-2 (2022): {len(balance_n2)} comptes")
        except:
            balance_n2 = None
            print(f"   ⚠️ Balance N-2 non trouvée, colonne N-2 sera vide")
        
        results = process_balance_to_liasse_format(balance_n, balance_n1, balance_n2, correspondances)
        print(f"   ✅ Traitement terminé")
        print(f"      - Compte de Résultat: {len(results['compte_resultat'])} postes")
        print(f"      - Bilan Actif: {len(results['bilan_actif'])} postes")
        print(f"      - Bilan Passif: {len(results['bilan_passif'])} postes")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 4. Calculer le TFT
    print("\n4. Calcul du Tableau des Flux de Trésorerie...")
    try:
        resultat_net_n = next((p['montant_n'] for p in results['compte_resultat'] if p['ref'] == 'XI'), 0)
        tft_data = calculer_tft(balance_n, balance_n1, resultat_net_n)
        results['tft'] = tft_data
        print(f"   ✅ TFT calculé")
        print(f"      - CAFG: {tft_data.get('FA_cafg', 0):,.0f} FCFA")
        print(f"      - Variation trésorerie: {tft_data.get('ZG_variation_tresorerie', 0):,.0f} FCFA")
    except Exception as e:
        print(f"   ⚠️ TFT non calculé: {e}")
    
    # 5. Calculer les annexes
    print("\n5. Calcul des annexes...")
    try:
        # Convertir au format ancien pour les annexes
        results_ancien = {
            'bilan_actif': {p['ref']: {'ref': p['ref'], 'libelle': p['libelle'], 'montant': p['montant_n']} 
                           for p in results['bilan_actif']},
            'bilan_passif': {p['ref']: {'ref': p['ref'], 'libelle': p['libelle'], 'montant': p['montant_n']} 
                            for p in results['bilan_passif']},
            'charges': {},
            'produits': {},
            'totaux': {
                'actif': sum(p['montant_n'] for p in results['bilan_actif']),
                'passif': sum(p['montant_n'] for p in results['bilan_passif']),
                'resultat_net': resultat_net_n
            }
        }
        annexes_data = calculer_annexes(results_ancien)
        results['annexes'] = annexes_data
        print(f"   ✅ Annexes calculées: {len(annexes_data)} notes")
    except Exception as e:
        print(f"   ⚠️ Annexes non calculées: {e}")
    
    # 6. Générer le HTML
    print("\n6. Génération du HTML...")
    try:
        html = generate_css_liasse()
        
        # En-tête
        html += """
        <div class='etats-fin-container' style='max-width: 1400px; margin: 0 auto;'>
            <div class='etats-fin-header' style='background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 20px;'>
                <h1 style='margin: 0 0 10px 0; font-size: 28px;'>📊 ÉTATS FINANCIERS SYSCOHADA RÉVISÉ</h1>
                <p style='margin: 0; font-size: 16px; opacity: 0.9;'>Format Liasse Officielle - Exercices N, N-1 et N-2</p>
            </div>
        """
        
        # Bilan
        html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>BILAN</h2>"
        html += generate_section_html_liasse("bilan_actif", "🏢 ACTIF", results['bilan_actif'], "EXERCICE N (2024)", "EXERCICE N-1 (2023)")
        html += generate_section_html_liasse("bilan_passif", "🏛️ PASSIF", results['bilan_passif'], "EXERCICE N (2024)", "EXERCICE N-1 (2023)")
        
        # Compte de Résultat
        html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>COMPTE DE RÉSULTAT</h2>"
        html += generate_section_html_liasse("compte_resultat", "📊 COMPTE DE RÉSULTAT", results['compte_resultat'], "EXERCICE N (2024)", "EXERCICE N-1 (2023)")
        
        # TFT
        if 'tft' in results and results['tft']:
            html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>TABLEAU DES FLUX DE TRÉSORERIE</h2>"
            html += generate_tft_html_accordeon(results['tft'])
        
        # Annexes
        if 'annexes' in results and results['annexes']:
            html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>NOTES ANNEXES</h2>"
            html += generate_annexes_html_accordeon(results['annexes'])
        
        html += "</div>"
        
        # Script pour les accordéons
        html += """
        <script>
        document.querySelectorAll('.section-header-ef').forEach(header => {
            header.addEventListener('click', function() {
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                content.classList.toggle('active');
            });
        });
        </script>
        """
        
        print(f"   ✅ HTML généré ({len(html)} caractères)")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 7. Sauvegarder le fichier
    print("\n7. Sauvegarde du fichier...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Etats_Financiers_Liasse_{timestamp}.html"
        output_path = os.path.join(output_dir, filename)
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>États Financiers - Format Liasse Officielle</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 20px; background: #f5f5f5; font-family: 'Segoe UI', Arial, sans-serif;">
{html}
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"   ✅ Fichier sauvegardé: {output_path}")
        return output_path
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None


def generate_tft_html_simple(tft_data):
    """Génère un HTML simple pour le TFT"""
    html = """
    <div style='background: white; padding: 20px; border-radius: 8px; margin: 10px 0; border: 1px solid #e5e7eb;'>
        <table style='width: 100%; border-collapse: collapse;'>
            <thead>
                <tr style='background: #f3f4f6;'>
                    <th style='padding: 12px; text-align: left; border: 1px solid #e5e7eb;'>LIBELLÉ</th>
                    <th style='padding: 12px; text-align: right; border: 1px solid #e5e7eb; width: 200px;'>MONTANT</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Flux opérationnels
    html += "<tr style='background: #dbeafe; font-weight: 700;'><td colspan='2' style='padding: 10px; border: 1px solid #e5e7eb;'>FLUX DE TRÉSORERIE DES ACTIVITÉS OPÉRATIONNELLES</td></tr>"
    for item in tft_data.get('flux_operationnels', []):
        montant = f"{item['montant']:,.0f}".replace(',', ' ') if item['montant'] != 0 else "-"
        html += f"<tr><td style='padding: 8px; border: 1px solid #e5e7eb;'>{item['libelle']}</td><td style='padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;'>{montant}</td></tr>"
    
    # Flux d'investissement
    html += "<tr style='background: #dbeafe; font-weight: 700;'><td colspan='2' style='padding: 10px; border: 1px solid #e5e7eb;'>FLUX DE TRÉSORERIE DES ACTIVITÉS D'INVESTISSEMENT</td></tr>"
    for item in tft_data.get('flux_investissement', []):
        montant = f"{item['montant']:,.0f}".replace(',', ' ') if item['montant'] != 0 else "-"
        html += f"<tr><td style='padding: 8px; border: 1px solid #e5e7eb;'>{item['libelle']}</td><td style='padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;'>{montant}</td></tr>"
    
    # Flux de financement
    html += "<tr style='background: #dbeafe; font-weight: 700;'><td colspan='2' style='padding: 10px; border: 1px solid #e5e7eb;'>FLUX DE TRÉSORERIE DES ACTIVITÉS DE FINANCEMENT</td></tr>"
    for item in tft_data.get('flux_financement', []):
        montant = f"{item['montant']:,.0f}".replace(',', ' ') if item['montant'] != 0 else "-"
        html += f"<tr><td style='padding: 8px; border: 1px solid #e5e7eb;'>{item['libelle']}</td><td style='padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;'>{montant}</td></tr>"
    
    # Variation de trésorerie
    variation = tft_data.get('variation_tresorerie', 0)
    variation_str = f"{variation:,.0f}".replace(',', ' ')
    html += f"<tr style='background: #f0f9ff; font-weight: 700; font-size: 16px;'><td style='padding: 12px; border: 2px solid #3b82f6;'>VARIATION DE TRÉSORERIE</td><td style='padding: 12px; text-align: right; border: 2px solid #3b82f6; font-family: monospace; color: #1e3a8a;'>{variation_str}</td></tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    return html


def generate_tft_html_accordeon(tft_data):
    """Génère un HTML accordéon pour le TFT"""
    html = """
    <div class="etats-fin-section" data-section="tft">
        <div class="section-header-ef">
            <span>💰 TABLEAU DES FLUX DE TRÉSORERIE</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef active">
            <table class="liasse-table">
                <thead>
                    <tr>
                        <th style="width: 60px;">REF</th>
                        <th style="width: auto;">LIBELLÉS</th>
                        <th style="width: 150px; text-align: right;">MONTANT</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Trésorerie d'ouverture
    tresorerie_ouverture = tft_data.get('ZA_tresorerie_ouverture', 0)
    html += f"""
                    <tr class="total-row">
                        <td class="ref-cell">ZA</td>
                        <td class="libelle-cell">TRÉSORERIE NETTE AU 1ER JANVIER (Trésorerie actif N-1 - Trésorerie passif N-1)</td>
                        <td class="montant-cell">{format_montant_liasse(tresorerie_ouverture)}</td>
                    </tr>
    """
    
    # Flux opérationnels
    html += """
                    <tr style="background: #dbeafe; font-weight: 700;">
                        <td colspan="3" style="padding: 10px;">A. FLUX DE TRÉSORERIE DES ACTIVITÉS OPÉRATIONNELLES</td>
                    </tr>
    """
    
    cafg = tft_data.get('FA_cafg', 0)
    html += f"""
                    <tr>
                        <td class="ref-cell">FA</td>
                        <td class="libelle-cell">Capacité d'Autofinancement Globale (CAFG)</td>
                        <td class="montant-cell">{format_montant_liasse(cafg)}</td>
                    </tr>
    """
    
    var_actif_hao = tft_data.get('FB_variation_actif_hao', 0)
    var_stocks = tft_data.get('FC_variation_stocks', 0)
    var_creances = tft_data.get('FD_variation_creances', 0)
    var_dettes = tft_data.get('FE_variation_dettes', 0)
    
    html += f"""
                    <tr>
                        <td class="ref-cell">FB</td>
                        <td class="libelle-cell">- Variation de l'actif circulant HAO</td>
                        <td class="montant-cell">{format_montant_liasse(var_actif_hao)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FC</td>
                        <td class="libelle-cell">- Variation des stocks</td>
                        <td class="montant-cell">{format_montant_liasse(var_stocks)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FD</td>
                        <td class="libelle-cell">- Variation des créances</td>
                        <td class="montant-cell">{format_montant_liasse(var_creances)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FE</td>
                        <td class="libelle-cell">+ Variation des dettes circulantes</td>
                        <td class="montant-cell">{format_montant_liasse(var_dettes)}</td>
                    </tr>
    """
    
    flux_operationnels = tft_data.get('ZB_flux_operationnels', 0)
    html += f"""
                    <tr class="total-row">
                        <td class="ref-cell">ZB</td>
                        <td class="libelle-cell">FLUX DE TRÉSORERIE DES ACTIVITÉS OPÉRATIONNELLES</td>
                        <td class="montant-cell">{format_montant_liasse(flux_operationnels)}</td>
                    </tr>
    """
    
    # Flux d'investissement
    html += """
                    <tr style="background: #dbeafe; font-weight: 700;">
                        <td colspan="3" style="padding: 10px;">B. FLUX DE TRÉSORERIE DES ACTIVITÉS D'INVESTISSEMENT</td>
                    </tr>
    """
    
    decaissement_incorp = tft_data.get('FF_decaissement_incorp', 0)
    decaissement_corp = tft_data.get('FG_decaissement_corp', 0)
    decaissement_fin = tft_data.get('FH_decaissement_fin', 0)
    encaissement_immob = tft_data.get('FI_encaissement_cessions_immob', 0)
    encaissement_fin = tft_data.get('FJ_encaissement_cessions_fin', 0)
    
    html += f"""
                    <tr>
                        <td class="ref-cell">FF</td>
                        <td class="libelle-cell">- Décaissements liés aux acquisitions d'immobilisations incorporelles</td>
                        <td class="montant-cell">{format_montant_liasse(decaissement_incorp)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FG</td>
                        <td class="libelle-cell">- Décaissements liés aux acquisitions d'immobilisations corporelles</td>
                        <td class="montant-cell">{format_montant_liasse(decaissement_corp)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FH</td>
                        <td class="libelle-cell">- Décaissements liés aux acquisitions d'immobilisations financières</td>
                        <td class="montant-cell">{format_montant_liasse(decaissement_fin)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FI</td>
                        <td class="libelle-cell">+ Encaissements liés aux cessions d'immobilisations</td>
                        <td class="montant-cell">{format_montant_liasse(encaissement_immob)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FJ</td>
                        <td class="libelle-cell">+ Encaissements liés aux cessions d'immobilisations financières</td>
                        <td class="montant-cell">{format_montant_liasse(encaissement_fin)}</td>
                    </tr>
    """
    
    flux_investissement = tft_data.get('ZC_flux_investissement', 0)
    html += f"""
                    <tr class="total-row">
                        <td class="ref-cell">ZC</td>
                        <td class="libelle-cell">FLUX DE TRÉSORERIE DES ACTIVITÉS D'INVESTISSEMENT</td>
                        <td class="montant-cell">{format_montant_liasse(flux_investissement)}</td>
                    </tr>
    """
    
    # Flux de financement
    html += """
                    <tr style="background: #dbeafe; font-weight: 700;">
                        <td colspan="3" style="padding: 10px;">C. FLUX DE TRÉSORERIE DES ACTIVITÉS DE FINANCEMENT</td>
                    </tr>
    """
    
    augmentation_capital = tft_data.get('FK_augmentation_capital', 0)
    subventions = tft_data.get('FL_subventions_recues', 0)
    prelevement = tft_data.get('FM_prelevement_capital', 0)
    dividendes = tft_data.get('FN_dividendes_verses', 0)
    
    html += f"""
                    <tr>
                        <td class="ref-cell">FK</td>
                        <td class="libelle-cell">+ Augmentation de capital par apports nouveaux</td>
                        <td class="montant-cell">{format_montant_liasse(augmentation_capital)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FL</td>
                        <td class="libelle-cell">+ Subventions d'investissement reçues</td>
                        <td class="montant-cell">{format_montant_liasse(subventions)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FM</td>
                        <td class="libelle-cell">- Prélèvements sur le capital</td>
                        <td class="montant-cell">{format_montant_liasse(prelevement)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FN</td>
                        <td class="libelle-cell">- Dividendes versés</td>
                        <td class="montant-cell">{format_montant_liasse(dividendes)}</td>
                    </tr>
    """
    
    flux_capitaux_propres = tft_data.get('ZD_flux_capitaux_propres', 0)
    html += f"""
                    <tr class="total-row">
                        <td class="ref-cell">ZD</td>
                        <td class="libelle-cell">FLUX DE TRÉSORERIE LIÉS AUX CAPITAUX PROPRES</td>
                        <td class="montant-cell">{format_montant_liasse(flux_capitaux_propres)}</td>
                    </tr>
    """
    
    nouveaux_emprunts = tft_data.get('FO_nouveaux_emprunts', 0)
    nouvelles_dettes = tft_data.get('FP_nouvelles_dettes', 0)
    remboursements = tft_data.get('FQ_remboursements', 0)
    
    html += f"""
                    <tr>
                        <td class="ref-cell">FO</td>
                        <td class="libelle-cell">+ Emprunts</td>
                        <td class="montant-cell">{format_montant_liasse(nouveaux_emprunts)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FP</td>
                        <td class="libelle-cell">+ Autres dettes financières</td>
                        <td class="montant-cell">{format_montant_liasse(nouvelles_dettes)}</td>
                    </tr>
                    <tr>
                        <td class="ref-cell">FQ</td>
                        <td class="libelle-cell">- Remboursements des emprunts et autres dettes financières</td>
                        <td class="montant-cell">{format_montant_liasse(remboursements)}</td>
                    </tr>
    """
    
    flux_capitaux_etrangers = tft_data.get('ZE_flux_capitaux_etrangers', 0)
    html += f"""
                    <tr class="total-row">
                        <td class="ref-cell">ZE</td>
                        <td class="libelle-cell">FLUX DE TRÉSORERIE LIÉS AUX CAPITAUX ÉTRANGERS</td>
                        <td class="montant-cell">{format_montant_liasse(flux_capitaux_etrangers)}</td>
                    </tr>
    """
    
    flux_financement = tft_data.get('ZF_flux_financement', 0)
    html += f"""
                    <tr class="total-row">
                        <td class="ref-cell">ZF</td>
                        <td class="libelle-cell">FLUX DE TRÉSORERIE DES ACTIVITÉS DE FINANCEMENT</td>
                        <td class="montant-cell">{format_montant_liasse(flux_financement)}</td>
                    </tr>
    """
    
    # Variation de trésorerie
    variation_tresorerie = tft_data.get('ZG_variation_tresorerie', 0)
    tresorerie_cloture = tft_data.get('ZH_tresorerie_cloture', 0)
    
    html += f"""
                    <tr class="total-row" style="background: #f0f9ff; font-weight: 700; font-size: 16px;">
                        <td class="ref-cell">ZG</td>
                        <td class="libelle-cell">VARIATION DE LA TRÉSORERIE NETTE DE LA PÉRIODE (A + B + C)</td>
                        <td class="montant-cell" style="color: #1e3a8a;">{format_montant_liasse(variation_tresorerie)}</td>
                    </tr>
                    <tr class="total-row">
                        <td class="ref-cell">ZH</td>
                        <td class="libelle-cell">TRÉSORERIE NETTE AU 31 DÉCEMBRE (Trésorerie actif N - Trésorerie passif N)</td>
                        <td class="montant-cell">{format_montant_liasse(tresorerie_cloture)}</td>
                    </tr>
    """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    return html


def generate_annexes_html_accordeon(annexes_data):
    """Génère un HTML accordéon pour les annexes"""
    html = """
    <div class="etats-fin-section" data-section="annexes">
        <div class="section-header-ef">
            <span>📋 NOTES ANNEXES</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef active">
    """
    
    # Parcourir les annexes
    for note_key, annexe in annexes_data.items():
        if not annexe:
            continue
            
        titre = annexe.get('titre', note_key)
        
        html += f"""
            <div style="margin-bottom: 20px; padding: 15px; background: #f9fafb; border-left: 4px solid #3b82f6; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: #1e3a8a; font-size: 16px;">{titre}</h3>
        """
        
        # Si c'est la note résultat
        if 'resultat_net' in annexe:
            resultat_net = annexe.get('resultat_net', 0)
            type_resultat = annexe.get('type', '')
            montant_absolu = annexe.get('montant_absolu', 0)
            
            html += f"""
                <div style="color: #374151; line-height: 1.6;">
                    <p><strong>Type:</strong> {type_resultat}</p>
                    <p><strong>Montant:</strong> {format_montant_liasse(montant_absolu)} FCFA</p>
                </div>
            """
        # Si c'est une note avec des postes
        elif 'postes' in annexe:
            postes = annexe.get('postes', {})
            total = annexe.get('total', 0)
            
            if postes:
                html += """
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr style="background: #f3f4f6;">
                                <th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">Libellé</th>
                                <th style="padding: 8px; text-align: right; border: 1px solid #e5e7eb; width: 150px;">Montant</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for ref, poste in postes.items():
                    libelle = poste.get('libelle', '')
                    montant = poste.get('montant', 0)
                    
                    html += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #e5e7eb;">{libelle}</td>
                                <td style="padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;">{format_montant_liasse(montant)}</td>
                            </tr>
                    """
                
                html += f"""
                            <tr style="background: #f3f4f6; font-weight: 700;">
                                <td style="padding: 8px; border: 1px solid #e5e7eb;">TOTAL</td>
                                <td style="padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;">{format_montant_liasse(total)}</td>
                            </tr>
                        </tbody>
                    </table>
                """
            else:
                html += f"""
                    <div style="color: #374151; line-height: 1.6;">
                        <p>Aucune donnée disponible pour cette note.</p>
                    </div>
                """
        
        html += """
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    return html


def format_montant_liasse(montant):
    """Formate un montant pour l'affichage dans la liasse"""
    if montant == 0:
        return "-"
    return f"{montant:,.0f}".replace(',', ' ')


if __name__ == "__main__":
    import sys
    
    # Vérifier les arguments
    fichier = "BALANCES_N_N1_N2.xlsx"
    if len(sys.argv) > 1:
        fichier = sys.argv[1]
    
    # Générer les états
    output_path = generer_etats_complets(fichier)
    
    if output_path:
        print("\n" + "=" * 80)
        print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 80)
        print(f"\n📂 Fichier: {output_path}\n")
        
        # Ouvrir le fichier
        try:
            import webbrowser
            webbrowser.open(output_path)
            print("🌐 Fichier ouvert dans le navigateur\n")
        except:
            print("⚠️ Impossible d'ouvrir automatiquement le fichier\n")
    else:
        print("\n" + "=" * 80)
        print("❌ ERREUR LORS DE LA GÉNÉRATION")
        print("=" * 80)
        sys.exit(1)
