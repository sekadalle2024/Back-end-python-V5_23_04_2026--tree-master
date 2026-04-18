# -*- coding: utf-8 -*-
"""
Module de contrôles exhaustifs pour les états financiers
Structuré par état (Bilan, CR, TFT) et par exercice (N et N-1)
"""
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("controles_exhaustifs")


def format_number(x: float) -> str:
    """Formate un nombre avec séparateurs de milliers"""
    try:
        return f"{x:,.2f}".replace(',', ' ').replace('.', ',')
    except:
        return str(x)


def calculer_controles_bilan(
    bilan_actif: List[Dict],
    bilan_passif: List[Dict],
    exercice: str = "N"
) -> Dict[str, Any]:
    """
    Contrôles exhaustifs du Bilan pour un exercice donné
    """
    # Calculer les totaux
    total_actif = sum(p.get(f'montant_{exercice.lower()}', 0) for p in bilan_actif)
    total_passif = sum(p.get(f'montant_{exercice.lower()}', 0) for p in bilan_passif)
    
    # Équilibre du bilan
    difference = total_actif - total_passif
    equilibre = abs(difference) < 0.01
    
    # Contrôles par rubrique
    controles_rubriques = []
    
    # Actif immobilisé
    actif_immo = sum(p.get(f'montant_{exercice.lower()}', 0) for p in bilan_actif 
                     if p['ref'] in ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS'])
    
    # Actif circulant
    actif_circ = sum(p.get(f'montant_{exercice.lower()}', 0) for p in bilan_actif 
                     if p['re