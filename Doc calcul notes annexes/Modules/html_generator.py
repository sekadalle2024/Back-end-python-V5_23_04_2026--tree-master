"""
Module de génération des fichiers HTML de visualisation.

Ce module génère des tableaux HTML formatés conformes au format SYSCOHADA.
"""

import logging
from typing import Dict
import pandas as pd

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Générateur de fichiers HTML pour les notes annexes."""
    
    def __init__(self, titre_note: str, numero_note: str):
        """
        Initialise le générateur avec le titre et numéro de la note.
        
        Args:
            titre_note: Titre de la note (ex: "IMMOBILISATIONS INCORPORELLES")
            numero_note: Numéro de la note (ex: "3A")
        """
        self.titre_note = titre_note
        self.numero_note = numero_note
        logger.debug(f"HTMLGenerator initialisé pour Note {numero_note}")
    
    def generer_html(self, df: pd.DataFrame, colonnes_config: Dict = None) -> str:
        """
        Génère le HTML complet d'une note annexe.
        
        Args:
            df: DataFrame avec les données de la note
            colonnes_config: Configuration des colonnes (optionnel)
            
        Returns:
            Code HTML complet
        """
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOTE {self.numero_note} - {self.titre_note}</title>
    {self.appliquer_style_css()}
</head>
<body>
    <div class="container">
        <h1>NOTE {self.numero_note}</h1>
        <h2>{self.titre_note}</h2>
        
        <table>
            {self.generer_entetes(colonnes_config)}
            {self.generer_lignes(df)}
        </table>
        
        <div class="footer">
            <p>Document généré automatiquement - Système SYSCOHADA Révisé</p>
        </div>
    </div>
</body>
</html>"""
        
        logger.info(f"✓ HTML généré pour Note {self.numero_note}")
        return html
    
    def generer_entetes(self, colonnes_config: Dict = None) -> str:
        """Génère les en-têtes du tableau avec groupes et sous-colonnes."""
        # En-têtes par défaut pour les immobilisations
        return """
            <thead>
                <tr class="header-group">
                    <th rowspan="2">POSTES</th>
                    <th colspan="4">VALEUR BRUTE</th>
                    <th colspan="4">AMORTISSEMENTS</th>
                    <th colspan="2">VALEUR NETTE COMPTABLE</th>
                </tr>
                <tr class="header-detail">
                    <th>Ouverture</th>
                    <th>Augmentations</th>
                    <th>Diminutions</th>
                    <th>Clôture</th>
                    <th>Ouverture</th>
                    <th>Dotations</th>
                    <th>Reprises</th>
                    <th>Clôture</th>
                    <th>Ouverture</th>
                    <th>Clôture</th>
                </tr>
            </thead>
        """
    
    def generer_lignes(self, df: pd.DataFrame) -> str:
        """Génère les lignes du tableau avec formatage des montants."""
        lignes_html = "<tbody>\n"
        
        for idx, row in df.iterrows():
            # Ligne de total avec style distinct
            classe = "total-row" if "TOTAL" in str(row.get('libelle', '')).upper() else ""
            
            lignes_html += f'    <tr class="{classe}">\n'
            lignes_html += f'        <td class="libelle">{row.get("libelle", "")}</td>\n'
            
            # Colonnes de montants
            colonnes_montants = [
                'brut_ouverture', 'augmentations', 'diminutions', 'brut_cloture',
                'amort_ouverture', 'dotations', 'reprises', 'amort_cloture',
                'vnc_ouverture', 'vnc_cloture'
            ]
            
            for col in colonnes_montants:
                valeur = row.get(col, 0.0)
                lignes_html += f'        <td class="montant">{self.formater_montant(valeur)}</td>\n'
            
            lignes_html += '    </tr>\n'
        
        lignes_html += "</tbody>"
        return lignes_html
    
    def formater_montant(self, montant: float) -> str:
        """
        Formate un montant: séparateur de milliers, 0 décimales.
        
        Args:
            montant: Montant à formater
            
        Returns:
            Montant formaté
        """
        if pd.isna(montant) or montant == 0:
            return "-"
        return f"{montant:,.0f}".replace(",", " ")
    
    def appliquer_style_css(self) -> str:
        """Retourne le CSS pour le tableau."""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #2c3e50;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #34495e;
            font-size: 18px;
            margin-bottom: 20px;
            font-weight: normal;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        
        thead th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            text-align: center;
        }
        
        .header-group th {
            background-color: #2980b9;
        }
        
        .header-detail th {
            background-color: #3498db;
            font-size: 12px;
        }
        
        tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        tbody tr:hover {
            background-color: #e8f4f8;
        }
        
        .libelle {
            font-weight: 500;
            color: #2c3e50;
        }
        
        .montant {
            text-align: right;
            font-family: 'Courier New', monospace;
            color: #34495e;
        }
        
        .total-row {
            background-color: #ecf0f1 !important;
            font-weight: bold;
        }
        
        .total-row .libelle {
            color: #2c3e50;
            font-weight: bold;
        }
        
        .total-row .montant {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #3498db;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }
        
        @media print {
            body {
                background-color: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                padding: 0;
            }
            
            .footer {
                page-break-after: avoid;
            }
        }
    </style>
        """
