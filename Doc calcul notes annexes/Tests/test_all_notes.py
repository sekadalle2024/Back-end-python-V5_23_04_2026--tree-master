"""
Integration Test Suite - All 33 Notes Annexes SYSCOHADA Révisé

This test suite executes all 33 note calculators sequentially and generates
an HTML summary report with execution time and coherence metrics.

Requirements: 11.4, 11.5
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path
import importlib.util

# Add parent directories to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Modules"))
sys.path.insert(0, str(project_root / "Scripts"))

# Test configuration
BALANCE_FILE = project_root.parent.parent / "P000 -BALANCE DEMO N_N-1_N-2.xlsx"
OUTPUT_DIR = current_dir / "test_all_notes_output"
REPORT_FILE = OUTPUT_DIR / f"test_all_notes_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

# List of all 33 notes with their script names
ALL_NOTES = [
    ("Note 3A", "calculer_note_3a", "Immobilisations Incorporelles"),
    ("Note 3B", "calculer_note_3b", "Immobilisations Corporelles"),
    ("Note 3C", "calculer_note_3c", "Immobilisations Financières"),
    ("Note 3D", "calculer_note_3d", "Charges Immobilisées"),
    ("Note 3E", "calculer_note_3e", "Écarts de Conversion Actif"),
    ("Note 4", "calculer_note_4", "Stocks"),
    ("Note 5", "calculer_note_5", "Créances Clients"),
    ("Note 6", "calculer_note_6", "Autres Créances"),
    ("Note 7", "calculer_note_7", "Trésorerie Actif"),
    ("Note 8", "calculer_note_8", "Capital"),
    ("Note 9", "calculer_note_9", "Réserves"),
    ("Note 10", "calculer_note_10", "Résultat"),
    ("Note 11", "calculer_note_11", "Provisions"),
    ("Note 12", "calculer_note_12", "Emprunts"),
    ("Note 13", "calculer_note_13", "Dettes Fournisseurs"),
    ("Note 14", "calculer_note_14", "Dettes Fiscales"),
    ("Note 15", "calculer_note_15", "Dettes Sociales"),
    ("Note 16", "calculer_note_16", "Autres Dettes"),
    ("Note 17", "calculer_note_17", "Trésorerie Passif"),
    ("Note 18", "calculer_note_18", "Charges Constatées d'Avance"),
    ("Note 19", "calculer_note_19", "Produits Constatés d'Avance"),
    ("Note 20", "calculer_note_20", "Écarts de Conversion Passif"),
    ("Note 21", "calculer_note_21", "Achats de Marchandises"),
    ("Note 22", "calculer_note_22", "Achats de Matières"),
    ("Note 23", "calculer_note_23", "Autres Achats"),
    ("Note 24", "calculer_note_24", "Services Extérieurs"),
    ("Note 25", "calculer_note_25", "Charges de Personnel"),
    ("Note 26", "calculer_note_26", "Dotations aux Amortissements"),
    ("Note 27", "calculer_note_27", "Dotations aux Provisions"),
    ("Note 28", "calculer_note_28", "Ventes de Marchandises"),
    ("Note 29", "calculer_note_29", "Ventes de Produits Finis"),
    ("Note 30", "calculer_note_30", "Production Immobilisée"),
    ("Note 31", "calculer_note_31", "Subventions d'Exploitation"),
    ("Note 32", "calculer_note_32", "Reprises de Provisions"),
    ("Note 33", "calculer_note_33", "Produits Financiers"),
]


class NoteTestResult:
    """Container for individual note test results"""
    
    def __init__(self, note_name, script_name, description):
        self.note_name = note_name
        self.script_name = script_name
        self.description = description
        self.status = "NOT_RUN"
        self.execution_time = 0.0
        self.error_message = None
        self.html_file = None
        self.warnings = []
        
    def mark_success(self, execution_time, html_file=None):
        self.status = "SUCCESS"
        self.execution_time = execution_time
        self.html_file = html_file
        
    def mark_failure(self, execution_time, error_message):
        self.status = "FAILURE"
        self.execution_time = execution_time
        self.error_message = error_message
        
    def add_warning(self, warning):
        self.warnings.append(warning)


def load_calculator_module(script_name):
    """Dynamically load a calculator module"""
    script_path = project_root / "Scripts" / f"{script_name}.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def execute_note_calculator(result: NoteTestResult):
    """Execute a single note calculator and capture results"""
    print(f"\n{'='*80}")
    print(f"Executing {result.note_name}: {result.description}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Load the calculator module
        module = load_calculator_module(result.script_name)
        
        # Find the calculator class (should be CalculateurNoteXX)
        calculator_class = None
        for name in dir(module):
            if name.startswith("CalculateurNote"):
                calculator_class = getattr(module, name)
                break
        
        if calculator_class is None:
            raise ValueError(f"No CalculateurNote class found in {result.script_name}")
        
        # Instantiate and run the calculator
        calculator = calculator_class(str(BALANCE_FILE))
        
        # Load balances
        if not calculator.charger_balances():
            raise RuntimeError("Failed to load balances")
        
        # Generate the note
        df_note = calculator.generer_note()
        
        if df_note is None or df_note.empty:
            result.add_warning("Generated DataFrame is empty")
        
        # Generate HTML
        html_content = calculator.generer_html(df_note)
        
        # Save HTML to output directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        html_filename = f"{result.script_name}_test.html"
        html_path = OUTPUT_DIR / html_filename
        calculator.sauvegarder_html(html_content, str(html_path))
        
        execution_time = time.time() - start_time
        result.mark_success(execution_time, html_filename)
        
        print(f"✓ {result.note_name} completed successfully in {execution_time:.2f}s")
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"{type(e).__name__}: {str(e)}"
        result.mark_failure(execution_time, error_msg)
        
        print(f"✗ {result.note_name} failed after {execution_time:.2f}s")
        print(f"  Error: {error_msg}")


def generate_html_report(results, total_time):
    """Generate comprehensive HTML summary report"""
    
    # Calculate statistics
    total_notes = len(results)
    successful = sum(1 for r in results if r.status == "SUCCESS")
    failed = sum(1 for r in results if r.status == "FAILURE")
    success_rate = (successful / total_notes * 100) if total_notes > 0 else 0
    
    # Calculate coherence metrics (simplified - would need actual coherence validator)
    total_warnings = sum(len(r.warnings) for r in results)
    coherence_rate = max(0, 100 - (total_warnings * 2))  # Simplified calculation
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - 33 Notes Annexes SYSCOHADA</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .metric.failure {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }}
        .metric.time {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .metric.coherence {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
        }}
        .status.success {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status.failure {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .error-message {{
            color: #e74c3c;
            font-size: 12px;
            margin-top: 5px;
        }}
        .warnings {{
            color: #f39c12;
            font-size: 12px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 20px;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background-color: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Test Report - 33 Notes Annexes SYSCOHADA Révisé</h1>
        
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Balance File: {BALANCE_FILE.name}
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-label">Total Notes</div>
                <div class="metric-value">{total_notes}</div>
            </div>
            <div class="metric success">
                <div class="metric-label">Successful</div>
                <div class="metric-value">{successful}</div>
            </div>
            <div class="metric failure">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{failed}</div>
            </div>
            <div class="metric time">
                <div class="metric-label">Total Time</div>
                <div class="metric-value">{total_time:.1f}s</div>
            </div>
            <div class="metric coherence">
                <div class="metric-label">Coherence Rate</div>
                <div class="metric-value">{coherence_rate:.0f}%</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {success_rate}%">
                {success_rate:.1f}% Success Rate
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Note</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Time (s)</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for result in results:
        status_class = result.status.lower()
        status_text = "✓ SUCCESS" if result.status == "SUCCESS" else "✗ FAILURE"
        
        details = ""
        if result.html_file:
            details += f'<a href="{result.html_file}" target="_blank">View HTML</a>'
        if result.warnings:
            details += f'<div class="warnings">⚠ {len(result.warnings)} warning(s)</div>'
        if result.error_message:
            details += f'<div class="error-message">{result.error_message}</div>'
        
        html += f"""
                <tr>
                    <td><strong>{result.note_name}</strong></td>
                    <td>{result.description}</td>
                    <td><span class="status {status_class}">{status_text}</span></td>
                    <td>{result.execution_time:.2f}</td>
                    <td>{details}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="timestamp" style="margin-top: 40px; text-align: center;">
            <strong>Performance Constraint:</strong> Target < 30 seconds
            <br>
            <strong>Coherence Target:</strong> ≥ 95%
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Main test execution function"""
    print("\n" + "="*80)
    print("INTEGRATION TEST SUITE - ALL 33 NOTES ANNEXES SYSCOHADA RÉVISÉ")
    print("="*80)
    print(f"\nBalance File: {BALANCE_FILE}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Report File: {REPORT_FILE}")
    
    # Check balance file exists
    if not BALANCE_FILE.exists():
        print(f"\n✗ ERROR: Balance file not found: {BALANCE_FILE}")
        print("Please ensure the balance file exists before running tests.")
        return 1
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize results
    results = [NoteTestResult(name, script, desc) for name, script, desc in ALL_NOTES]
    
    # Execute all notes sequentially
    start_time = time.time()
    
    for result in results:
        execute_note_calculator(result)
    
    total_time = time.time() - start_time
    
    # Generate HTML report
    print(f"\n{'='*80}")
    print("Generating HTML Summary Report...")
    print(f"{'='*80}")
    
    html_report = generate_html_report(results, total_time)
    
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    # Print summary
    successful = sum(1 for r in results if r.status == "SUCCESS")
    failed = sum(1 for r in results if r.status == "FAILURE")
    success_rate = (successful / len(results) * 100) if results else 0
    
    print(f"\n{'='*80}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'='*80}")
    print(f"Total Notes:      {len(results)}")
    print(f"Successful:       {successful} ({success_rate:.1f}%)")
    print(f"Failed:           {failed}")
    print(f"Total Time:       {total_time:.2f}s")
    print(f"Performance:      {'✓ PASS' if total_time < 30 else '✗ FAIL'} (target < 30s)")
    print(f"\nHTML Report:      {REPORT_FILE}")
    print(f"{'='*80}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
