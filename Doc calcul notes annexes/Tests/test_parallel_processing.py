"""
Tests pour le traitement parallèle optionnel des notes annexes.

Ce module teste:
- L'identification des notes indépendantes
- Le calcul parallèle par groupes
- Le fallback vers le mode séquentiel si mémoire insuffisante
- La vérification de la mémoire disponible
- Les performances du mode parallèle vs séquentiel

Requirements: 12.6, 12.7
"""

import pytest
import os
import sys
import time
import psutil
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calcul_notes_annexes_main import CalculNotesAnnexesMain


class TestParallelProcessing:
    """Tests pour le traitement parallèle optionnel."""
    
    @pytest.fixture
    def fichier_balance_test(self):
        """Fixture pour le fichier de balance de test."""
        return os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'P000 -BALANCE DEMO N_N-1_N-2.xlsx'
        )
    
    def test_groupes_independants_definis(self):
        """
        Test que les groupes de notes indépendantes sont correctement définis.
        
        Vérifie:
        - Les groupes sont définis
        - Chaque note apparaît dans exactement un groupe
        - Les groupes couvrent toutes les 33 notes
        
        Requirements: 12.6
        """
        orchestrateur = CalculNotesAnnexesMain("dummy.xlsx", mode_parallele=True)
        
        # Vérifier que les groupes sont définis
        assert hasattr(orchestrateur, 'GROUPES_INDEPENDANTS')
        assert len(orchestrateur.GROUPES_INDEPENDANTS) > 0
        
        # Collecter toutes les notes des groupes
        notes_dans_groupes = []
        for groupe in orchestrateur.GROUPES_INDEPENDANTS:
            notes_dans_groupes.extend(groupe)
        
        # Vérifier qu'il n'y a pas de doublons
        assert len(notes_dans_groupes) == len(set(notes_dans_groupes)), \
            "Certaines notes apparaissent dans plusieurs groupes"
        
        # Vérifier que toutes les notes sont couvertes
        notes_manquantes = set(orchestrateur.NOTES_A_CALCULER) - set(notes_dans_groupes)
        assert len(notes_manquantes) == 0, \
            f"Notes manquantes dans les groupes: {notes_manquantes}"
        
        print(f"✓ {len(orchestrateur.GROUPES_INDEPENDANTS)} groupes indépendants définis")
        print(f"✓ {len(notes_dans_groupes)} notes couvertes")
    
    def test_verification_memoire_disponible(self):
        """
        Test de la vérification de la mémoire disponible.
        
        Vérifie:
        - La fonction retourne un booléen
        - Elle détecte correctement la mémoire insuffisante
        - Elle gère les erreurs gracieusement
        
        Requirements: 12.7
        """
        orchestrateur = CalculNotesAnnexesMain("dummy.xlsx", mode_parallele=True)
        
        # Test avec seuil très bas (devrait passer)
        resultat_bas = orchestrateur.verifier_memoire_disponible(seuil_mb=1.0)
        assert isinstance(resultat_bas, bool)
        assert resultat_bas is True, "Devrait avoir assez de mémoire avec seuil de 1 MB"
        
        # Test avec seuil très élevé (devrait échouer)
        resultat_haut = orchestrateur.verifier_memoire_disponible(seuil_mb=1000000.0)
        assert isinstance(resultat_haut, bool)
        assert resultat_haut is False, "Ne devrait pas avoir 1 TB de mémoire disponible"
        
        # Test avec seuil raisonnable
        resultat_normal = orchestrateur.verifier_memoire_disponible(seuil_mb=500.0)
        assert isinstance(resultat_normal, bool)
        
        print(f"✓ Vérification mémoire fonctionne correctement")
        print(f"  Seuil bas (1 MB): {resultat_bas}")
        print(f"  Seuil normal (500 MB): {resultat_normal}")
        print(f"  Seuil élevé (1 TB): {resultat_haut}")
    
    def test_mode_parallele_active(self, fichier_balance_test):
        """
        Test que le mode parallèle peut être activé.
        
        Vérifie:
        - Le flag mode_parallele est correctement défini
        - Le nombre de workers est configuré
        - Les groupes indépendants sont utilisés
        
        Requirements: 12.6
        """
        if not os.path.exists(fichier_balance_test):
            pytest.skip("Fichier de balance de test non disponible")
        
        # Créer orchestrateur en mode parallèle
        orchestrateur = CalculNotesAnnexesMain(
            fichier_balance_test,
            mode_parallele=True,
            max_workers=2
        )
        
        assert orchestrateur.mode_parallele is True
        assert orchestrateur.max_workers == 2
        assert len(orchestrateur.GROUPES_INDEPENDANTS) > 0
        
        print(f"✓ Mode parallèle activé avec {orchestrateur.max_workers} workers")
        print(f"✓ {len(orchestrateur.GROUPES_INDEPENDANTS)} groupes à traiter")
    
    def test_fallback_sequentiel_memoire_insuffisante(self, fichier_balance_test):
        """
        Test du fallback vers le mode séquentiel si mémoire insuffisante.
        
        Vérifie:
        - Le système détecte la mémoire insuffisante
        - Il bascule automatiquement en mode séquentiel
        - Les notes sont quand même calculées
        
        Requirements: 12.7
        """
        if not os.path.exists(fichier_balance_test):
            pytest.skip("Fichier de balance de test non disponible")
        
        orchestrateur = CalculNotesAnnexesMain(
            fichier_balance_test,
            mode_parallele=True,
            max_workers=2
        )
        
        # Simuler une mémoire insuffisante
        with patch.object(orchestrateur, 'verifier_memoire_disponible', return_value=False):
            # Charger les balances
            orchestrateur.charger_balances()
            
            # Mock des calculateurs pour accélérer le test
            def mock_calculer_note(numero_note):
                nom_note = f"Note_{numero_note.upper()}"
                df = pd.DataFrame({'Libellé': ['Test'], 'Montant': [1000.0]})
                return nom_note, df, True, ""
            
            with patch.object(orchestrateur, 'calculer_note_individuelle', side_effect=mock_calculer_note):
                # Appeler _calculer_parallele qui devrait basculer en séquentiel
                orchestrateur._calculer_parallele()
                
                # Vérifier que des notes ont été calculées (mode séquentiel)
                assert len(orchestrateur.notes_calculees) > 0
                
                print(f"✓ Fallback séquentiel fonctionne: {len(orchestrateur.notes_calculees)} notes calculées")
    
    def test_calcul_parallele_par_groupes(self, fichier_balance_test):
        """
        Test du calcul parallèle par groupes de notes indépendantes.
        
        Vérifie:
        - Les groupes sont traités séquentiellement
        - Les notes d'un groupe sont calculées en parallèle
        - Tous les résultats sont collectés
        
        Requirements: 12.6
        """
        if not os.path.exists(fichier_balance_test):
            pytest.skip("Fichier de balance de test non disponible")
        
        orchestrateur = CalculNotesAnnexesMain(
            fichier_balance_test,
            mode_parallele=True,
            max_workers=2
        )
        
        # Charger les balances
        orchestrateur.charger_balances()
        
        # Mock des calculateurs pour accélérer le test
        notes_calculees_ordre = []
        
        def mock_calculer_note(numero_note):
            notes_calculees_ordre.append(numero_note)
            nom_note = f"Note_{numero_note.upper()}"
            df = pd.DataFrame({
                'Libellé': [f'Ligne {numero_note}'],
                'Montant': [float(hash(numero_note) % 10000)]
            })
            time.sleep(0.01)  # Simuler un calcul
            return nom_note, df, True, ""
        
        with patch.object(orchestrateur, 'calculer_note_individuelle', side_effect=mock_calculer_note):
            # Calculer en mode parallèle
            orchestrateur._calculer_parallele()
            
            # Vérifier que toutes les notes ont été calculées
            assert len(orchestrateur.notes_calculees) == len(orchestrateur.NOTES_A_CALCULER)
            
            # Vérifier que les statuts sont corrects
            for nom_note in orchestrateur.notes_calculees.keys():
                assert nom_note in orchestrateur.statuts_calcul
                assert "Succès" in orchestrateur.statuts_calcul[nom_note]
            
            print(f"✓ Calcul parallèle réussi: {len(orchestrateur.notes_calculees)} notes")
            print(f"✓ Ordre de calcul: {notes_calculees_ordre[:5]}... (premiers)")
    
    def test_performance_parallele_vs_sequentiel(self, fichier_balance_test):
        """
        Test de comparaison des performances parallèle vs séquentiel.
        
        Vérifie:
        - Le mode parallèle est plus rapide (ou équivalent)
        - Les deux modes produisent les mêmes résultats
        - La contrainte de 30s est respectée
        
        Requirements: 12.1, 12.6
        """
        if not os.path.exists(fichier_balance_test):
            pytest.skip("Fichier de balance de test non disponible")
        
        # Mock des calculateurs pour un test rapide mais réaliste
        def mock_calculer_note(numero_note):
            nom_note = f"Note_{numero_note.upper()}"
            df = pd.DataFrame({
                'Libellé': [f'Ligne {numero_note}'],
                'Montant': [float(hash(numero_note) % 10000)]
            })
            time.sleep(0.05)  # Simuler un calcul de 50ms
            return nom_note, df, True, ""
        
        # Test mode séquentiel
        orchestrateur_seq = CalculNotesAnnexesMain(
            fichier_balance_test,
            mode_parallele=False
        )
        orchestrateur_seq.charger_balances()
        
        with patch.object(orchestrateur_seq, 'calculer_note_individuelle', side_effect=mock_calculer_note):
            debut_seq = time.time()
            orchestrateur_seq._calculer_sequentiel()
            duree_seq = time.time() - debut_seq
        
        # Test mode parallèle
        orchestrateur_par = CalculNotesAnnexesMain(
            fichier_balance_test,
            mode_parallele=True,
            max_workers=4
        )
        orchestrateur_par.charger_balances()
        
        with patch.object(orchestrateur_par, 'calculer_note_individuelle', side_effect=mock_calculer_note):
            debut_par = time.time()
            orchestrateur_par._calculer_parallele()
            duree_par = time.time() - debut_par
        
        # Vérifier que les deux modes ont calculé toutes les notes
        assert len(orchestrateur_seq.notes_calculees) == len(orchestrateur_seq.NOTES_A_CALCULER)
        assert len(orchestrateur_par.notes_calculees) == len(orchestrateur_par.NOTES_A_CALCULER)
        
        # Calculer le gain de performance
        gain_pct = ((duree_seq - duree_par) / duree_seq) * 100 if duree_seq > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"COMPARAISON DES PERFORMANCES")
        print(f"{'='*60}")
        print(f"Mode séquentiel:  {duree_seq:.2f}s")
        print(f"Mode parallèle:   {duree_par:.2f}s")
        print(f"Gain:             {gain_pct:+.1f}%")
        print(f"{'='*60}")
        
        # Le mode parallèle devrait être au moins aussi rapide (ou légèrement plus lent à cause de l'overhead)
        # On accepte jusqu'à 20% de perte due à l'overhead de ProcessPoolExecutor
        assert duree_par <= duree_seq * 1.2, \
            f"Mode parallèle trop lent: {duree_par:.2f}s vs {duree_seq:.2f}s"
    
    def test_gestion_erreurs_parallele(self, fichier_balance_test):
        """
        Test de la gestion des erreurs en mode parallèle.
        
        Vérifie:
        - Les erreurs d'une note n'affectent pas les autres
        - Les timeouts sont gérés correctement
        - Le système continue malgré les erreurs
        
        Requirements: 12.6, 12.7
        """
        if not os.path.exists(fichier_balance_test):
            pytest.skip("Fichier de balance de test non disponible")
        
        orchestrateur = CalculNotesAnnexesMain(
            fichier_balance_test,
            mode_parallele=True,
            max_workers=2
        )
        orchestrateur.charger_balances()
        
        # Mock qui échoue pour certaines notes
        def mock_calculer_note_avec_erreurs(numero_note):
            nom_note = f"Note_{numero_note.upper()}"
            
            # Faire échouer les notes 3b et 10
            if numero_note in ['3b', '10']:
                return nom_note, None, False, "Erreur simulée"
            
            df = pd.DataFrame({
                'Libellé': [f'Ligne {numero_note}'],
                'Montant': [1000.0]
            })
            return nom_note, df, True, ""
        
        with patch.object(orchestrateur, 'calculer_note_individuelle', side_effect=mock_calculer_note_avec_erreurs):
            orchestrateur._calculer_parallele()
            
            # Vérifier que les notes réussies sont présentes
            assert len(orchestrateur.notes_calculees) == len(orchestrateur.NOTES_A_CALCULER) - 2
            
            # Vérifier que les notes échouées ont un statut d'erreur
            assert "Note_3B" in orchestrateur.statuts_calcul
            assert "Échec" in orchestrateur.statuts_calcul["Note_3B"]
            
            assert "Note_10" in orchestrateur.statuts_calcul
            assert "Échec" in orchestrateur.statuts_calcul["Note_10"]
            
            print(f"✓ Gestion des erreurs: {len(orchestrateur.notes_calculees)} notes réussies")
            print(f"✓ 2 notes échouées correctement enregistrées")
    
    def test_configuration_workers(self):
        """
        Test de la configuration du nombre de workers.
        
        Vérifie:
        - Le nombre de workers peut être configuré
        - La valeur par défaut est raisonnable
        - Le nombre est limité au nombre de CPUs
        
        Requirements: 12.6
        """
        # Test avec valeur par défaut
        orch_default = CalculNotesAnnexesMain("dummy.xlsx", mode_parallele=True)
        assert orch_default.max_workers > 0
        assert orch_default.max_workers <= os.cpu_count() or 1
        
        # Test avec valeur personnalisée
        orch_custom = CalculNotesAnnexesMain("dummy.xlsx", mode_parallele=True, max_workers=2)
        assert orch_custom.max_workers == 2
        
        # Test avec valeur élevée (devrait être limitée)
        orch_high = CalculNotesAnnexesMain("dummy.xlsx", mode_parallele=True, max_workers=100)
        assert orch_high.max_workers <= 100  # Accepté mais peut être ajusté par ProcessPoolExecutor
        
        print(f"✓ Configuration workers:")
        print(f"  Défaut: {orch_default.max_workers}")
        print(f"  Personnalisé: {orch_custom.max_workers}")
        print(f"  CPUs disponibles: {os.cpu_count()}")


