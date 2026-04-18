"""
Module pour générer les états financiers avec format liasse officielle
- Affichage de TOUS les postes (même vides)
- 2 colonnes: Exercice N et Exercice N-1
- Format tableau conforme à la liasse officielle
"""

import pandas as pd
import json
import os
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger("etats_financiers_v2")


def format_montant_liasse(montant: float) -> str:
    """
    Formate un montant pour la liasse officielle.
    Retourne "-" si montant est nul ou proche de zéro.
    """
    if abs(montant) < 0.01:
        return "-"
    return f"{montant:,.0f}".replace(',', ' ')


def load_structure_liasse_complete() -> Dict:
    """Charge la structure complète de la liasse officielle"""
    file_path = os.path.join(os.path.dirname(__file__), "structure_liasse_complete.json")
    
    if not os.path.exists(file_path):
        logger.warning(f"Structure liasse complète non trouvée: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculer_poste_formule(ref: str, formule: str, postes_calcules: Dict[str, float]) -> float:
    """
    Calcule un poste de totalisation à partir d'une formule.
    Exemple: "TA - RA - RB" ou "XA + TE + TF"
    """
    try:
        # Remplacer les références par les valeurs (0 si absent)
        expression = formule
        for ref_poste in set(re.findall(r'[A-Z]{2}', formule)):
            valeur = postes_calcules.get(ref_poste, 0)
            expression = expression.replace(ref_poste, str(valeur))
        
        # Évaluer l'expression
        resultat = eval(expression)
        return float(resultat)
    except Exception as e:
        logger.error(f"Erreur calcul formule {ref} ({formule}): {e}")
        return 0.0


def process_balance_to_liasse_format(
    balance_n_df: pd.DataFrame,
    balance_n1_df: Optional[pd.DataFrame],
    balance_n2_df: Optional[pd.DataFrame],
    correspondances: Dict
) -> Dict[str, Any]:
    """
    Traite les balances N et N-1 et génère les états au format liasse officielle.
    
    Returns:
        Dict avec structure:
        {
            'compte_resultat': [
                {
                    'ref': 'TA',
                    'libelle': 'Ventes de marchandises',
                    'note': '21',
                    'montant_n': 1000000,
                    'montant_n1': 950000
                },
                ...
            ],
            'bilan_actif': [...],
            'bilan_passif': [...]
        }
    """
    from etats_financiers import (
        detect_balance_columns,
        clean_number,
        match_compte_to_poste
    )
    from calculer_actif_brut_amort import enrichir_actif_avec_brut_amort
    
    # Charger la structure complète
    structure_complete = load_structure_liasse_complete()
    
    # Détecter les colonnes
    col_map_n = detect_balance_columns(balance_n_df)
    col_map_n1 = detect_balance_columns(balance_n1_df) if balance_n1_df is not None else None
    col_map_n2 = detect_balance_columns(balance_n2_df) if balance_n2_df is not None else None
    
    # Fonction pour calculer les montants d'une balance
    def calculer_montants_balance(balance_df, col_map, correspondances_section):
        """Calcule les montants pour une balance donnée"""
        montants = {}
        
        for idx, row in balance_df.iterrows():
            numero = str(row.get(col_map['numero'], '')).strip()
            if not numero or numero == 'nan' or not numero[0].isdigit():
                continue
            
            solde_debit = clean_number(row.get(col_map['solde_debit'], 0)) if col_map['solde_debit'] else 0
            solde_credit = clean_number(row.get(col_map['solde_credit'], 0)) if col_map['solde_credit'] else 0
            solde_net = solde_debit - solde_credit
            
            # Chercher correspondance
            for poste in correspondances_section:
                for racine in poste.get('racines', []):
                    if numero.startswith(racine):
                        ref = poste['ref']
                        if ref not in montants:
                            montants[ref] = 0
                        
                        # Appliquer le sens selon le type
                        type_poste = poste.get('type', '')
                        if type_poste == 'charge' or type_poste == 'actif':
                            montants[ref] += solde_net
                        elif type_poste == 'produit' or type_poste == 'passif':
                            montants[ref] += -solde_net
                        else:
                            montants[ref] += solde_net
                        break
        
        return montants
    
    # Traiter le Compte de Résultat
    resultat_complet = []
    
    if 'compte_resultat' in structure_complete:
        # Calculer montants N
        montants_n = calculer_montants_balance(
            balance_n_df,
            col_map_n,
            structure_complete['compte_resultat']
        )
        
        # Calculer montants N-1
        montants_n1 = {}
        if balance_n1_df is not None and col_map_n1:
            montants_n1 = calculer_montants_balance(
                balance_n1_df,
                col_map_n1,
                structure_complete['compte_resultat']
            )
        
        # Calculer montants N-2
        montants_n2 = {}
        if balance_n2_df is not None and col_map_n2:
            montants_n2 = calculer_montants_balance(
                balance_n2_df,
                col_map_n2,
                structure_complete['compte_resultat']
            )
        
        # Construire la liste complète avec TOUS les postes
        for poste in structure_complete['compte_resultat']:
            ref = poste['ref']
            
            # Si c'est un poste de totalisation, calculer avec la formule
            if poste.get('type') == 'total' and 'formule' in poste:
                montant_n = calculer_poste_formule(ref, poste['formule'], montants_n)
                montant_n1 = calculer_poste_formule(ref, poste['formule'], montants_n1) if montants_n1 else 0
                montant_n2 = calculer_poste_formule(ref, poste['formule'], montants_n2) if montants_n2 else 0
                
                # Stocker pour les calculs suivants
                montants_n[ref] = montant_n
                montants_n1[ref] = montant_n1
                montants_n2[ref] = montant_n2
            else:
                montant_n = montants_n.get(ref, 0)
                montant_n1 = montants_n1.get(ref, 0)
                montant_n2 = montants_n2.get(ref, 0)
            
            resultat_complet.append({
                'ref': ref,
                'libelle': poste['libelle'],
                'note': poste.get('note', ''),
                'montant_n': montant_n,
                'montant_n1': montant_n1,
                'montant_n2': montant_n2
            })
    
    # Traiter le Bilan (utiliser les correspondances existantes)
    bilan_actif_complet = []
    bilan_passif_complet = []
    
    actif_enrichi = enrichir_actif_avec_brut_amort(balance_n_df, correspondances, col_map_n)
    actif_detaille_n = actif_enrichi.get('actif_detaille', {})
    
    # Pour le bilan, on utilise les correspondances existantes
    for section_name in ['bilan_actif', 'bilan_passif']:
        if section_name in correspondances:
            montants_n = calculer_montants_balance(
                balance_n_df,
                col_map_n,
                correspondances[section_name]
            )
            
            montants_n1 = {}
            if balance_n1_df is not None and col_map_n1:
                montants_n1 = calculer_montants_balance(
                    balance_n1_df,
                    col_map_n1,
                    correspondances[section_name]
                )
            
            montants_n2 = {}
            if balance_n2_df is not None and col_map_n2:
                montants_n2 = calculer_montants_balance(
                    balance_n2_df,
                    col_map_n2,
                    correspondances[section_name]
                )
            
            liste_postes = bilan_actif_complet if section_name == 'bilan_actif' else bilan_passif_complet
            
            for poste in correspondances[section_name]:
                ref = poste['ref']
                poste_dict = {
                    'ref': ref,
                    'libelle': poste['libelle'],
                    'note': '',
                    'montant_n': montants_n.get(ref, 0),
                    'montant_n1': montants_n1.get(ref, 0),
                    'montant_n2': montants_n2.get(ref, 0)
                }
                
                if section_name == 'bilan_actif' and ref in actif_detaille_n:
                    poste_dict['brut'] = actif_detaille_n[ref]['brut']
                    poste_dict['amort_deprec'] = actif_detaille_n[ref]['amort_deprec']
                    poste_dict['net'] = actif_detaille_n[ref]['net']
                    poste_dict['montant_n'] = actif_detaille_n[ref]['net']
                
                liste_postes.append(poste_dict)
    
    # Calculer les totaux généraux pour le bilan
    total_actif_n = sum(p['montant_n'] for p in bilan_actif_complet if p['ref'] in ['AZ', 'BP', 'BT', 'BU'])
    total_actif_n1 = sum(p['montant_n1'] for p in bilan_actif_complet if p['ref'] in ['AZ', 'BP', 'BT', 'BU'])
    total_actif_n2 = sum(p['montant_n2'] for p in bilan_actif_complet if p['ref'] in ['AZ', 'BP', 'BT', 'BU'])
    
    total_actif_brut = sum(p.get('brut', 0) for p in bilan_actif_complet if p['ref'] in ['AZ', 'BP', 'BT', 'BU'])
    total_actif_amort = sum(p.get('amort_deprec', 0) for p in bilan_actif_complet if p['ref'] in ['AZ'])
    
    bilan_actif_complet.append({
        'ref': 'BZ',  # BZ = TOTAL GENERAL ACTIF
        'libelle': 'TOTAL GÉNÉRAL ACTIF',
        'note': '',
        'brut': total_actif_brut,
        'amort_deprec': total_actif_amort,
        'net': total_actif_n,
        'montant_n': total_actif_n,
        'montant_n1': total_actif_n1,
        'montant_n2': total_actif_n2
    })
    
    total_passif_n = sum(p['montant_n'] for p in bilan_passif_complet)
    total_passif_n1 = sum(p['montant_n1'] for p in bilan_passif_complet)
    total_passif_n2 = sum(p['montant_n2'] for p in bilan_passif_complet)
    
    bilan_passif_complet.append({
        'ref': 'DZ',
        'libelle': 'TOTAL GÉNÉRAL PASSIF',
        'note': '',
        'montant_n': total_passif_n,
        'montant_n1': total_passif_n1,
        'montant_n2': total_passif_n2
    })
    
    return {
        'compte_resultat': resultat_complet,
        'bilan_actif': bilan_actif_complet,
        'bilan_passif': bilan_passif_complet
    }


def generate_section_html_liasse(
    section_id: str,
    title: str,
    postes: List[Dict],
    exercice_n_label: str = "EXERCICE N",
    exercice_n1_label: str = "EXERCICE N-1",
    exercice_n2_label: str = "EXERCICE N-2"
) -> str:
    """
    Génère le HTML pour une section au format liasse officielle.
    Affiche TOUS les postes avec 2 colonnes de montants (N et N-1 seulement).
    Si Bilan Actif, affiche BRUT, AMORT ET DEPREC, NET N, NET N-1.
    """
    if not postes:
        return ''
    
    is_actif = (section_id == 'bilan_actif')
    
    html = f"""
    <div class="etats-fin-section" data-section="{section_id}">
        <div class="section-header-ef">
            <span>{title}</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef active">
            <table class="liasse-table">
                <thead>
                    <tr>
                        <th style="width: 60px;">REF</th>
                        <th style="width: auto;">LIBELLÉS</th>
                        <th style="width: 60px;">NOTE</th>
    """
    if is_actif:
        html += f"""
                        <th style="width: 120px; text-align: right;">BRUT</th>
                        <th style="width: 120px; text-align: right;">AMORT/DEPREC</th>
                        <th style="width: 120px; text-align: right;">NET N</th>
                        <th style="width: 120px; text-align: right;">NET N-1</th>
        """
    else:
        html += f"""
                        <th style="width: 150px; text-align: right;">{exercice_n_label}</th>
                        <th style="width: 150px; text-align: right;">{exercice_n1_label}</th>
        """
        
    html += """
                    </tr>
                </thead>
                <tbody>
    """
    
    for poste in postes:
        ref = poste['ref']
        libelle = poste['libelle']
        note = poste.get('note', '')
        montant_n = poste.get('montant_n', 0)
        montant_n1 = poste.get('montant_n1', 0)
        brut = poste.get('brut', 0)
        amort_deprec = poste.get('amort_deprec', 0)
        
        # Déterminer si c'est un poste de totalisation
        is_total = ref.startswith('X') or ref in ['DZ', 'BZ', 'TZ', 'UZ', 'VZ'] or libelle.isupper() or 'TOTAL' in libelle.upper()
        row_class = 'total-row' if is_total else ''
        
        html += f"""
                    <tr class="{row_class}">
                        <td class="ref-cell">{ref}</td>
                        <td class="libelle-cell">{libelle}</td>
                        <td class="note-cell">{note}</td>
        """
        
        if is_actif:
            html += f"""
                        <td class="montant-cell">{format_montant_liasse(brut)}</td>
                        <td class="montant-cell" style="color: #d97706;">{format_montant_liasse(amort_deprec)}</td>
                        <td class="montant-cell">{format_montant_liasse(montant_n)}</td>
                        <td class="montant-cell" style="color: #6b7280;">{format_montant_liasse(montant_n1)}</td>
            """
        else:
            html += f"""
                        <td class="montant-cell">{format_montant_liasse(montant_n)}</td>
                        <td class="montant-cell" style="color: #6b7280;">{format_montant_liasse(montant_n1)}</td>
            """
            
        html += """
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


def generate_css_liasse() -> str:
    """Génère le CSS pour le format liasse officielle avec accordéons"""
    return """
    <style>
    /* Container principal */
    .etats-fin-container {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        max-width: 100%;
        margin: 16px 0;
    }
    
    .etats-fin-header {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 20px;
        border-radius: 12px 12px 0 0;
        text-align: center;
    }
    
    .etats-fin-header h2 { 
        margin: 0 0 8px 0; 
        font-size: 22px; 
    }
    
    .etats-fin-header p { 
        margin: 0; 
        opacity: 0.9; 
        font-size: 16px; 
    }
    
    /* Sections accordéon */
    .etats-fin-section {
        margin: 16px 0;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        overflow: hidden;
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
        transition: background 0.2s;
    }
    
    .section-header-ef:hover { 
        background: #e9ecef; 
    }
    
    .section-header-ef.active { 
        background: #dee2e6; 
    }
    
    .section-header-ef .arrow {
        transition: transform 0.3s;
        font-size: 18px;
    }
    
    .section-header-ef.active .arrow { 
        transform: rotate(90deg); 
    }
    
    .section-content-ef {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease-out;
        background: white;
    }
    
    .section-content-ef.active { 
        max-height: 10000px; 
    }
    
    /* Tables liasse */
    .liasse-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }
    
    .liasse-table thead {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
    }
    
    .liasse-table th {
        padding: 12px 8px;
        text-align: left;
        font-weight: 600;
        border: 1px solid #2563eb;
    }
    
    .liasse-table tbody tr {
        border-bottom: 1px solid #e5e7eb;
    }
    
    .liasse-table tbody tr:hover {
        background: #f9fafb;
    }
    
    .liasse-table tbody tr.total-row {
        background: #f0f9ff;
        font-weight: 700;
        border-top: 2px solid #3b82f6;
        border-bottom: 2px solid #3b82f6;
    }
    
    .liasse-table td {
        padding: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .liasse-table .ref-cell {
        font-weight: 600;
        color: #1e3a8a;
        text-align: center;
    }
    
    .liasse-table .libelle-cell {
        color: #374151;
    }
    
    .liasse-table .note-cell {
        text-align: center;
        color: #6b7280;
        font-size: 11px;
    }
    
    .liasse-table .montant-cell {
        text-align: right;
        font-family: 'Consolas', 'Courier New', monospace;
        color: #059669;
        font-weight: 500;
    }
    
    .liasse-table .total-row .montant-cell {
        color: #1e3a8a;
        font-weight: 700;
    }
    </style>
    """
