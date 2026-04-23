"""
Property-Based Tests for Trace Export Format Conversion

Feature: calcul-notes-annexes-syscohada
Property 24: Trace Export Format Conversion

For any trace file in JSON format, the system must be able to export it to 
CSV format preserving all calculation details for analysis in Excel.

Validates: Requirements 15.6
"""

import pytest
from hypothesis import given, settings, strategies as st, assume
import json
import csv
import os
import hashlib
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Modules.trace_manager import TraceManager


# ============================================================================
# Hypothesis Strategies
# ============================================================================

@st.composite
def st_numero_note(draw):
    """Generate valid note numbers (01-33)"""
    numero = draw(st.integers(min_value=1, max_value=33))
    return f"{numero:02d}"


@st.composite
def st_calcul_data(draw):
    """Generate calculation data for tracing"""
    libelle = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' -éèêàâùûôîç')))
    montant = draw(st.floats(min_value=0, max_value=1e9, allow_nan=False, allow_infinity=False))
    
    # Generate source accounts
    num_comptes = draw(st.integers(min_value=1, max_value=5))
    comptes_sources = []
    
    for _ in range(num_comptes):
        compte = {
            'compte': draw(st.text(min_size=3, max_size=5, alphabet='0123456789')),
            'intitule': draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll'), whitelist_characters=' '))),
            'valeur': draw(st.floats(min_value=0, max_value=1e8, allow_nan=False, allow_infinity=False)),
            'type_valeur': draw(st.sampled_from([
                'brut_ouverture', 'brut_cloture', 'augmentations', 'diminutions',
                'amort_ouverture', 'amort_cloture', 'dotations', 'reprises'
            ]))
        }
        comptes_sources.append(compte)
    
    return {
        'libelle': libelle,
        'montant': montant,
        'comptes_sources': comptes_sources
    }


@st.composite
def st_fichier_balance(draw):
    """Generate balance file name"""
    prefixe = draw(st.sampled_from(['P000', 'P001', 'BALANCE', 'TEST']))
    suffixe = draw(st.sampled_from(['N_N-1_N-2', 'DEMO', 'TEST']))
    return f"{prefixe} - {suffixe}.xlsx"


# ============================================================================
# Property 24: Trace Export Format Conversion
# ============================================================================

