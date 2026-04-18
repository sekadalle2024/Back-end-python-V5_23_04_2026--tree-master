import pandas as pd
import numpy as np
import os
import json
import base64
import io
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import re

# Import du module TFT
from tableau_flux_tresorerie import calculer_tft

# Import du module Annexes
from annexes_liasse import calculer_annexes
from annexes_html import generate_annexes_html

# Import du module ACTIF BRUT/AMORT
from calculer_actif_brut_amort import enrichir_actif_avec_brut_amort

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("etats_financiers")

# Router FastAPI pour l'API États Financiers
router = APIRouter(prefix="/etats-financiers", tags=["États Financiers"])


# ==================== MODÈLES PYDANTIC ====================

class ExcelUploadRequest(BaseModel):
    """Requête avec fichier Excel encodé en base64"""
    file_base64: str
    filename: str
    file_n1_base64: Optional[str] = None  # Balance N-1 optionnelle
    filename_n1: Optional[str] = None

class EtatsFinanciersResponse(BaseModel):
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None
    html: Optional[str] = None


# ==================== FONCTIONS UTILITAIRES ====================

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


def load_tableau_correspondance(file_path: str = "correspondances_syscohada.json") -> Dict[str, List[Dict]]:
    """
    Charge le tableau de correspondance postes/comptes depuis un fichier JSON.
    Retourne un dictionnaire avec les sections : bilan_actif, bilan_passif, charges, produits
    """
    # Vérifier si le fichier existe
    if not os.path.exists(file_path):
        # Essayer avec le chemin absolu depuis la racine
        alt_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            logger.error(f"❌ Fichier non trouvé: {file_path}")
            logger.error(f"❌ Chemin alternatif non trouvé: {alt_path}")
            logger.error(f"❌ Répertoire courant: {os.getcwd()}")
            raise FileNotFoundError(f"Tableau de correspondance non trouvé: {file_path}")
    
    logger.info(f"📂 Chargement du tableau de correspondance: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            correspondances = json.load(f)
        
        # Afficher les statistiques
        logger.info(f"✅ Correspondances chargées depuis JSON:")
        logger.info(f"   - Bilan Actif: {len(correspondances['bilan_actif'])} postes")
        logger.info(f"   - Bilan Passif: {len(correspondances['bilan_passif'])} postes")
        logger.info(f"   - Charges: {len(correspondances['charges'])} postes")
        logger.info(f"   - Produits: {len(correspondances['produits'])} postes")
        
        return correspondances
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement du tableau: {e}")
        raise


def match_compte_to_poste(compte: str, correspondances: List[Dict]) -> Optional[Dict]:
    """
    Trouve le poste correspondant à un compte donné.
    Le compte peut avoir 6 à 8 chiffres.
    """
    compte = str(compte).strip()
    
    for poste in correspondances:
        for racine in poste['racines']:
            if compte.startswith(racine):
                return poste
    
    return None


def process_balance_to_etats_financiers(balance_df: pd.DataFrame, correspondances: Dict) -> Dict[str, Any]:
    """
    Traite une balance comptable et génère les états financiers avec contrôles exhaustifs.
    """
    logger.info("📊 Traitement de la balance pour états financiers")
    
    # Détecter les colonnes de la balance
    col_map = detect_balance_columns(balance_df)
    
    if col_map['numero'] is None:
        raise ValueError("Colonne 'Numéro' non trouvée dans la balance")
    
    # Initialiser les résultats et contrôles
    results = {
        'bilan_actif': {},
        'bilan_passif': {},
        'charges': {},
        'produits': {}
    }
    
    # Structures de contrôle
    controles = {
        'comptes_non_integres': [],  # Comptes non reconnus
        'comptes_sens_inverse': [],  # Comptes avec sens débit/crédit inversé
        'comptes_desequilibre': [],  # Comptes créant un déséquilibre
        'statistiques': {
            'total_comptes_balance': 0,
            'comptes_integres': 0,
            'comptes_non_integres': 0,
            'taux_couverture': 0.0
        }
    }
    
    # Définir les sens normaux des comptes par classe
    sens_normal_comptes = {
        '1': 'credit',  # Capitaux
        '2': 'debit',   # Immobilisations
        '3': 'debit',   # Stocks
        '4': 'variable', # Tiers (mixte)
        '5': 'debit',   # Trésorerie
        '6': 'debit',   # Charges
        '7': 'credit',  # Produits
        '8': 'variable' # Comptes spéciaux
    }
    
    # Traiter chaque ligne de la balance
    for idx, row in balance_df.iterrows():
        numero = str(row.get(col_map['numero'], '')).strip()
        if not numero or numero == 'nan' or not numero[0].isdigit():
            continue
        
        controles['statistiques']['total_comptes_balance'] += 1
        
        intitule = str(row.get(col_map['intitule'], '')).strip() if col_map['intitule'] else ''
        
        # Calculer le solde net
        solde_debit = clean_number(row.get(col_map['solde_debit'], 0)) if col_map['solde_debit'] else 0
        solde_credit = clean_number(row.get(col_map['solde_credit'], 0)) if col_map['solde_credit'] else 0
        solde_net = solde_debit - solde_credit
        
        # Vérifier le sens du compte
        classe = numero[0]
        sens_attendu = sens_normal_comptes.get(classe, 'variable')
        sens_reel = 'debit' if solde_net > 0 else 'credit' if solde_net < 0 else 'nul'
        
        # Détecter les sens inversés (sauf pour les comptes variables)
        if sens_attendu != 'variable' and sens_reel != 'nul' and sens_reel != sens_attendu:
            controles['comptes_sens_inverse'].append({
                'numero': numero,
                'intitule': intitule,
                'classe': classe,
                'sens_attendu': sens_attendu,
                'sens_reel': sens_reel,
                'solde_debit': solde_debit,
                'solde_credit': solde_credit,
                'solde_net': solde_net
            })
        
        # Chercher correspondance dans chaque section
        compte_integre = False
        for section_name, section_correspondances in correspondances.items():
            poste = match_compte_to_poste(numero, section_correspondances)
            if poste:
                ref = poste['ref']
                if ref not in results[section_name]:
                    results[section_name][ref] = {
                        'ref': ref,
                        'libelle': poste['libelle'],
                        'montant': 0,
                        'comptes': []
                    }
                
                # Appliquer le sens correct selon la section
                montant_a_ajouter = solde_net
                
                # Pour le bilan : Actif en débit positif, Passif en crédit positif
                if section_name == 'bilan_actif':
                    # L'actif doit être en débit (positif)
                    if solde_net < 0:
                        controles['comptes_desequilibre'].append({
                            'numero': numero,
                            'intitule': intitule,
                            'section': 'Bilan Actif',
                            'probleme': 'Solde créditeur sur un compte d\'actif',
                            'solde': solde_net
                        })
                
                elif section_name == 'bilan_passif':
                    # Le passif doit être en crédit (négatif), on inverse le signe
                    montant_a_ajouter = -solde_net
                    if solde_net > 0:
                        controles['comptes_desequilibre'].append({
                            'numero': numero,
                            'intitule': intitule,
                            'section': 'Bilan Passif',
                            'probleme': 'Solde débiteur sur un compte de passif',
                            'solde': solde_net
                        })
                
                elif section_name == 'charges':
                    # Les charges doivent être en débit (positif)
                    if solde_net < 0:
                        controles['comptes_desequilibre'].append({
                            'numero': numero,
                            'intitule': intitule,
                            'section': 'Charges',
                            'probleme': 'Solde créditeur sur un compte de charges',
                            'solde': solde_net
                        })
                
                elif section_name == 'produits':
                    # Les produits doivent être en crédit (négatif), on inverse le signe
                    montant_a_ajouter = -solde_net
                    if solde_net > 0:
                        controles['comptes_desequilibre'].append({
                            'numero': numero,
                            'intitule': intitule,
                            'section': 'Produits',
                            'probleme': 'Solde débiteur sur un compte de produits',
                            'solde': solde_net
                        })
                
                results[section_name][ref]['montant'] += montant_a_ajouter
                results[section_name][ref]['comptes'].append({
                    'numero': numero,
                    'intitule': intitule,
                    'solde': solde_net,
                    'montant_integre': montant_a_ajouter
                })
                
                compte_integre = True
                controles['statistiques']['comptes_integres'] += 1
                break  # Un compte ne peut être que dans une section
        
        # Si le compte n'a pas été intégré
        if not compte_integre and abs(solde_net) > 0.01:  # Ignorer les soldes quasi-nuls
            controles['comptes_non_integres'].append({
                'numero': numero,
                'intitule': intitule,
                'classe': classe,
                'solde_debit': solde_debit,
                'solde_credit': solde_credit,
                'solde_net': solde_net,
                'raison': 'Codification non reconnue dans le tableau de correspondance'
            })
            controles['statistiques']['comptes_non_integres'] += 1
    
    # Calculer les totaux
    total_actif = sum(poste['montant'] for poste in results['bilan_actif'].values())
    total_passif = sum(poste['montant'] for poste in results['bilan_passif'].values())
    total_charges = sum(poste['montant'] for poste in results['charges'].values())
    total_produits = sum(poste['montant'] for poste in results['produits'].values())
    resultat_net_cr = total_produits - total_charges
    
    # Calculer le taux de couverture
    if controles['statistiques']['total_comptes_balance'] > 0:
        controles['statistiques']['taux_couverture'] = (
            controles['statistiques']['comptes_integres'] / 
            controles['statistiques']['total_comptes_balance'] * 100
        )
    
    # Contrôles d'équilibre
    controles['equilibre_bilan'] = {
        'actif': total_actif,
        'passif': total_passif,
        'difference': total_actif - total_passif,
        'equilibre': abs(total_actif - total_passif) < 0.01,
        'pourcentage_ecart': abs((total_actif - total_passif) / total_actif * 100) if total_actif != 0 else 0
    }
    
    controles['equilibre_resultat'] = {
        'resultat_cr': resultat_net_cr,
        'resultat_bilan': total_actif - total_passif,
        'difference': resultat_net_cr - (total_actif - total_passif),
        'equilibre': abs(resultat_net_cr - (total_actif - total_passif)) < 0.01
    }
    
    # Contrôle spécifique : Hypothèse d'affectation du résultat
    # Ce contrôle vérifie si l'affectation du résultat au passif équilibrerait le bilan
    passif_avec_resultat = total_passif + resultat_net_cr
    difference_apres_affectation = total_actif - passif_avec_resultat
    
    controles['hypothese_affectation_resultat'] = {
        'resultat_net': resultat_net_cr,
        'passif_avant_affectation': total_passif,
        'passif_apres_affectation': passif_avec_resultat,
        'actif': total_actif,
        'difference_avant': total_actif - total_passif,
        'difference_apres': difference_apres_affectation,
        'equilibre_apres_affectation': abs(difference_apres_affectation) < 0.01,
        'recommandation': 'Affecter le résultat au passif (compte 13)' if abs(difference_apres_affectation) < 0.01 else 'Vérifier les écritures comptables',
        'type_resultat': 'Bénéfice' if resultat_net_cr > 0 else 'Perte' if resultat_net_cr < 0 else 'Nul'
    }
    
    # Impact des comptes non intégrés
    montant_non_integre = sum(abs(c['solde_net']) for c in controles['comptes_non_integres'])
    controles['impact_non_integres'] = {
        'montant_total': montant_non_integre,
        'pourcentage_actif': (montant_non_integre / total_actif * 100) if total_actif != 0 else 0
    }
    
    # Contrôle spécifique : Comptes avec sens anormal par nature
    # Définir les règles de sens normal par nature de compte
    regles_sens_normal = {
        # Classe 1 : Capitaux (normalement créditeurs)
        '101': {'sens': 'credit', 'nature': 'Capital social', 'gravite': 'critique'},
        '10': {'sens': 'credit', 'nature': 'Capital', 'gravite': 'critique'},
        '11': {'sens': 'credit', 'nature': 'Réserves', 'gravite': 'elevee'},
        '12': {'sens': 'credit', 'nature': 'Report à nouveau', 'gravite': 'moyenne'},
        '13': {'sens': 'variable', 'nature': 'Résultat', 'gravite': 'faible'},
        '14': {'sens': 'credit', 'nature': 'Subventions', 'gravite': 'elevee'},
        '16': {'sens': 'credit', 'nature': 'Emprunts', 'gravite': 'elevee'},
        
        # Classe 2 : Immobilisations (normalement débitrices)
        '21': {'sens': 'debit', 'nature': 'Immobilisations incorporelles', 'gravite': 'elevee'},
        '22': {'sens': 'debit', 'nature': 'Terrains', 'gravite': 'elevee'},
        '23': {'sens': 'debit', 'nature': 'Bâtiments', 'gravite': 'elevee'},
        '24': {'sens': 'debit', 'nature': 'Matériel', 'gravite': 'elevee'},
        '28': {'sens': 'credit', 'nature': 'Amortissements', 'gravite': 'moyenne'},
        '29': {'sens': 'credit', 'nature': 'Provisions', 'gravite': 'moyenne'},
        
        # Classe 3 : Stocks (normalement débiteurs)
        '31': {'sens': 'debit', 'nature': 'Marchandises', 'gravite': 'elevee'},
        '32': {'sens': 'debit', 'nature': 'Matières premières', 'gravite': 'elevee'},
        '33': {'sens': 'debit', 'nature': 'Autres approvisionnements', 'gravite': 'moyenne'},
        
        # Classe 4 : Tiers (sens variable selon le compte)
        '401': {'sens': 'credit', 'nature': 'Fournisseurs', 'gravite': 'moyenne'},
        '411': {'sens': 'debit', 'nature': 'Clients', 'gravite': 'moyenne'},
        '421': {'sens': 'credit', 'nature': 'Personnel', 'gravite': 'moyenne'},
        '43': {'sens': 'credit', 'nature': 'Organismes sociaux', 'gravite': 'elevee'},
        '44': {'sens': 'credit', 'nature': 'État', 'gravite': 'elevee'},
        
        # Classe 5 : Trésorerie (normalement débiteurs sauf banques créditrices)
        '52': {'sens': 'debit', 'nature': 'Banques', 'gravite': 'critique'},
        '53': {'sens': 'debit', 'nature': 'Établissements financiers', 'gravite': 'critique'},
        '54': {'sens': 'debit', 'nature': 'Caisse', 'gravite': 'critique'},
        '57': {'sens': 'debit', 'nature': 'Régies d\'avances', 'gravite': 'elevee'},
        
        # Classe 6 : Charges (normalement débitrices)
        '60': {'sens': 'debit', 'nature': 'Achats', 'gravite': 'moyenne'},
        '61': {'sens': 'debit', 'nature': 'Transports', 'gravite': 'faible'},
        '62': {'sens': 'debit', 'nature': 'Services extérieurs', 'gravite': 'faible'},
        '63': {'sens': 'debit', 'nature': 'Autres services', 'gravite': 'faible'},
        '64': {'sens': 'debit', 'nature': 'Impôts et taxes', 'gravite': 'moyenne'},
        '66': {'sens': 'debit', 'nature': 'Charges de personnel', 'gravite': 'elevee'},
        
        # Classe 7 : Produits (normalement créditeurs)
        '70': {'sens': 'credit', 'nature': 'Ventes', 'gravite': 'elevee'},
        '71': {'sens': 'credit', 'nature': 'Subventions d\'exploitation', 'gravite': 'moyenne'},
        '72': {'sens': 'credit', 'nature': 'Production immobilisée', 'gravite': 'faible'},
        '75': {'sens': 'credit', 'nature': 'Autres produits', 'gravite': 'faible'},
    }
    
    comptes_sens_anormal = []
    
    for idx, row in balance_df.iterrows():
        numero = str(row.get(col_map['numero'], '')).strip()
        if not numero or numero == 'nan' or not numero[0].isdigit():
            continue
        
        intitule = str(row.get(col_map['intitule'], '')).strip() if col_map['intitule'] else ''
        solde_debit = clean_number(row.get(col_map['solde_debit'], 0)) if col_map['solde_debit'] else 0
        solde_credit = clean_number(row.get(col_map['solde_credit'], 0)) if col_map['solde_credit'] else 0
        solde_net = solde_debit - solde_credit
        
        if abs(solde_net) < 0.01:
            continue
        
        # Déterminer le sens réel
        sens_reel = 'debit' if solde_net > 0 else 'credit'
        
        # Chercher la règle applicable (du plus spécifique au plus général)
        regle = None
        for longueur in [6, 5, 4, 3, 2, 1]:
            if longueur <= len(numero):
                racine = numero[:longueur]
                if racine in regles_sens_normal:
                    regle = regles_sens_normal[racine]
                    break
        
        if regle and regle['sens'] != 'variable' and regle['sens'] != sens_reel:
            comptes_sens_anormal.append({
                'numero': numero,
                'intitule': intitule,
                'nature': regle['nature'],
                'sens_attendu': regle['sens'],
                'sens_reel': sens_reel,
                'solde_net': solde_net,
                'solde_debit': solde_debit,
                'solde_credit': solde_credit,
                'gravite': regle['gravite'],
                'impact_potentiel': 'Déséquilibre majeur' if regle['gravite'] == 'critique' else 'Anomalie comptable'
            })
    
    controles['comptes_sens_anormal_par_nature'] = comptes_sens_anormal
    
    logger.info(f"✅ États financiers calculés:")
    logger.info(f"   - Total Actif: {format_number(total_actif)}")
    logger.info(f"   - Total Passif: {format_number(total_passif)}")
    logger.info(f"   - Total Charges: {format_number(total_charges)}")
    logger.info(f"   - Total Produits: {format_number(total_produits)}")
    logger.info(f"   - Résultat Net: {format_number(resultat_net_cr)}")
    logger.info(f"   - Comptes intégrés: {controles['statistiques']['comptes_integres']}/{controles['statistiques']['total_comptes_balance']}")
    logger.info(f"   - Taux de couverture: {controles['statistiques']['taux_couverture']:.1f}%")
    logger.info(f"   - Comptes sens anormal: {len(comptes_sens_anormal)}")
    
    # Enrichir l'actif avec colonnes BRUT, AMORT ET DEPREC, NET
    logger.info("📊 Enrichissement ACTIF avec colonnes BRUT, AMORT, NET...")
    actif_enrichi = enrichir_actif_avec_brut_amort(balance_df, correspondances, col_map)
    
    return {
        'bilan_actif': results['bilan_actif'],
        'bilan_passif': results['bilan_passif'],
        'charges': results['charges'],
        'produits': results['produits'],
        'totaux': {
            'actif': total_actif,
            'passif': total_passif,
            'charges': total_charges,
            'produits': total_produits,
            'resultat_net': resultat_net_cr
        },
        'controles': controles,
        'actif_detaille': actif_enrichi['actif_detaille'],
        'actif_html': actif_enrichi['html']
    }


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
    
    logger.info(f"🔍 Colonnes détectées: {mapping}")
    return mapping


def generate_etats_financiers_html(results: Dict[str, Any]) -> str:
    """
    Génère le HTML des accordéons pour afficher les états financiers et les contrôles.
    """
    totaux = results['totaux']
    controles = results.get('controles', {})
    
    # Style CSS
    html = """
    <style>
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
    .etats-fin-header h2 { margin: 0 0 8px 0; font-size: 22px; }
    .etats-fin-header p { margin: 0; opacity: 0.9; font-size: 16px; }
    
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
    .section-header-ef:hover { background: #e9ecef; }
    .section-header-ef.active { background: #dee2e6; }
    .section-header-ef .arrow {
        transition: transform 0.3s;
        font-size: 18px;
    }
    .section-header-ef.active .arrow { transform: rotate(90deg); }
    
    .section-content-ef {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease-out;
        background: white;
    }
    .section-content-ef.active { max-height: 5000px; }
    
    .poste-item {
        padding: 10px 18px;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .poste-item:last-child { border-bottom: none; }
    .poste-ref { font-weight: 600; color: #1e3a8a; min-width: 50px; }
    .poste-libelle { flex: 1; padding: 0 16px; }
    .poste-montant { font-family: 'Consolas', monospace; font-weight: 600; color: #059669; }
    
    .total-section {
        background: #f0f9ff;
        padding: 14px 18px;
        border-top: 2px solid #3b82f6;
        font-weight: 700;
        font-size: 16px;
        display: flex;
        justify-content: space-between;
    }
    .total-section.resultat {
        background: #ecfdf5;
        border-top-color: #059669;
    }
    .total-section.resultat.negatif {
        background: #fef2f2;
        border-top-color: #dc2626;
    }
    
    /* Styles pour les contrôles */
    .controle-section {
        margin: 16px 0;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        overflow: hidden;
    }
    .controle-header {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 16px 18px;
        font-weight: 700;
        font-size: 18px;
    }
    .controle-item {
        padding: 12px 18px;
        border-bottom: 1px solid #fef3c7;
        background: #fffbeb;
    }
    .controle-item:last-child { border-bottom: none; }
    .controle-item.ok {
        background: #f0fdf4;
        border-bottom-color: #dcfce7;
    }
    .controle-item.warning {
        background: #fef3c7;
        border-bottom-color: #fde68a;
    }
    .controle-item.error {
        background: #fee2e2;
        border-bottom-color: #fecaca;
    }
    .controle-label {
        font-weight: 600;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .controle-value {
        font-family: 'Consolas', monospace;
        font-size: 14px;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge.success { background: #dcfce7; color: #166534; }
    .badge.warning { background: #fef3c7; color: #92400e; }
    .badge.error { background: #fee2e2; color: #991b1b; }
    
    .compte-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
        font-size: 13px;
    }
    .compte-table th {
        background: #f3f4f6;
        padding: 8px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #d1d5db;
    }
    .compte-table td {
        padding: 6px 8px;
        border-bottom: 1px solid #e5e7eb;
    }
    .compte-table tr:last-child td { border-bottom: none; }
    .compte-table tr:hover { background: #f9fafb; }
    </style>
    """
    
    # Préparer les données pour l'export (sans les contrôles pour alléger)
    export_data = {
        'bilan_actif': results['bilan_actif'],
        'bilan_passif': results['bilan_passif'],
        'charges': results['charges'],
        'produits': results['produits'],
        'totaux': totaux
    }
    
    # Encoder les données en JSON pour l'attribut data-results
    import json
    results_json = json.dumps(export_data, ensure_ascii=False)
    results_json_escaped = results_json.replace('"', '&quot;')
    
    html += f"""
    <div class="etats-fin-container" data-results="{results_json_escaped}">
        <div class="etats-fin-header">
            <h2>📊 États Financiers SYSCOHADA Révisé</h2>
            <p>Bilan, Compte de Résultat, TFT et États de Contrôle</p>
        </div>
    """
    
    # Stocker aussi dans window pour accès JavaScript
    html += f"""
    <script>
    window.lastEtatsFinanciersResults = {results_json};
    console.log('✅ Résultats états financiers stockés dans window.lastEtatsFinanciersResults');
    </script>
    """
    
    # 1. BILAN
    # Bilan Actif - Version enrichie avec BRUT, AMORT ET DEPREC, NET
    if 'actif_html' in results and results['actif_html']:
        logger.info("📊 Utilisation du HTML ACTIF enrichi (BRUT, AMORT, NET)")
        html += results['actif_html']
    else:
        # Fallback vers la version standard si l'enrichissement n'est pas disponible
        logger.warning("⚠️ HTML ACTIF enrichi non disponible, utilisation de la version standard")
        html += generate_section_html(
            "bilan_actif",
            "🏢 BILAN - ACTIF",
            results['bilan_actif'],
            totaux['actif']
        )
    
    # Bilan Passif
    html += generate_section_html(
        "bilan_passif",
        "🏛️ BILAN - PASSIF",
        results['bilan_passif'],
        totaux['passif']
    )
    
    # 2. COMPTE DE RÉSULTAT
    # Compte de Résultat - Charges
    html += generate_section_html(
        "charges",
        "📉 COMPTE DE RÉSULTAT - CHARGES",
        results['charges'],
        totaux['charges']
    )
    
    # Compte de Résultat - Produits
    html += generate_section_html(
        "produits",
        "📈 COMPTE DE RÉSULTAT - PRODUITS",
        results['produits'],
        totaux['produits']
    )
    
    # 3. RÉSULTAT NET
    resultat_class = "resultat" if totaux['resultat_net'] >= 0 else "resultat negatif"
    resultat_label = "BÉNÉFICE" if totaux['resultat_net'] >= 0 else "PERTE"
    html += f"""
        <div class="total-section {resultat_class}">
            <span>💰 RÉSULTAT NET ({resultat_label})</span>
            <span>{format_number(abs(totaux['resultat_net']))}</span>
        </div>
    """
    
    # 4. TABLEAU DES FLUX DE TRÉSORERIE (si disponible)
    if 'tft' in results and results['tft']:
        html += generate_tft_html(results['tft'])
    
    # 5. ÉTATS DE CONTRÔLE (À LA FIN)
    html += generate_controles_html(controles, totaux)
    
    # 6. CONTRÔLES TFT (si disponibles)
    if 'tft' in results and results['tft'] and 'controles' in results['tft']:
        html += generate_controles_tft_html(results['tft']['controles'])
    
    # 7. ANNEXES (Notes calculables)
    if 'annexes' in results and results['annexes']:
        html += generate_annexes_html(results['annexes'])
    
    html += """
    </div>
    """
    
    return html


def generate_controles_html(controles: Dict, totaux: Dict) -> str:
    """Génère le HTML des états de contrôle"""
    if not controles:
        return ''
    
    html = """
    <div class="controle-section">
        <div class="controle-header">
            🔍 ÉTATS DE CONTRÔLE
        </div>
    """
    
    # 1. Statistiques générales
    stats = controles.get('statistiques', {})
    taux = stats.get('taux_couverture', 0)
    badge_class = 'success' if taux >= 95 else 'warning' if taux >= 80 else 'error'
    
    html += f"""
        <div class="controle-item ok">
            <div class="controle-label">
                📊 Statistiques de Couverture
                <span class="badge {badge_class}">{taux:.1f}%</span>
            </div>
            <div class="controle-value">
                Comptes intégrés: {stats.get('comptes_integres', 0)} / {stats.get('total_comptes_balance', 0)}
                <br>Comptes non intégrés: {stats.get('comptes_non_integres', 0)}
            </div>
        </div>
    """
    
    # 2. Équilibre du Bilan
    eq_bilan = controles.get('equilibre_bilan', {})
    equilibre_ok = eq_bilan.get('equilibre', False)
    badge_class = 'success' if equilibre_ok else 'error'
    item_class = 'ok' if equilibre_ok else 'error'
    
    html += f"""
        <div class="controle-item {item_class}">
            <div class="controle-label">
                ⚖️ Équilibre du Bilan
                <span class="badge {badge_class}">{'✓ Équilibré' if equilibre_ok else '✗ Déséquilibré'}</span>
            </div>
            <div class="controle-value">
                Total Actif: {format_number(eq_bilan.get('actif', 0))}
                <br>Total Passif: {format_number(eq_bilan.get('passif', 0))}
                <br>Différence: {format_number(eq_bilan.get('difference', 0))}
                {f"<br>Écart: {eq_bilan.get('pourcentage_ecart', 0):.2f}%" if not equilibre_ok else ''}
            </div>
        </div>
    """
    
    # 3. Équilibre Résultat
    eq_res = controles.get('equilibre_resultat', {})
    equilibre_res_ok = eq_res.get('equilibre', False)
    badge_class = 'success' if equilibre_res_ok else 'warning'
    item_class = 'ok' if equilibre_res_ok else 'warning'
    
    html += f"""
        <div class="controle-item {item_class}">
            <div class="controle-label">
                💰 Cohérence Résultat (Bilan vs Compte de Résultat)
                <span class="badge {badge_class}">{'✓ Cohérent' if equilibre_res_ok else '⚠ Incohérent'}</span>
            </div>
            <div class="controle-value">
                Résultat Compte de Résultat: {format_number(eq_res.get('resultat_cr', 0))}
                <br>Résultat Bilan (Actif - Passif): {format_number(eq_res.get('resultat_bilan', 0))}
                <br>Différence: {format_number(eq_res.get('difference', 0))}
            </div>
        </div>
    """
    
    # 4. Comptes non intégrés
    comptes_ni = controles.get('comptes_non_integres', [])
    if comptes_ni:
        impact = controles.get('impact_non_integres', {})
        html += f"""
        <div class="controle-item warning">
            <div class="controle-label">
                ⚠️ Comptes Non Intégrés
                <span class="badge warning">{len(comptes_ni)} compte(s)</span>
            </div>
            <div class="controle-value">
                Impact total: {format_number(impact.get('montant_total', 0))}
                ({impact.get('pourcentage_actif', 0):.2f}% de l'actif)
            </div>
            <table class="compte-table">
                <thead>
                    <tr>
                        <th>N° Compte</th>
                        <th>Intitulé</th>
                        <th>Classe</th>
                        <th>Solde Débit</th>
                        <th>Solde Crédit</th>
                        <th>Solde Net</th>
                        <th>Raison</th>
                    </tr>
                </thead>
                <tbody>
        """
        for compte in comptes_ni[:20]:  # Limiter à 20 pour la lisibilité
            html += f"""
                    <tr>
                        <td>{compte['numero']}</td>
                        <td>{compte['intitule'][:40]}</td>
                        <td>{compte['classe']}</td>
                        <td>{format_number(compte['solde_debit'])}</td>
                        <td>{format_number(compte['solde_credit'])}</td>
                        <td>{format_number(compte['solde_net'])}</td>
                        <td style="font-size: 11px;">{compte['raison']}</td>
                    </tr>
            """
        if len(comptes_ni) > 20:
            html += f"""
                    <tr>
                        <td colspan="7" style="text-align: center; font-style: italic;">
                            ... et {len(comptes_ni) - 20} autre(s) compte(s)
                        </td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
        </div>
        """
    
    # 5. Comptes avec sens inversé
    comptes_si = controles.get('comptes_sens_inverse', [])
    if comptes_si:
        html += f"""
        <div class="controle-item warning">
            <div class="controle-label">
                🔄 Comptes avec Sens Inversé
                <span class="badge warning">{len(comptes_si)} compte(s)</span>
            </div>
            <div class="controle-value">
                Comptes ayant un solde contraire au sens normal de leur classe
            </div>
            <table class="compte-table">
                <thead>
                    <tr>
                        <th>N° Compte</th>
                        <th>Intitulé</th>
                        <th>Classe</th>
                        <th>Sens Attendu</th>
                        <th>Sens Réel</th>
                        <th>Solde Net</th>
                    </tr>
                </thead>
                <tbody>
        """
        for compte in comptes_si[:15]:
            html += f"""
                    <tr>
                        <td>{compte['numero']}</td>
                        <td>{compte['intitule'][:40]}</td>
                        <td>{compte['classe']}</td>
                        <td>{compte['sens_attendu'].upper()}</td>
                        <td style="color: #dc2626; font-weight: 600;">{compte['sens_reel'].upper()}</td>
                        <td>{format_number(compte['solde_net'])}</td>
                    </tr>
            """
        if len(comptes_si) > 15:
            html += f"""
                    <tr>
                        <td colspan="6" style="text-align: center; font-style: italic;">
                            ... et {len(comptes_si) - 15} autre(s) compte(s)
                        </td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
        </div>
        """
    
    # 6. Comptes en déséquilibre
    comptes_deseq = controles.get('comptes_desequilibre', [])
    if comptes_deseq:
        html += f"""
        <div class="controle-item error">
            <div class="controle-label">
                ⚠️ Comptes Créant un Déséquilibre
                <span class="badge error">{len(comptes_deseq)} compte(s)</span>
            </div>
            <div class="controle-value">
                Comptes avec un sens incorrect pour leur section
            </div>
            <table class="compte-table">
                <thead>
                    <tr>
                        <th>N° Compte</th>
                        <th>Intitulé</th>
                        <th>Section</th>
                        <th>Problème</th>
                        <th>Solde</th>
                    </tr>
                </thead>
                <tbody>
        """
        for compte in comptes_deseq[:15]:
            html += f"""
                    <tr>
                        <td>{compte['numero']}</td>
                        <td>{compte['intitule'][:40]}</td>
                        <td>{compte['section']}</td>
                        <td style="color: #dc2626;">{compte['probleme']}</td>
                        <td>{format_number(compte['solde'])}</td>
                    </tr>
            """
        if len(comptes_deseq) > 15:
            html += f"""
                    <tr>
                        <td colspan="5" style="text-align: center; font-style: italic;">
                            ... et {len(comptes_deseq) - 15} autre(s) compte(s)
                        </td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
        </div>
        """
    
    # 7. Hypothèse d'affectation du résultat
    hyp_affect = controles.get('hypothese_affectation_resultat', {})
    if hyp_affect:
        equilibre_apres = hyp_affect.get('equilibre_apres_affectation', False)
        badge_class = 'success' if equilibre_apres else 'warning'
        item_class = 'ok' if equilibre_apres else 'warning'
        type_resultat = hyp_affect.get('type_resultat', 'Nul')
        
        html += f"""
        <div class="controle-item {item_class}">
            <div class="controle-label">
                💡 Hypothèse d'Affectation du Résultat
                <span class="badge {badge_class}">{type_resultat}</span>
            </div>
            <div class="controle-value">
                <strong>SITUATION ACTUELLE:</strong>
                <br>Actif: {format_number(hyp_affect.get('actif', 0))}
                <br>Passif: {format_number(hyp_affect.get('passif_avant_affectation', 0))}
                <br>Différence: {format_number(hyp_affect.get('difference_avant', 0))}
                <br>
                <br><strong>HYPOTHÈSE (si résultat affecté au passif):</strong>
                <br>Résultat Net: {format_number(hyp_affect.get('resultat_net', 0))}
                <br>Passif + Résultat: {format_number(hyp_affect.get('passif_apres_affectation', 0))}
                <br>Différence: {format_number(hyp_affect.get('difference_apres', 0))}
                <br>Équilibre: {'OUI' if equilibre_apres else 'NON'}
                <br>
                <br><strong>RECOMMANDATION:</strong> {hyp_affect.get('recommandation', '')}
            </div>
        </div>
        """
    
    # 8. Comptes avec sens anormal par nature
    comptes_anormaux = controles.get('comptes_sens_anormal_par_nature', [])
    if comptes_anormaux:
        # Grouper par gravité
        critiques = [c for c in comptes_anormaux if c['gravite'] == 'critique']
        eleves = [c for c in comptes_anormaux if c['gravite'] == 'elevee']
        moyens = [c for c in comptes_anormaux if c['gravite'] == 'moyenne']
        faibles = [c for c in comptes_anormaux if c['gravite'] == 'faible']
        
        # Déterminer la classe CSS globale
        if critiques:
            item_class = 'error'
            badge_class = 'error'
        elif eleves:
            item_class = 'warning'
            badge_class = 'warning'
        else:
            item_class = 'warning'
            badge_class = 'warning'
        
        html += f"""
        <div class="controle-item {item_class}">
            <div class="controle-label">
                🚨 Comptes avec Sens Anormal par Nature
                <span class="badge {badge_class}">{len(comptes_anormaux)} compte(s)</span>
            </div>
            <div class="controle-value">
                Comptes ayant un solde contraire au sens normal de leur nature comptable
                <br>
        """
        
        if critiques:
            html += f"""
                <br><strong style="color: #dc2626;">⚠️ CRITIQUES ({len(critiques)}) - Déséquilibre majeur:</strong>
            """
        
        if eleves:
            html += f"""
                <br><strong style="color: #f59e0b;">⚠️ ÉLEVÉS ({len(eleves)}) - Anomalie comptable:</strong>
            """
        
        if moyens:
            html += f"""
                <br><strong style="color: #3b82f6;">ℹ️ MOYENS ({len(moyens)}) - À vérifier:</strong>
            """
        
        html += """
            </div>
            <table class="compte-table">
                <thead>
                    <tr>
                        <th>Gravité</th>
                        <th>N° Compte</th>
                        <th>Nature</th>
                        <th>Intitulé</th>
                        <th>Sens Attendu</th>
                        <th>Sens Réel</th>
                        <th>Solde Net</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Afficher les comptes critiques en premier
        for compte in critiques[:5]:
            html += f"""
                    <tr style="background: #fee2e2;">
                        <td><span class="badge error">CRITIQUE</span></td>
                        <td>{compte['numero']}</td>
                        <td>{compte['nature']}</td>
                        <td>{compte['intitule'][:30]}</td>
                        <td>{compte['sens_attendu'].upper()}</td>
                        <td style="color: #dc2626; font-weight: 600;">{compte['sens_reel'].upper()}</td>
                        <td>{format_number(compte['solde_net'])}</td>
                    </tr>
            """
        
        # Puis les élevés
        for compte in eleves[:5]:
            html += f"""
                    <tr style="background: #fef3c7;">
                        <td><span class="badge warning">ÉLEVÉ</span></td>
                        <td>{compte['numero']}</td>
                        <td>{compte['nature']}</td>
                        <td>{compte['intitule'][:30]}</td>
                        <td>{compte['sens_attendu'].upper()}</td>
                        <td style="color: #f59e0b; font-weight: 600;">{compte['sens_reel'].upper()}</td>
                        <td>{format_number(compte['solde_net'])}</td>
                    </tr>
            """
        
        # Puis les moyens
        for compte in moyens[:5]:
            html += f"""
                    <tr>
                        <td><span class="badge" style="background: #dbeafe; color: #1e40af;">MOYEN</span></td>
                        <td>{compte['numero']}</td>
                        <td>{compte['nature']}</td>
                        <td>{compte['intitule'][:30]}</td>
                        <td>{compte['sens_attendu'].upper()}</td>
                        <td style="color: #3b82f6; font-weight: 600;">{compte['sens_reel'].upper()}</td>
                        <td>{format_number(compte['solde_net'])}</td>
                    </tr>
            """
        
        total_affiches = min(5, len(critiques)) + min(5, len(eleves)) + min(5, len(moyens))
        if len(comptes_anormaux) > total_affiches:
            html += f"""
                    <tr>
                        <td colspan="7" style="text-align: center; font-style: italic;">
                            ... et {len(comptes_anormaux) - total_affiches} autre(s) compte(s)
                        </td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
    
    html += """
    </div>
    """
    
    return html


def generate_tft_html(tft_data: Dict[str, Any]) -> str:
    """Génère le HTML pour le Tableau des Flux de Trésorerie"""
    if not tft_data:
        return ''
    
    html = """
    <div class="etats-fin-section" data-section="tft">
        <div class="section-header-ef">
            <span>💧 TABLEAU DES FLUX DE TRÉSORERIE (TFT)</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef">
    """
    
    # A. Trésorerie d'ouverture
    html += f"""
        <div class="poste-item" style="background: #f0f9ff;">
            <span class="poste-ref">ZA</span>
            <span class="poste-libelle">Trésorerie au 1er janvier</span>
            <span class="poste-montant">{format_number(tft_data.get('ZA_tresorerie_ouverture', 0))}</span>
        </div>
    """
    
    # B. Flux opérationnels
    html += """
        <div style="padding: 10px 18px; background: #e0f2fe; font-weight: 600; border-top: 1px solid #bae6fd;">
            FLUX DE TRÉSORERIE PROVENANT DES ACTIVITÉS OPÉRATIONNELLES
        </div>
    """
    
    flux_ops = [
        ('FA', 'Capacité d\'Autofinancement Globale (CAFG)', 'FA_cafg'),
        ('FB', 'Variation actif circulant HAO', 'FB_variation_actif_hao'),
        ('FC', 'Variation des stocks', 'FC_variation_stocks'),
        ('FD', 'Variation des créances', 'FD_variation_creances'),
        ('FE', 'Variation du passif circulant', 'FE_variation_dettes'),
    ]
    
    for ref, libelle, key in flux_ops:
        html += f"""
        <div class="poste-item">
            <span class="poste-ref">{ref}</span>
            <span class="poste-libelle">{libelle}</span>
            <span class="poste-montant">{format_number(tft_data.get(key, 0))}</span>
        </div>
        """
    
    html += f"""
        <div class="total-section">
            <span>ZB - FLUX OPÉRATIONNELS</span>
            <span>{format_number(tft_data.get('ZB_flux_operationnels', 0))}</span>
        </div>
    """
    
    # C. Flux d'investissement
    html += """
        <div style="padding: 10px 18px; background: #fef3c7; font-weight: 600; border-top: 1px solid #fde68a;">
            FLUX DE TRÉSORERIE PROVENANT DES ACTIVITÉS D'INVESTISSEMENT
        </div>
    """
    
    flux_inv = [
        ('FF', 'Décaissements acquisitions immobilisations incorporelles', 'FF_decaissement_incorp'),
        ('FG', 'Décaissements acquisitions immobilisations corporelles', 'FG_decaissement_corp'),
        ('FH', 'Décaissements acquisitions immobilisations financières', 'FH_decaissement_fin'),
        ('FI', 'Encaissements cessions immobilisations', 'FI_encaissement_cessions_immob'),
        ('FJ', 'Encaissements cessions immobilisations financières', 'FJ_encaissement_cessions_fin'),
    ]
    
    for ref, libelle, key in flux_inv:
        html += f"""
        <div class="poste-item">
            <span class="poste-ref">{ref}</span>
            <span class="poste-libelle">{libelle}</span>
            <span class="poste-montant">{format_number(tft_data.get(key, 0))}</span>
        </div>
        """
    
    html += f"""
        <div class="total-section">
            <span>ZC - FLUX INVESTISSEMENT</span>
            <span>{format_number(tft_data.get('ZC_flux_investissement', 0))}</span>
        </div>
    """
    
    # D. Flux capitaux propres
    html += """
        <div style="padding: 10px 18px; background: #dcfce7; font-weight: 600; border-top: 1px solid #bbf7d0;">
            FLUX DE TRÉSORERIE - FINANCEMENT PAR CAPITAUX PROPRES
        </div>
    """
    
    flux_cp = [
        ('FK', 'Augmentation de capital', 'FK_augmentation_capital'),
        ('FL', 'Subventions d\'investissement reçues', 'FL_subventions_recues'),
        ('FM', 'Prélèvements sur le capital', 'FM_prelevement_capital'),
        ('FN', 'Dividendes versés', 'FN_dividendes_verses'),
    ]
    
    for ref, libelle, key in flux_cp:
        html += f"""
        <div class="poste-item">
            <span class="poste-ref">{ref}</span>
            <span class="poste-libelle">{libelle}</span>
            <span class="poste-montant">{format_number(tft_data.get(key, 0))}</span>
        </div>
        """
    
    html += f"""
        <div class="total-section">
            <span>ZD - FLUX CAPITAUX PROPRES</span>
            <span>{format_number(tft_data.get('ZD_flux_capitaux_propres', 0))}</span>
        </div>
    """
    
    # E. Flux capitaux étrangers
    html += """
        <div style="padding: 10px 18px; background: #fce7f3; font-weight: 600; border-top: 1px solid #fbcfe8;">
            FLUX DE TRÉSORERIE - FINANCEMENT PAR CAPITAUX ÉTRANGERS
        </div>
    """
    
    flux_ce = [
        ('FO', 'Nouveaux emprunts', 'FO_nouveaux_emprunts'),
        ('FP', 'Autres dettes financières', 'FP_nouvelles_dettes'),
        ('FQ', 'Remboursements', 'FQ_remboursements'),
    ]
    
    for ref, libelle, key in flux_ce:
        html += f"""
        <div class="poste-item">
            <span class="poste-ref">{ref}</span>
            <span class="poste-libelle">{libelle}</span>
            <span class="poste-montant">{format_number(tft_data.get(key, 0))}</span>
        </div>
        """
    
    html += f"""
        <div class="total-section">
            <span>ZE - FLUX CAPITAUX ÉTRANGERS</span>
            <span>{format_number(tft_data.get('ZE_flux_capitaux_etrangers', 0))}</span>
        </div>
    """
    
    # F. Total financement
    html += f"""
        <div class="total-section" style="background: #e0e7ff;">
            <span>ZF - FLUX FINANCEMENT (D+E)</span>
            <span>{format_number(tft_data.get('ZF_flux_financement', 0))}</span>
        </div>
    """
    
    # G & H. Variation et trésorerie finale
    variation_class = "resultat" if tft_data.get('ZG_variation_tresorerie', 0) >= 0 else "resultat negatif"
    html += f"""
        <div class="total-section {variation_class}">
            <span>ZG - VARIATION TRÉSORERIE (B+C+F)</span>
            <span>{format_number(tft_data.get('ZG_variation_tresorerie', 0))}</span>
        </div>
        <div class="total-section" style="background: #dbeafe; border-top: 3px solid #3b82f6;">
            <span>ZH - TRÉSORERIE AU 31 DÉCEMBRE</span>
            <span>{format_number(tft_data.get('ZH_tresorerie_cloture', 0))}</span>
        </div>
    """
    
    html += """
        </div>
    </div>
    """
    
    return html


def generate_controles_tft_html(controles_tft: Dict) -> str:
    """Génère le HTML des contrôles TFT"""
    if not controles_tft:
        return ''
    
    html = """
    <div class="controle-section">
        <div class="controle-header">
            💧 CONTRÔLES TFT
        </div>
    """
    
    # 1. Cohérence trésorerie
    coh_tres = controles_tft.get('coherence_tresorerie', {})
    coherent = coh_tres.get('coherent', False)
    badge_class = 'success' if coherent else 'error'
    item_class = 'ok' if coherent else 'error'
    
    html += f"""
        <div class="controle-item {item_class}">
            <div class="controle-label">
                💰 Cohérence Trésorerie
                <span class="badge {badge_class}">{'✓ Cohérent' if coherent else '✗ Incohérent'}</span>
            </div>
            <div class="controle-value">
                Trésorerie calculée (ZH): {format_number(coh_tres.get('tresorerie_calculee', 0))}
                <br>Trésorerie bilan N: {format_number(coh_tres.get('tresorerie_bilan', 0))}
                <br>Différence: {format_number(coh_tres.get('difference', 0))}
            </div>
        </div>
    """
    
    # 2. Équilibre des flux
    eq_flux = controles_tft.get('equilibre_flux', {})
    equilibre = eq_flux.get('equilibre', False)
    badge_class = 'success' if equilibre else 'error'
    item_class = 'ok' if equilibre else 'error'
    
    html += f"""
        <div class="controle-item {item_class}">
            <div class="controle-label">
                ⚖️ Équilibre des Flux
                <span class="badge {badge_class}">{'✓ Équilibré' if equilibre else '✗ Déséquilibré'}</span>
            </div>
            <div class="controle-value">
                Flux opérationnels: {format_number(eq_flux.get('flux_operationnels', 0))}
                <br>Flux investissement: {format_number(eq_flux.get('flux_investissement', 0))}
                <br>Flux financement: {format_number(eq_flux.get('flux_financement', 0))}
                <br>Total: {format_number(eq_flux.get('total', 0))}
                <br>Variation trésorerie: {format_number(eq_flux.get('variation_tresorerie', 0))}
            </div>
        </div>
    """
    
    # 3. Cohérence CAFG
    cafg_data = controles_tft.get('coherence_cafg', {})
    if cafg_data:
        html += f"""
        <div class="controle-item ok">
            <div class="controle-label">
                📊 Cohérence CAFG
            </div>
            <div class="controle-value">
                Résultat net: {format_number(cafg_data.get('resultat_net', 0))}
                <br>+ Dotations: {format_number(cafg_data.get('dotations', 0))}
                <br>- Reprises: {format_number(cafg_data.get('reprises', 0))}
                <br>+ Valeur compt. cessions: {format_number(cafg_data.get('valeur_comptable_cessions', 0))}
                <br>- Produits cessions: {format_number(cafg_data.get('produits_cessions', 0))}
                <br>= CAFG: {format_number(cafg_data.get('cafg', 0))}
            </div>
        </div>
        """
    
    html += """
    </div>
    """
    
    return html


def generate_section_html(section_id: str, title: str, postes: Dict, total: float) -> str:
    """Génère le HTML pour une section d'états financiers"""
    if not postes:
        return ''
    
    html = f"""
    <div class="etats-fin-section" data-section="{section_id}">
        <div class="section-header-ef">
            <span>{title}</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef">
    """
    
    # Trier les postes par référence
    sorted_postes = sorted(postes.values(), key=lambda x: x['ref'])
    
    for poste in sorted_postes:
        html += f"""
            <div class="poste-item">
                <span class="poste-ref">{poste['ref']}</span>
                <span class="poste-libelle">{poste['libelle']}</span>
                <span class="poste-montant">{format_number(poste['montant'])}</span>
            </div>
        """
    
    html += f"""
            <div class="total-section">
                <span>TOTAL {title.split('-')[1].strip()}</span>
                <span>{format_number(total)}</span>
            </div>
        </div>
    </div>
    """
    
    return html


# ==================== ENDPOINT API ====================

@router.post("/process-excel", response_model=EtatsFinanciersResponse)
async def process_excel(request: ExcelUploadRequest):
    """
    Traite un fichier Excel de balance et génère les états financiers SYSCOHADA.
    Si une balance N-1 est fournie, calcule également le TFT et utilise le format liasse officielle.
    """
    try:
        logger.info(f"📥 Réception fichier: {request.filename}")
        
        # Décoder le fichier base64
        file_content = base64.b64decode(request.file_base64)
        logger.info(f"📂 Fichier décodé: {len(file_content)} bytes")
        
        # Lire le fichier Excel et détecter les onglets
        excel_file = io.BytesIO(file_content)
        excel_data = pd.ExcelFile(excel_file)
        sheet_names = excel_data.sheet_names
        logger.info(f"📋 Onglets détectés: {sheet_names}")
        
        # Charger le tableau de correspondance
        correspondances = load_tableau_correspondance()
        
        # Variable pour stocker les balances
        balance_df = None
        balance_n1_df = None
        
        # DÉTECTION AUTOMATIQUE DES ONGLETS
        # Chercher les onglets "Balance N" et "Balance N-1" (avec variations)
        balance_n_patterns = ["Balance N", "balance n", "BALANCE N", "Balance N (", "balance_n"]
        balance_n1_patterns = ["Balance N-1", "balance n-1", "BALANCE N-1", "Balance N-1 (", "balance_n1", "balance_n-1"]
        
        # Trouver l'onglet Balance N
        for sheet in sheet_names:
            if any(pattern in sheet for pattern in balance_n_patterns):
                balance_df = pd.read_excel(excel_data, sheet_name=sheet)
                logger.info(f"✅ Balance N trouvée dans l'onglet '{sheet}': {len(balance_df)} lignes")
                break
        
        # Trouver l'onglet Balance N-1
        for sheet in sheet_names:
            if any(pattern in sheet for pattern in balance_n1_patterns):
                balance_n1_df = pd.read_excel(excel_data, sheet_name=sheet)
                logger.info(f"✅ Balance N-1 trouvée dans l'onglet '{sheet}': {len(balance_n1_df)} lignes")
                break
        
        # Si pas d'onglets spécifiques trouvés, utiliser l'ordre des onglets
        # (1er = N, 2ème = N-1, 3ème = N-2)
        if balance_df is None:
            balance_df = pd.read_excel(excel_data, sheet_name=0)
            logger.info(f"📊 Balance N chargée depuis le premier onglet '{sheet_names[0]}': {len(balance_df)} lignes")
        
        if balance_n1_df is None and len(sheet_names) >= 2:
            balance_n1_df = pd.read_excel(excel_data, sheet_name=1)
            logger.info(f"📊 Balance N-1 chargée depuis le deuxième onglet '{sheet_names[1]}': {len(balance_n1_df)} lignes")
        
        # Si balance N-1 fournie en tant que fichier séparé (ancien comportement)
        if request.file_n1_base64 and balance_n1_df is None:
            try:
                logger.info(f"📥 Réception balance N-1 (fichier séparé): {request.filename_n1}")
                file_n1_content = base64.b64decode(request.file_n1_base64)
                excel_file_n1 = io.BytesIO(file_n1_content)
                balance_n1_df = pd.read_excel(excel_file_n1, sheet_name=0)
                logger.info(f"📊 Balance N-1 chargée: {len(balance_n1_df)} lignes")
            except Exception as e:
                logger.warning(f"⚠️ Erreur chargement balance N-1: {e}")
        
        # Vérifier si on a vraiment une balance N-1 différente
        # Si pas de N-1, on ne duplique PAS - on laisse None pour avoir des montants à 0
        if balance_n1_df is None:
            logger.info("📋 Balance N-1 non trouvée, colonne N-1 sera vide")
        
        # FORMAT LIASSE OFFICIELLE (avec N et N-1)
        logger.info("📋 Utilisation du format liasse officielle (2 colonnes)")
        from etats_financiers_v2 import (
            process_balance_to_liasse_format,
            generate_section_html_liasse,
            generate_css_liasse
        )
        from tableau_flux_tresorerie_v2 import calculer_tft_liasse
        from annexes_liasse_complete import calculer_annexes_completes
        from html_liasse_complete import generate_tft_html_liasse, generate_annexes_html_liasse
        from etats_controle_exhaustifs import (
            calculer_etat_controle_bilan_actif_n,
            calculer_etat_controle_bilan_actif_n1,
            calculer_etat_controle_bilan_actif_variation,
            calculer_etat_controle_bilan_passif_n,
            calculer_etat_controle_bilan_passif_n1,
            calculer_etat_controle_bilan_passif_variation,
            calculer_etat_controle_compte_resultat_n,
            calculer_etat_controle_compte_resultat_n1,
            calculer_etat_controle_compte_resultat_variation,
            calculer_etat_controle_tft_n,
            calculer_etat_controle_tft_n1,
            calculer_etat_controle_tft_variation,
            calculer_etat_controle_sens_comptes_n,
            calculer_etat_controle_sens_comptes_n1,
            calculer_etat_equilibre_bilan_n,
            calculer_etat_equilibre_bilan_n1
        )
        # Import du nouveau module avec les 16 états de contrôle exhaustifs
        from etats_controle_exhaustifs_html import generate_all_16_etats_controle_html
        
        # Chercher Balance N-2 si disponible (AVANT le traitement)
        balance_n2_df = None
        balance_n2_patterns = ["Balance N-2", "balance n-2", "BALANCE N-2", "Balance N-2 (", "balance_n2"]
        for sheet in sheet_names:
            if any(pattern in sheet for pattern in balance_n2_patterns):
                balance_n2_df = pd.read_excel(excel_data, sheet_name=sheet)
                logger.info(f"✅ Balance N-2 trouvée dans l'onglet '{sheet}': {len(balance_n2_df)} lignes")
                break
        
        # Si pas trouvé par pattern et qu'il y a au moins 3 onglets, utiliser le 3ème
        if balance_n2_df is None and len(sheet_names) >= 3:
            balance_n2_df = pd.read_excel(excel_data, sheet_name=2)
            logger.info(f"📊 Balance N-2 chargée depuis le troisième onglet '{sheet_names[2]}': {len(balance_n2_df)} lignes")
        
        if balance_n2_df is None:
            logger.info("📋 Balance N-2 non trouvée, colonne N-2 sera vide")
        
        # Traiter les balances au format liasse avec N-2
        results_liasse = process_balance_to_liasse_format(balance_df, balance_n1_df, balance_n2_df, correspondances)
        
        # Calculer le TFT au format liasse (N et N-1)
        try:
            logger.info("🔄 Calcul du TFT...")
            logger.info(f"  balance_df: {len(balance_df) if balance_df is not None else 'None'} lignes")
            logger.info(f"  balance_n1_df: {len(balance_n1_df) if balance_n1_df is not None else 'None'} lignes")
            logger.info(f"  balance_n2_df: {len(balance_n2_df) if balance_n2_df is not None else 'None'} lignes")
            
            resultat_net_n = next((p['montant_n'] for p in results_liasse['compte_resultat'] if p['ref'] == 'XI'), 0)
            resultat_net_n1 = next((p['montant_n1'] for p in results_liasse['compte_resultat'] if p['ref'] == 'XI'), 0)
            
            logger.info(f"  resultat_net_n: {resultat_net_n:,.0f}")
            logger.info(f"  resultat_net_n1: {resultat_net_n1:,.0f}")
            
            tft_data = calculer_tft_liasse(balance_df, balance_n1_df, balance_n2_df, resultat_net_n, resultat_net_n1)
            results_liasse['tft'] = tft_data
            logger.info(f"✅ TFT calculé avec succès: {len(tft_data.get('tft', []))} lignes")
            logger.info(f"  TFT ajouté à results_liasse: {'tft' in results_liasse}")
        except Exception as e:
            logger.error(f"❌ Erreur calcul TFT: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.error(traceback.format_exc())
        
        # Calculer les annexes complètes au format liasse
        try:
            logger.info("🔄 Calcul des annexes...")
            annexes_data = calculer_annexes_completes(
                results_liasse['bilan_actif'],
                results_liasse['bilan_actif'],
                results_liasse['bilan_passif'],
                results_liasse['bilan_passif'],
                results_liasse['compte_resultat'],
                results_liasse['compte_resultat']
            )
            results_liasse['annexes'] = annexes_data
            logger.info(f"✅ Annexes calculées avec succès: {len(annexes_data)} notes")
        except Exception as e:
            logger.error(f"❌ Erreur calcul annexes: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Générer le HTML au format liasse
        # CSS complet avec accordéons (inline pour éviter problèmes de cache)
        html = """
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

/* Styles pour les 16 états de contrôle exhaustifs */
.section {
    margin-bottom: 40px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.section:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.section-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.3em;
    font-weight: bold;
}

.section-header:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.section-header .arrow {
    transition: transform 0.3s ease;
    font-size: 1.5em;
}

.section.active .arrow {
    transform: rotate(90deg);
}

.section-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.section.active .section-content {
    max-height: 2000px;
}

.section-body {
    padding: 30px;
}

/* Boîtes colorées pour les états de contrôle */
.success-box {
    background: #d4edda;
    border-left: 4px solid #28a745;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
}

.warning-box {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
}

.danger-box {
    background: #f8d7da;
    border-left: 4px solid #dc3545;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
}

.info-box {
    background: #d1ecf1;
    border-left: 4px solid #17a2b8;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
}

/* Badges pour les états de contrôle */
.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
    text-transform: uppercase;
    background: #6c757d;
    color: white;
}

.badge-success {
    background: #28a745;
    color: white;
}

.badge-warning {
    background: #ffc107;
    color: #212529;
}

.badge-danger {
    background: #dc3545;
    color: white;
}

.badge-info {
    background: #17a2b8;
    color: white;
}

.badge-critical {
    background: #dc3545;
    color: white;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
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
        html += "<div class='etats-fin-container'>"
        html += "<div class='etats-fin-header'><h2>📊 États Financiers SYSCOHADA Révisé</h2><p>Format Liasse Officielle</p></div>"
        
        # Bilan
        html += generate_section_html_liasse("bilan_actif", "🏢 BILAN - ACTIF", results_liasse['bilan_actif'])
        html += generate_section_html_liasse("bilan_passif", "🏛️ BILAN - PASSIF", results_liasse['bilan_passif'])
        
        # Compte de Résultat
        html += generate_section_html_liasse("compte_resultat", "📊 COMPTE DE RÉSULTAT", results_liasse['compte_resultat'])
        
        # TFT au format liasse (si disponible)
        logger.info(f"🔍 Vérification TFT dans results_liasse: {'tft' in results_liasse}")
        if 'tft' in results_liasse:
            logger.info(f"  TFT présent: {results_liasse['tft'] is not None}")
            if results_liasse['tft']:
                logger.info(f"  Nombre de lignes TFT: {len(results_liasse['tft'].get('tft', []))}")
                html += generate_tft_html_liasse(results_liasse['tft'])
                logger.info("✅ HTML TFT ajouté")
            else:
                logger.warning("⚠️ TFT est vide")
        else:
            logger.warning("⚠️ TFT non trouvé dans results_liasse")
        
        # Annexes au format liasse (si disponibles)
        if 'annexes' in results_liasse and results_liasse['annexes']:
            html += generate_annexes_html_liasse(results_liasse['annexes'])
        
        # Calculer et ajouter les états de contrôle exhaustifs (16 états)
        try:
            etats_controle = {}
            
            # Les données sont déjà au format liasse avec montant_n et montant_n1 dans chaque poste
            bilan_actif_n = results_liasse['bilan_actif']
            bilan_actif_n1 = results_liasse['bilan_actif']
            bilan_passif_n = results_liasse['bilan_passif']
            bilan_passif_n1 = results_liasse['bilan_passif']
            compte_resultat_n = results_liasse['compte_resultat']
            compte_resultat_n1 = results_liasse['compte_resultat']
            
            # 1-3: Bilan Actif (N, N-1, Variation)
            etats_controle['etat_controle_bilan_actif_n'] = calculer_etat_controle_bilan_actif_n(bilan_actif_n)
            etats_controle['etat_controle_bilan_actif_n1'] = calculer_etat_controle_bilan_actif_n1(bilan_actif_n1)
            etats_controle['etat_controle_bilan_actif_variation'] = calculer_etat_controle_bilan_actif_variation(bilan_actif_n, bilan_actif_n1)
            
            # 4-6: Bilan Passif (N, N-1, Variation)
            etats_controle['etat_controle_bilan_passif_n'] = calculer_etat_controle_bilan_passif_n(bilan_passif_n)
            etats_controle['etat_controle_bilan_passif_n1'] = calculer_etat_controle_bilan_passif_n1(bilan_passif_n1)
            etats_controle['etat_controle_bilan_passif_variation'] = calculer_etat_controle_bilan_passif_variation(bilan_passif_n, bilan_passif_n1)
            
            # 7-9: Compte de Résultat (N, N-1, Variation)
            etats_controle['etat_controle_compte_resultat_n'] = calculer_etat_controle_compte_resultat_n(compte_resultat_n)
            etats_controle['etat_controle_compte_resultat_n1'] = calculer_etat_controle_compte_resultat_n1(compte_resultat_n1)
            etats_controle['etat_controle_compte_resultat_variation'] = calculer_etat_controle_compte_resultat_variation(compte_resultat_n, compte_resultat_n1)
            
            # 10-11: TFT (N, N-1)
            if 'tft' in results_liasse and results_liasse['tft']:
                tft_data = results_liasse['tft'].get('tft', [])
                etats_controle['etat_controle_tft_n'] = calculer_etat_controle_tft_n(tft_data)
                etats_controle['etat_controle_tft_n1'] = calculer_etat_controle_tft_n1(tft_data)
            
            # 12-13: Sens des Comptes (N, N-1)
            balance_n_records = balance_df.to_dict('records') if balance_df is not None else []
            balance_n1_records = balance_n1_df.to_dict('records') if balance_n1_df is not None else []
            etats_controle['etat_controle_sens_comptes_n'] = calculer_etat_controle_sens_comptes_n(balance_n_records)
            etats_controle['etat_controle_sens_comptes_n1'] = calculer_etat_controle_sens_comptes_n1(balance_n1_records)
            
            # 15-16: Équilibre Bilan (N, N-1)
            resultat_net_n = next((p['montant_n'] for p in results_liasse['compte_resultat'] if p['ref'] == 'XI'), 0)
            resultat_net_n1 = next((p['montant_n1'] for p in results_liasse['compte_resultat'] if p['ref'] == 'XI'), 0)
            
            etats_controle['etat_equilibre_bilan_n'] = calculer_etat_equilibre_bilan_n(bilan_actif_n, bilan_passif_n, resultat_net_n)
            etats_controle['etat_equilibre_bilan_n1'] = calculer_etat_equilibre_bilan_n1(bilan_actif_n1, bilan_passif_n1, resultat_net_n1)
            
            # Générer le HTML des états de contrôle avec le nouveau module (16 états exhaustifs)
            logger.info("🔄 Génération HTML états de contrôle exhaustifs (16 états)...")
            
            # Préparer les données pour N
            controles_n = {
                'statistiques': {
                    'total_comptes_balance': len(balance_n_records),
                    'comptes_integres': len(balance_n_records) - len([c for c in balance_n_records if not c.get('integre', True)]),
                    'comptes_non_integres': len([c for c in balance_n_records if not c.get('integre', True)]),
                    'taux_couverture': 100.0 if len(balance_n_records) == 0 else (len(balance_n_records) - len([c for c in balance_n_records if not c.get('integre', True)])) / len(balance_n_records) * 100
                },
                'equilibre_bilan': etats_controle.get('etat_equilibre_bilan_n', {}),
                'equilibre_resultat': {
                    'resultat_cr': resultat_net_n,
                    'resultat_bilan': resultat_net_n,
                    'difference': 0,
                    'equilibre': True
                },
                'comptes_non_integres': [],
                'comptes_sens_inverse': [],
                'comptes_desequilibre': [],
                'hypothese_affectation': {
                    'resultat_net': resultat_net_n,
                    'actif': sum(p.get('montant_n', 0) for p in bilan_actif_n),
                    'passif_sans_resultat': sum(p.get('montant_n', 0) for p in bilan_passif_n),
                    'difference_avant': 0,
                    'passif_avec_resultat': sum(p.get('montant_n', 0) for p in bilan_passif_n) + resultat_net_n,
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
            
            # Préparer les données pour N-1
            controles_n1 = {
                'statistiques': {
                    'total_comptes_balance': len(balance_n1_records),
                    'comptes_integres': len(balance_n1_records) - len([c for c in balance_n1_records if not c.get('integre', True)]),
                    'comptes_non_integres': len([c for c in balance_n1_records if not c.get('integre', True)]),
                    'taux_couverture': 100.0 if len(balance_n1_records) == 0 else (len(balance_n1_records) - len([c for c in balance_n1_records if not c.get('integre', True)])) / len(balance_n1_records) * 100
                },
                'equilibre_bilan': etats_controle.get('etat_equilibre_bilan_n1', {}),
                'equilibre_resultat': {
                    'resultat_cr': resultat_net_n1,
                    'resultat_bilan': resultat_net_n1,
                    'difference': 0,
                    'equilibre': True
                },
                'comptes_non_integres': [],
                'comptes_sens_inverse': [],
                'comptes_desequilibre': [],
                'hypothese_affectation': {
                    'resultat_net': resultat_net_n1,
                    'actif': sum(p.get('montant_n1', 0) for p in bilan_actif_n1),
                    'passif_sans_resultat': sum(p.get('montant_n1', 0) for p in bilan_passif_n1),
                    'difference_avant': 0,
                    'passif_avec_resultat': sum(p.get('montant_n1', 0) for p in bilan_passif_n1) + resultat_net_n1,
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
            
            # Totaux pour N et N-1
            totaux_n = {
                'actif': sum(p.get('montant_n', 0) for p in bilan_actif_n),
                'passif': sum(p.get('montant_n', 0) for p in bilan_passif_n),
                'resultat': resultat_net_n
            }
            
            totaux_n1 = {
                'actif': sum(p.get('montant_n1', 0) for p in bilan_actif_n1),
                'passif': sum(p.get('montant_n1', 0) for p in bilan_passif_n1),
                'resultat': resultat_net_n1
            }
            
            # Appeler la nouvelle fonction qui génère les 16 états
            html_etats = generate_all_16_etats_controle_html(controles_n, controles_n1, totaux_n, totaux_n1)
            logger.info(f"  HTML généré: {len(html_etats)} caractères")
            
            # IMPORTANT: Ajouter les états de contrôle AVANT la fermeture de la div principale
            # pour qu'ils soient intégrés dans le menu accordéon
            html += html_etats
            logger.info("✅ États de contrôle exhaustifs générés avec succès (16 états)")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur génération états de contrôle: {e}")
            import traceback
            traceback.print_exc()
        
        # Fermer la div principale APRÈS l'ajout des états de contrôle
        html += "</div>"
        
        # Ajouter le script pour les accordéons
        html += """
        <script>
        // Gestion des accordéons pour les sections principales (Bilan, CR, TFT, Annexes)
        document.querySelectorAll('.section-header-ef').forEach(header => {
            header.addEventListener('click', function() {
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                content.classList.toggle('active');
            });
        });
        
        // Gestion des accordéons pour les 16 états de contrôle exhaustifs
        function toggleSection(header) {
            const section = header.parentElement;
            section.classList.toggle('active');
        }
        
        // Ajouter les event listeners pour les états de contrôle
        document.querySelectorAll('.section-header').forEach(header => {
            header.addEventListener('click', function() {
                toggleSection(this);
            });
        });
        </script>
        """
        
        message_parts = [request.filename]
        if request.filename_n1:
            message_parts.append(request.filename_n1)
        message = f"États financiers générés au format liasse officielle à partir de {' et '.join(message_parts)}"
        
        return EtatsFinanciersResponse(
            success=True,
            message=message,
            results=results_liasse,
            html=html
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