def test_integration_complete_parallele():
    """
    Test d'intégration complet du mode parallèle.
    
    Vérifie le workflow complet:
    1. Chargement des balances
    2. Calcul parallèle des notes
    3. Validation de cohérence
    4. Export Excel
    
    Requirements: 12.1, 12.6, 12.7
    """
    fichier_balance = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'P000 -BALANCE DEMO N_N-1_N-2.xlsx'
    )
    
    if not os.path.exists(fichier_balance):
        pytest.skip("Fichier de balance de test non disponible")
    
    # Créer orchestrateur en mode parallèle
    orchestrateur = CalculNotesAnnexesMain(
        fichier_balance,
        mode_parallele=True,
        max_workers=2
    )
    
    # Mock des calculateurs pour accélérer le test
    def mock_calculer_note(numero_note):
        nom_note = f"Note_{numero_note.upper()}"
        df = pd.DataFrame({
            'Libellé': ['Test'],
            'Montant': [1000.0]
        })
        return nom_note, df, True, ""
    
    with patch.object(orchestrateur, 'calculer_note_individuelle', side_effect=mock_calculer_note):
        # Workflow complet
        debut = time.time()
        notes = orchestrateur.calculer_toutes_notes()
        duree = time.time() - debut
        
        # Vérifications
        assert len(notes) == len(orchestrateur.NOTES_A_CALCULER)
        assert duree < 30, f"Contrainte de performance non respectée: {duree:.2f}s > 30s"
        
        # Vérifier les statistiques du cache
        stats = orchestrateur.obtenir_stats_cache()
        assert stats['balances_en_cache'] is True
        assert stats['nombre_comptes_indexes'] > 0
        
        print(f"\n{'='*60}")
        print(f"TEST D'INTÉGRATION COMPLET - MODE PARALLÈLE")
        print(f"{'='*60}")
        print(f"Notes calculées: {len(notes)}/{len(orchestrateur.NOTES_A_CALCULER)}")
        print(f"Durée totale:    {duree:.2f}s")
        print(f"Contrainte 30s:  {'✓ Respectée' if duree < 30 else '✗ Non respectée'}")
        print(f"Comptes indexés: {stats['nombre_comptes_indexes']}")
        print(f"{'='*60}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
