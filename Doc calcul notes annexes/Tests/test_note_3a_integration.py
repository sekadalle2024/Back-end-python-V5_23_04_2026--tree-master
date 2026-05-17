#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration Test for Note 3A - Complete Calculation Workflow

This test validates the complete workflow from balance loading to HTML generation
for Note 3A (Immobilisations Incorporelles), ensuring all 11 columns are calculated
correctly and accounting equations are coherent.

Test Coverage:
- Complete workflow execution
- Balance loading from Excel file
- All 11 columns calculation (brut, amortissements, VNC)
- Accounting equation coherence verification
- HTML generation and structure validation
- Trace file generation

Requirements Validated: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7

Author: Système de calcul automatique des notes annexes SYSCOHADA
Date: 25 Avril 2026
"""

import sys
import os
from pathlib import Path
import pytest
import pandas as pd
from bs4 import BeautifulSoup
import json
import tempfile
import shutil

# Add Scripts directory to path
current_dir = Path(__file__).parent
scripts_dir = current_dir.parent / "Scripts"
sys.path.insert(0, str(scripts_dir))

from calculer_note_3a import CalculateurNote3A


class TestNote3AIntegration:
    """
    Integration test suite for Note 3A complete calculation workflow.
    
    This test class validates the end-to-end workflow of calculating Note 3A,
    from loading balance sheets to generating HTML output, ensuring all
    calculations are correct and coherent.
    """
    
    @pytest.fixture
    def fichier_balance(self):
        """
        Fixture providing the path to the demo balance file.
        
        Returns:
            str: Path to the balance file
        """
        # Path to demo balance file (relative to test file)
        # Try both .xlsx and .xls extensions
        balance_path_xlsx = current_dir.parent.parent.parent / "P000 -BALANCE DEMO N_N-1_N-2.xlsx"
        balance_path_xls = current_dir.parent.parent.parent / "P000 -BALANCE DEMO N_N-1_N-2.xls"
        
        if balance_path_xlsx.exists():
            return str(balance_path_xlsx)
        elif balance_path_xls.exists():
            return str(balance_path_xls)
        else:
            pytest.skip(f"Balance file not found: {balance_path_xlsx} or {balance_path_xls}")
        
        return str(balance_path_xlsx)
    
    @pytest.fixture
    def temp_output_dir(self):
        """
        Fixture providing a temporary directory for output files.
        
        Yields:
            str: Path to temporary directory
        """
        temp_dir = tempfile.mkdtemp(prefix="test_note_3a_")
        yield temp_dir
        # Cleanup after test
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def calculateur(self, fichier_balance):
        """
        Fixture providing an initialized CalculateurNote3A instance.
        
        Args:
            fichier_balance: Path to balance file (from fixture)
        
        Returns:
            CalculateurNote3A: Initialized calculator
        """
        return CalculateurNote3A(fichier_balance)
    
    def test_complete_workflow_execution(self, calculateur, temp_output_dir):
        """
        Test the complete workflow from balance loading to HTML generation.
        
        This test validates:
        1. Balance loading succeeds
        2. Note calculation completes without errors
        3. HTML file is generated
        4. Trace file is generated
        5. All expected files exist
        
        Requirements: 5.1, 5.2, 5.5, 5.6, 5.7
        """
        # Define output file paths
        html_file = os.path.join(temp_output_dir, "note_3a_test.html")
        trace_file = os.path.join(temp_output_dir, "note_3a_trace_test.json")
        
        # Execute complete workflow
        calculateur.executer(
            fichier_html=html_file,
            fichier_trace=trace_file
        )
        
        # Verify HTML file was created
        assert os.path.exists(html_file), "HTML file was not created"
        assert os.path.getsize(html_file) > 0, "HTML file is empty"
        
        # Verify trace file was created
        assert os.path.exists(trace_file), "Trace file was not created"
        assert os.path.getsize(trace_file) > 0, "Trace file is empty"
        
        print(f"✓ Complete workflow executed successfully")
        print(f"  - HTML file: {html_file} ({os.path.getsize(html_file)} bytes)")
        print(f"  - Trace file: {trace_file} ({os.path.getsize(trace_file)} bytes)")
    
    def test_all_11_columns_calculated(self, calculateur):
        """
        Test that all 11 columns are calculated correctly for each line.
        
        This test validates that each line of Note 3A contains all expected columns:
        - libelle (label)
        - brut_ouverture, augmentations, diminutions, brut_cloture (4 columns)
        - amort_ouverture, dotations, reprises, amort_cloture (4 columns)
        - vnc_ouverture, vnc_cloture (2 columns)
        
        Total: 11 columns
        
        Requirements: 5.2, 5.3, 5.4
        """
        # Load balances
        assert calculateur.charger_balances(), "Failed to load balances"
        
        # Generate note
        df_note = calculateur.generer_note()
        
        # Expected columns
        expected_columns = [
            'libelle',
            'brut_ouverture', 'augmentations', 'diminutions', 'brut_cloture',
            'amort_ouverture', 'dotations', 'reprises', 'amort_cloture',
            'vnc_ouverture', 'vnc_cloture'
        ]
        
        # Verify all columns exist
        for col in expected_columns:
            assert col in df_note.columns, f"Column '{col}' is missing"
        
        # Verify each line has all columns with numeric values (except libelle)
        for idx, row in df_note.iterrows():
            assert row['libelle'] is not None, f"Line {idx}: libelle is None"
            
            for col in expected_columns[1:]:  # Skip 'libelle'
                assert col in row, f"Line {idx}: column '{col}' is missing"
                assert isinstance(row[col], (int, float)), \
                    f"Line {idx}: column '{col}' is not numeric (type: {type(row[col])})"
                assert not pd.isna(row[col]), f"Line {idx}: column '{col}' is NaN"
        
        print(f"✓ All 11 columns calculated for {len(df_note)} lines")
        print(f"  Columns: {', '.join(expected_columns)}")
    
    def test_accounting_equation_coherence(self, calculateur):
        """
        Test the coherence of accounting equations for all lines.
        
        This test validates that for each line:
        1. Brut equation: Brut_Cloture = Brut_Ouverture + Augmentations - Diminutions
        2. Amort equation: Amort_Cloture = Amort_Ouverture + Dotations - Reprises
        3. VNC equation: VNC = Brut - Amortissements (for both opening and closing)
        
        Requirements: 5.3, 5.4
        """
        # Load balances
        assert calculateur.charger_balances(), "Failed to load balances"
        
        # Generate note
        df_note = calculateur.generer_note()
        
        # Tolerance for floating point comparison
        tolerance = 0.01
        
        # Test each line (excluding total line for detailed checks)
        for idx, row in df_note.iterrows():
            libelle = row['libelle']
            
            # Skip total line for detailed equation checks (it's a sum)
            if 'TOTAL' in libelle.upper():
                continue
            
            # Test 1: Brut equation
            brut_calculated = row['brut_ouverture'] + row['augmentations'] - row['diminutions']
            brut_actual = row['brut_cloture']
            brut_diff = abs(brut_calculated - brut_actual)
            
            assert brut_diff < tolerance, \
                f"{libelle}: Brut equation failed. " \
                f"Expected {brut_calculated:.2f}, got {brut_actual:.2f}, diff {brut_diff:.2f}"
            
            # Test 2: Amortissement equation
            amort_calculated = row['amort_ouverture'] + row['dotations'] - row['reprises']
            amort_actual = row['amort_cloture']
            amort_diff = abs(amort_calculated - amort_actual)
            
            assert amort_diff < tolerance, \
                f"{libelle}: Amort equation failed. " \
                f"Expected {amort_calculated:.2f}, got {amort_actual:.2f}, diff {amort_diff:.2f}"
            
            # Test 3: VNC opening equation
            vnc_ouv_calculated = row['brut_ouverture'] - row['amort_ouverture']
            vnc_ouv_actual = row['vnc_ouverture']
            vnc_ouv_diff = abs(vnc_ouv_calculated - vnc_ouv_actual)
            
            assert vnc_ouv_diff < tolerance, \
                f"{libelle}: VNC opening equation failed. " \
                f"Expected {vnc_ouv_calculated:.2f}, got {vnc_ouv_actual:.2f}, diff {vnc_ouv_diff:.2f}"
            
            # Test 4: VNC closing equation
            vnc_clo_calculated = row['brut_cloture'] - row['amort_cloture']
            vnc_clo_actual = row['vnc_cloture']
            vnc_clo_diff = abs(vnc_clo_calculated - vnc_clo_actual)
            
            assert vnc_clo_diff < tolerance, \
                f"{libelle}: VNC closing equation failed. " \
                f"Expected {vnc_clo_calculated:.2f}, got {vnc_clo_actual:.2f}, diff {vnc_clo_diff:.2f}"
        
        print(f"✓ Accounting equations coherent for all {len(df_note)-1} detail lines")
    
    def test_total_line_calculation(self, calculateur):
        """
        Test that the total line correctly sums all detail lines.
        
        Requirements: 5.3, 5.4
        """
        # Load balances
        assert calculateur.charger_balances(), "Failed to load balances"
        
        # Generate note
        df_note = calculateur.generer_note()
        
        # Get total line (last line)
        total_line = df_note.iloc[-1]
        assert 'TOTAL' in total_line['libelle'].upper(), "Last line is not a total line"
        
        # Get detail lines (all except last)
        detail_lines = df_note.iloc[:-1]
        
        # Tolerance for floating point comparison
        tolerance = 0.01
        
        # Columns to sum
        columns_to_sum = [
            'brut_ouverture', 'augmentations', 'diminutions', 'brut_cloture',
            'amort_ouverture', 'dotations', 'reprises', 'amort_cloture',
            'vnc_ouverture', 'vnc_cloture'
        ]
        
        # Verify each column sum
        for col in columns_to_sum:
            expected_sum = detail_lines[col].sum()
            actual_sum = total_line[col]
            diff = abs(expected_sum - actual_sum)
            
            assert diff < tolerance, \
                f"Total line column '{col}' incorrect. " \
                f"Expected {expected_sum:.2f}, got {actual_sum:.2f}, diff {diff:.2f}"
        
        print(f"✓ Total line correctly sums {len(detail_lines)} detail lines")
    
    def test_html_structure_validation(self, calculateur, temp_output_dir):
        """
        Test that the generated HTML has the correct structure.
        
        This test validates:
        1. HTML is valid and parseable
        2. Contains expected title and headers
        3. Contains a table with correct structure
        4. Table has correct number of rows
        5. Table has correct number of columns
        
        Requirements: 5.6, 5.7
        """
        # Define output file path
        html_file = os.path.join(temp_output_dir, "note_3a_structure_test.html")
        
        # Execute workflow
        calculateur.executer(fichier_html=html_file)
        
        # Read and parse HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Test 1: Title exists
        title = soup.find('title')
        assert title is not None, "HTML title not found"
        assert '3A' in title.text, "Title does not contain note number"
        
        # Test 2: H1 header exists
        h1 = soup.find('h1')
        assert h1 is not None, "H1 header not found"
        assert '3A' in h1.text, "H1 does not contain note number"
        
        # Test 3: H2 header exists
        h2 = soup.find('h2')
        assert h2 is not None, "H2 header not found"
        assert 'IMMOBILISATIONS INCORPORELLES' in h2.text.upper(), \
            "H2 does not contain note title"
        
        # Test 4: Table exists
        table = soup.find('table')
        assert table is not None, "Table not found in HTML"
        
        # Test 5: Table has thead
        thead = table.find('thead')
        assert thead is not None, "Table thead not found"
        
        # Test 6: Table has tbody
        tbody = table.find('tbody')
        assert tbody is not None, "Table tbody not found"
        
        # Test 7: Correct number of data rows (4 detail lines + 1 total = 5)
        rows = tbody.find_all('tr')
        assert len(rows) == 5, f"Expected 5 rows, found {len(rows)}"
        
        # Test 8: Each row has correct number of cells (1 libelle + 10 montants = 11)
        for idx, row in enumerate(rows):
            cells = row.find_all('td')
            assert len(cells) == 11, \
                f"Row {idx}: Expected 11 cells, found {len(cells)}"
        
        print(f"✓ HTML structure validated")
        print(f"  - Title: {title.text}")
        print(f"  - Rows: {len(rows)}")
        print(f"  - Columns per row: 11")
    
    def test_trace_file_content(self, calculateur, temp_output_dir):
        """
        Test that the trace file contains expected information.
        
        This test validates:
        1. Trace file is valid JSON
        2. Contains note metadata
        3. Contains calculation details for each line
        4. Contains source account information
        
        Requirements: 5.7
        """
        # Define output file path
        trace_file = os.path.join(temp_output_dir, "note_3a_trace_content_test.json")
        
        # Execute workflow
        calculateur.executer(fichier_trace=trace_file)
        
        # Read and parse trace file
        with open(trace_file, 'r', encoding='utf-8') as f:
            trace_data = json.load(f)
        
        # Test 1: Note metadata exists
        assert 'note' in trace_data, "Trace file missing 'note' field"
        assert trace_data['note'] == '3A', "Incorrect note number in trace"
        
        assert 'titre' in trace_data, "Trace file missing 'titre' field"
        
        assert 'date_generation' in trace_data, "Trace file missing 'date_generation' field"
        
        assert 'fichier_balance' in trace_data, "Trace file missing 'fichier_balance' field"
        
        assert 'hash_md5_balance' in trace_data, "Trace file missing 'hash_md5_balance' field"
        
        # Test 2: Calculation lines exist
        assert 'lignes' in trace_data, "Trace file missing 'lignes' field"
        lignes = trace_data['lignes']
        assert len(lignes) > 0, "Trace file has no calculation lines"
        
        # Test 3: Each line has required fields
        for idx, ligne in enumerate(lignes):
            assert 'libelle' in ligne, f"Line {idx}: missing 'libelle'"
            assert 'comptes_sources' in ligne, f"Line {idx}: missing 'comptes_sources'"
            
            # Verify comptes_sources is a list
            assert isinstance(ligne['comptes_sources'], list), \
                f"Line {idx}: 'comptes_sources' is not a list"
            
            # Verify each compte_source has required fields
            for compte in ligne['comptes_sources']:
                assert 'compte' in compte, f"Line {idx}: compte missing 'compte' field"
                assert 'type' in compte, f"Line {idx}: compte missing 'type' field"
        
        print(f"✓ Trace file content validated")
        print(f"  - Note: {trace_data['note']}")
        print(f"  - Lines traced: {len(lignes)}")
        print(f"  - Balance file: {trace_data['fichier_balance']}")
    
    def test_vnc_non_negative(self, calculateur):
        """
        Test that all VNC values are non-negative.
        
        VNC (Valeur Nette Comptable) should never be negative as it represents
        the net book value of assets.
        
        Requirements: 5.4
        """
        # Load balances
        assert calculateur.charger_balances(), "Failed to load balances"
        
        # Generate note
        df_note = calculateur.generer_note()
        
        # Check all VNC values
        for idx, row in df_note.iterrows():
            libelle = row['libelle']
            
            vnc_ouv = row['vnc_ouverture']
            vnc_clo = row['vnc_cloture']
            
            assert vnc_ouv >= 0, \
                f"{libelle}: VNC ouverture is negative ({vnc_ouv:.2f})"
            
            assert vnc_clo >= 0, \
                f"{libelle}: VNC clôture is negative ({vnc_clo:.2f})"
        
        print(f"✓ All VNC values are non-negative for {len(df_note)} lines")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
