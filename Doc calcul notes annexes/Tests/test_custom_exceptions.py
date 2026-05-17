"""
Test Suite for Custom Exceptions

This module tests all custom exceptions to ensure they provide proper
error messages and context information.

Author: Claraverse
Date: 2026-04-28
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Modules.custom_exceptions import (
    BalanceNotFoundException,
    InvalidBalanceFormatException,
    InvalidJSONException,
    FilePermissionException,
    EmptyBalanceException,
    InvalidAccountNumberException
)


class TestBalanceNotFoundException:
    """Test BalanceNotFoundException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        with pytest.raises(BalanceNotFoundException) as exc_info:
            raise BalanceNotFoundException("Onglet manquant")
        
        assert "Onglet manquant" in str(exc_info.value)
    
    def test_exception_with_missing_sheets(self):
        """Test exception with missing sheets information."""
        with pytest.raises(BalanceNotFoundException) as exc_info:
            raise BalanceNotFoundException(
                "Onglets requis manquants",
                missing_sheets=["BALANCE N", "BALANCE N-1"],
                available_sheets=["BALANCE N-2", "Autre"]
            )
        
        error_str = str(exc_info.value)
        assert "Onglets requis manquants" in error_str
        assert "BALANCE N" in error_str
        assert "BALANCE N-1" in error_str
        assert "BALANCE N-2" in error_str
    
    def test_exception_attributes(self):
        """Test exception attributes are accessible."""
        exc = BalanceNotFoundException(
            "Test",
            missing_sheets=["N"],
            available_sheets=["N-1"]
        )
        
        assert exc.missing_sheets == ["N"]
        assert exc.available_sheets == ["N-1"]
        assert exc.message == "Test"


class TestInvalidBalanceFormatException:
    """Test InvalidBalanceFormatException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        with pytest.raises(InvalidBalanceFormatException) as exc_info:
            raise InvalidBalanceFormatException("Format invalide")
        
        assert "Format invalide" in str(exc_info.value)
    
    def test_exception_with_columns(self):
        """Test exception with column information."""
        with pytest.raises(InvalidBalanceFormatException) as exc_info:
            raise InvalidBalanceFormatException(
                "Colonnes manquantes",
                missing_columns=["Débit", "Crédit"],
                expected_columns=["Numéro", "Débit", "Crédit"],
                sheet_name="BALANCE N"
            )
        
        error_str = str(exc_info.value)
        assert "Colonnes manquantes" in error_str
        assert "Débit" in error_str
        assert "Crédit" in error_str
        assert "BALANCE N" in error_str
    
    def test_exception_attributes(self):
        """Test exception attributes are accessible."""
        exc = InvalidBalanceFormatException(
            "Test",
            missing_columns=["Col1"],
            expected_columns=["Col1", "Col2"],
            sheet_name="Sheet1"
        )
        
        assert exc.missing_columns == ["Col1"]
        assert exc.expected_columns == ["Col1", "Col2"]
        assert exc.sheet_name == "Sheet1"


class TestInvalidJSONException:
    """Test InvalidJSONException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        with pytest.raises(InvalidJSONException) as exc_info:
            raise InvalidJSONException("JSON invalide")
        
        assert "JSON invalide" in str(exc_info.value)
    
    def test_exception_with_details(self):
        """Test exception with file and error details."""
        with pytest.raises(InvalidJSONException) as exc_info:
            raise InvalidJSONException(
                "Erreur de parsing",
                file_path="test.json",
                json_error="Expecting property name"
            )
        
        error_str = str(exc_info.value)
        assert "Erreur de parsing" in error_str
        assert "test.json" in error_str
        assert "Expecting property name" in error_str
    
    def test_exception_attributes(self):
        """Test exception attributes are accessible."""
        exc = InvalidJSONException(
            "Test",
            file_path="file.json",
            json_error="Error"
        )
        
        assert exc.file_path == "file.json"
        assert exc.json_error == "Error"


