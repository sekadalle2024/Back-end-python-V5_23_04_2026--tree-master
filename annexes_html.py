# -*- coding: utf-8 -*-
"""
Module de génération HTML pour les annexes
"""
from typing import Dict, Any


def format_number(x: float) -> str:
    """Formate un nombre avec séparateurs de milliers"""
    try:
        return f"{x:,.2f}".replace(',', ' ').replace('.', ',')
    except:
        return str(x)


def generate_annexes_html(annexes: Dict[str, Any]) -> str:
    """
    Génère le HTML pour afficher les annexes dans le menu accordéon
    """
    if not annexes:
        return ''
    
    html = """
    <div class="etats-fin-section" data-section="annexes">
        <div class="section-header-ef">
            <span>📋 ANNEXES (Notes calculables)</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef">
    """
    
    # Générer chaque note
    for note_key, note_data in annexes.items():
        if not note_data:
            continue
        
        titre = note_data.get('titre', '')
        
        # Note 13 (Résultat) - Format spécial
        if note_key == 'note_13':
            resultat_net = note_data.get('resultat_net', 0)
            type_resultat = note_data.get('type', '')
            montant = note_data.get('montant_absolu', 0)
            
            html += f"""
            <div style="padding: 12px 18px; background: #f0f9ff; border-bottom: 1px solid #e0e7ff; margin: 8px 0;">
                <div style="font-weight: 600; color: #1e3a8a; margin-bottom: 6px;">{titre}</div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0;">
                    <span>Type: {type_resultat}</span>
                    <span style="font-family: 'Consolas', monospace; font-weight: 600;">
                        {format_number(montant)}
                    </span>
                </div>
            </div>
            """
            continue
        
        # Notes avec postes détaillés
        postes = note_data.get('postes', {})
        total = note_data.get('total', 0)
        
        if not postes:
            continue
        
        html += f"""
        <div style="padding: 12px 18px; background: #fefce8; border-bottom: 1px solid #fef3c7; margin: 8px 0;">
            <div style="font-weight: 600; color: #854d0e; margin-bottom: 8px;">{titre}</div>
        """
        
        # Afficher les postes
        for ref, poste_data in postes.items():
            libelle = poste_data.get('libelle', '')
            montant = poste_data.get('montant', 0)
            
            html += f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px;">
                <span style="color: #78716c;">
                    <span style="font-weight: 600; color: #1e3a8a; margin-right: 8px;">{ref}</span>
                    {libelle}
                </span>
                <span style="font-family: 'Consolas', monospace; font-weight: 600; color: #059669;">
                    {format_number(montant)}
                </span>
            </div>
            """
        
        # Total
        if total != 0:
            html += f"""
            <div style="display: flex; justify-content: space-between; padding: 8px 0; margin-top: 8px; border-top: 2px solid #fbbf24; font-weight: 700;">
                <span>TOTAL</span>
                <span style="font-family: 'Consolas', monospace; color: #059669;">
                    {format_number(total)}
                </span>
            </div>
            """
        
        html += """
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html
