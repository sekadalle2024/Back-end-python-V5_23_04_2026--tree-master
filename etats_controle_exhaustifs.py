# -*- coding: utf-8 -*-
"""
Module de génération des états de contrôle exhaustifs
- Un état de contrôle par document (Actif, Passif, Compte Résultat, TFT)
- Pour chaque exercice (N et N-1)
- Contrôle du sens des comptes pour chaque balance
"""

from typing import Dict, List, Any


def format_montant_controle(montant: float) -> str:
    """Formate un montant pour les contrôles"""
    if abs(montant) < 0.01:
        return "0"
    return f"{montant:,.0f}".replace(',', ' ')


def calculer_etat_controle_bilan_actif_n(bilan_actif_n: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du bilan actif pour l'exercice N"""
    total_n = sum(p.get('montant_n', 0) for p in bilan_actif_n)
    postes_n = len([p for p in bilan_actif_n if p.get('montant_n', 0) != 0])
    
    return {
        'titre': '1. Etat de contrôle Bilan Actif (Exercice N)',
        'postes': [
            {'ref': 'CA', 'libelle': 'Total Actif', 'montant_n': total_n, 'montant_n1': 0},
            {'ref': 'CB', 'libelle': 'Nombre de postes', 'montant_n': postes_n, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_bilan_actif_n1(bilan_actif_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du bilan actif pour l'exercice N-1"""
    total_n1 = sum(p.get('montant_n1', 0) for p in bilan_actif_n1)
    postes_n1 = len([p for p in bilan_actif_n1 if p.get('montant_n1', 0) != 0])
    
    return {
        'titre': '2. Etat de contrôle Bilan Actif (Exercice N-1)',
        'postes': [
            {'ref': 'CC', 'libelle': 'Total Actif', 'montant_n': 0, 'montant_n1': total_n1},
            {'ref': 'CD', 'libelle': 'Nombre de postes', 'montant_n': 0, 'montant_n1': postes_n1},
        ]
    }


def calculer_etat_controle_bilan_actif_variation(bilan_actif_n: List[Dict], bilan_actif_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule les variations du bilan actif"""
    total_n = sum(p.get('montant_n', 0) for p in bilan_actif_n)
    total_n1 = sum(p.get('montant_n1', 0) for p in bilan_actif_n1)
    
    return {
        'titre': '3. Variation Bilan Actif',
        'postes': [
            {'ref': 'CD', 'libelle': 'Variation Total', 'montant_n': total_n - total_n1, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_bilan_passif_n(bilan_passif_n: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du bilan passif pour l'exercice N"""
    total_n = sum(p.get('montant_n', 0) for p in bilan_passif_n)
    postes_n = len([p for p in bilan_passif_n if p.get('montant_n', 0) != 0])
    
    return {
        'titre': '4. Etat de contrôle Bilan Passif (Exercice N)',
        'postes': [
            {'ref': 'PA', 'libelle': 'Total Passif', 'montant_n': total_n, 'montant_n1': 0},
            {'ref': 'PB', 'libelle': 'Nombre de postes', 'montant_n': postes_n, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_bilan_passif_n1(bilan_passif_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du bilan passif pour l'exercice N-1"""
    total_n1 = sum(p.get('montant_n1', 0) for p in bilan_passif_n1)
    postes_n1 = len([p for p in bilan_passif_n1 if p.get('montant_n1', 0) != 0])
    
    return {
        'titre': '5. Etat de contrôle Bilan Passif (Exercice N-1)',
        'postes': [
            {'ref': 'PC', 'libelle': 'Total Passif', 'montant_n': 0, 'montant_n1': total_n1},
            {'ref': 'PD', 'libelle': 'Nombre de postes', 'montant_n': 0, 'montant_n1': postes_n1},
        ]
    }


def calculer_etat_controle_bilan_passif_variation(bilan_passif_n: List[Dict], bilan_passif_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule les variations du bilan passif"""
    total_n = sum(p.get('montant_n', 0) for p in bilan_passif_n)
    total_n1 = sum(p.get('montant_n1', 0) for p in bilan_passif_n1)
    
    return {
        'titre': '6. Variation Bilan Passif',
        'postes': [
            {'ref': 'PD', 'libelle': 'Variation Total', 'montant_n': total_n - total_n1, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_compte_resultat_n(compte_resultat_n: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du compte de résultat pour l'exercice N"""
    resultat_n = compte_resultat_n[-1].get('montant_n', 0) if compte_resultat_n else 0
    postes_n = len([p for p in compte_resultat_n if p.get('montant_n', 0) != 0])
    
    return {
        'titre': '7. Etat de contrôle Compte de Résultat (Exercice N)',
        'postes': [
            {'ref': 'RA', 'libelle': 'Résultat Net', 'montant_n': resultat_n, 'montant_n1': 0},
            {'ref': 'RC', 'libelle': 'Nombre de postes', 'montant_n': postes_n, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_compte_resultat_n1(compte_resultat_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du compte de résultat pour l'exercice N-1"""
    resultat_n1 = compte_resultat_n1[-1].get('montant_n1', 0) if compte_resultat_n1 else 0
    postes_n1 = len([p for p in compte_resultat_n1 if p.get('montant_n1', 0) != 0])
    
    return {
        'titre': '8. Etat de contrôle Compte de Résultat (Exercice N-1)',
        'postes': [
            {'ref': 'RD', 'libelle': 'Résultat Net', 'montant_n': 0, 'montant_n1': resultat_n1},
            {'ref': 'RF', 'libelle': 'Nombre de postes', 'montant_n': 0, 'montant_n1': postes_n1},
        ]
    }


def calculer_etat_controle_compte_resultat_variation(compte_resultat_n: List[Dict], compte_resultat_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule les variations du compte de résultat"""
    resultat_n = compte_resultat_n[-1].get('montant_n', 0) if compte_resultat_n else 0
    resultat_n1 = compte_resultat_n1[-1].get('montant_n1', 0) if compte_resultat_n1 else 0
    
    return {
        'titre': '9. Variation Compte de Résultat',
        'postes': [
            {'ref': 'RE', 'libelle': 'Variation Résultat', 'montant_n': resultat_n - resultat_n1, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_tft_n(tft_n: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du TFT pour l'exercice N"""
    tresorerie_fin_n = next((p['montant_n'] for p in tft_n if p['ref'] == 'ZF'), 0) if tft_n else 0
    variation_n = next((p['montant_n'] for p in tft_n if p['ref'] == 'ZE'), 0) if tft_n else 0
    flux_op_n = next((p['montant_n'] for p in tft_n if p['ref'] == 'ZB'), 0) if tft_n else 0
    
    return {
        'titre': '10. Etat de contrôle Tableau des Flux de Trésorerie (Exercice N)',
        'postes': [
            {'ref': 'TA', 'libelle': 'Trésorerie finale', 'montant_n': tresorerie_fin_n, 'montant_n1': 0},
            {'ref': 'TC', 'libelle': 'Variation trésorerie', 'montant_n': variation_n, 'montant_n1': 0},
            {'ref': 'TE', 'libelle': 'Flux opérationnels', 'montant_n': flux_op_n, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_tft_n1(tft_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du TFT pour l'exercice N-1"""
    tresorerie_fin_n1 = next((p['montant_n1'] for p in tft_n1 if p['ref'] == 'ZF'), 0) if tft_n1 else 0
    variation_n1 = next((p['montant_n1'] for p in tft_n1 if p['ref'] == 'ZE'), 0) if tft_n1 else 0
    flux_op_n1 = next((p['montant_n1'] for p in tft_n1 if p['ref'] == 'ZB'), 0) if tft_n1 else 0
    
    return {
        'titre': '11. Etat de contrôle Tableau des Flux de Trésorerie (Exercice N-1)',
        'postes': [
            {'ref': 'TG', 'libelle': 'Trésorerie finale', 'montant_n': 0, 'montant_n1': tresorerie_fin_n1},
            {'ref': 'TI', 'libelle': 'Variation trésorerie', 'montant_n': 0, 'montant_n1': variation_n1},
            {'ref': 'TK', 'libelle': 'Flux opérationnels', 'montant_n': 0, 'montant_n1': flux_op_n1},
        ]
    }


def calculer_etat_controle_tft_variation(tft_n: List[Dict], tft_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule les variations du TFT"""
    tresorerie_fin_n = next((p['montant_n'] for p in tft_n if p['ref'] == 'ZF'), 0) if tft_n else 0
    tresorerie_fin_n1 = next((p['montant_n1'] for p in tft_n1 if p['ref'] == 'ZF'), 0) if tft_n1 else 0
    
    return {
        'titre': '12. Variation Tableau des Flux de Trésorerie',
        'postes': [
            {'ref': 'TL', 'libelle': 'Variation Trésorerie', 'montant_n': tresorerie_fin_n - tresorerie_fin_n1, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_sens_comptes_n(balance_n: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du sens des comptes pour l'exercice N"""
    comptes_debit_n = len([c for c in balance_n if c.get('solde_debit', 0) > 0])
    comptes_credit_n = len([c for c in balance_n if c.get('solde_credit', 0) > 0])
    total_debit_n = sum(c.get('solde_debit', 0) for c in balance_n)
    total_credit_n = sum(c.get('solde_credit', 0) for c in balance_n)
    
    return {
        'titre': '13. Etat de contrôle Sens des Comptes (Exercice N)',
        'postes': [
            {'ref': 'SA', 'libelle': 'Comptes en débit', 'montant_n': comptes_debit_n, 'montant_n1': 0},
            {'ref': 'SB', 'libelle': 'Comptes en crédit', 'montant_n': comptes_credit_n, 'montant_n1': 0},
            {'ref': 'SE', 'libelle': 'Total débit', 'montant_n': total_debit_n, 'montant_n1': 0},
            {'ref': 'SF', 'libelle': 'Total crédit', 'montant_n': total_credit_n, 'montant_n1': 0},
            {'ref': 'SI', 'libelle': 'Équilibre', 'montant_n': total_debit_n - total_credit_n, 'montant_n1': 0},
        ]
    }


def calculer_etat_controle_sens_comptes_n1(balance_n1: List[Dict]) -> Dict[str, Any]:
    """Calcule l'état de contrôle du sens des comptes pour l'exercice N-1"""
    comptes_debit_n1 = len([c for c in balance_n1 if c.get('solde_debit', 0) > 0])
    comptes_credit_n1 = len([c for c in balance_n1 if c.get('solde_credit', 0) > 0])
    total_debit_n1 = sum(c.get('solde_debit', 0) for c in balance_n1)
    total_credit_n1 = sum(c.get('solde_credit', 0) for c in balance_n1)
    
    return {
        'titre': '14. Etat de contrôle Sens des Comptes (Exercice N-1)',
        'postes': [
            {'ref': 'SJ', 'libelle': 'Comptes en débit', 'montant_n': 0, 'montant_n1': comptes_debit_n1},
            {'ref': 'SK', 'libelle': 'Comptes en crédit', 'montant_n': 0, 'montant_n1': comptes_credit_n1},
            {'ref': 'SN', 'libelle': 'Total débit', 'montant_n': 0, 'montant_n1': total_debit_n1},
            {'ref': 'SO', 'libelle': 'Total crédit', 'montant_n': 0, 'montant_n1': total_credit_n1},
            {'ref': 'SR', 'libelle': 'Équilibre', 'montant_n': 0, 'montant_n1': total_debit_n1 - total_credit_n1},
        ]
    }


def calculer_etat_equilibre_bilan_n(bilan_actif_n: List[Dict], bilan_passif_n: List[Dict], resultat_net_n: float) -> Dict[str, Any]:
    """Calcule l'état d'équilibre du bilan pour l'exercice N"""
    total_actif_n = sum(p.get('montant_n', 0) for p in bilan_actif_n)
    total_passif_n = sum(p.get('montant_n', 0) for p in bilan_passif_n)
    equilibre_n = total_actif_n - (total_passif_n + resultat_net_n)
    
    return {
        'titre': '15. Etat d\'équilibre Bilan (Exercice N)',
        'postes': [
            {'ref': 'EA', 'libelle': 'Total Actif', 'montant_n': total_actif_n, 'montant_n1': 0},
            {'ref': 'EB', 'libelle': 'Total Passif', 'montant_n': total_passif_n, 'montant_n1': 0},
            {'ref': 'EC', 'libelle': 'Résultat Net', 'montant_n': resultat_net_n, 'montant_n1': 0},
            {'ref': 'ED', 'libelle': 'Passif + Résultat', 'montant_n': total_passif_n + resultat_net_n, 'montant_n1': 0},
            {'ref': 'EE', 'libelle': 'Équilibre', 'montant_n': equilibre_n, 'montant_n1': 0},
        ]
    }


def calculer_etat_equilibre_bilan_n1(bilan_actif_n1: List[Dict], bilan_passif_n1: List[Dict], resultat_net_n1: float) -> Dict[str, Any]:
    """Calcule l'état d'équilibre du bilan pour l'exercice N-1"""
    total_actif_n1 = sum(p.get('montant_n1', 0) for p in bilan_actif_n1)
    total_passif_n1 = sum(p.get('montant_n1', 0) for p in bilan_passif_n1)
    equilibre_n1 = total_actif_n1 - (total_passif_n1 + resultat_net_n1)
    
    return {
        'titre': '16. Etat d\'équilibre Bilan (Exercice N-1)',
        'postes': [
            {'ref': 'EF', 'libelle': 'Total Actif', 'montant_n': 0, 'montant_n1': total_actif_n1},
            {'ref': 'EG', 'libelle': 'Total Passif', 'montant_n': 0, 'montant_n1': total_passif_n1},
            {'ref': 'EH', 'libelle': 'Résultat Net', 'montant_n': 0, 'montant_n1': resultat_net_n1},
            {'ref': 'EI', 'libelle': 'Passif + Résultat', 'montant_n': 0, 'montant_n1': total_passif_n1 + resultat_net_n1},
            {'ref': 'EJ', 'libelle': 'Équilibre', 'montant_n': 0, 'montant_n1': equilibre_n1},
        ]
    }
