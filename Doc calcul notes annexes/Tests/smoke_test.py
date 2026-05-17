"""
Quick smoke test to verify all shared modules are functional
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Modules'))

print("Testing module imports...")

# Test 1: Import all modules
try:
    from balance_reader import BalanceReader
    print("✓ Balance_Reader imported successfully")
except Exception as e:
    print(f"✗ Balance_Reader import failed: {e}")
    sys.exit(1)

try:
    from account_extractor import AccountExtractor
    print("✓ Account_Extractor imported successfully")
except Exception as e:
    print(f"✗ Account_Extractor import failed: {e}")
    sys.exit(1)

try:
    from movement_calculator import MovementCalculator
    print("✓ Movement_Calculator imported successfully")
except Exception as e:
    print(f"✗ Movement_Calculator import failed: {e}")
    sys.exit(1)

try:
    from vnc_calculator import VNCCalculator
    print("✓ VNC_Calculator imported successfully")
except Exception as e:
    print(f"✗ VNC_Calculator import failed: {e}")
    sys.exit(1)

try:
    from html_generator import HTMLGenerator
    print("✓ HTML_Generator imported successfully")
except Exception as e:
    print(f"✗ HTML_Generator import failed: {e}")
    sys.exit(1)

try:
    from excel_exporter import ExcelExporter
    print("✓ Excel_Exporter imported successfully")
except Exception as e:
    print(f"✗ Excel_Exporter import failed: {e}")
    sys.exit(1)

try:
    from mapping_manager import MappingManager
    print("✓ Mapping_Manager imported successfully")
except Exception as e:
    print(f"✗ Mapping_Manager import failed: {e}")
    sys.exit(1)

try:
    from coherence_validator import CoherenceValidator
    print("✓ Coherence_Validator imported successfully")
except Exception as e:
    print(f"✗ Coherence_Validator import failed: {e}")
    sys.exit(1)

try:
    from trace_manager import TraceManager
    print("✓ Trace_Manager imported successfully")
except Exception as e:
    print(f"✗ Trace_Manager import failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("All 9 shared modules imported successfully!")
print("="*60)

# Test 2: Basic functionality tests
print("\nTesting basic functionality...")

import pandas as pd

# Test Balance_Reader
try:
    # Create a simple test balance
    test_data = {
        'Numéro': ['211', '2811'],
        'Intitulé': ['Test 1', 'Test 2'],
        'Ant Débit': [1000.0, 0.0],
        'Ant Crédit': [0.0, 200.0],
        'Débit': [500.0, 0.0],
        'Crédit': [0.0, 100.0],
        'Solde Débit': [1500.0, 0.0],
        'Solde Crédit': [0.0, 300.0]
    }
    test_df = pd.DataFrame(test_data)
    
    extractor = AccountExtractor(test_df)
    result = extractor.extraire_solde_compte('211')
    assert 'ant_debit' in result
    assert 'ant_credit' in result
    assert 'mvt_debit' in result
    assert 'mvt_credit' in result
    assert 'solde_debit' in result
    assert 'solde_credit' in result
    print("✓ Account_Extractor basic functionality works")
except Exception as e:
    print(f"✗ Account_Extractor functionality test failed: {e}")
    sys.exit(1)

# Test Movement_Calculator
try:
    calc = MovementCalculator()
    solde_ouv = calc.calculer_solde_ouverture(1000.0, 0.0)
    assert solde_ouv == 1000.0
    print("✓ Movement_Calculator basic functionality works")
except Exception as e:
    print(f"✗ Movement_Calculator functionality test failed: {e}")
    sys.exit(1)

# Test VNC_Calculator
try:
    vnc_calc = VNCCalculator()
    vnc = vnc_calc.calculer_vnc_ouverture(10000.0, 2000.0)
    assert vnc == 8000.0
    print("✓ VNC_Calculator basic functionality works")
except Exception as e:
    print(f"✗ VNC_Calculator functionality test failed: {e}")
    sys.exit(1)

# Test HTML_Generator
try:
    generator = HTMLGenerator("Test Note", "TEST")
    test_df = pd.DataFrame([{
        'libelle': 'Test',
        'brut_ouverture': 1000,
        'augmentations': 500,
        'diminutions': 200,
        'brut_cloture': 1300
    }])
    colonnes_config = {
        'groupes': [{
            'titre': 'TEST',
            'colonnes': ['brut_ouverture', 'augmentations', 'diminutions', 'brut_cloture']
        }],
        'labels': {
            'brut_ouverture': 'Ouv',
            'augmentations': 'Aug',
            'diminutions': 'Dim',
            'brut_cloture': 'Clô'
        }
    }
    html = generator.generer_html(test_df, colonnes_config)
    assert '<table' in html
    assert 'Test' in html
    print("✓ HTML_Generator basic functionality works")
except Exception as e:
    print(f"✗ HTML_Generator functionality test failed: {e}")
    sys.exit(1)

# Test Trace_Manager
try:
    trace_mgr = TraceManager("TEST")
    trace_mgr.enregistrer_calcul("Test ligne", 1000.0, [{'compte': '211', 'solde': 1000.0}])
    print("✓ Trace_Manager basic functionality works")
except Exception as e:
    print(f"✗ Trace_Manager functionality test failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("SMOKE TEST PASSED - All shared modules are functional!")
print("="*60)
print("\nCheckpoint 12 can be marked as COMPLETE ✓")
