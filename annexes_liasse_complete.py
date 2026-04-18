# -*- coding: utf-8 -*-
"""
Module de calcul des Annexes COMPLÈTES de la Liasse Officielle SYSCOHADA
Toutes les notes avec colonnes N et N-1
"""
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("annexes_complete")


def format_montant_liasse(montant: float) -> str:
    """Formate un montant pour la liasse (- si nul)"""
    if abs(montant) < 0.01:
        return "-"
    return f"{montant:,.0f}".replace(',', ' ')


def calculer_annexes_completes(
    bilan_actif_n: List[Dict],
    bilan_actif_n1: List[Dict],
    bilan_passif_n: List[Dict],
    bilan_passif_n1: List[Dict],
    cr_n: List[Dict],
    cr_n1: List[Dict]
) -> Dict[str, Any]:
    """
    Calcule TOUTES les annexes de la liasse officielle avec colonnes N et N-1
    """
    logger.info("📋 Calcul des annexes complètes (format liasse)")
    
    # Convertir les listes en dictionnaires pour faciliter l'accès
    def list_to_dict(liste):
        return {item['ref']: item for item in liste}
    
    actif_n = list_to_dict(bilan_actif_n)
    actif_n1 = list_to_dict(bilan_actif_n1)
    passif_n = list_to_dict(bilan_passif_n)
    passif_n1 = list_to_dict(bilan_passif_n1)
    cr_dict_n = list_to_dict(cr_n)
    cr_dict_n1 = list_to_dict(cr_n1)
    
    annexes = {}
    
    # ========== NOTE 3A - IMMOBILISATIONS INCORPORELLES ==========
    annexes['note_3a'] = {
        'titre': 'NOTE 3A - Immobilisations incorporelles',
        'postes': [
            {
                'ref': 'AD',
                'libelle': 'IMMOBILISATIONS INCORPORELLES',
                'montant_n': actif_n.get('AD', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AD', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AE',
                'libelle': 'Frais de recherche et de développement',
                'montant_n': actif_n.get('AE', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AE', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AF',
                'libelle': 'Brevets, licences, logiciels',
                'montant_n': actif_n.get('AF', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AF', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AG',
                'libelle': 'Fonds commercial',
                'montant_n': actif_n.get('AG', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AG', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AH',
                'libelle': 'Autres immobilisations incorporelles',
                'montant_n': actif_n.get('AH', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AH', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 3B - IMMOBILISATIONS CORPORELLES ==========
    annexes['note_3b'] = {
        'titre': 'NOTE 3B - Immobilisations corporelles',
        'postes': [
            {
                'ref': 'AI',
                'libelle': 'IMMOBILISATIONS CORPORELLES',
                'montant_n': actif_n.get('AI', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AI', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AJ',
                'libelle': 'Terrains',
                'montant_n': actif_n.get('AJ', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AJ', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AK',
                'libelle': 'Bâtiments',
                'montant_n': actif_n.get('AK', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AK', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AL',
                'libelle': 'Installations et agencements',
                'montant_n': actif_n.get('AL', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AL', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AM',
                'libelle': 'Matériel',
                'montant_n': actif_n.get('AM', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AM', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AN',
                'libelle': 'Matériel de transport',
                'montant_n': actif_n.get('AN', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AN', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 4 - IMMOBILISATIONS FINANCIÈRES ==========
    annexes['note_4'] = {
        'titre': 'NOTE 4 - Immobilisations financières',
        'postes': [
            {
                'ref': 'AQ',
                'libelle': 'IMMOBILISATIONS FINANCIÈRES',
                'montant_n': actif_n.get('AQ', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AQ', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AR',
                'libelle': 'Titres de participation',
                'montant_n': actif_n.get('AR', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AR', {}).get('montant_n1', 0)
            },
            {
                'ref': 'AS',
                'libelle': 'Autres immobilisations financières',
                'montant_n': actif_n.get('AS', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('AS', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 6 - ÉTAT DES STOCKS ==========
    annexes['note_6'] = {
        'titre': 'NOTE 6 - État des stocks',
        'postes': [
            {
                'ref': 'BB',
                'libelle': 'STOCKS ET ENCOURS',
                'montant_n': actif_n.get('BB', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BB', {}).get('montant_n1', 0)
            },
            {
                'ref': 'BG',
                'libelle': 'Marchandises',
                'montant_n': actif_n.get('BG', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BG', {}).get('montant_n1', 0)
            },
            {
                'ref': 'BH',
                'libelle': 'Matières premières et autres approvisionnements',
                'montant_n': actif_n.get('BH', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BH', {}).get('montant_n1', 0)
            },
            {
                'ref': 'BI',
                'libelle': 'En-cours',
                'montant_n': actif_n.get('BI', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BI', {}).get('montant_n1', 0)
            },
            {
                'ref': 'BJ',
                'libelle': 'Produits fabriqués',
                'montant_n': actif_n.get('BJ', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BJ', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 7 - ÉTAT DES CRÉANCES ==========
    annexes['note_7'] = {
        'titre': 'NOTE 7 - État des créances',
        'postes': [
            {
                'ref': 'BK',
                'libelle': 'CRÉANCES ET EMPLOIS ASSIMILÉS',
                'montant_n': actif_n.get('BK', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BK', {}).get('montant_n1', 0)
            },
            {
                'ref': 'BM',
                'libelle': 'Clients',
                'montant_n': actif_n.get('BM', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BM', {}).get('montant_n1', 0)
            },
            {
                'ref': 'BN',
                'libelle': 'Autres créances',
                'montant_n': actif_n.get('BN', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BN', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 8 - TRÉSORERIE-ACTIF ==========
    annexes['note_8'] = {
        'titre': 'NOTE 8 - Trésorerie-Actif',
        'postes': [
            {
                'ref': 'BQ',
                'libelle': 'TRÉSORERIE-ACTIF',
                'montant_n': actif_n.get('BQ', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BQ', {}).get('montant_n1', 0)
            },
            {
                'ref': 'BR',
                'libelle': 'Banques, chèques postaux, caisse',
                'montant_n': actif_n.get('BR', {}).get('montant_n', 0),
                'montant_n1': actif_n1.get('BR', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 10 - CAPITAL SOCIAL ==========
    annexes['note_10'] = {
        'titre': 'NOTE 10 - Capital social',
        'postes': [
            {
                'ref': 'CA',
                'libelle': 'Capital',
                'montant_n': passif_n.get('CA', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('CA', {}).get('montant_n1', 0)
            },
            {
                'ref': 'CB',
                'libelle': 'Apporteurs, capital non appelé',
                'montant_n': passif_n.get('CB', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('CB', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 11 - RÉSERVES ==========
    annexes['note_11'] = {
        'titre': 'NOTE 11 - Réserves et report à nouveau',
        'postes': [
            {
                'ref': 'CC',
                'libelle': 'Primes liées au capital social',
                'montant_n': passif_n.get('CC', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('CC', {}).get('montant_n1', 0)
            },
            {
                'ref': 'CD',
                'libelle': 'Écarts de réévaluation',
                'montant_n': passif_n.get('CD', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('CD', {}).get('montant_n1', 0)
            },
            {
                'ref': 'CE',
                'libelle': 'Réserves indisponibles',
                'montant_n': passif_n.get('CE', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('CE', {}).get('montant_n1', 0)
            },
            {
                'ref': 'CF',
                'libelle': 'Réserves libres',
                'montant_n': passif_n.get('CF', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('CF', {}).get('montant_n1', 0)
            },
            {
                'ref': 'CG',
                'libelle': 'Report à nouveau',
                'montant_n': passif_n.get('CG', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('CG', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 13 - RÉSULTAT NET ==========
    resultat_n = cr_dict_n.get('XI', {}).get('montant_n', 0)
    resultat_n1 = cr_dict_n1.get('XI', {}).get('montant_n1', 0)
    
    annexes['note_13'] = {
        'titre': 'NOTE 13 - Résultat net de l\'exercice',
        'postes': [
            {
                'ref': 'XI',
                'libelle': 'RÉSULTAT NET',
                'montant_n': resultat_n,
                'montant_n1': resultat_n1,
                'type': 'Bénéfice' if resultat_n > 0 else 'Perte' if resultat_n < 0 else 'Nul'
            }
        ]
    }
    
    # ========== NOTE 14 - EMPRUNTS ET DETTES FINANCIÈRES ==========
    annexes['note_14'] = {
        'titre': 'NOTE 14 - Emprunts et dettes financières',
        'postes': [
            {
                'ref': 'DA',
                'libelle': 'Emprunts',
                'montant_n': passif_n.get('DA', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DA', {}).get('montant_n1', 0)
            },
            {
                'ref': 'DB',
                'libelle': 'Dettes de crédit-bail et contrats assimilés',
                'montant_n': passif_n.get('DB', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DB', {}).get('montant_n1', 0)
            },
            {
                'ref': 'DC',
                'libelle': 'Dettes financières diverses',
                'montant_n': passif_n.get('DC', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DC', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 16 - DETTES CIRCULANTES ==========
    annexes['note_16'] = {
        'titre': 'NOTE 16 - Dettes circulantes et ressources assimilées',
        'postes': [
            {
                'ref': 'DH',
                'libelle': 'DETTES CIRCULANTES ET RESSOURCES ASSIMILÉES',
                'montant_n': passif_n.get('DH', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DH', {}).get('montant_n1', 0)
            },
            {
                'ref': 'DI',
                'libelle': 'Clients, avances reçues',
                'montant_n': passif_n.get('DI', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DI', {}).get('montant_n1', 0)
            },
            {
                'ref': 'DJ',
                'libelle': 'Fournisseurs d\'exploitation',
                'montant_n': passif_n.get('DJ', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DJ', {}).get('montant_n1', 0)
            },
            {
                'ref': 'DK',
                'libelle': 'Dettes fiscales',
                'montant_n': passif_n.get('DK', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DK', {}).get('montant_n1', 0)
            },
            {
                'ref': 'DL',
                'libelle': 'Dettes sociales',
                'montant_n': passif_n.get('DL', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DL', {}).get('montant_n1', 0)
            },
            {
                'ref': 'DM',
                'libelle': 'Autres dettes',
                'montant_n': passif_n.get('DM', {}).get('montant_n', 0),
                'montant_n1': passif_n1.get('DM', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 21 - CHIFFRE D'AFFAIRES ==========
    annexes['note_21'] = {
        'titre': 'NOTE 21 - Chiffre d\'affaires',
        'postes': [
            {
                'ref': 'TA',
                'libelle': 'Ventes de marchandises',
                'montant_n': cr_dict_n.get('TA', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('TA', {}).get('montant_n1', 0)
            },
            {
                'ref': 'TB',
                'libelle': 'Ventes de produits fabriqués',
                'montant_n': cr_dict_n.get('TB', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('TB', {}).get('montant_n1', 0)
            },
            {
                'ref': 'TC',
                'libelle': 'Travaux, services vendus',
                'montant_n': cr_dict_n.get('TC', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('TC', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 22 - ACHATS CONSOMMÉS ==========
    annexes['note_22'] = {
        'titre': 'NOTE 22 - Achats consommés',
        'postes': [
            {
                'ref': 'RA',
                'libelle': 'Achats de marchandises',
                'montant_n': cr_dict_n.get('RA', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('RA', {}).get('montant_n1', 0)
            },
            {
                'ref': 'RB',
                'libelle': 'Variation de stocks de marchandises',
                'montant_n': cr_dict_n.get('RB', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('RB', {}).get('montant_n1', 0)
            },
            {
                'ref': 'RC',
                'libelle': 'Achats de matières premières',
                'montant_n': cr_dict_n.get('RC', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('RC', {}).get('montant_n1', 0)
            },
            {
                'ref': 'RD',
                'libelle': 'Variation de stocks de matières',
                'montant_n': cr_dict_n.get('RD', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('RD', {}).get('montant_n1', 0)
            }
        ]
    }
    
    # ========== NOTE 24 - CHARGES DE PERSONNEL ==========
    annexes['note_24'] = {
        'titre': 'NOTE 24 - Charges de personnel',
        'postes': [
            {
                'ref': 'RK',
                'libelle': 'Salaires et traitements',
                'montant_n': cr_dict_n.get('RK', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('RK', {}).get('montant_n1', 0)
            },
            {
                'ref': 'RL',
                'libelle': 'Charges sociales',
                'montant_n': cr_dict_n.get('RL', {}).get('montant_n', 0),
                'montant_n1': cr_dict_n1.get('RL', {}).get('montant_n1', 0)
            }
        ]
    }
    
    logger.info(f"✅ {len(annexes)} notes annexes calculées")
    
    return annexes
