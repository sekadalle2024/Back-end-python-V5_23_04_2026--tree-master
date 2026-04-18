"""
Script pour calculer la Note 3A - Immobilisations incorporelles
à partir des balances à 8 colonnes (N, N-1, N-2)

Structure de la Note 3A:
- Frais de recherche et de développement (211)
- Brevets, licences, logiciels (212, 213, 214)
- Fonds commercial (215, 216)
- Autres immobilisations incorporelles (217, 218)

Colonnes de la Note 3A:
- Solde d'ouverture (Brut N-1)
- Augmentations (Mouvements débit N)
- Diminutions (Mouvements crédit N)
- Solde de clôture (Brut N)
- Amortissements d'ouverture (N-1)
- Dotations aux amortissements (N)
- Reprises d'amortissements (N)
- Amortissements de clôture (N)
- Valeur nette comptable d'ouverture (N-1)
- Valeur nette comptable de clôture (N)
"""

import pandas as pd
import json
from typing import Dict, List, Tuple

class CalculateurNote3A:
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur avec le fichier de balances
        
        Args:
            fichier_balance: Chemin vers le fichier Excel des balances
        """
        self.fichier_balance = fichier_balance
        self.balance_n = None
        self.balance_n1 = None
        self.balance_n2 = None
        
        # Mapping des comptes pour la Note 3A
        self.mapping_comptes = {
            "Frais de recherche et de développement": {
                "brut": ["211"],
                "amort": ["2811", "2919"]
            },
            "Brevets, licences, logiciels": {
                "brut": ["212", "213", "214"],
                "amort": ["2812", "2813", "2814", "2912", "2913", "2914"]
            },
            "Fonds commercial": {
                "brut": ["215", "216"],
                "amort": ["2815", "2816", "2915", "2916"]
            },
            "Autres immobilisations incorporelles": {
                "brut": ["217", "218"],
                "amort": ["2817", "2818", "2917", "2918"]
            }
        }
    
    def charger_balances(self):
        """Charge les 3 balances depuis le fichier Excel"""
        try:
            xls = pd.ExcelFile(self.fichier_balance)
            
            # Afficher les noms des onglets disponibles
            print(f"Onglets disponibles: {xls.sheet_names}")
            
            # Détecter automatiquement les noms des onglets (avec espaces)
            onglets = xls.sheet_names
            
            # Trouver les onglets N, N-1, N-2
            onglet_n = None
            onglet_n1 = None
            onglet_n2 = None
            
            for onglet in onglets:
                onglet_clean = onglet.strip().upper()
                if 'BALANCE N-2' in onglet_clean:
                    onglet_n2 = onglet
                elif 'BALANCE N-1' in onglet_clean:
                    onglet_n1 = onglet
                elif 'BALANCE N' in onglet_clean and 'N-' not in onglet_clean:
                    onglet_n = onglet
            
            if not all([onglet_n, onglet_n1, onglet_n2]):
                print(f"✗ Impossible de trouver tous les onglets nécessaires")
                print(f"  - BALANCE N: {onglet_n}")
                print(f"  - BALANCE N-1: {onglet_n1}")
                print(f"  - BALANCE N-2: {onglet_n2}")
                return False
            
            # Charger les 3 onglets
            print(f"Chargement de '{onglet_n}'...")
            self.balance_n = pd.read_excel(xls, onglet_n)
            
            print(f"Chargement de '{onglet_n1}'...")
            self.balance_n1 = pd.read_excel(xls, onglet_n1)
            
            print(f"Chargement de '{onglet_n2}'...")
            self.balance_n2 = pd.read_excel(xls, onglet_n2)
            
            # Nettoyer les noms de colonnes
            for df in [self.balance_n, self.balance_n1, self.balance_n2]:
                df.columns = df.columns.str.strip()
            
            print("✓ Balances chargées avec succès")
            print(f"  - Balance N: {len(self.balance_n)} lignes")
            print(f"  - Balance N-1: {len(self.balance_n1)} lignes")
            print(f"  - Balance N-2: {len(self.balance_n2)} lignes")
            
            return True
            
        except Exception as e:
            print(f"✗ Erreur lors du chargement des balances: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extraire_solde_compte(self, balance: pd.DataFrame, numero_compte: str) -> Dict[str, float]:
        """
        Extrait les soldes d'un compte depuis une balance
        
        Args:
            balance: DataFrame de la balance
            numero_compte: Numéro du compte (ex: "211")
        
        Returns:
            Dict avec les colonnes de la balance
        """
        # Nettoyer la colonne Numéro
        balance['Numéro'] = balance['Numéro'].astype(str).str.strip()
        
        # Filtrer par racine de compte
        ligne = balance[balance['Numéro'].str.startswith(numero_compte)]
        
        if ligne.empty:
            return {
                'ant_debit': 0.0,
                'ant_credit': 0.0,
                'mvt_debit': 0.0,
                'mvt_credit': 0.0,
                'solde_debit': 0.0,
                'solde_credit': 0.0
            }
        
        # Fonction pour convertir en float
        def to_float(val):
            if pd.isna(val) or val == '' or val is None:
                return 0.0
            try:
                # Nettoyer les espaces et convertir
                if isinstance(val, str):
                    val = val.strip().replace(' ', '').replace(',', '.')
                return float(val)
            except:
                return 0.0
        
        # Extraire les valeurs et convertir en float
        result = {
            'ant_debit': to_float(ligne.iloc[0].get('Ant  Débit', 0)),
            'ant_credit': to_float(ligne.iloc[0].get('Ant     Crédit', 0)),
            'mvt_debit': to_float(ligne.iloc[0].get('Ant    Débit', 0)),
            'mvt_credit': to_float(ligne.iloc[0].get('Ant  Crédit', 0)),
            'solde_debit': to_float(ligne.iloc[0].get('Solde  Débit', 0)),
            'solde_credit': to_float(ligne.iloc[0].get('Solde Crédit', 0))
        }
        
        return result
    
    def calculer_ligne_note_3a(self, libelle: str, comptes_brut: List[str], comptes_amort: List[str]) -> Dict:
        """
        Calcule une ligne de la Note 3A
        
        Args:
            libelle: Libellé de la ligne
            comptes_brut: Liste des comptes de brut (classe 21)
            comptes_amort: Liste des comptes d'amortissement (classe 28, 29)
        
        Returns:
            Dict avec toutes les colonnes de la Note 3A
        """
        # Initialiser les totaux
        brut_ouverture = 0
        brut_cloture = 0
        augmentations = 0
        diminutions = 0
        
        amort_ouverture = 0
        amort_cloture = 0
        dotations = 0
        reprises = 0
        
        # Calculer les valeurs brutes
        for compte in comptes_brut:
            # Solde d'ouverture = Solde N-1
            solde_n1 = self.extraire_solde_compte(self.balance_n1, compte)
            brut_ouverture += solde_n1['solde_debit'] - solde_n1['solde_credit']
            
            # Mouvements de l'exercice N
            solde_n = self.extraire_solde_compte(self.balance_n, compte)
            augmentations += solde_n['mvt_debit']
            diminutions += solde_n['mvt_credit']
            
            # Solde de clôture = Solde N
            brut_cloture += solde_n['solde_debit'] - solde_n['solde_credit']
        
        # Calculer les amortissements
        for compte in comptes_amort:
            # Amortissements d'ouverture = Solde N-1
            solde_n1 = self.extraire_solde_compte(self.balance_n1, compte)
            amort_ouverture += solde_n1['solde_credit'] - solde_n1['solde_debit']
            
            # Dotations et reprises de l'exercice N
            solde_n = self.extraire_solde_compte(self.balance_n, compte)
            dotations += solde_n['mvt_credit']
            reprises += solde_n['mvt_debit']
            
            # Amortissements de clôture = Solde N
            amort_cloture += solde_n['solde_credit'] - solde_n['solde_debit']
        
        # Calculer les valeurs nettes comptables
        vnc_ouverture = brut_ouverture - amort_ouverture
        vnc_cloture = brut_cloture - amort_cloture
        
        return {
            'libelle': libelle,
            'brut_ouverture': brut_ouverture,
            'augmentations': augmentations,
            'diminutions': diminutions,
            'brut_cloture': brut_cloture,
            'amort_ouverture': amort_ouverture,
            'dotations': dotations,
            'reprises': reprises,
            'amort_cloture': amort_cloture,
            'vnc_ouverture': vnc_ouverture,
            'vnc_cloture': vnc_cloture
        }
    
    def generer_note_3a(self) -> pd.DataFrame:
        """
        Génère la Note 3A complète
        
        Returns:
            DataFrame avec toutes les lignes de la Note 3A
        """
        lignes = []
        
        for libelle, comptes in self.mapping_comptes.items():
            ligne = self.calculer_ligne_note_3a(
                libelle,
                comptes['brut'],
                comptes['amort']
            )
            lignes.append(ligne)
        
        # Calculer la ligne de total
        total = {
            'libelle': 'TOTAL IMMOBILISATIONS INCORPORELLES',
            'brut_ouverture': sum(l['brut_ouverture'] for l in lignes),
            'augmentations': sum(l['augmentations'] for l in lignes),
            'diminutions': sum(l['diminutions'] for l in lignes),
            'brut_cloture': sum(l['brut_cloture'] for l in lignes),
            'amort_ouverture': sum(l['amort_ouverture'] for l in lignes),
            'dotations': sum(l['dotations'] for l in lignes),
            'reprises': sum(l['reprises'] for l in lignes),
            'amort_cloture': sum(l['amort_cloture'] for l in lignes),
            'vnc_ouverture': sum(l['vnc_ouverture'] for l in lignes),
            'vnc_cloture': sum(l['vnc_cloture'] for l in lignes)
        }
        lignes.append(total)
        
        df = pd.DataFrame(lignes)
        return df
    
    def generer_html(self, df: pd.DataFrame) -> str:
        """
        Génère le HTML de la Note 3A
        
        Args:
            df: DataFrame de la Note 3A
        
        Returns:
            Code HTML du tableau
        """
        html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOTE 3A - Immobilisations incorporelles</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: right;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            text-align: center;
        }
        td:first-child, th:first-child {
            text-align: left;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #e8f4f8;
        }
        tr:last-child {
            background-color: #ecf0f1;
            font-weight: bold;
        }
        .number {
            font-family: 'Courier New', monospace;
        }
        .section-header {
            background-color: #2c3e50 !important;
            color: white !important;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>NOTE 3A - IMMOBILISATIONS INCORPORELLES</h1>
        <table>
            <thead>
                <tr>
                    <th rowspan="2">LIBELLÉ</th>
                    <th colspan="4" class="section-header">VALEUR BRUTE</th>
                    <th colspan="4" class="section-header">AMORTISSEMENTS</th>
                    <th colspan="2" class="section-header">VALEUR NETTE COMPTABLE</th>
                </tr>
                <tr>
                    <th>Solde d'ouverture</th>
                    <th>Augmentations</th>
                    <th>Diminutions</th>
                    <th>Solde de clôture</th>
                    <th>Solde d'ouverture</th>
                    <th>Dotations</th>
                    <th>Reprises</th>
                    <th>Solde de clôture</th>
                    <th>Ouverture</th>
                    <th>Clôture</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for _, row in df.iterrows():
            html += f"""
                <tr>
                    <td>{row['libelle']}</td>
                    <td class="number">{row['brut_ouverture']:,.0f}</td>
                    <td class="number">{row['augmentations']:,.0f}</td>
                    <td class="number">{row['diminutions']:,.0f}</td>
                    <td class="number">{row['brut_cloture']:,.0f}</td>
                    <td class="number">{row['amort_ouverture']:,.0f}</td>
                    <td class="number">{row['dotations']:,.0f}</td>
                    <td class="number">{row['reprises']:,.0f}</td>
                    <td class="number">{row['amort_cloture']:,.0f}</td>
                    <td class="number">{row['vnc_ouverture']:,.0f}</td>
                    <td class="number">{row['vnc_cloture']:,.0f}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html


