# -*- coding: utf-8 -*-
"""
Module de génération HTML pour les états de contrôle exhaustifs
"""

from typing import Dict, Any, List


def format_montant_controle(montant: float) -> str:
    """Formate un montant pour les contrôles"""
    if abs(montant) < 0.01:
        return "-"
    return f"{montant:,.0f}".replace(',', ' ')


def generate_etat_controle_html(etat_controle: Dict[str, Any], section_id: str) -> str:
    """Génère le HTML pour un état de contrôle"""
    
    if not etat_controle or 'postes' not in etat_controle:
        return ''
    
    titre = etat_controle.get('titre', 'État de contrôle')
    postes = etat_controle.get('postes', [])
    
    html = f"""
    <div class="etats-fin-section" data-section="{section_id}">
        <div class="section-header-ef">
            <span>🔍 {titre}</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef">
            <table class="liasse-table">
                <thead>
                    <tr>
                        <th style="width: 60px;">REF</th>
                        <th style="width: auto;">LIBELLÉS</th>
                        <th style="width: 150px; text-align: right;">EXERCICE N</th>
                        <th style="width: 150px; text-align: right;">EXERCICE N-1</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for poste in postes:
        ref = poste.get('ref', '')
        libelle = poste.get('libelle', '')
        montant_n = poste.get('montant_n', 0)
        montant_n1 = poste.get('montant_n1', 0)
        
        # Déterminer si c'est un total
        is_total = 'Total' in libelle or 'Équilibre' in libelle or 'Variation' in libelle
        row_class = 'total-row' if is_total else ''
        
        html += f"""
                    <tr class="{row_class}">
                        <td class="ref-cell">{ref}</td>
                        <td class="libelle-cell">{libelle}</td>
                        <td class="montant-cell">{format_montant_controle(montant_n)}</td>
                        <td class="montant-cell">{format_montant_controle(montant_n1)}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


def generate_all_etats_controle_html(etats_controle: Dict[str, Dict[str, Any]]) -> str:
    """Génère le HTML pour tous les 16 états de contrôle"""
    
    html = ""
    
    # Ordre des 16 états de contrôle (format exhaustif)
    ordre = [
        ('etat_controle_bilan_actif_n', '1. Etat de contrôle Bilan Actif (Exercice N)'),
        ('etat_controle_bilan_actif_n1', '2. Etat de contrôle Bilan Actif (Exercice N-1)'),
        ('etat_controle_bilan_actif_variation', '3. Variation Bilan Actif'),
        ('etat_controle_bilan_passif_n', '4. Etat de contrôle Bilan Passif (Exercice N)'),
        ('etat_controle_bilan_passif_n1', '5. Etat de contrôle Bilan Passif (Exercice N-1)'),
        ('etat_controle_bilan_passif_variation', '6. Variation Bilan Passif'),
        ('etat_controle_compte_resultat_n', '7. Etat de contrôle Compte de Résultat (Exercice N)'),
        ('etat_controle_compte_resultat_n1', '8. Etat de contrôle Compte de Résultat (Exercice N-1)'),
        ('etat_controle_compte_resultat_variation', '9. Variation Compte de Résultat'),
        ('etat_controle_tft_n', '10. Etat de contrôle Tableau des Flux de Trésorerie (Exercice N)'),
        ('etat_controle_tft_n1', '11. Etat de contrôle Tableau des Flux de Trésorerie (Exercice N-1)'),
        ('etat_controle_tft_variation', '12. Variation Tableau des Flux de Trésorerie'),
        ('etat_controle_sens_comptes_n', '13. Etat de contrôle Sens des Comptes (Exercice N)'),
        ('etat_controle_sens_comptes_n1', '14. Etat de contrôle Sens des Comptes (Exercice N-1)'),
        ('etat_equilibre_bilan_n', '15. Etat d\'équilibre Bilan (Exercice N)'),
        ('etat_equilibre_bilan_n1', '16. Etat d\'équilibre Bilan (Exercice N-1)'),
    ]
    
    for key, _ in ordre:
        if key in etats_controle:
            html += generate_etat_controle_html(etats_controle[key], key)
    
    return html
