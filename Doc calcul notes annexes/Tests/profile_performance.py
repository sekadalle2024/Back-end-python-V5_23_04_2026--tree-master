"""
Performance Profiling Script for Calcul Notes Annexes System

This script profiles execution time for each module and identifies bottlenecks.
It measures:
- Balance loading time
- Account extraction time
- Movement calculation time
- HTML/Excel generation time
- Total execution time for all 33 notes

Requirements: 12.1 (< 30 seconds total execution time)
"""

import time
import cProfile
import pstats
import io
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "Modules"))

from Modules.balance_reader import BalanceReader
from Modules.account_extractor import AccountExtractor
from Modules.movement_calculator import MovementCalculator
from Modules.vnc_calculator import VNCCalculator
from Modules.html_generator import HTMLGenerator
from Modules.excel_exporter import ExcelExporter


class PerformanceProfiler:
    """Profile performance of the calcul notes annexes system"""
    
    def __init__(self, balance_file: str):
        self.balance_file = balance_file
        self.timings: Dict[str, float] = {}
        self.profiler = cProfile.Profile()
        
    def profile_balance_loading(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Profile balance loading performance"""
        print("\n" + "="*80)
        print("PROFILING: Balance Loading")
        print("="*80)
        
        start_time = time.time()
        
        reader = BalanceReader(self.balance_file)
        balance_n, balance_n1, balance_n2 = reader.charger_balances()
        
        elapsed = time.time() - start_time
        self.timings['balance_loading'] = elapsed
        
        print(f"✓ Balance loading completed in {elapsed:.3f} seconds")
        print(f"  - Balance N: {len(balance_n)} accounts")
        print(f"  - Balance N-1: {len(balance_n1)} accounts")
        print(f"  - Balance N-2: {len(balance_n2)} accounts")
        
        return balance_n, balance_n1, balance_n2
    
    def profile_account_extraction(self, balance: pd.DataFrame) -> None:
        """Profile account extraction performance"""
        print("\n" + "="*80)
        print("PROFILING: Account Extraction")
        print("="*80)
        
        extractor = AccountExtractor(balance)
        
        # Test single account extraction
        start_time = time.time()
        for _ in range(1000):
            extractor.extraire_solde_compte("211")
        single_elapsed = time.time() - start_time
        
        # Test multiple account extraction
        start_time = time.time()
        for _ in range(1000):
            extractor.extraire_comptes_multiples(["211", "212", "213"])
        multiple_elapsed = time.time() - start_time
        
        self.timings['account_extraction_single'] = single_elapsed / 1000
        self.timings['account_extraction_multiple'] = multiple_elapsed / 1000
        
        print(f"✓ Single account extraction: {single_elapsed/1000:.6f} seconds per call")
        print(f"✓ Multiple account extraction: {multiple_elapsed/1000:.6f} seconds per call")
    
    def profile_movement_calculation(self) -> None:
        """Profile movement calculation performance"""
        print("\n" + "="*80)
        print("PROFILING: Movement Calculation")
        print("="*80)
        
        calculator = MovementCalculator()
        
        # Test movement calculations
        start_time = time.time()
        for _ in range(10000):
            calculator.calculer_solde_ouverture(1000000, 0)
            calculator.calculer_augmentations(500000)
            calculator.calculer_diminutions(200000)
            calculator.calculer_solde_cloture(1300000, 0)
            calculator.verifier_coherence(1000000, 500000, 200000, 1300000)
        elapsed = time.time() - start_time
        
        self.timings['movement_calculation'] = elapsed / 10000
        
        print(f"✓ Movement calculation: {elapsed/10000:.6f} seconds per calculation")
    
    def profile_vnc_calculation(self) -> None:
        """Profile VNC calculation performance"""
        print("\n" + "="*80)
        print("PROFILING: VNC Calculation")
        print("="*80)
        
        calculator = VNCCalculator()
        
        # Test VNC calculations
        start_time = time.time()
        for _ in range(10000):
            calculator.calculer_vnc_ouverture(1000000, 300000)
            calculator.calculer_vnc_cloture(1500000, 500000)
            calculator.valider_vnc(700000)
        elapsed = time.time() - start_time
        
        self.timings['vnc_calculation'] = elapsed / 10000
        
        print(f"✓ VNC calculation: {elapsed/10000:.6f} seconds per calculation")
    
    def profile_html_generation(self) -> None:
        """Profile HTML generation performance"""
        print("\n" + "="*80)
        print("PROFILING: HTML Generation")
        print("="*80)
        
        # Create sample data
        data = {
            'Libellé': ['Ligne 1', 'Ligne 2', 'Ligne 3', 'Total'],
            'Brut Ouverture': [1000000, 2000000, 3000000, 6000000],
            'Augmentations': [500000, 300000, 200000, 1000000],
            'Diminutions': [100000, 50000, 75000, 225000],
            'Brut Clôture': [1400000, 2250000, 3125000, 6775000]
        }
        df = pd.DataFrame(data)
        
        colonnes_config = {
            'groupes': [
                {'titre': 'Valeurs Brutes', 'colonnes': ['Brut Ouverture', 'Augmentations', 'Diminutions', 'Brut Clôture']}
            ]
        }
        
        generator = HTMLGenerator("Note Test", "XX")
        
        start_time = time.time()
        for _ in range(100):
            html = generator.generer_html(df, colonnes_config)
        elapsed = time.time() - start_time
        
        self.timings['html_generation'] = elapsed / 100
        
        print(f"✓ HTML generation: {elapsed/100:.6f} seconds per note")
        print(f"  - Estimated time for 33 notes: {(elapsed/100)*33:.3f} seconds")
    
    def profile_excel_export(self) -> None:
        """Profile Excel export performance"""
        print("\n" + "="*80)
        print("PROFILING: Excel Export")
        print("="*80)
        
        # Create sample data
        data = {
            'Libellé': ['Ligne 1', 'Ligne 2', 'Ligne 3', 'Total'],
            'Brut Ouverture': [1000000, 2000000, 3000000, 6000000],
            'Augmentations': [500000, 300000, 200000, 1000000]
        }
        df = pd.DataFrame(data)
        
        colonnes_config = {
            'colonnes': ['Libellé', 'Brut Ouverture', 'Augmentations']
        }
        
        output_file = Path(__file__).parent / "test_profile_export.xlsx"
        exporter = ExcelExporter(str(output_file))
        
        start_time = time.time()
        for i in range(10):
            exporter.exporter_note(df, f"Note_{i}", colonnes_config)
        exporter.sauvegarder()
        elapsed = time.time() - start_time
        
        self.timings['excel_export'] = elapsed / 10
        
        print(f"✓ Excel export: {elapsed/10:.6f} seconds per note")
        print(f"  - Estimated time for 33 notes: {(elapsed/10)*33:.3f} seconds")
        
        # Cleanup
        if output_file.exists():
            output_file.unlink()
    
    def profile_pandas_operations(self, balance: pd.DataFrame) -> None:
        """Profile pandas operations for optimization opportunities"""
        print("\n" + "="*80)
        print("PROFILING: Pandas Operations")
        print("="*80)
        
        # Test filtering operations
        start_time = time.time()
        for _ in range(1000):
            filtered = balance[balance['Numéro'].str.startswith('21', na=False)]
        filter_elapsed = time.time() - start_time
        
        # Test aggregation operations
        start_time = time.time()
        for _ in range(1000):
            total = balance['Solde Débit'].sum()
        agg_elapsed = time.time() - start_time
        
        # Test vectorized operations
        start_time = time.time()
        for _ in range(1000):
            result = balance['Solde Débit'] - balance['Solde Crédit']
        vec_elapsed = time.time() - start_time
        
        self.timings['pandas_filter'] = filter_elapsed / 1000
        self.timings['pandas_aggregation'] = agg_elapsed / 1000
        self.timings['pandas_vectorized'] = vec_elapsed / 1000
        
        print(f"✓ Pandas filtering: {filter_elapsed/1000:.6f} seconds per operation")
        print(f"✓ Pandas aggregation: {agg_elapsed/1000:.6f} seconds per operation")
        print(f"✓ Pandas vectorized ops: {vec_elapsed/1000:.6f} seconds per operation")
    
    def profile_full_note_calculation(self, balance_n: pd.DataFrame, 
                                     balance_n1: pd.DataFrame) -> None:
        """Profile a complete note calculation"""
        print("\n" + "="*80)
        print("PROFILING: Complete Note Calculation (Note 3A)")
        print("="*80)
        
        start_time = time.time()
        
        # Simulate Note 3A calculation
        extractor_n = AccountExtractor(balance_n)
        extractor_n1 = AccountExtractor(balance_n1)
        calculator = MovementCalculator()
        vnc_calc = VNCCalculator()
        
        # Extract accounts for immobilisations incorporelles
        comptes_brut = ["211", "212", "213", "214"]
        comptes_amort = ["2811", "2812", "2813", "2814"]
        
        for compte_brut, compte_amort in zip(comptes_brut, comptes_amort):
            # Extract brut values
            brut_n = extractor_n.extraire_solde_compte(compte_brut)
            brut_n1 = extractor_n1.extraire_solde_compte(compte_brut)
            
            # Calculate movements
            brut_ouverture = calculator.calculer_solde_ouverture(
                brut_n1['solde_debit'], brut_n1['solde_credit']
            )
            augmentations = calculator.calculer_augmentations(brut_n['mvt_debit'])
            diminutions = calculator.calculer_diminutions(brut_n['mvt_credit'])
            brut_cloture = calculator.calculer_solde_cloture(
                brut_n['solde_debit'], brut_n['solde_credit']
            )
            
            # Extract amortissement values
            amort_n = extractor_n.extraire_solde_compte(compte_amort)
            amort_n1 = extractor_n1.extraire_solde_compte(compte_amort)
            
            # Calculate VNC
            vnc_ouverture = vnc_calc.calculer_vnc_ouverture(
                brut_ouverture, 
                calculator.calculer_solde_ouverture(amort_n1['solde_credit'], amort_n1['solde_debit'])
            )
            vnc_cloture = vnc_calc.calculer_vnc_cloture(
                brut_cloture,
                calculator.calculer_solde_cloture(amort_n['solde_credit'], amort_n['solde_debit'])
            )
        
        elapsed = time.time() - start_time
        self.timings['full_note_calculation'] = elapsed
        
        print(f"✓ Complete note calculation: {elapsed:.3f} seconds")
        print(f"  - Estimated time for 33 notes: {elapsed*33:.3f} seconds")
    
    def generate_report(self) -> None:
        """Generate performance report"""
        print("\n" + "="*80)
        print("PERFORMANCE REPORT")
        print("="*80)
        
        total_estimated = 0
        
        print("\n📊 Module Performance:")
        print("-" * 80)
        
        for module, timing in sorted(self.timings.items()):
            print(f"  {module:.<50} {timing:.6f}s")
            
            # Estimate contribution to total time
            if module == 'balance_loading':
                total_estimated += timing
            elif module == 'full_note_calculation':
                total_estimated += timing * 33
            elif module == 'html_generation':
                total_estimated += timing * 33
            elif module == 'excel_export':
                total_estimated += timing * 33
        
        print("-" * 80)
        print(f"  {'ESTIMATED TOTAL TIME':.<50} {total_estimated:.3f}s")
        print("="*80)
        
        # Performance assessment
        print("\n🎯 Performance Assessment:")
        if total_estimated < 30:
            print(f"  ✓ PASS: Total execution time ({total_estimated:.3f}s) is under 30 seconds")
            print(f"  ✓ Performance margin: {30 - total_estimated:.3f}s")
        else:
            print(f"  ✗ FAIL: Total execution time ({total_estimated:.3f}s) exceeds 30 seconds")
            print(f"  ✗ Optimization needed: {total_estimated - 30:.3f}s reduction required")
        
        # Identify bottlenecks
        print("\n🔍 Bottleneck Analysis:")
        bottlenecks = []
        
        if self.timings.get('balance_loading', 0) > 2:
            bottlenecks.append(("Balance Loading", self.timings['balance_loading'], 
                              "Consider caching or optimizing Excel reading"))
        
        if self.timings.get('full_note_calculation', 0) * 33 > 15:
            bottlenecks.append(("Note Calculations", self.timings['full_note_calculation'] * 33,
                              "Optimize account extraction and calculations"))
        
        if self.timings.get('html_generation', 0) * 33 > 5:
            bottlenecks.append(("HTML Generation", self.timings['html_generation'] * 33,
                              "Optimize HTML template rendering"))
        
        if self.timings.get('excel_export', 0) * 33 > 5:
            bottlenecks.append(("Excel Export", self.timings['excel_export'] * 33,
                              "Optimize Excel writing operations"))
        
        if bottlenecks:
            for name, time_val, recommendation in bottlenecks:
                print(f"  ⚠️  {name}: {time_val:.3f}s")
                print(f"      → {recommendation}")
        else:
            print("  ✓ No significant bottlenecks detected")
        
        # Optimization recommendations
        print("\n💡 Optimization Recommendations:")
        print("  1. Balance Caching: Load balances once and reuse across all notes")
        print("  2. Vectorization: Use pandas vectorized operations instead of loops")
        print("  3. Dictionary Lookup: Convert balance to dict for O(1) account access")
        print("  4. Template Caching: Cache HTML/Excel templates")
        print("  5. Parallel Processing: Calculate independent notes in parallel")
        print("  6. Lazy Loading: Generate HTML/Excel only when requested")


def main():
    """Main profiling execution"""
    print("="*80)
    print("CALCUL NOTES ANNEXES - PERFORMANCE PROFILING")
    print("="*80)
    print("\nRequirement 12.1: Total execution time must be < 30 seconds")
    print("="*80)
    
    # Use demo balance file
    balance_file = Path(__file__).parent.parent.parent.parent / "P000 -BALANCE DEMO N_N-1_N-2.xlsx"
    
    if not balance_file.exists():
        print(f"\n❌ ERROR: Balance file not found: {balance_file}")
        print("Please ensure the demo balance file exists.")
        return 1
    
    profiler = PerformanceProfiler(str(balance_file))
    
    try:
        # Profile each component
        balance_n, balance_n1, balance_n2 = profiler.profile_balance_loading()
        profiler.profile_account_extraction(balance_n)
        profiler.profile_movement_calculation()
        profiler.profile_vnc_calculation()
        profiler.profile_html_generation()
        profiler.profile_excel_export()
        profiler.profile_pandas_operations(balance_n)
        profiler.profile_full_note_calculation(balance_n, balance_n1)
        
        # Generate report
        profiler.generate_report()
        
        print("\n" + "="*80)
        print("✓ PROFILING COMPLETE")
        print("="*80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR during profiling: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
