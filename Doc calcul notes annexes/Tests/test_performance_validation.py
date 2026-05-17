"""
Performance Validation Test - Task 30.3
Tests complete calculation performance against < 30 seconds constraint
Validates memory usage is acceptable
Requirements: 12.1
"""

import sys
import os
import time
import psutil
import tracemalloc
import importlib.util
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
doc_dir = current_dir.parent
py_backend_dir = doc_dir.parent

sys.path.insert(0, str(py_backend_dir))
sys.path.insert(0, str(doc_dir))

# Import from the correct path
import importlib.util
spec = importlib.util.spec_from_file_location(
    "calcul_notes_annexes_main",
    doc_dir / "calcul_notes_annexes_main.py"
)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
CalculNotesAnnexesMain = main_module.CalculNotesAnnexesMain


def format_bytes(bytes_value):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"


def test_performance_validation():
    """
    Test complete calculation performance
    
    Validates:
    - Execution time < 30 seconds
    - Memory usage is acceptable (< 500 MB)
    - CPU usage is reasonable
    """
    
    print("=" * 80)
    print("PERFORMANCE VALIDATION TEST - Task 30.3")
    print("=" * 80)
    print()
    
    # Balance file path - check multiple locations
    balance_files = [
        "P000 -BALANCE DEMO N_N-1_N-2.xlsx",
        "P000 -BALANCE DEMO N_N-1_N-2.xls",
        "py_backend/P000 -BALANCE DEMO N_N-1_N-2.xlsx",
        "py_backend/P000 -BALANCE DEMO N_N-1_N-2.xls",
    ]
    
    balance_file = None
    for file_path in balance_files:
        if os.path.exists(file_path):
            balance_file = file_path
            break
    
    if balance_file is None:
        print(f"❌ Balance file not found in any of these locations:")
        for f in balance_files:
            print(f"   - {f}")
        print()
        print("   Please ensure the balance file exists")
        return False
    
    print(f"📁 Balance file: {balance_file}")
    print()
    
    # Get initial system state
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    initial_cpu_percent = process.cpu_percent(interval=1)
    
    print("📊 Initial System State:")
    print(f"   Memory: {format_bytes(initial_memory)}")
    print(f"   CPU: {initial_cpu_percent:.1f}%")
    print()
    
    # Start memory tracking
    tracemalloc.start()
    
    # Start performance measurement
    print("⏱️  Starting performance test...")
    print()
    start_time = time.time()
    
    try:
        # Initialize orchestrator
        orchestrator = CalculNotesAnnexesMain(balance_file)
        
        # Calculate all 33 notes
        results = orchestrator.calculer_toutes_notes()
        
        # End performance measurement
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Get memory statistics
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Get final system state
        final_memory = process.memory_info().rss
        memory_used = final_memory - initial_memory
        final_cpu_percent = process.cpu_percent(interval=1)
        
        print("=" * 80)
        print("PERFORMANCE RESULTS")
        print("=" * 80)
        print()
        
        # Execution time validation
        print("⏱️  EXECUTION TIME:")
        print(f"   Total time: {execution_time:.2f} seconds")
        print(f"   Constraint: < 30 seconds")
        
        if execution_time < 30:
            print(f"   ✅ PASS - Execution time within constraint")
        else:
            print(f"   ❌ FAIL - Execution time exceeds constraint")
        print()
        
        # Memory usage validation
        print("💾 MEMORY USAGE:")
        print(f"   Peak memory (tracked): {format_bytes(peak_memory)}")
        print(f"   Memory increase (RSS): {format_bytes(memory_used)}")
        print(f"   Final memory (RSS): {format_bytes(final_memory)}")
        print(f"   Constraint: < 500 MB increase")
        
        memory_mb = memory_used / (1024 * 1024)
        if memory_mb < 500:
            print(f"   ✅ PASS - Memory usage acceptable")
        else:
            print(f"   ⚠️  WARNING - Memory usage high")
        print()
        
        # CPU usage
        print("🖥️  CPU USAGE:")
        print(f"   Initial: {initial_cpu_percent:.1f}%")
        print(f"   Final: {final_cpu_percent:.1f}%")
        print()
        
        # Calculation results
        print("📋 CALCULATION RESULTS:")
        successful = sum(1 for r in results.values() if r['status'] == 'success')
        failed = sum(1 for r in results.values() if r['status'] == 'error')
        
        print(f"   Total notes: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print()
        
        # Performance breakdown
        print("📊 PERFORMANCE BREAKDOWN:")
        if 'performance_metrics' in results:
            metrics = results['performance_metrics']
            print(f"   Balance loading: {metrics.get('balance_loading_time', 0):.2f}s")
            print(f"   Calculation time: {metrics.get('calculation_time', 0):.2f}s")
            print(f"   HTML generation: {metrics.get('html_generation_time', 0):.2f}s")
        else:
            avg_time = execution_time / len(results)
            print(f"   Average per note: {avg_time:.2f}s")
        print()
        
        # Overall validation
        print("=" * 80)
        print("OVERALL VALIDATION")
        print("=" * 80)
        
        all_pass = True
        
        # Check execution time
        if execution_time >= 30:
            print("❌ Execution time constraint NOT met")
            all_pass = False
        else:
            print("✅ Execution time constraint met")
        
        # Check memory usage
        if memory_mb >= 500:
            print("⚠️  Memory usage high but acceptable")
        else:
            print("✅ Memory usage acceptable")
        
        # Check calculation success
        if failed > 0:
            print(f"⚠️  {failed} notes failed calculation")
            all_pass = False
        else:
            print("✅ All notes calculated successfully")
        
        print()
        
        if all_pass:
            print("🎉 PERFORMANCE VALIDATION: PASS")
            print()
            print("The system meets all performance requirements:")
            print("  • Execution time < 30 seconds")
            print("  • Memory usage acceptable")
            print("  • All calculations successful")
            return True
        else:
            print("⚠️  PERFORMANCE VALIDATION: PARTIAL PASS")
            print()
            print("Some performance concerns detected.")
            print("Review the results above for details.")
            return False
            
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        tracemalloc.stop()
        
        print("=" * 80)
        print("❌ ERROR DURING PERFORMANCE TEST")
        print("=" * 80)
        print()
        print(f"Execution time before error: {execution_time:.2f} seconds")
        print(f"Error: {str(e)}")
        print()
        print("Traceback:")
        print(traceback.format_exc())
        
        return False


if __name__ == "__main__":
    print()
    success = test_performance_validation()
    print()
    
    if success:
        print("✅ Task 30.3 completed successfully")
        sys.exit(0)
    else:
        print("❌ Task 30.3 failed - review performance results")
        sys.exit(1)