@given(
    numero_note=st_numero_note(),
    calculs=st.lists(st_calcul_data(), min_size=1, max_size=10),
    fichier_balance=st_fichier_balance()
)
@settings(max_examples=100, deadline=None)
def test_property_24_trace_export_format_conversion(numero_note, calculs, fichier_balance):
    """
    Property 24: Trace Export Format Conversion
    
    For any trace file in JSON format, the system must be able to export it 
    to CSV format preserving all calculation details for analysis in Excel.
    
    This property verifies that:
    1. JSON trace data can be converted to CSV format
    2. All trace information is preserved during conversion
    3. The CSV format is valid and can be parsed
    4. Data types and structure are maintained
    
    Validates: Requirements 15.6
    """
    # Arrange
    trace_manager = TraceManager(numero_note)
    
    # Generate MD5 hash for the balance file
    hash_md5 = hashlib.md5(fichier_balance.encode()).hexdigest()
    
    # Record metadata
    trace_manager.enregistrer_metadata(
        fichier_balance=fichier_balance,
        hash_md5=hash_md5,
        titre_note=f"Test Note {numero_note}"
    )
    
    # Record all calculations
    for calcul in calculs:
        trace_manager.enregistrer_calcul(
            libelle=calcul['libelle'],
            montant=calcul['montant'],
            comptes_sources=calcul['comptes_sources']
        )
    
    # Act - Save JSON trace and export to CSV
    json_file = f"temp_trace_note_{numero_note}.json"
    csv_file = f"temp_trace_note_{numero_note}.csv"
    
    try:
        # Save JSON trace
        trace_manager.sauvegarder_trace(json_file)
        
        # Export to CSV
        csv_path = trace_manager.exporter_csv(csv_file)
        
        # Assert - Property 1: CSV file must be created
        assert os.path.exists(csv_path), "CSV file must be created"
        
        # Assert - Property 2: CSV file must be valid and parseable
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.reader(f, delimiter=';')
            csv_rows = list(csv_reader)
        
        assert len(csv_rows) > 0, "CSV must contain data"
        
        # Assert - Property 3: CSV must have header row
        header = csv_rows[0]
        expected_headers = [
            'Note', 'Titre', 'Date Génération', 'Fichier Balance', 'Hash MD5',
            'Libellé Ligne', 'Montant', 'Compte Source', 'Intitulé Compte',
            'Valeur Compte', 'Type Valeur'
        ]
        assert header == expected_headers, "CSV must have correct headers"
        
        # Assert - Property 4: CSV must contain all metadata
        # Check that metadata appears in data rows
        data_rows = csv_rows[1:]  # Skip header
        assert len(data_rows) > 0, "CSV must have data rows"
        
        # Verify metadata is present in all rows
        for row in data_rows:
            assert row[0] == numero_note, "Note number must be preserved"
            assert row[1] == f"Test Note {numero_note}", "Title must be preserved"
            assert row[3] == fichier_balance, "Balance file name must be preserved"
            assert row[4] == hash_md5, "MD5 hash must be preserved"
            
            # Date generation should be valid ISO format
            date_gen = row[2]
            if date_gen:  # May be empty for some rows
                try:
                    datetime.fromisoformat(date_gen)
                except ValueError:
                    pytest.fail(f"Date generation must be valid ISO format: {date_gen}")
        
        # Assert - Property 5: All calculations must be present in CSV
        # Count unique libellés in CSV
        csv_libelles = set()
        for row in data_rows:
            libelle = row[5]  # Libellé Ligne column
            if libelle:
                csv_libelles.add(libelle)
        
        # Count unique libellés in original calculations
        original_libelles = set(c['libelle'] for c in calculs)
        
        assert csv_libelles == original_libelles, \
            "All calculation libellés must be present in CSV"
        
        # Assert - Property 6: All source accounts must be preserved
        # For each calculation, verify all source accounts are in CSV
        for calcul in calculs:
            libelle = calcul['libelle']
            comptes_sources = calcul['comptes_sources']
            
            # Find all CSV rows for this libellé
            csv_rows_for_libelle = [row for row in data_rows if row[5] == libelle]
            
            # Should have one row per source account
            assert len(csv_rows_for_libelle) == len(comptes_sources), \
                f"CSV must have one row per source account for {libelle}"
            
            # Verify each source account is present
            csv_comptes = set(row[7] for row in csv_rows_for_libelle)  # Compte Source column
            original_comptes = set(c['compte'] for c in comptes_sources)
            
            assert csv_comptes == original_comptes, \
                f"All source accounts must be preserved for {libelle}"
        
        # Assert - Property 7: Montants must be preserved with correct precision
        for calcul in calculs:
            libelle = calcul['libelle']
            montant_original = calcul['montant']
            
            # Find CSV rows for this libellé
            csv_rows_for_libelle = [row for row in data_rows if row[5] == libelle]
            
            # All rows for the same libellé should have the same montant
            for row in csv_rows_for_libelle:
                montant_csv = float(row[6]) if row[6] else 0.0
                # Allow small floating point differences
                assert abs(montant_csv - montant_original) < 0.01, \
                    f"Montant must be preserved for {libelle}"
        
        # Assert - Property 8: Source account details must be preserved
        for calcul in calculs:
            libelle = calcul['libelle']
            comptes_sources = calcul['comptes_sources']
            
            csv_rows_for_libelle = [row for row in data_rows if row[5] == libelle]
            
            for compte_original in comptes_sources:
                # Find the CSV row for this compte
                csv_row = next(
                    (row for row in csv_rows_for_libelle if row[7] == compte_original['compte']),
                    None
                )
                
                assert csv_row is not None, \
                    f"Source account {compte_original['compte']} must be in CSV"
                
                # Verify intitulé
                assert csv_row[8] == compte_original['intitule'], \
                    "Account intitulé must be preserved"
                
                # Verify valeur (with tolerance for floats)
                valeur_csv = float(csv_row[9]) if csv_row[9] else 0.0
                assert abs(valeur_csv - compte_original['valeur']) < 0.01, \
                    "Account valeur must be preserved"
                
                # Verify type_valeur
                assert csv_row[10] == compte_original['type_valeur'], \
                    "Account type_valeur must be preserved"
        
        # Assert - Property 9: CSV must be Excel-compatible
        # Verify delimiter is semicolon (Excel-friendly for European locales)
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            assert ';' in first_line, "CSV must use semicolon delimiter for Excel compatibility"
        
        # Assert - Property 10: CSV encoding must support special characters
        # Verify UTF-8-BOM encoding for Excel compatibility
        with open(csv_path, 'rb') as f:
            bom = f.read(3)
            # UTF-8 BOM is EF BB BF
            assert bom == b'\xef\xbb\xbf', "CSV must use UTF-8-BOM encoding for Excel"
        
    finally:
        # Cleanup
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(csv_file):
            os.remove(csv_file)


