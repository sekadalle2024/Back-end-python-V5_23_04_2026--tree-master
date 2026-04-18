"""
Template pour les scripts de calcul des notes annexes.

Ce template doit être copié et adapté pour chaque note (01 à 33).
Structure commune à tous les calculateurs.
"""

import sys
import os
import logging
import pandas as pd

# Ajouter le dossier Modules au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Modules'))

from balance_reader import BalanceReader
from account_extractor import AccountExtractor
from movement_calculator import MovementCalculator
from vnc_calculator import VNCCalculator
from html_generator import HTMLGenerator
from trace_manager import TraceManager

logger = logging.getLogger(__name__)


class CalculateurNoteXX:
    """
    Calculateur pour la Note XX - [TITRE DE LA NOTE].
    
    Cette classe calcule la note annexe XX selon le format SYSCOHADA révisé.
    """
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le calculateur.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel de balances
        """
        self.fichier_balance = fichier_balance
        self.balance_n = None
        self.balance_n1 = None
        self.balance_n2 = None
        
        # Mapping des comptes spécifique à cette note
        # À adapter pour chaque note
        self.mapping_comptes = {
            'Ligne 1': {
                'brut': ['211', '2111'],
                'amort': ['2811', '28111']
            },
            'Ligne 2': {
                'brut': ['212', '2121'],
                'amort': ['2812', '28121']
            },
            # Ajouter les autres lignes...
        }
        
        logger.info(f"CalculateurNoteXX initialisé avec {fichier_balance}")
    
    def charger_balances(self) -> bool:
        """
        Charge les 3 balances via Balance_Reader.
        
        Returns:
            True si le chargement a réussi
        """
        try:
            reader = BalanceReader(self.fichier_balance)
            self.balance_n, self.balance_n1, self.balance_n2 = reader.charger_balances()
            logger.info("✓ Balances chargées")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur lors du chargement des balances: {e}")
            return False
    
    def calculer_ligne_note(self, libelle: str, comptes_brut: list, 
                           comptes_amort: list) -> dict:
        """
        Calcule une ligne de la note.
        
        Args:
            libelle: Libellé de la ligne
            comptes_brut: Liste des racines de comptes brut
            comptes_amort: Liste des racines de comptes d'amortissement
            
        Returns:
            Dict avec toutes les colonnes de la note
        """
        # Extracteurs pour chaque exercice
        extractor_n = AccountExtractor(self.balance_n)
        extractor_n1 = AccountExtractor(self.balance_n1)
        
        # Extraire les soldes brut
        soldes_brut_n = extractor_n.extraire_comptes_multiples(comptes_brut)
        soldes_brut_n1 = extractor_n1.extraire_comptes_multiples(comptes_brut)
        
        # Extraire les soldes amortissement
        soldes_amort_n = extractor_n.extraire_comptes_multiples(comptes_amort)
        soldes_amort_n1 = extractor_n1.extraire_comptes_multiples(comptes_amort)
        
        # Calculer les valeurs brutes
        brut_ouverture = MovementCalculator.calculer_solde_ouverture(
            soldes_brut_n1['solde_debit'],
            soldes_brut_n1['solde_credit']
        )
        augmentations = MovementCalculator.calculer_augmentations(
            soldes_brut_n['mvt_debit']
        )
        diminutions = MovementCalculator.calculer_diminutions(
            soldes_brut_n['mvt_credit']
        )
        brut_cloture = MovementCalculator.calculer_solde_cloture(
            soldes_brut_n['solde_debit'],
            soldes_brut_n['solde_credit']
        )
        
        # Calculer les amortissements
        amort_ouverture = MovementCalculator.calculer_solde_ouverture(
            soldes_amort_n1['solde_credit'],  # Inversé pour amortissements
            soldes_amort_n1['solde_debit']
        )
        dotations = soldes_amort_n['mvt_credit']  # Crédit = augmentation amort
        reprises = soldes_amort_n['mvt_debit']    # Débit = diminution amort
        amort_cloture = MovementCalculator.calculer_solde_cloture(
            soldes_amort_n['solde_credit'],  # Inversé pour amortissements
            soldes_amort_n['solde_debit']
        )
        
        # Calculer les VNC
        vnc_ouverture = VNCCalculator.calculer_vnc_ouverture(
            brut_ouverture, amort_ouverture
        )
        vnc_cloture = VNCCalculator.calculer_vnc_cloture(
            brut_cloture, amort_cloture
        )
        
        # Vérifier la cohérence
        coherent, ecart = MovementCalculator.verifier_coherence(
            brut_ouverture, augmentations, diminutions, brut_cloture
        )
        
        if not coherent:
            logger.warning(f"Incohérence détectée pour '{libelle}': écart = {ecart:.2f}")
        
        # Valider la VNC
        valide, message = VNCCalculator.valider_vnc(vnc_cloture, libelle)
        if not valide:
            logger.warning(message)
        
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
    
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la note complète avec toutes les lignes et le total.
        
        Returns:
            DataFrame de la note
        """
        lignes = []
        
        # Calculer chaque ligne selon le mapping
        for libelle, comptes in self.mapping_comptes.items():
            ligne = self.calculer_ligne_note(
                libelle,
                comptes['brut'],
                comptes['amort']
            )
            lignes.append(ligne)
        
        # Créer le DataFrame
        df = pd.DataFrame(lignes)
        
        # Calculer la ligne de total
        total = {
            'libelle': 'TOTAL [NOM DE LA NOTE]',
            'brut_ouverture': df['brut_ouverture'].sum(),
            'augmentations': df['augmentations'].sum(),
            'diminutions': df['diminutions'].sum(),
            'brut_cloture': df['brut_cloture'].sum(),
            'amort_ouverture': df['amort_ouverture'].sum(),
            'dotations': df['dotations'].sum(),
            'reprises': df['reprises'].sum(),
            'amort_cloture': df['amort_cloture'].sum(),
            'vnc_ouverture': df['vnc_ouverture'].sum(),
            'vnc_cloture': df['vnc_cloture'].sum()
        }
        
        # Ajouter le total
        df = pd.concat([df, pd.DataFrame([total])], ignore_index=True)
        
        logger.info(f"✓ Note générée: {len(df)-1} lignes + total")
        return df
    
    def generer_html(self, df: pd.DataFrame) -> str:
        """
        Génère le HTML de la note via HTML_Generator.
        
        Args:
            df: DataFrame de la note
            
        Returns:
            Code HTML
        """
        generator = HTMLGenerator('[TITRE DE LA NOTE]', 'XX')
        return generator.generer_html(df)
    
    def sauvegarder_html(self, html: str, fichier_sortie: str = None):
        """
        Sauvegarde le fichier HTML.
        
        Args:
            html: Code HTML
            fichier_sortie: Chemin du fichier (optionnel)
        """
        if fichier_sortie is None:
            fichier_sortie = os.path.join(
                os.path.dirname(__file__),
                '..',
                'Tests',
                'test_note_XX.html'
            )
        
        with open(fichier_sortie, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"✓ HTML sauvegardé: {fichier_sortie}")


def main():
    """Point d'entrée pour l'exécution standalone."""
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s'
    )
    
    # Chemin vers le fichier de balance
    fichier_balance = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'P000 -BALANCE DEMO N_N-1_N-2.xls'
    )
    
    # Créer le calculateur
    calculateur = CalculateurNoteXX(fichier_balance)
    
    # Charger les balances
    if not calculateur.charger_balances():
        logger.error("Impossible de charger les balances")
        return
    
    # Générer la note
    df_note = calculateur.generer_note()
    
    # Afficher un résumé
    print("\n" + "=" * 80)
    print("NOTE XX - [TITRE DE LA NOTE]")
    print("=" * 80)
    print(df_note.to_string(index=False))
    print("=" * 80)
    
    # Générer et sauvegarder le HTML
    html = calculateur.generer_html(df_note)
    calculateur.sauvegarder_html(html)
    
    print("\n✓ Calcul terminé avec succès")


if __name__ == "__main__":
    main()
