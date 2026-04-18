# -*- coding: utf-8 -*-
"""
Module TFT avec format liasse officielle (colonnes N et N-1)
"""
import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("tft_v2")


def clean_number(value) -> float:
    """Nettoie et convertit une valeur en float"""
    if pd.isna(value) or value == '' or value is None:
        return 0.0
    try:
        cleaned = str(value).replace(' ', '').replace(',', '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def detect_balance_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Détecte automatiquement les colonnes de balance"""
    columns = df.columns.tolist()
    columns_lower = [str(c).lower().strip() for c in columns]
    
    mapping = {
        'numero': None,
        'intitule': None,
        'solde_debit': None,
        'solde_credit': None
    }
    
    for idx, col in enumerate(columns_lower):
        original_col = columns[idx]
        
        if 'numéro' in col or 'numero' in col or col == 'n°' or 'compte' in col:
            if mapping['numero'] is None:
                mapping['numero'] = original_col
        
        if 'intitulé' in col or 'intitule' in col or 'libellé' in col or 'libelle' in col:
            if mapping['intitule'] is None:
                mapping['intitule'] = original_col
        
        if 'solde' in col and 'débit' in col:
            mapping['solde_debit'] = original_col
        elif 'solde' in col and 'debit' in col:
            mapping['solde_debit'] = original_col
        
        if 'solde' in col and 'crédit' in col:
            mapping['solde_credit'] = original_col
        elif 'solde' in col and 'credit' in col:
            mapping['solde_credit'] = original_col
    
    return mapping


def get_solde_by_racine(balance_df: pd.DataFrame, col_map: Dict, racines: list) -> float:
    """Calcule le solde total pour une liste de racines de comptes"""
    total = 0.0
    
    for _, row in balance_df.iterrows():
        numero = str(row.get(col_map['numero'], '')).strip()
        if not numero or numero == 'nan' or not numero[0].isdigit():
            continue
        
        for racine in racines:
            if numero.startswith(racine):
                solde_debit = clean_number(row.get(col_map['solde_debit'], 0)) if col_map['solde_debit'] else 0
                solde_credit = clean_number(row.get(col_map['solde_credit'], 0)) if col_map['solde_credit'] else 0
                total += (solde_debit - solde_credit)
                break
    
    return total


def calculer_tft_liasse(
    balance_n: pd.DataFrame,
    balance_n1: pd.DataFrame,
    balance_n2: Optional[pd.DataFrame],
    resultat_net_n: float,
    resultat_net_n1: float
) -> Dict[str, Any]:
    """
    Calcule le TFT au format liasse officielle avec colonnes N et N-1
    """
    logger.info("📊 Calcul TFT format liasse (N et N-1)")
    
    col_map_n = detect_balance_columns(balance_n)
    col_map_n1 = detect_balance_columns(balance_n1)
    col_map_n2 = detect_balance_columns(balance_n2) if balance_n2 is not None else None
    
    # Structure du TFT avec toutes les lignes
    tft_structure = [
        {'ref': 'ZA', 'libelle': 'Trésorerie nette au 1er janvier', 'type': 'tresorerie_debut'},
        {'ref': 'FA', 'libelle': 'Capacité d\'Autofinancement Globale (CAFG)', 'type': 'cafg'},
        {'ref': 'FB', 'libelle': 'Variation actif circulant HAO', 'type': 'var_actif_hao'},
        {'ref': 'FC', 'libelle': 'Variation des stocks', 'type': 'var_stocks'},
        {'ref': 'FD', 'libelle': 'Variation des créances', 'type': 'var_creances'},
        {'ref': 'FE', 'libelle': 'Variation du passif circulant', 'type': 'var_passif_circ'},
        {'ref': 'ZB', 'libelle': 'FLUX OPÉRATIONNELS', 'type': 'total', 'formule': 'FA+FB+FC+FD+FE'},
        {'ref': 'FF', 'libelle': 'Décaissements acquisitions immobilisations incorporelles', 'type': 'invest_incorp'},
        {'ref': 'FG', 'libelle': 'Décaissements acquisitions immobilisations corporelles', 'type': 'invest_corp'},
        {'ref': 'FH', 'libelle': 'Décaissements acquisitions immobilisations financières', 'type': 'invest_fin'},
        {'ref': 'FI', 'libelle': 'Encaissements cessions immobilisations', 'type': 'cessions'},
        {'ref': 'ZC', 'libelle': 'FLUX D\'INVESTISSEMENT', 'type': 'total', 'formule': 'FF+FG+FH+FI'},
        {'ref': 'FJ', 'libelle': 'Augmentation de capital', 'type': 'aug_capital'},
        {'ref': 'FK', 'libelle': 'Dividendes versés', 'type': 'dividendes'},
        {'ref': 'FL', 'libelle': 'Nouveaux emprunts', 'type': 'emprunts'},
        {'ref': 'FM', 'libelle': 'Remboursements emprunts', 'type': 'rembours'},
        {'ref': 'ZD', 'libelle': 'FLUX DE FINANCEMENT', 'type': 'total', 'formule': 'FJ+FK+FL+FM'},
        {'ref': 'ZE', 'libelle': 'VARIATION DE TRÉSORERIE', 'type': 'total', 'formule': 'ZB+ZC+ZD'},
        {'ref': 'ZF', 'libelle': 'Trésorerie nette au 31 décembre', 'type': 'tresorerie_fin'}
    ]
    
    # Fonction pour calculer un poste
    def calculer_poste(type_poste: str, balance: pd.DataFrame, col_map: Dict, balance_prev: Optional[pd.DataFrame] = None, col_map_prev: Optional[Dict] = None) -> float:
        if type_poste == 'tresorerie_debut':
            # Trésorerie début = Trésorerie fin N-1
            if balance_prev is not None:
                tresorerie = get_solde_by_racine(balance_prev, col_map_prev, ['52', '53', '54', '57'])
                return tresorerie
            return 0
        
        elif type_poste == 'cafg':
            # CAFG = Résultat + Dotations - Reprises + VNC cessions - Produits cessions
            resultat = resultat_net_n if balance is balance_n else resultat_net_n1
            dotations = abs(get_solde_by_racine(balance, col_map, ['681', '691', '697', '851']))
            reprises = abs(get_solde_by_racine(balance, col_map, ['781', '791', '797', '861']))
            vnc_cessions = abs(get_solde_by_racine(balance, col_map, ['81']))
            produits_cessions = abs(get_solde_by_racine(balance, col_map, ['82']))
            return resultat + dotations - reprises + vnc_cessions - produits_cessions
        
        elif type_poste == 'var_stocks':
            if balance_prev is not None:
                stocks_n = get_solde_by_racine(balance, col_map, ['31', '32', '33', '34', '35', '36', '37'])
                stocks_prev = get_solde_by_racine(balance_prev, col_map_prev, ['31', '32', '33', '34', '35', '36', '37'])
                return -(stocks_n - stocks_prev)  # Négatif car augmentation = besoin
            return 0
        
        elif type_poste == 'var_creances':
            if balance_prev is not None:
                creances_n = get_solde_by_racine(balance, col_map, ['40', '41', '42', '43', '44', '45', '46', '47'])
                creances_prev = get_solde_by_racine(balance_prev, col_map_prev, ['40', '41', '42', '43', '44', '45', '46', '47'])
                return -(max(0, creances_n) - max(0, creances_prev))
            return 0
        
        elif type_poste == 'var_passif_circ':
            if balance_prev is not None:
                dettes_n = abs(min(0, get_solde_by_racine(balance, col_map, ['40', '42', '43', '44', '45', '46', '47'])))
                dettes_prev = abs(min(0, get_solde_by_racine(balance_prev, col_map_prev, ['40', '42', '43', '44', '45', '46', '47'])))
                return dettes_n - dettes_prev  # Positif car augmentation = ressource
            return 0
        
        elif type_poste == 'invest_incorp':
            # Acquisitions immo incorporelles (augmentation brute)
            if balance_prev is not None:
                immo_n = get_solde_by_racine(balance, col_map, ['21'])
                immo_prev = get_solde_by_racine(balance_prev, col_map_prev, ['21'])
                return -(max(0, immo_n - immo_prev))  # Négatif car décaissement
            return 0
        
        elif type_poste == 'invest_corp':
            if balance_prev is not None:
                immo_n = get_solde_by_racine(balance, col_map, ['22', '23', '24'])
                immo_prev = get_solde_by_racine(balance_prev, col_map_prev, ['22', '23', '24'])
                return -(max(0, immo_n - immo_prev))
            return 0
        
        elif type_poste == 'invest_fin':
            if balance_prev is not None:
                immo_n = get_solde_by_racine(balance, col_map, ['26', '27'])
                immo_prev = get_solde_by_racine(balance_prev, col_map_prev, ['26', '27'])
                return -(max(0, immo_n - immo_prev))
            return 0
        
        elif type_poste == 'cessions':
            # Produits de cessions
            produits = abs(get_solde_by_racine(balance, col_map, ['82']))
            return produits  # Positif car encaissement
        
        elif type_poste == 'aug_capital':
            if balance_prev is not None:
                capital_n = abs(get_solde_by_racine(balance, col_map, ['10']))
                capital_prev = abs(get_solde_by_racine(balance_prev, col_map_prev, ['10']))
                return max(0, capital_n - capital_prev)
            return 0
        
        elif type_poste == 'dividendes':
            # Dividendes versés (compte 46)
            dividendes = abs(get_solde_by_racine(balance, col_map, ['465']))
            return -dividendes  # Négatif car décaissement
        
        elif type_poste == 'emprunts':
            if balance_prev is not None:
                emprunts_n = abs(get_solde_by_racine(balance, col_map, ['16', '17']))
                emprunts_prev = abs(get_solde_by_racine(balance_prev, col_map_prev, ['16', '17']))
                return max(0, emprunts_n - emprunts_prev)
            return 0
        
        elif type_poste == 'rembours':
            if balance_prev is not None:
                emprunts_n = abs(get_solde_by_racine(balance, col_map, ['16', '17']))
                emprunts_prev = abs(get_solde_by_racine(balance_prev, col_map_prev, ['16', '17']))
                return -max(0, emprunts_prev - emprunts_n)  # Négatif car décaissement
            return 0
        
        elif type_poste == 'tresorerie_fin':
            tresorerie = get_solde_by_racine(balance, col_map, ['52', '53', '54', '57'])
            return tresorerie
        
        return 0
    
    # Calculer tous les postes pour N et N-1
    tft_data = []
    montants_n = {}
    montants_n1 = {}
    
    for ligne in tft_structure:
        ref = ligne['ref']
        libelle = ligne['libelle']
        type_poste = ligne.get('type', '')
        formule = ligne.get('formule', '')
        
        # Calculer N
        if type_poste == 'total' and formule:
            # Calculer avec formule
            try:
                montant_n = eval(formule, {}, montants_n)
            except:
                montant_n = 0
        else:
            montant_n = calculer_poste(type_poste, balance_n, col_map_n, balance_n1, col_map_n1)
        
        montants_n[ref] = montant_n
        
        # Calculer N-1
        if type_poste == 'total' and formule:
            try:
                montant_n1 = eval(formule, {}, montants_n1)
            except:
                montant_n1 = 0
        else:
            montant_n1 = calculer_poste(type_poste, balance_n1, col_map_n1, balance_n2, col_map_n2) if balance_n2 is not None else 0
        
        montants_n1[ref] = montant_n1
        
        tft_data.append({
            'ref': ref,
            'libelle': libelle,
            'montant_n': montant_n,
            'montant_n1': montant_n1,
            'is_total': type_poste == 'total' or ref.startswith('Z')
        })
    
    logger.info(f"✅ TFT calculé: {len(tft_data)} lignes")
    
    return {
        'tft': tft_data,
        'variation_tresorerie_n': montants_n.get('ZE', 0),
        'variation_tresorerie_n1': montants_n1.get('ZE', 0)
    }
