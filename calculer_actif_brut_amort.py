"""
Module pour calculer les colonnes BRUT, AMORT ET DEPREC, et NET pour l'ACTIF du bilan
Conforme au référentiel SYSCOHADA Révisé

Date: 07 Avril 2026
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("calculer_actif_brut_amort")


def calculer_actif_avec_brut_amort(balance_df: pd.DataFrame, correspondances: Dict, col_map: Dict) -> Dict[str, Any]:
    """
    Calcule les valeurs BRUT, AMORT ET DEPREC, et NET pour chaque poste d'actif.
    
    Principe SYSCOHADA:
    - BRUT = Comptes de classe 2 (immobilisations) en débit
    - AMORT ET DEPREC = Comptes 28 (amortissements) + 29 (provisions) en crédit
    - NET = BRUT - AMORT ET DEPREC
    
    Args:
        balance_df: DataFrame de la balance comptable
        correspondances: Dictionnaire des correspondances postes/comptes
        col_map: Mapping des colonnes de la balance
    
    Returns:
        Dictionnaire avec les postes d'actif enrichis (brut, amort, net)
    """
    logger.info("📊 Calcul ACTIF avec colonnes BRUT, AMORT ET DEPREC, NET")
    
    # Résultats pour chaque poste d'actif
    actif_detaille = {}
    
    # Parcourir les postes d'actif
    for poste in correspondances['bilan_actif']:
        ref = poste['ref']
        libelle = poste['libelle']
        racines = poste['racines']
        
        # Initialiser les valeurs
        actif_detaille[ref] = {
            'ref': ref,
            'libelle': libelle,
            'brut': 0.0,
            'amort_deprec': 0.0,
            'net': 0.0,
            'comptes_brut': [],
            'comptes_amort': []
        }
        
        # Si pas de racines, c'est un poste de totalisation
        if not racines:
            continue
        
        # Parcourir la balance pour trouver les comptes correspondants
        for idx, row in balance_df.iterrows():
            numero = str(row.get(col_map['numero'], '')).strip()
            if not numero or numero == 'nan' or not numero[0].isdigit():
                continue
            
            intitule = str(row.get(col_map['intitule'], '')).strip() if col_map['intitule'] else ''
            
            # Calculer les soldes
            solde_debit = clean_number(row.get(col_map['solde_debit'], 0)) if col_map['solde_debit'] else 0
            solde_credit = clean_number(row.get(col_map['solde_credit'], 0)) if col_map['solde_credit'] else 0
            solde_net = solde_debit - solde_credit
            
            # Vérifier si le compte correspond à une racine du poste
            for racine in racines:
                if numero.startswith(racine):
                    # Distinguer les comptes bruts des comptes d'amortissement/provision
                    if numero.startswith('28') or numero.startswith('29'):
                        # Comptes d'amortissement (28) ou de provision (29)
                        # Ces comptes sont normalement créditeurs, donc solde_net négatif
                        # On prend la valeur absolue pour l'affichage
                        actif_detaille[ref]['amort_deprec'] += abs(solde_net)
                        actif_detaille[ref]['comptes_amort'].append({
                            'numero': numero,
                            'intitule': intitule,
                            'montant': abs(solde_net)
                        })
                    else:
                        # Comptes bruts (classe 2 hors 28 et 29)
                        # Ces comptes sont normalement débiteurs, donc solde_net positif
                        actif_detaille[ref]['brut'] += solde_net
                        actif_detaille[ref]['comptes_brut'].append({
                            'numero': numero,
                            'intitule': intitule,
                            'montant': solde_net
                        })
                    break
        
        # Calculer le NET
        actif_detaille[ref]['net'] = actif_detaille[ref]['brut'] - actif_detaille[ref]['amort_deprec']
    
    # Calculer les totalisations
    actif_detaille = calculer_totalisations_actif(actif_detaille)
    
    logger.info(f"✅ Calcul ACTIF terminé:")
    for ref, data in actif_detaille.items():
        if data['brut'] > 0 or data['amort_deprec'] > 0:
            logger.info(f"   {ref} - {data['libelle']}: BRUT={data['brut']:,.0f}, AMORT={data['amort_deprec']:,.0f}, NET={data['net']:,.0f}")
    
    return actif_detaille


def calculer_totalisations_actif(actif_detaille: Dict) -> Dict:
    """
    Calcule les postes de totalisation pour l'ACTIF.
    
    Postes de totalisation SYSCOHADA:
    - AZ: TOTAL ACTIF IMMOBILISÉ (AA à AS)
    - BP: TOTAL ACTIF CIRCULANT (BA à BN)
    - BT: TOTAL TRÉSORERIE-ACTIF (BQ à BS)
    - BZ: TOTAL GÉNÉRAL (AZ + BP + BT + BU)
    """
    
    # AZ: TOTAL ACTIF IMMOBILISÉ (AA à AS)
    total_immo_brut = 0
    total_immo_amort = 0
    for ref in ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AP', 'AQ', 'AR', 'AS']:
        if ref in actif_detaille:
            total_immo_brut += actif_detaille[ref]['brut']
            total_immo_amort += actif_detaille[ref]['amort_deprec']
    
    actif_detaille['AZ'] = {
        'ref': 'AZ',
        'libelle': 'TOTAL ACTIF IMMOBILISÉ',
        'brut': total_immo_brut,
        'amort_deprec': total_immo_amort,
        'net': total_immo_brut - total_immo_amort,
        'comptes_brut': [],
        'comptes_amort': []
    }
    
    # BP: TOTAL ACTIF CIRCULANT (BA à BN)
    # Note: L'actif circulant n'a généralement pas d'amortissement
    total_circ_net = 0
    for ref in ['BA', 'BB', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN']:
        if ref in actif_detaille:
            total_circ_net += actif_detaille[ref]['net']
    
    actif_detaille['BP'] = {
        'ref': 'BP',
        'libelle': 'TOTAL ACTIF CIRCULANT',
        'brut': total_circ_net,  # Pour l'actif circulant, brut = net
        'amort_deprec': 0,
        'net': total_circ_net,
        'comptes_brut': [],
        'comptes_amort': []
    }
    
    # BT: TOTAL TRÉSORERIE-ACTIF (BQ à BS)
    total_treso_net = 0
    for ref in ['BQ', 'BR', 'BS']:
        if ref in actif_detaille:
            total_treso_net += actif_detaille[ref]['net']
    
    actif_detaille['BT'] = {
        'ref': 'BT',
        'libelle': 'TOTAL TRÉSORERIE-ACTIF',
        'brut': total_treso_net,  # Pour la trésorerie, brut = net
        'amort_deprec': 0,
        'net': total_treso_net,
        'comptes_brut': [],
        'comptes_amort': []
    }
    
    # BU: Écarts de conversion-Actif (pas de totalisation)
    if 'BU' not in actif_detaille:
        actif_detaille['BU'] = {
            'ref': 'BU',
            'libelle': 'Écarts de conversion-Actif',
            'brut': 0,
            'amort_deprec': 0,
            'net': 0,
            'comptes_brut': [],
            'comptes_amort': []
        }
    
    # BZ: TOTAL GÉNÉRAL
    total_general_brut = actif_detaille['AZ']['brut'] + actif_detaille['BP']['brut'] + actif_detaille['BT']['brut'] + actif_detaille['BU']['brut']
    total_general_amort = actif_detaille['AZ']['amort_deprec']
    
    actif_detaille['BZ'] = {
        'ref': 'BZ',
        'libelle': 'TOTAL GÉNÉRAL',
        'brut': total_general_brut,
        'amort_deprec': total_general_amort,
        'net': total_general_brut - total_general_amort,
        'comptes_brut': [],
        'comptes_amort': []
    }
    
    return actif_detaille


def clean_number(value) -> float:
    """Nettoie et convertit une valeur en float"""
    if pd.isna(value) or value == '' or value is None:
        return 0.0
    try:
        cleaned = str(value).replace(' ', '').replace(',', '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def format_number(x: float) -> str:
    """Formate un nombre avec séparateurs de milliers"""
    try:
        if abs(x) < 0.01:
            return "-"
        return f"{x:,.0f}".replace(',', ' ')
    except:
        return str(x)


def generer_html_actif_detaille(actif_detaille: Dict) -> str:
    """
    Génère le HTML pour afficher l'ACTIF avec les colonnes BRUT, AMORT ET DEPREC, NET.
    Format conforme à la liasse SYSCOHADA Révisé.
    """
    
    html = """
    <style>
    .actif-detaille-container {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 20px 0;
        border: 2px solid #1e3a8a;
        border-radius: 8px;
        overflow: hidden;
    }
    .actif-header {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 18px;
    }
    .actif-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
    }
    .actif-table th {
        background: #f3f4f6;
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        border-bottom: 2px solid #d1d5db;
        font-size: 14px;
    }
    .actif-table td {
        padding: 10px 8px;
        border-bottom: 1px solid #e5e7eb;
        font-size: 13px;
    }
    .actif-table tr:hover {
        background: #f9fafb;
    }
    .actif-table .ref-col {
        width: 60px;
        text-align: center;
        font-weight: 600;
        color: #1e3a8a;
    }
    .actif-table .libelle-col {
        text-align: left;
        padding-left: 16px;
    }
    .actif-table .note-col {
        width: 60px;
        text-align: center;
        color: #6b7280;
    }
    .actif-table .montant-col {
        width: 120px;
        text-align: right;
        font-family: 'Consolas', monospace;
        padding-right: 16px;
    }
    .actif-table .total-row {
        background: #eff6ff;
        font-weight: 700;
    }
    .actif-table .total-row td {
        border-top: 2px solid #3b82f6;
        border-bottom: 2px solid #3b82f6;
    }
    .actif-table .section-header {
        background: #dbeafe;
        font-weight: 700;
        color: #1e3a8a;
    }
    </style>
    
    <div class="actif-detaille-container">
        <div class="actif-header">
            🏢 BILAN - ACTIF (Format Liasse Officielle)
        </div>
        <table class="actif-table">
            <thead>
                <tr>
                    <th class="ref-col">REF</th>
                    <th class="libelle-col">ACTIF</th>
                    <th class="note-col">NOTE</th>
                    <th class="montant-col">BRUT</th>
                    <th class="montant-col">AMORT ET DEPREC</th>
                    <th class="montant-col">NET</th>
                    <th class="montant-col">NET N-1</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Ordre d'affichage des postes selon SYSCOHADA
    ordre_postes = [
        # ACTIF IMMOBILISÉ
        'AA', 'AB', 'AC',  # Charges immobilisées
        'AD', 'AE', 'AF', 'AG', 'AH',  # Immobilisations incorporelles
        'AI', 'AJ', 'AK', 'AL', 'AM', 'AN',  # Immobilisations corporelles
        'AP',  # Avances et acomptes
        'AQ', 'AR', 'AS',  # Immobilisations financières
        'AZ',  # TOTAL ACTIF IMMOBILISÉ
        # ACTIF CIRCULANT
        'BA',  # Actif circulant HAO
        'BB', 'BG', 'BH', 'BI', 'BJ',  # Stocks
        'BK', 'BL', 'BM', 'BN',  # Créances
        'BP',  # TOTAL ACTIF CIRCULANT
        # TRÉSORERIE
        'BQ', 'BR', 'BS',
        'BT',  # TOTAL TRÉSORERIE-ACTIF
        'BU',  # Écarts de conversion
        'BZ'   # TOTAL GÉNÉRAL
    ]
    
    # Postes qui sont des en-têtes de section (affichage spécial)
    sections_headers = ['AA', 'AD', 'AI', 'AP', 'AQ', 'BA', 'BB', 'BK']
    
    # Postes de totalisation
    totaux = ['AZ', 'BP', 'BT', 'BZ']
    
    for ref in ordre_postes:
        if ref not in actif_detaille:
            continue
        
        data = actif_detaille[ref]
        libelle = data['libelle']
        brut = format_number(data['brut'])
        amort = format_number(data['amort_deprec'])
        net = format_number(data['net'])
        
        # Classe CSS selon le type de ligne
        row_class = ''
        if ref in totaux:
            row_class = 'total-row'
        elif ref in sections_headers:
            row_class = 'section-header'
        
        html += f"""
                <tr class="{row_class}">
                    <td class="ref-col">{ref}</td>
                    <td class="libelle-col">{libelle}</td>
                    <td class="note-col">-</td>
                    <td class="montant-col">{brut}</td>
                    <td class="montant-col">{amort}</td>
                    <td class="montant-col">{net}</td>
                    <td class="montant-col">-</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html


# Fonction principale pour intégration dans etats_financiers.py
def enrichir_actif_avec_brut_amort(balance_df: pd.DataFrame, correspondances: Dict, col_map: Dict) -> Dict[str, Any]:
    """
    Fonction principale pour enrichir les données d'actif avec BRUT, AMORT, NET.
    À intégrer dans le workflow principal de etats_financiers.py
    """
    actif_detaille = calculer_actif_avec_brut_amort(balance_df, correspondances, col_map)
    html = generer_html_actif_detaille(actif_detaille)
    
    return {
        'actif_detaille': actif_detaille,
        'html': html
    }
