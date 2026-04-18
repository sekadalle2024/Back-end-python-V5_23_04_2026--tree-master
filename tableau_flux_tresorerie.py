# -*- coding: utf-8 -*-
"""
Module de calcul du Tableau des Flux de Trésorerie (TFT) SYSCOHADA
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("tft")


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
        return f"{x:,.2f}".replace(',', ' ').replace('.', ',')
    except:
        return str(x)


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
    """
    Calcule le solde total pour une liste de racines de comptes
    """
    total = 0.0
    
    for _, row in balance_df.iterrows():
        numero = str(row.get(col_map['numero'], '')).strip()
        if not numero or numero == 'nan' or not numero[0].isdigit():
            continue
        
        # Vérifier si le compte commence par une des racines
        for racine in racines:
            if numero.startswith(racine):
                solde_debit = clean_number(row.get(col_map['solde_debit'], 0)) if col_map['solde_debit'] else 0
                solde_credit = clean_number(row.get(col_map['solde_credit'], 0)) if col_map['solde_credit'] else 0
                total += (solde_debit - solde_credit)
                break
    
    return total


def calculer_cafg(balance_n: pd.DataFrame, col_map: Dict, resultat_net: float) -> Dict[str, Any]:
    """
    Calcule la Capacité d'Autofinancement Globale (CAFG)
    Méthode additive à partir du résultat net
    """
    # Dotations aux amortissements et provisions
    dotations = get_solde_by_racine(balance_n, col_map, ['681', '691', '697', '851'])
    
    # Reprises sur amortissements et provisions
    reprises = get_solde_by_racine(balance_n, col_map, ['781', '791', '797', '861'])
    
    # Valeur comptable des cessions d'immobilisations
    valeur_comptable_cessions = get_solde_by_racine(balance_n, col_map, ['81'])
    
    # Produits de cessions d'immobilisations
    produits_cessions = get_solde_by_racine(balance_n, col_map, ['82'])
    
    # Subventions d'investissement virées au résultat
    subventions_virees = get_solde_by_racine(balance_n, col_map, ['865'])
    
    # Calcul CAFG
    cafg = (resultat_net 
            + abs(dotations)  # Les dotations sont en débit (charges)
            - abs(reprises)   # Les reprises sont en crédit (produits)
            + abs(valeur_comptable_cessions)  # Charges HAO
            - abs(produits_cessions)  # Produits HAO
            - abs(subventions_virees))  # Produits HAO
    
    return {
        'cafg': cafg,
        'resultat_net': resultat_net,
        'dotations': abs(dotations),
        'reprises': abs(reprises),
        'valeur_comptable_cessions': abs(valeur_comptable_cessions),
        'produits_cessions': abs(produits_cessions),
        'subventions_virees': abs(subventions_virees)
    }


def calculer_variation_bfr(balance_n: pd.DataFrame, balance_n1: pd.DataFrame, col_map_n: Dict, col_map_n1: Dict) -> Dict[str, float]:
    """
    Calcule les variations du Besoin en Fonds de Roulement
    """
    # Variation des stocks (classe 3)
    stocks_n = get_solde_by_racine(balance_n, col_map_n, ['31', '32', '33', '34', '35', '36', '37', '38'])
    stocks_n1 = get_solde_by_racine(balance_n1, col_map_n1, ['31', '32', '33', '34', '35', '36', '37', '38'])
    variation_stocks = stocks_n - stocks_n1
    
    # Variation des créances (classe 4 - créances)
    creances_n = get_solde_by_racine(balance_n, col_map_n, ['40', '41', '42', '43', '44', '45', '46', '47', '48'])
    creances_n1 = get_solde_by_racine(balance_n1, col_map_n1, ['40', '41', '42', '43', '44', '45', '46', '47', '48'])
    # Filtrer pour ne garder que les soldes débiteurs (créances)
    variation_creances = max(0, creances_n) - max(0, creances_n1)
    
    # Variation du passif circulant (classe 4 - dettes)
    dettes_n = abs(min(0, get_solde_by_racine(balance_n, col_map_n, ['40', '42', '43', '44', '45', '46', '47', '48'])))
    dettes_n1 = abs(min(0, get_solde_by_racine(balance_n1, col_map_n1, ['40', '42', '43', '44', '45', '46', '47', '48'])))
    variation_dettes = dettes_n - dettes_n1
    
    # Variation actif circulant HAO
    actif_hao_n = get_solde_by_racine(balance_n, col_map_n, ['48'])  # Comptes HAO
    actif_hao_n1 = get_solde_by_racine(balance_n1, col_map_n1, ['48'])
    variation_actif_hao = actif_hao_n - actif_hao_n1
    
    return {
        'variation_actif_hao': variation_actif_hao,
        'variation_stocks': variation_stocks,
        'variation_creances': variation_creances,
        'variation_dettes': variation_dettes,
        'stocks_n': stocks_n,
        'stocks_n1': stocks_n1,
        'creances_n': creances_n,
        'creances_n1': creances_n1,
        'dettes_n': dettes_n,
        'dettes_n1': dettes_n1
    }


def calculer_flux_investissement(balance_n: pd.DataFrame, balance_n1: pd.DataFrame, col_map_n: Dict, col_map_n1: Dict) -> Dict[str, float]:
    """
    Calcule les flux de trésorerie liés aux investissements
    """
    # Immobilisations incorporelles (classe 21)
    immob_incorp_n = get_solde_by_racine(balance_n, col_map_n, ['21'])
    immob_incorp_n1 = get_solde_by_racine(balance_n1, col_map_n1, ['21'])
    decaissement_incorp = max(0, immob_incorp_n - immob_incorp_n1)
    
    # Immobilisations corporelles (classe 22-24)
    immob_corp_n = get_solde_by_racine(balance_n, col_map_n, ['22', '23', '24'])
    immob_corp_n1 = get_solde_by_racine(balance_n1, col_map_n1, ['22', '23', '24'])
    decaissement_corp = max(0, immob_corp_n - immob_corp_n1)
    
    # Immobilisations financières (classe 26-27)
    immob_fin_n = get_solde_by_racine(balance_n, col_map_n, ['26', '27'])
    immob_fin_n1 = get_solde_by_racine(balance_n1, col_map_n1, ['26', '27'])
    decaissement_fin = max(0, immob_fin_n - immob_fin_n1)
    
    # Produits de cessions (compte 82)
    encaissement_cessions_immob = abs(get_solde_by_racine(balance_n, col_map_n, ['82']))
    
    # Produits de cessions financières (compte 826)
    encaissement_cessions_fin = abs(get_solde_by_racine(balance_n, col_map_n, ['826']))
    
    return {
        'decaissement_incorp': -decaissement_incorp,
        'decaissement_corp': -decaissement_corp,
        'decaissement_fin': -decaissement_fin,
        'encaissement_cessions_immob': encaissement_cessions_immob,
        'encaissement_cessions_fin': encaissement_cessions_fin,
        'immob_incorp_n': immob_incorp_n,
        'immob_incorp_n1': immob_incorp_n1,
        'immob_corp_n': immob_corp_n,
        'immob_corp_n1': immob_corp_n1,
        'immob_fin_n': immob_fin_n,
        'immob_fin_n1': immob_fin_n1
    }


def calculer_flux_financement(balance_n: pd.DataFrame, balance_n1: pd.DataFrame, col_map_n: Dict, col_map_n1: Dict) -> Dict[str, float]:
    """
    Calcule les flux de trésorerie liés au financement
    """
    # Augmentation de capital (compte 101)
    capital_n = abs(get_solde_by_racine(balance_n, col_map_n, ['101']))
    capital_n1 = abs(get_solde_by_racine(balance_n1, col_map_n1, ['101']))
    augmentation_capital = max(0, capital_n - capital_n1)
    prelevement_capital = max(0, capital_n1 - capital_n)
    
    # Subventions d'investissement (compte 14)
    subventions_n = abs(get_solde_by_racine(balance_n, col_map_n, ['14']))
    subventions_n1 = abs(get_solde_by_racine(balance_n1, col_map_n1, ['14']))
    subventions_recues = max(0, subventions_n - subventions_n1)
    
    # Dividendes versés (compte 46 ou variation 12)
    dividendes = abs(get_solde_by_racine(balance_n, col_map_n, ['46']))
    
    # Emprunts (comptes 161, 162, 1661, 1662)
    emprunts_n = abs(get_solde_by_racine(balance_n, col_map_n, ['161', '162', '1661', '1662']))
    emprunts_n1 = abs(get_solde_by_racine(balance_n1, col_map_n1, ['161', '162', '1661', '1662']))
    nouveaux_emprunts = max(0, emprunts_n - emprunts_n1)
    remboursement_emprunts = max(0, emprunts_n1 - emprunts_n)
    
    # Autres dettes financières (compte 16 sauf ci-dessus, et compte 18)
    autres_dettes_n = abs(get_solde_by_racine(balance_n, col_map_n, ['16', '18']))
    autres_dettes_n1 = abs(get_solde_by_racine(balance_n1, col_map_n1, ['16', '18']))
    # Soustraire les emprunts déjà comptés
    autres_dettes_n -= emprunts_n
    autres_dettes_n1 -= emprunts_n1
    nouvelles_dettes = max(0, autres_dettes_n - autres_dettes_n1)
    
    # Remboursements totaux
    remboursements_totaux = remboursement_emprunts + max(0, autres_dettes_n1 - autres_dettes_n)
    
    return {
        'augmentation_capital': augmentation_capital,
        'subventions_recues': subventions_recues,
        'prelevement_capital': -prelevement_capital,
        'dividendes_verses': -dividendes,
        'nouveaux_emprunts': nouveaux_emprunts,
        'nouvelles_dettes': nouvelles_dettes,
        'remboursements': -remboursements_totaux,
        'capital_n': capital_n,
        'capital_n1': capital_n1,
        'emprunts_n': emprunts_n,
        'emprunts_n1': emprunts_n1
    }


def calculer_tresorerie(balance_df: pd.DataFrame, col_map: Dict) -> float:
    """
    Calcule la trésorerie nette (Actif - Passif)
    """
    # Trésorerie actif (comptes 50, 51, 52, 53, 54, 57, 58)
    tresorerie_actif = get_solde_by_racine(balance_df, col_map, ['50', '51', '52', '53', '54', '57', '58'])
    tresorerie_actif = max(0, tresorerie_actif)  # Ne garder que les soldes débiteurs
    
    # Trésorerie passif (compte 56 - crédits de trésorerie)
    tresorerie_passif = abs(min(0, get_solde_by_racine(balance_df, col_map, ['56'])))
    
    return tresorerie_actif - tresorerie_passif


def calculer_tft(balance_n: pd.DataFrame, balance_n1: pd.DataFrame, resultat_net: float) -> Dict[str, Any]:
    """
    Calcule le Tableau des Flux de Trésorerie complet
    
    Args:
        balance_n: Balance de l'exercice N
        balance_n1: Balance de l'exercice N-1
        resultat_net: Résultat net de l'exercice N
    
    Returns:
        Dictionnaire contenant tous les flux et contrôles
    """
    logger.info("📊 Calcul du Tableau des Flux de Trésorerie")
    
    # Détecter les colonnes
    col_map_n = detect_balance_columns(balance_n)
    col_map_n1 = detect_balance_columns(balance_n1)
    
    # A. Trésorerie d'ouverture
    tresorerie_ouverture = calculer_tresorerie(balance_n1, col_map_n1)
    
    # B. Flux opérationnels
    cafg_data = calculer_cafg(balance_n, col_map_n, resultat_net)
    cafg = cafg_data['cafg']
    
    bfr_data = calculer_variation_bfr(balance_n, balance_n1, col_map_n, col_map_n1)
    
    flux_operationnels = (cafg 
                         - bfr_data['variation_actif_hao']
                         - bfr_data['variation_stocks']
                         - bfr_data['variation_creances']
                         + bfr_data['variation_dettes'])
    
    # C. Flux d'investissement
    invest_data = calculer_flux_investissement(balance_n, balance_n1, col_map_n, col_map_n1)
    
    flux_investissement = (invest_data['decaissement_incorp']
                          + invest_data['decaissement_corp']
                          + invest_data['decaissement_fin']
                          + invest_data['encaissement_cessions_immob']
                          + invest_data['encaissement_cessions_fin'])
    
    # D & E. Flux de financement
    fin_data = calculer_flux_financement(balance_n, balance_n1, col_map_n, col_map_n1)
    
    flux_capitaux_propres = (fin_data['augmentation_capital']
                             + fin_data['subventions_recues']
                             + fin_data['prelevement_capital']
                             + fin_data['dividendes_verses'])
    
    flux_capitaux_etrangers = (fin_data['nouveaux_emprunts']
                               + fin_data['nouvelles_dettes']
                               + fin_data['remboursements'])
    
    flux_financement = flux_capitaux_propres + flux_capitaux_etrangers
    
    # G. Variation de trésorerie
    variation_tresorerie = flux_operationnels + flux_investissement + flux_financement
    
    # H. Trésorerie de clôture
    tresorerie_cloture_calculee = tresorerie_ouverture + variation_tresorerie
    tresorerie_cloture_bilan = calculer_tresorerie(balance_n, col_map_n)
    
    # Contrôles
    controles = {
        'coherence_tresorerie': {
            'tresorerie_calculee': tresorerie_cloture_calculee,
            'tresorerie_bilan': tresorerie_cloture_bilan,
            'difference': tresorerie_cloture_calculee - tresorerie_cloture_bilan,
            'coherent': abs(tresorerie_cloture_calculee - tresorerie_cloture_bilan) < 0.01
        },
        'equilibre_flux': {
            'flux_operationnels': flux_operationnels,
            'flux_investissement': flux_investissement,
            'flux_financement': flux_financement,
            'total': flux_operationnels + flux_investissement + flux_financement,
            'variation_tresorerie': variation_tresorerie,
            'difference': (flux_operationnels + flux_investissement + flux_financement) - variation_tresorerie,
            'equilibre': abs((flux_operationnels + flux_investissement + flux_financement) - variation_tresorerie) < 0.01
        },
        'coherence_cafg': cafg_data
    }
    
    logger.info(f"✅ TFT calculé:")
    logger.info(f"   - CAFG: {format_number(cafg)}")
    logger.info(f"   - Flux opérationnels: {format_number(flux_operationnels)}")
    logger.info(f"   - Flux investissement: {format_number(flux_investissement)}")
    logger.info(f"   - Flux financement: {format_number(flux_financement)}")
    logger.info(f"   - Variation trésorerie: {format_number(variation_tresorerie)}")
    logger.info(f"   - Trésorerie clôture: {format_number(tresorerie_cloture_calculee)}")
    
    return {
        'ZA_tresorerie_ouverture': tresorerie_ouverture,
        'FA_cafg': cafg,
        'FB_variation_actif_hao': -bfr_data['variation_actif_hao'],
        'FC_variation_stocks': -bfr_data['variation_stocks'],
        'FD_variation_creances': -bfr_data['variation_creances'],
        'FE_variation_dettes': bfr_data['variation_dettes'],
        'ZB_flux_operationnels': flux_operationnels,
        'FF_decaissement_incorp': invest_data['decaissement_incorp'],
        'FG_decaissement_corp': invest_data['decaissement_corp'],
        'FH_decaissement_fin': invest_data['decaissement_fin'],
        'FI_encaissement_cessions_immob': invest_data['encaissement_cessions_immob'],
        'FJ_encaissement_cessions_fin': invest_data['encaissement_cessions_fin'],
        'ZC_flux_investissement': flux_investissement,
        'FK_augmentation_capital': fin_data['augmentation_capital'],
        'FL_subventions_recues': fin_data['subventions_recues'],
        'FM_prelevement_capital': fin_data['prelevement_capital'],
        'FN_dividendes_verses': fin_data['dividendes_verses'],
        'ZD_flux_capitaux_propres': flux_capitaux_propres,
        'FO_nouveaux_emprunts': fin_data['nouveaux_emprunts'],
        'FP_nouvelles_dettes': fin_data['nouvelles_dettes'],
        'FQ_remboursements': fin_data['remboursements'],
        'ZE_flux_capitaux_etrangers': flux_capitaux_etrangers,
        'ZF_flux_financement': flux_financement,
        'ZG_variation_tresorerie': variation_tresorerie,
        'ZH_tresorerie_cloture': tresorerie_cloture_calculee,
        'controles': controles,
        'details': {
            'cafg': cafg_data,
            'bfr': bfr_data,
            'investissement': invest_data,
            'financement': fin_data
        }
    }
