"""
Test de la mise en cache des balances dans l'orchestrateur.

Ce test vérifie que:
1. Les balances sont chargées une seule fois
2. L'accès aux comptes est en O(1) via dictionnaire
3. Les résultats de calculs répétés sont mis en cache
4. Les statistiques du cache sont correctes

Requirements: 12.2, 12.3, 12.4
"""

import os
import sys
import time
import unittest

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Modules'))

from calcul_notes_annexes_main import CalculNotesAnnexesMain


class TestBalanceCaching(unittest.TestCase):
    """Tests pour la mise en cache des balances."""
    
    @classmethod
    def setUpClass(cls):
        """Configuration initiale pour tous les tests."""
        cls.fichier_balance = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'P000 -BALANCE DEMO N_N-1_N-2.xls'
        )
        
        if not os.path.exists(cls.fichier_balance):
            raise FileNotFoundError(f"Fichier de balance introuvable: {cls.fichier_balance}")
    
    def test_01_chargement_unique_balances(self):
        """
        Test 1: Les balances sont chargées une seule fois.
        
        Vérifie que:
        - Le premier chargement prend du temps
        - Les chargements suivants sont instantanés (cache)
        """
        print("\n" + "=" * 80)
        print("TEST 1: Chargement unique des balances")
        print("=" * 80)
        
        orchestrateur = CalculNotesAnnexesMain(self.fichier_balance)
        
        # Premier chargement
        debut = time.time()
        succes1 = orchestrateur.charger_balances()
        duree1 = time.time() - debut
        
        self.assertTrue(succes1, "Le premier chargement doit réussir")
        self.assertIsNotNone(orchestrateur.balances, "Les balances doivent être en cache")
        print(f"✓ Premier chargement: {duree1:.4f}s")
        
        # Deuxième chargement (doit utiliser le cache)
        debut = time.time()
        succes2 = orchestrateur.charger_balances()
        duree2 = time.time() - debut
        
        self.assertTrue(succes2, "Le deuxième chargement doit réussir")
        self.assertLess(duree2, duree1 / 10, "Le cache doit être beaucoup plus rapide")
        print(f"✓ Deuxième chargement (cache): {duree2:.4f}s")
        print(f"✓ Gain de performance: {duree1/duree2:.1f}x plus rapide")
    
    def test_02_index_dictionnaire_o1(self):
        """
        Test 2: L'accès aux comptes est en O(1) via dictionnaire.
        
        Vérifie que:
        - Les balances sont indexées en dictionnaires
        - L'accès par numéro de compte est instantané
        - Tous les comptes sont indexés
        """
        print("\n" + "=" * 80)
        print("TEST 2: Index dictionnaire pour accès O(1)")
        print("=" * 80)
        
        orchestrateur = CalculNotesAnnexesMain(self.fichier_balance)
        orchestrateur.charger_balances()
        
        # Vérifier que les dictionnaires sont créés
        self.assertIsNotNone(orchestrateur.balances_dict, "Les dictionnaires doivent être créés")
        self.assertEqual(len(orchestrateur.balances_dict), 3, "Doit avoir 3 dictionnaires (N, N-1, N-2)")
        
        # Vérifier que les comptes sont indexés
        for i, balance_dict in enumerate(orchestrateur.balances_dict):
            self.assertIsInstance(balance_dict, dict, f"Balance {i} doit être un dictionnaire")
            self.assertGreater(len(balance_dict), 0, f"Balance {i} doit contenir des comptes")
            print(f"✓ Balance {['N', 'N-1', 'N-2'][i]}: {len(balance_dict)} comptes indexés")
        
        # Tester l'accès O(1) à un compte
        debut = time.time()
        compte = orchestrateur.obtenir_compte_cache('211', exercice=0)
        duree = time.time() - debut
        
        print(f"✓ Accès à un compte: {duree*1000:.4f}ms (O(1))")
        self.assertLess(duree, 0.001, "L'accès doit être quasi-instantané (< 1ms)")
    
    def test_03_acces_comptes_par_racine(self):
        """
        Test 3: L'accès aux comptes par racine utilise l'index.
        
        Vérifie que:
        - La recherche par racine fonctionne
        - Les comptes trouvés sont corrects
        """
        print("\n" + "=" * 80)
        print("TEST 3: Accès aux comptes par racine")
        print("=" * 80)
        
        orchestrateur = CalculNotesAnnexesMain(self.fichier_balance)
        orchestrateur.charger_balances()
        
        # Rechercher tous les comptes commençant par "21" (immobilisations incorporelles)
        debut = time.time()
        comptes_21 = orchestrateur.obtenir_comptes_par_racine_cache('21', exercice=0)
        duree = time.time() - debut
        
        self.assertIsInstance(comptes_21, list, "Doit retourner une liste")
        print(f"✓ Comptes trouvés avec racine '21': {len(comptes_21)}")
        print(f"✓ Temps de recherche: {duree*1000:.4f}ms")
        
        # Vérifier que tous les comptes trouvés commencent bien par "21"
        for compte in comptes_21:
            numero = compte.get('Numéro', '')
            self.assertTrue(numero.startswith('21'), f"Le compte {numero} doit commencer par '21'")
    
    def test_04_cache_resultats(self):
        """
        Test 4: Les résultats de calculs répétés sont mis en cache.
        
        Vérifie que:
        - Les résultats peuvent être mis en cache
        - Les résultats peuvent être récupérés du cache
        - Le cache améliore les performances
        """
        print("\n" + "=" * 80)
        print("TEST 4: Cache des résultats de calculs")
        print("=" * 80)
        
        orchestrateur = CalculNotesAnnexesMain(self.fichier_balance)
        orchestrateur.charger_balances()
        
        # Mettre un résultat en cache
        cle = "test_calcul_211"
        resultat = {"brut_ouverture": 1500000, "vnc_cloture": 1200000}
        
        orchestrateur.mettre_en_cache_resultat(cle, resultat)
        
        # Récupérer le résultat du cache
        resultat_cache = orchestrateur.obtenir_resultat_cache(cle)
        
        self.assertIsNotNone(resultat_cache, "Le résultat doit être en cache")
        self.assertEqual(resultat_cache, resultat, "Le résultat doit être identique")
        print(f"✓ Résultat mis en cache et récupéré avec succès")
        
        # Vérifier qu'un résultat non existant retourne None
        resultat_inexistant = orchestrateur.obtenir_resultat_cache("cle_inexistante")
        self.assertIsNone(resultat_inexistant, "Une clé inexistante doit retourner None")
        print(f"✓ Clé inexistante retourne None comme attendu")
    
    def test_05_statistiques_cache(self):
        """
        Test 5: Les statistiques du cache sont correctes.
        
        Vérifie que:
        - Les statistiques sont disponibles
        - Les valeurs sont cohérentes
        """
        print("\n" + "=" * 80)
        print("TEST 5: Statistiques du cache")
        print("=" * 80)
        
        orchestrateur = CalculNotesAnnexesMain(self.fichier_balance)
        orchestrateur.charger_balances()
        
        # Ajouter quelques résultats en cache
        for i in range(5):
            orchestrateur.mettre_en_cache_resultat(f"test_{i}", {"valeur": i * 1000})
        
        # Obtenir les statistiques
        stats = orchestrateur.obtenir_stats_cache()
        
        self.assertIsInstance(stats, dict, "Les stats doivent être un dictionnaire")
        self.assertTrue(stats['balances_en_cache'], "Les balances doivent être en cache")
        self.assertGreater(stats['nombre_comptes_indexes'], 0, "Des comptes doivent être indexés")
        self.assertEqual(stats['nombre_resultats_caches'], 5, "5 résultats doivent être en cache")
        
        print(f"✓ Balances en cache: {stats['balances_en_cache']}")
        print(f"✓ Comptes indexés: {stats['nombre_comptes_indexes']}")
        print(f"✓ Résultats en cache: {stats['nombre_resultats_caches']}")
        print(f"✓ Taille cache: {stats['taille_cache_resultats_mb']:.4f} MB")
    
    def test_06_performance_avec_cache(self):
        """
        Test 6: Le cache améliore significativement les performances.
        
        Vérifie que:
        - Le chargement avec cache est beaucoup plus rapide
        - L'accès aux comptes est optimisé
        """
        print("\n" + "=" * 80)
        print("TEST 6: Performance avec cache")
        print("=" * 80)
        
        orchestrateur = CalculNotesAnnexesMain(self.fichier_balance)
        
        # Mesurer le temps total avec cache
        debut_total = time.time()
        
        # Premier chargement
        orchestrateur.charger_balances()
        
        # Accès multiples aux comptes (doivent utiliser le cache)
        for _ in range(100):
            orchestrateur.obtenir_compte_cache('211', exercice=0)
            orchestrateur.obtenir_comptes_par_racine_cache('28', exercice=0)
        
        duree_total = time.time() - debut_total
        
        print(f"✓ 100 accès aux comptes avec cache: {duree_total:.4f}s")
        print(f"✓ Temps moyen par accès: {duree_total/100*1000:.4f}ms")
        
        # Vérifier que c'est rapide (< 1s pour 100 accès)
        self.assertLess(duree_total, 1.0, "100 accès doivent prendre moins de 1 seconde")


def run_tests():
    """Exécute tous les tests."""
    print("\n" + "=" * 80)
    print("TESTS DE MISE EN CACHE DES BALANCES")
    print("=" * 80)
    
    # Créer la suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBalanceCaching)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Succès: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ TOUS LES TESTS ONT RÉUSSI")
    else:
        print("\n✗ CERTAINS TESTS ONT ÉCHOUÉ")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
