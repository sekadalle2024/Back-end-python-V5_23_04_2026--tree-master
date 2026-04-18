# -*- coding: utf-8 -*-
"""
Module de génération HTML pour TFT et Annexes au format liasse officielle
"""
from typing import Dict, Any, List


def format_montant_liasse(montant: float) -> str:
    """Formate un montant pour la liasse (- si nul)"""
    if abs(montant) < 0.01:
        return "-"
    return f"{montant:,.0f}".replace(',', ' ')


def generate_tft_html_liasse(tft_data: Dict[str, Any]) -> str:
    """
    Génère le HTML du TFT au format liasse officielle (colonnes N et N-1)
    """
    if not tft_data or 'tft' not in tft_data:
        return ''
    
    tft_lignes = tft_data['tft']
    
    html = """
    <div class="etats-fin-section" data-section="tft">
        <div class="section-header-ef">
            <span>💧 TABLEAU DES FLUX DE TRÉSORERIE (TFT)</span>
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
    
    for ligne in tft_lignes:
        ref = ligne['ref']
        libelle = ligne['libelle']
        montant_n = ligne['montant_n']
        montant_n1 = ligne['montant_n1']
        is_total = ligne.get('is_total', False)
        
        row_class = 'total-row' if is_total else ''
        
        html += f"""
                    <tr class="{row_class}">
                        <td class="ref-cell">{ref}</td>
                        <td class="libelle-cell">{libelle}</td>
                        <td class="montant-cell">{format_montant_liasse(montant_n)}</td>
                        <td class="montant-cell">{format_montant_liasse(montant_n1)}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


def generate_annexes_html_liasse(annexes: Dict[str, Any]) -> str:
    """
    Génère le HTML des annexes au format liasse officielle (colonnes N et N-1)
    """
    if not annexes:
        return ''
    
    html = """
    <div class="etats-fin-section" data-section="annexes">
        <div class="section-header-ef">
            <span>📋 NOTES ANNEXES</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef">
    """
    
    # Générer chaque note
    for note_key, note_data in annexes.items():
        if not note_data:
            continue
        
        titre = note_data.get('titre', '')
        postes = note_data.get('postes', [])
        
        if not postes:
            continue
        
        html += f"""
            <div style="margin: 16px 0; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 12px 16px; font-weight: 600;">
                    {titre}
                </div>
                <table class="liasse-table" style="margin: 0;">
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
        
        # Afficher les postes
        for poste in postes:
            ref = poste.get('ref', '')
            libelle = poste.get('libelle', '')
            montant_n = poste.get('montant_n', 0)
            montant_n1 = poste.get('montant_n1', 0)
            
            # Déterminer si c'est un total
            is_total = ref.startswith('X') or libelle.isupper() or 'TOTAL' in libelle.upper()
            row_class = 'total-row' if is_total else ''
            
            html += f"""
                        <tr class="{row_class}">
                            <td class="ref-cell">{ref}</td>
                            <td class="libelle-cell">{libelle}</td>
                            <td class="montant-cell">{format_montant_liasse(montant_n)}</td>
                            <td class="montant-cell">{format_montant_liasse(montant_n1)}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html