@given(
    numero_note=st_numero_note(),
    fichier_balance=st_fichier_balance()
)
@settings(max_examples=50, deadline=None)
def test_property_24_csv_export_with_no_calculations(numero_note, fichier_balance):
    """
    Property 24 Edge Case: CSV Export with No Calculations
    
    Even if no calculations are recorded, the CSV export must still contain
    valid headers and metadata rows.
    
    Validates: Requirements 15.6
    """
    # Arrange
    trace_manager = TraceManager(numero_note)
    hash_md5 = hashlib.md5(fichier_balance.encode()).hexdigest()
    
    # Only record metadata, no calculations
    trace_manager.enregistrer_metadata(
        fichier_balance=fichier_balance,
        hash_md5=hash_md5,
        titre_note=f"Empty Note {numero_note}"
    )
    
    # Act
    json_file = f"temp_trace_empty_{numero_note}.json"
    csv_file = f"temp_trace_empty_{numero_note}.csv"
    
    try:
        trace_manager.sauvegarder_trace(json_file)
        csv_path = trace_manager.exporter_csv(csv_file)
        
        # Assert
        assert os.path.exists(csv_path), "CSV file must be created even with no calculations"
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.reader(f, delimiter=';')
            csv_rows = list(csv_reader)
        
        # Must have at least header row
        assert len(csv_rows) >= 1, "CSV must have header row"
        
        # Header must be correct
        header = csv_rows[0]
        expected_headers = [
            'Note', 'Titre', 'Date Génération', 'Fichier Balance', 'Hash MD5',
            'Libellé Ligne', 'Montant', 'Compte Source', 'Intitulé Compte',
            'Valeur Compte', 'Type Valeur'
        ]
        assert header == expected_headers, "CSV must have correct headers"
        
        # If there are data rows, they should have metadata
        if len(csv_rows) > 1:
            for row in csv_rows[1:]:
                assert row[0] == numero_note, "Note number must be present"
                assert row[3] == fichier_balance, "Balance file must be present"
    
    finally:
        # Cleanup
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(csv_file):
            os.remove(csv_file)