def main():
    """Fonction principale"""
    print("=" * 80)
    print("CALCUL DE LA NOTE 3A - IMMOBILISATIONS INCORPORELLES")
    print("=" * 80)
    print()
    
    # Initialiser le calculateur
    fichier_balance = "P000 -BALANCE DEMO N_N-1_N-2.xls"
    calculateur = CalculateurNote3A(fichier_balance)
    
    # Charger les balances
    if not calculateur.charger_balances():
        return
    
    print()
    print("Calcul de la Note 3A en cours...")
    
    # Générer la Note 3A
    df_note_3a = calculateur.generer_note_3a()
    
    print("✓ Note 3A calculée avec succès")
    print()
    print("=" * 80)
    print("RÉSULTATS")
    print("=" * 80)
    print()
    print(df_note_3a.to_string(index=False))
    print()
    
    # Générer le HTML
    html = calculateur.generer_html(df_note_3a)
    
    # Sauvegarder le fichier HTML dans le dossier Tests
    dossier_tests = os.path.join(os.path.dirname(__file__), '..', 'Tests')
    os.makedirs(dossier_tests, exist_ok=True)
    fichier_html = os.path.join(dossier_tests, 'test_note_3a.html')
    with open(fichier_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Fichier HTML généré: {fichier_html}")
    print()
    print("=" * 80)
    print("MISSION ACCOMPLIE")
    print("=" * 80)


if __name__ == "__main__":
    main()
