"""
Template de base pour les calculateurs de notes annexes SYSCOHADA Révisé

Ce module fournit une classe de base CalculateurNote qui définit la structure commune
pour tous les 33 calculateurs de notes annexes. Chaque calculateur spécifique hérite
de cette classe et implémente les méthodes spécifiques à sa note.

Architecture:
    - Chargement unique des balances via Balance_Reader
    - Extraction des comptes via Account_Extractor
    - Calculs via Movement_Calculator et VNC_Calculator
    - Génération HTML via HTML_Generator
    - Traçabilité via Trace_Manager

Usage:
    class CalculateurNote3A(CalculateurNote):
        def __init__(self, fichier_balance: str):
            super().__init__(fichier_balance, "3A", "Immobilisations Incorporelles")
            self.mapping_comptes = {
                "Frais de recherche": {"brut": ["211"], "amort": ["2811", "2911"]},
                ...
            }
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
from datetime import datetime

# Ajouter le chemin des modules au PYTHONPATH
current_dir = Path(__file__).parent
modules_dir = current_dir.parent / "Modules"
sys.path.insert(0, str(modules_dir))

from balance_reader import BalanceReader
from account_extractor import AccountExtractor
from movement_calculator import MovementCalculator
from vnc_calculator import VNCCalculator
from html_generator import HTMLGenerator
from trace_manager import TraceManager


class CalculateurNote:
    """
    Classe de base pour tous les calculateurs de notes annexes.
    
    Cette classe fournit la structure commune et les méthodes partagées par tous
    les calculateurs de notes. Chaque calculateur spécifique hérite de cette classe
    et implémente ses propres mappings de comptes et logique de calcul.
    
    Attributes:
        fichier_balance (str): Chemin vers le fichier Excel de balances
        numero_note (str): Numéro de la note (ex: "3A", "3B", "4", etc.)
        titre_note (str): Titre complet de la note
        balance_n (pd.DataFrame): Balance de l'exercice N
        balance_n1 (pd.DataFrame): Balance de l'exercice N-1
        balance_n2 (pd.DataFrame): Balance de l'exercice N-2
        mapping_comptes (Dict): Mapping des lignes de la note aux comptes SYSCOHADA
        trace_manager (TraceManager): Gestionnaire de traçabilité
    """
    
    def __init__(self, fichier_balance: str, numero_note: str, titre_note: str):
        """
        Initialise le calculateur de note.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel de balances
            numero_note: Numéro de la note (ex: "3A")
            titre_note: Titre complet de la note
        """
        self.fichier_balance = fichier_balance
        self.numero_note = numero_note
        self.titre_note = titre_note
        
        # DataFrames des balances (chargés par charger_balances())
        self.balance_n: Optional[pd.DataFrame] = None
        self.balance_n1: Optional[pd.DataFrame] = None
        self.balance_n2: Optional[pd.DataFrame] = None
        
        # Mapping des comptes (défini par les classes filles)
        self.mapping_comptes: Dict[str, Dict[str, List[str]]] = {}
        
        # Gestionnaire de traçabilité
        self.trace_manager = TraceManager(numero_note)
        
        print(f"\n{'='*80}")
        print(f"  CALCULATEUR NOTE {self.numero_note} - {self.titre_note}")
        print(f"{'='*80}\n")
    
    def charger_balances(self) -> bool:
        """
        Charge les balances des 3 exercices (N, N-1, N-2) via Balance_Reader.
        
        Cette méthode utilise le module Balance_Reader pour charger les balances
        depuis le fichier Excel. Elle gère les erreurs de chargement et affiche
        des informations sur les balances chargées.
        
        Returns:
            bool: True si le chargement est réussi, False sinon
            
        Raises:
            BalanceNotFoundException: Si un onglet requis est manquant
            InvalidBalanceFormatException: Si le format est invalide
        """
        try:
            print(f"📂 Chargement des balances depuis: {self.fichier_balance}")
            
            reader = BalanceReader(self.fichier_balance)
            self.balance_n, self.balance_n1, self.balance_n2 = reader.charger_balances()
            
            print(f"✓ Balance N   : {len(self.balance_n)} lignes chargées")
            print(f"✓ Balance N-1 : {len(self.balance_n1)} lignes chargées")
            print(f"✓ Balance N-2 : {len(self.balance_n2)} lignes chargées")
            print()
            
            # Enregistrer les métadonnées dans le trace manager
            import hashlib
            with open(self.fichier_balance, 'rb') as f:
                hash_md5 = hashlib.md5(f.read()).hexdigest()
            self.trace_manager.enregistrer_metadata(self.fichier_balance, hash_md5)
            
            return True
            
        except Exception as e:
            print(f"✗ Erreur lors du chargement des balances: {str(e)}")
            return False
    
    def calculer_ligne_note(
        self,
        libelle: str,
        comptes_brut: List[str],
        comptes_amort: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Calcule une ligne de note annexe avec tous ses montants.
        
        Cette méthode template calcule les 11 colonnes standard d'une ligne de note:
        - Brut: ouverture, augmentations, diminutions, clôture
        - Amortissements: ouverture, dotations, reprises, clôture
        - VNC: ouverture, clôture
        
        Args:
            libelle: Libellé de la ligne
            comptes_brut: Liste des racines de comptes pour les valeurs brutes
            comptes_amort: Liste des racines de comptes pour les amortissements (optionnel)
            
        Returns:
            Dict contenant les 11 colonnes calculées
        """
        # Extracteurs pour chaque exercice
        extractor_n = AccountExtractor(self.balance_n)
        extractor_n1 = AccountExtractor(self.balance_n1)
        
        # Calculateurs
        movement_calc = MovementCalculator()
        vnc_calc = VNCCalculator()
        
        # === CALCUL DES VALEURS BRUTES ===
        
        # Extraire les soldes des comptes bruts
        soldes_brut_n = extractor_n.extraire_comptes_multiples(comptes_brut)
        soldes_brut_n1 = extractor_n1.extraire_comptes_multiples(comptes_brut)
        
        # Calculer les mouvements bruts
        brut_ouverture = movement_calc.calculer_solde_ouverture(
            soldes_brut_n1['solde_debit'],
            soldes_brut_n1['solde_credit']
        )
        
        augmentations = movement_calc.calculer_augmentations(soldes_brut_n['mvt_debit'])
        diminutions = movement_calc.calculer_diminutions(soldes_brut_n['mvt_credit'])
        
        brut_cloture = movement_calc.calculer_solde_cloture(
            soldes_brut_n['solde_debit'],
            soldes_brut_n['solde_credit']
        )
        
        # Vérifier la cohérence
        coherent, ecart = movement_calc.verifier_coherence(
            brut_ouverture, augmentations, diminutions, brut_cloture
        )
        if not coherent:
            print(f"  ⚠ Incohérence détectée pour '{libelle}': écart de {ecart:.2f}")
        
        # === CALCUL DES AMORTISSEMENTS ===
        
        if comptes_amort:
            # Extraire les soldes des comptes d'amortissement
            soldes_amort_n = extractor_n.extraire_comptes_multiples(comptes_amort)
            soldes_amort_n1 = extractor_n1.extraire_comptes_multiples(comptes_amort)
            
            # Calculer les mouvements d'amortissement (signes inversés)
            mouvements_amort = movement_calc.calculer_mouvements_amortissement(
                comptes_amort[0], self.balance_n
            )
            
            amort_ouverture = movement_calc.calculer_solde_ouverture(
                soldes_amort_n1['solde_credit'],  # Inversé pour amortissements
                soldes_amort_n1['solde_debit']
            )
            
            dotations = mouvements_amort['dotations']
            reprises = mouvements_amort['reprises']
            
            amort_cloture = movement_calc.calculer_solde_cloture(
                soldes_amort_n['solde_credit'],  # Inversé pour amortissements
                soldes_amort_n['solde_debit']
            )
        else:
            # Pas d'amortissements pour cette ligne
            amort_ouverture = 0.0
            dotations = 0.0
            reprises = 0.0
            amort_cloture = 0.0
        
        # === CALCUL DES VNC ===
        
        vnc_ouverture = vnc_calc.calculer_vnc_ouverture(brut_ouverture, amort_ouverture)
        vnc_cloture = vnc_calc.calculer_vnc_cloture(brut_cloture, amort_cloture)
        
        # Valider les VNC
        valide_ouv, msg_ouv = vnc_calc.valider_vnc(vnc_ouverture)
        valide_clo, msg_clo = vnc_calc.valider_vnc(vnc_cloture)
        
        if not valide_ouv:
            print(f"  ⚠ {msg_ouv}")
        if not valide_clo:
            print(f"  ⚠ {msg_clo}")
        
        # === TRAÇABILITÉ ===
        
        # Enregistrer le calcul dans le trace manager
        comptes_sources = []
        for compte in comptes_brut:
            solde = extractor_n.extraire_solde_compte(compte)
            comptes_sources.append({
                'compte': compte,
                'type': 'brut',
                'solde_debit_n': solde['solde_debit'],
                'solde_credit_n': solde['solde_credit']
            })
        
        if comptes_amort:
            for compte in comptes_amort:
                solde = extractor_n.extraire_solde_compte(compte)
                comptes_sources.append({
                    'compte': compte,
                    'type': 'amortissement',
                    'solde_debit_n': solde['solde_debit'],
                    'solde_credit_n': solde['solde_credit']
                })
        
        self.trace_manager.enregistrer_calcul(
            libelle=libelle,
            montant=vnc_cloture,
            comptes_sources=comptes_sources
        )
        
        # === RETOUR DES RÉSULTATS ===
        
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
        
        Cette méthode doit être implémentée par chaque classe fille pour définir
        les lignes spécifiques de la note et leur mapping aux comptes.
        
        Returns:
            pd.DataFrame: DataFrame contenant toutes les lignes de la note
            
        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée par la classe fille
        """
        raise NotImplementedError(
            "La méthode generer_note() doit être implémentée par la classe fille"
        )
    
    def generer_html(self, df: pd.DataFrame) -> str:
        """
        Génère le fichier HTML de la note via HTML_Generator.
        
        Args:
            df: DataFrame contenant les données de la note
            
        Returns:
            str: Code HTML complet de la note
        """
        # Configuration des colonnes pour le HTML
        colonnes_config = {
            'groupes': [
                {'titre': 'VALEURS BRUTES', 'colonnes': ['brut_ouverture', 'augmentations', 'diminutions', 'brut_cloture']},
                {'titre': 'AMORTISSEMENTS', 'colonnes': ['amort_ouverture', 'dotations', 'reprises', 'amort_cloture']},
                {'titre': 'VALEURS NETTES', 'colonnes': ['vnc_ouverture', 'vnc_cloture']}
            ],
            'en_tetes': {
                'libelle': 'POSTES',
                'brut_ouverture': 'Début exercice',
                'augmentations': 'Augmentations',
                'diminutions': 'Diminutions',
                'brut_cloture': 'Fin exercice',
                'amort_ouverture': 'Début exercice',
                'dotations': 'Dotations',
                'reprises': 'Reprises',
                'amort_cloture': 'Fin exercice',
                'vnc_ouverture': 'Début exercice',
                'vnc_cloture': 'Fin exercice'
            }
        }
        
        generator = HTMLGenerator(self.titre_note, self.numero_note)
        html = generator.generer_html(df, colonnes_config)
        
        return html
    
    def sauvegarder_html(self, html: str, fichier_sortie: str):
        """
        Sauvegarde le fichier HTML généré.
        
        Args:
            html: Code HTML à sauvegarder
            fichier_sortie: Chemin du fichier de sortie
        """
        try:
            # Créer le dossier de sortie si nécessaire
            output_dir = Path(fichier_sortie).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Écrire le fichier HTML
            with open(fichier_sortie, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✓ Fichier HTML sauvegardé: {fichier_sortie}")
            
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde du HTML: {str(e)}")
    
    def sauvegarder_trace(self, fichier_sortie: str):
        """
        Sauvegarde le fichier de trace JSON.
        
        Args:
            fichier_sortie: Chemin du fichier de trace
        """
        try:
            self.trace_manager.sauvegarder_trace(fichier_sortie)
            print(f"✓ Fichier de trace sauvegardé: {fichier_sortie}")
            
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde de la trace: {str(e)}")
    
    def afficher_resume(self, df: pd.DataFrame):
        """
        Affiche un résumé des calculs dans la console.
        
        Args:
            df: DataFrame contenant les données de la note
        """
        print(f"\n{'─'*80}")
        print(f"  RÉSUMÉ NOTE {self.numero_note}")
        print(f"{'─'*80}\n")
        
        # Ligne de total (dernière ligne)
        total = df.iloc[-1]
        
        print(f"  Nombre de lignes: {len(df) - 1}")  # -1 pour exclure le total
        print(f"  VNC Ouverture:    {total['vnc_ouverture']:>15,.0f}")
        print(f"  VNC Clôture:      {total['vnc_cloture']:>15,.0f}")
        print(f"  Variation:        {total['vnc_cloture'] - total['vnc_ouverture']:>15,.0f}")
        print()
    
    def executer(self, fichier_html: Optional[str] = None, fichier_trace: Optional[str] = None):
        """
        Exécute le calcul complet de la note (méthode principale).
        
        Cette méthode orchestre l'ensemble du processus:
        1. Chargement des balances
        2. Génération de la note
        3. Génération du HTML
        4. Sauvegarde des fichiers
        5. Affichage du résumé
        
        Args:
            fichier_html: Chemin du fichier HTML de sortie (optionnel)
            fichier_trace: Chemin du fichier de trace JSON (optionnel)
        """
        start_time = datetime.now()
        
        # Étape 1: Charger les balances
        if not self.charger_balances():
            print("✗ Échec du chargement des balances. Arrêt du traitement.")
            return
        
        # Étape 2: Générer la note
        print(f"🔢 Calcul de la note {self.numero_note}...")
        df_note = self.generer_note()
        print(f"✓ Note calculée: {len(df_note)} lignes")
        print()
        
        # Étape 3: Générer le HTML
        print(f"📄 Génération du HTML...")
        html = self.generer_html(df_note)
        print(f"✓ HTML généré")
        print()
        
        # Étape 4: Sauvegarder les fichiers
        if fichier_html:
            self.sauvegarder_html(html, fichier_html)
        
        if fichier_trace:
            self.sauvegarder_trace(fichier_trace)
        
        # Étape 5: Afficher le résumé
        self.afficher_resume(df_note)
        
        # Durée totale
        end_time = datetime.now()
        duree = (end_time - start_time).total_seconds()
        
        print(f"{'='*80}")
        print(f"  ✓ NOTE {self.numero_note} CALCULÉE AVEC SUCCÈS EN {duree:.2f}s")
        print(f"{'='*80}\n")


# Point d'entrée pour les tests
if __name__ == "__main__":
    print("Ce module fournit la classe de base CalculateurNote.")
    print("Utilisez les classes filles (CalculateurNote3A, etc.) pour calculer des notes spécifiques.")