@given(
    numero_note=st_numero_note(),
    calculs=st.lists(st_calcul_data(), min_size=1, max_size=5),
    fichier_balance=st_fichier_balance()
)
@settings(max_examples=50, deadline=None)
def test_property_24_csv_round_trip_data_integrity(numero_note, calculs, fichier_balance):
    """
    Property 24 Data Integrity: CSV Round-Trip Preservation
    
    After exporting to CSV, all data from the JSON trace must be recoverable
    from the CSV file, demonstrating complete data preservation.
    
    Validates: Requirements 15.6
    """
    # Arrange
    trace_manager = TraceManager(numero_note)
    hash_md5 = hashlib.md5(fichier_balance.encode()).hexdigest()
    
    trace_manager.enregistrer_metadata(
        fichier_balance=fichier_balance,
        hash_md5=hash_md5,
        titre_note=f"Round Trip Test {numero_note}"
    )
    
    for calcul in calculs:
        trace_manager.enregistrer_calcul(
            libelle=calcul['libelle'],
            montant=calcul['montant'],
            comptes_sources=calcul['comptes_sources']
        )
    
    # Act
    json_file = f"temp_trace_roundtrip_{numero_note}.json"
    csv_file = f"temp_trace_roundtrip_{numero_note}.csv"
    
    try:
        # Save JSON and export CSV
        trace_manager.sauvegarder_trace(json_file)
        trace_manager.exporter_csv(csv_file)
        
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Load CSV data
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.DictReader(f, delimiter=';')
            csv_rows = list(csv_reader)
        
        # Assert - Verify all JSON data is present in CSV
        
        # 1. Metadata verification
        if csv_rows:
            first_row = csv_rows[0]
            assert first_row['Note'] == json_data['note']
            assert first_row['Titre'] == json_data['titre']
            assert first_row['Fichier Balance'] == json_data['fichier_balance']
            assert first_row['Hash MD5'] == json_data['hash_md5_balance']
        
        # 2. Calculations verification
        json_lignes = json_data.get('lignes', [])
        
        # Group CSV rows by libellé
        csv_by_libelle = {}
        for row in csv_rows:
            libelle = row['Libellé Ligne']
            if libelle not in csv_by_libelle:
                csv_by_libelle[libelle] = []
            csv_by_libelle[libelle].append(row)
        
        # Verify each JSON ligne is in CSV
        for json_ligne in json_lignes:
            libelle = json_ligne['libelle']
            assert libelle in csv_by_libelle, f"Libellé {libelle} must be in CSV"
            
            csv_rows_for_libelle = csv_by_libelle[libelle]
            json_comptes = json_ligne['comptes_sources']
            
            # Verify montant
            for csv_row in csv_rows_for_libelle:
                montant_csv = float(csv_row['Montant']) if csv_row['Montant'] else 0.0
                assert abs(montant_csv - json_ligne['montant']) < 0.01
            
            # Verify all source accounts
            assert len(csv_rows_for_libelle) == len(json_comptes), \
                f"Number of source accounts must match for {libelle}"
            
            for json_compte in json_comptes:
                # Find matching CSV row
                matching_row = next(
                    (row for row in csv_rows_for_libelle 
                     if row['Compte Source'] == json_compte['compte']),
                    None
                )
                
                assert matching_row is not None, \
                    f"Source account {json_compte['compte']} must be in CSV"
                
                # Verify all fields
                assert matching_row['Intitulé Compte'] == json_compte['intitule']
                
                valeur_csv = float(matching_row['Valeur Compte']) if matching_row['Valeur Compte'] else 0.0
                assert abs(valeur_csv - json_compte['valeur']) < 0.01
                
                assert matching_row['Type Valeur'] == json_compte['type_valeur']
        
    finally:
        # Cleanup
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(csv_file):
            os.remove(csv_file)