class TestFilePermissionException:
    """Test FilePermissionException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        with pytest.raises(FilePermissionException) as exc_info:
            raise FilePermissionException("Accès refusé")
        
        assert "Accès refusé" in str(exc_info.value)
    
    def test_exception_with_details(self):
        """Test exception with file and operation details."""
        with pytest.raises(FilePermissionException) as exc_info:
            raise FilePermissionException(
                "Permission denied",
                file_path="balance.xlsx",
                operation="read"
            )
        
        error_str = str(exc_info.value)
        assert "Permission denied" in error_str
        assert "balance.xlsx" in error_str
        assert "read" in error_str
    
    def test_exception_attributes(self):
        """Test exception attributes are accessible."""
        exc = FilePermissionException(
            "Test",
            file_path="file.xlsx",
            operation="write"
        )
        
        assert exc.file_path == "file.xlsx"
        assert exc.operation == "write"


class TestEmptyBalanceException:
    """Test EmptyBalanceException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        with pytest.raises(EmptyBalanceException) as exc_info:
            raise EmptyBalanceException("Balance vide")
        
        assert "Balance vide" in str(exc_info.value)
    
    def test_exception_with_details(self):
        """Test exception with sheet and row count details."""
        with pytest.raises(EmptyBalanceException) as exc_info:
            raise EmptyBalanceException(
                "Aucune donnée",
                sheet_name="BALANCE N",
                row_count=0
            )
        
        error_str = str(exc_info.value)
        assert "Aucune donnée" in error_str
        assert "BALANCE N" in error_str
        assert "0" in error_str
    
    def test_exception_attributes(self):
        """Test exception attributes are accessible."""
        exc = EmptyBalanceException(
            "Test",
            sheet_name="Sheet1",
            row_count=5
        )
        
        assert exc.sheet_name == "Sheet1"
        assert exc.row_count == 5


class TestInvalidAccountNumberException:
    """Test InvalidAccountNumberException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        with pytest.raises(InvalidAccountNumberException) as exc_info:
            raise InvalidAccountNumberException("Compte invalide")
        
        assert "Compte invalide" in str(exc_info.value)
    
    def test_exception_with_details(self):
        """Test exception with account details."""
        with pytest.raises(InvalidAccountNumberException) as exc_info:
            raise InvalidAccountNumberException(
                "Format incorrect",
                account_number="ABC123",
                expected_format="Numérique",
                line_number=42
            )
        
        error_str = str(exc_info.value)
        assert "Format incorrect" in error_str
        assert "ABC123" in error_str
        assert "Numérique" in error_str
        assert "42" in error_str
    
    def test_exception_attributes(self):
        """Test exception attributes are accessible."""
        exc = InvalidAccountNumberException(
            "Test",
            account_number="123",
            expected_format="Format",
            line_number=10
        )
        
        assert exc.account_number == "123"
        assert exc.expected_format == "Format"
        assert exc.line_number == 10


class TestExceptionInheritance:
    """Test that all exceptions inherit from Exception."""
    
    def test_all_inherit_from_exception(self):
        """Test all custom exceptions inherit from Exception."""
        exceptions = [
            BalanceNotFoundException,
            InvalidBalanceFormatException,
            InvalidJSONException,
            FilePermissionException,
            EmptyBalanceException,
            InvalidAccountNumberException
        ]
        
        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)


class TestExceptionUsageScenarios:
    """Test realistic usage scenarios."""
    
    def test_balance_reader_scenario(self):
        """Test exception in balance reader context."""
        def load_balance(sheet_names):
            required = ["BALANCE N", "BALANCE N-1", "BALANCE N-2"]
            missing = [s for s in required if s not in sheet_names]
            
            if missing:
                raise BalanceNotFoundException(
                    "Onglets requis manquants",
                    missing_sheets=missing,
                    available_sheets=sheet_names
                )
        
        with pytest.raises(BalanceNotFoundException) as exc_info:
            load_balance(["BALANCE N", "Autre"])
        
        exc = exc_info.value
        assert len(exc.missing_sheets) == 2
        assert "BALANCE N-1" in exc.missing_sheets
        assert "BALANCE N-2" in exc.missing_sheets
    
    def test_format_validation_scenario(self):
        """Test exception in format validation context."""
        def validate_columns(columns):
            required = ["Numéro", "Intitulé", "Débit", "Crédit"]
            missing = [c for c in required if c not in columns]
            
            if missing:
                raise InvalidBalanceFormatException(
                    "Colonnes requises manquantes",
                    missing_columns=missing,
                    expected_columns=required,
                    sheet_name="BALANCE N"
                )
        
        with pytest.raises(InvalidBalanceFormatException) as exc_info:
            validate_columns(["Numéro", "Intitulé"])
        
        exc = exc_info.value
        assert "Débit" in exc.missing_columns
        assert "Crédit" in exc.missing_columns


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
