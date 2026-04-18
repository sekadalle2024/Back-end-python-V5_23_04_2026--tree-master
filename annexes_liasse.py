# -*- coding: utf-8 -*-
"""Module de calcul des Annexes de la Liasse Officielle SYSCOHADA"""
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("annexes")


def format_number(x: float) -> str:
    """Formate un nombre avec séparateurs de milliers"""
    try:
        return f"{x:,.2f}".replace(',', ' ').replace('.', ',')
    except:
        return str(x)


def calculer_note_3a_immobilisations_incorporelles(bilan_actif: Dict) -> Dict[str, Any]:
    """NOTE 3A - Immobilisations incorporelles"""
    immo_incorp = {}
    for ref, poste in bilan_actif.items():
        if ref.startswith('A') and 'incorporel' in poste['libelle'].lower():
            immo_incorp[ref] = {
                'libelle': poste['libelle'],
                'montant_brut': poste['montant'],
                'amortissements': 0,
                'montant_net': poste['montant']
            }
    return {
        'titre': 'NOTE 3A - Immobilisations incorporelles',
        'postes': immo_incorp,
        'total': sum(p['montant_net'] for p in immo_incorp.values())
    }


def calculer_note_6_stocks(bilan_actif: Dict) -> Dict[str, Any]:
    """NOTE 6 - État des stocks"""
    stocks = {}
    for ref, poste in bilan_actif.items():
        if 'stock' in poste['libelle'].lower() or 'marchandise' in poste['libelle'].lower():
            stocks[ref] = {'libelle': poste['libelle'], 'montant': poste['montant']}
    return {
        'titre': 'NOTE 6 - État des stocks',
        'postes': stocks,
        'total': sum(p['montant'] for p in stocks.values())
    }


def calculer_note_7_creances(bilan_actif: Dict) -> Dict[str, Any]:
    """NOTE 7 - État des créances"""
    creances = {}
    for ref, poste in bilan_actif.items():
        if any(mot in poste['libelle'].lower() for mot in ['créance', 'client', 'débiteur']):
            creances[ref] = {'libelle': poste['libelle'], 'montant': poste['montant']}
    return {
        'titre': 'NOTE 7 - État des créances',
        'postes': creances,
        'total': sum(p['montant'] for p in creances.values())
    }


def calculer_note_10_capital(bilan_passif: Dict) -> Dict[str, Any]:
    """NOTE 10 - Capital social"""
    capital_data = {}
    for ref, poste in bilan_passif.items():
        if 'capital' in poste['libelle'].lower():
            capital_data[ref] = {'libelle': poste['libelle'], 'montant': poste['montant']}
    return {
        'titre': 'NOTE 10 - Capital social',
        'postes': capital_data,
        'total': sum(p['montant'] for p in capital_data.values())
    }


def calculer_note_13_resultat(totaux: Dict) -> Dict[str, Any]:
    """NOTE 13 - Resultat net"""
    resultat_net = totaux.get('resultat_net', 0)
    return {
        'titre': 'NOTE 13 - Résultat net',
        'resultat_net': resultat_net,
        'type': 'Bénéfice' if resultat_net > 0 else 'Perte' if resultat_net < 0 else 'Nul',
        'montant_absolu': abs(resultat_net)
    }


def calculer_note_21_chiffre_affaires(produits: Dict) -> Dict[str, Any]:
    """NOTE 21 - Chiffre d affaires"""
    ca_data = {}
    for ref, poste in produits.items():
        if any(mot in poste['libelle'].lower() for mot in ['vente', 'chiffre', 'produit']):
            ca_data[ref] = {'libelle': poste['libelle'], 'montant': poste['montant']}
    return {
        'titre': 'NOTE 21 - Chiffre d affaires',
        'postes': ca_data,
        'total': sum(p['montant'] for p in ca_data.values())
    }


def calculer_note_22_achats(charges: Dict) -> Dict[str, Any]:
    """NOTE 22 - Achats consommés"""
    achats = {}
    for ref, poste in charges.items():
        if 'achat' in poste['libelle'].lower():
            achats[ref] = {'libelle': poste['libelle'], 'montant': poste['montant']}
    return {
        'titre': 'NOTE 22 - Achats consommés',
        'postes': achats,
        'total': sum(p['montant'] for p in achats.values())
    }


def calculer_annexes(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule toutes les annexes calculables"""
    logger.info("📋 Calcul des annexes de la liasse")
    
    bilan_actif = results.get('bilan_actif', {})
    bilan_passif = results.get('bilan_passif', {})
    charges = results.get('charges', {})
    produits = results.get('produits', {})
    totaux = results.get('totaux', {})
    
    annexes = {
        'note_3a': calculer_note_3a_immobilisations_incorporelles(bilan_actif),
        'note_6': calculer_note_6_stocks(bilan_actif),
        'note_7': calculer_note_7_creances(bilan_actif),
        'note_10': calculer_note_10_capital(bilan_passif),
        'note_13': calculer_note_13_resultat(totaux),
        'note_21': calculer_note_21_chiffre_affaires(produits),
        'note_22': calculer_note_22_achats(charges),
    }
    
    nb_annexes = len([a for a in annexes.values() if a.get('postes') or a.get('resultat_net') is not None])
    logger.info(f"✅ {nb_annexes} annexes calculées")
    
    return annexes