@given(
    numero_note=st_numero_note(),
    calculs=st.lists(st_calcul_data(), min_size=1, max_size=3),
    fichier_balance=st_fichier_balance()
)
@settings(max_examples=50, deadline=None)
def test_property_24_csv_structure_for_excel_analysis(numero_note, calculs, fichier_balance):
    """
    Property 24 Excel Analysis: CSV Structure Optimized for Excel
    
    The CSV structure must be optimized for analysis in Excel, with:
    - Denormalized structure (one row per source account)
    - Repeated metadata for easy filtering
    - Semicolon delimiter for European Excel
    - UTF-8-BOM encoding for special characters
    
    Validates: Requirements 15.6
    """
    # Arrange
    trace_manager = TraceManager(numero_note)
    hash_md5 = hashlib.md5(fichier_balance.encode()).hexdigest()
    
    trace_manager.enregistrer_metadata(
        fichier_balance=fichier_balance,
        hash_md5=hash_md5,
        titre_note=f"Excel Analysis Test {numero_note}"
    )
    
    for calcul in calculs:
        trace_manager.enregistrer_calcul(
            libelle=calcul['libelle'],
            montant=calcul['montant'],
            comptes_sources=calcul['comptes_sources']
        )
    
    # Act
    json_file = f"temp_trace_excel_{numero_note}.json"
    csv_file = f"temp_trace_excel_{numero_note}.csv"
    
    try:
        trace_manager.sauvegarder_trace(json_file)
        trace_manager.exporter_csv(csv_file)
        
        # Assert - Property 1: Denormalized structure
        # Each source account should be a separate row
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.DictReader(f, delimiter=';')
            csv_rows = list(csv_reader)
        
        # Count total source accounts
        total_source_accounts = sum(len(c['comptes_sources']) for c in calculs)
        
        # CSV should have one row per source account
        assert len(csv_rows) == total_source_accounts, \
            "CSV must have one row per source account (denormalized)"
        
        # Assert - Property 2: Metadata repeated in each row
        # This allows easy filtering in Excel
        for row in csv_rows:
            assert row['Note'] == numero_note, "Note must be in every row"
            assert row['Titre'] == f"Excel Analysis Test {numero_note}", "Title must be in every row"
            assert row['Fichier Balance'] == fichier_balance, "Balance file must be in every row"
            assert row['Hash MD5'] == hash_md5, "Hash must be in every row"
        
        # Assert - Property 3: Each row has complete information
        # No need to join multiple rows to get complete picture
        for row in csv_rows:
            # Must have libellé
            assert row['Libellé Ligne'], "Each row must have libellé"
            
            # Must have montant
            assert row['Montant'], "Each row must have montant"
            
            # Must have source account details
            assert row['Compte Source'], "Each row must have compte source"
            assert row['Intitulé Compte'], "Each row must have intitulé compte"
            assert row['Valeur Compte'], "Each row must have valeur compte"
            assert row['Type Valeur'], "Each row must have type valeur"
        
        # Assert - Property 4: Semicolon delimiter for European Excel
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            # Count semicolons vs commas
            semicolon_count = content.count(';')
            comma_count = content.count(',')
            
            # Should have many more semicolons than commas
            assert semicolon_count > comma_count, \
                "CSV must use semicolon as primary delimiter"
        
        # Assert - Property 5: UTF-8-BOM for special characters
        with open(csv_file, 'rb') as f:
            bom = f.read(3)
            assert bom == b'\xef\xbb\xbf', \
                "CSV must use UTF-8-BOM for Excel compatibility with special characters"
        
    finally:
        # Cleanup
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(csv_file):
            os.remove(csv_file)


@given(
    numero_note=st_numero_note(),
    calculs=st.lists(st_calcul_data(), min_size=2, max_size=5),
    fichier_balance=st_fichier_balance()
)
@settings(max_examples=50, deadline=None)
def test_property_24_csv_preserves_calculation_order(numero_note, calculs, fichier_balance):
    """
    Property 24 Ordering: CSV Preserves Calculation Order
    
    The CSV export must preserve the order of calculations as they were
    recorded in the JSON trace.
    
    Validates: Requirements 15.6
    """
    # Arrange
    trace_manager = TraceManager(numero_note)
    hash_md5 = hashlib.md5(fichier_balance.encode()).hexdigest()
    
    trace_manager.enregistrer_metadata(
        fichier_balance=fichier_balance,
        hash_md5=hash_md5
    )
    
    # Record calculations in specific order
    for calcul in calculs:
        trace_manager.enregistrer_calcul(
            libelle=calcul['libelle'],
            montant=calcul['montant'],
            comptes_sources=calcul['comptes_sources']
        )
    
    # Act
    json_file = f"temp_trace_order_{numero_note}.json"
    csv_file = f"temp_trace_order_{numero_note}.csv"
    
    try:
        trace_manager.sauvegarder_trace(json_file)
        trace_manager.exporter_csv(csv_file)
        
        # Load CSV
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.DictReader(f, delimiter=';')
            csv_rows = list(csv_reader)
        
        # Assert - Extract unique libellés in order from CSV
        csv_libelles_order = []
        seen_libelles = set()
        for row in csv_rows:
            libelle = row['Libellé Ligne']
            if libelle and libelle not in seen_libelles:
                csv_libelles_order.append(libelle)
                seen_libelles.add(libelle)
        
        # Extract libellés in order from original calculations
        original_libelles_order = [c['libelle'] for c in calculs]
        
        # Order must be preserved
        assert csv_libelles_order == original_libelles_order, \
            "CSV must preserve the order of calculations"
        
    finally:
        # Cleanup
        if os.path.exists(json_file):
            os.remove(json_file)
        if os.path.exists(csv_file):
            os.remove(csv_file)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
