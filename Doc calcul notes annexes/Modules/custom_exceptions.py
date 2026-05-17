"""
Custom Exceptions for Calcul Notes Annexes SYSCOHADA Révisé

This module defines custom exceptions used throughout the system for error handling.
Each exception provides specific error information to help with debugging and user feedback.

Author: Claraverse
Date: 2026-04-28
"""


class BalanceNotFoundException(Exception):
    """
    Exception raised when a required balance worksheet is not found in the Excel file.
    
    This exception is raised by Balance_Reader when one or more of the required
    worksheets (BALANCE N, BALANCE N-1, BALANCE N-2) cannot be found.
    
    Attributes:
        message (str): Explanation of the error
        missing_sheets (list): List of missing worksheet names
        available_sheets (list): List of available worksheet names in the file
    """
    
    def __init__(self, message: str, missing_sheets: list = None, available_sheets: list = None):
        """
        Initialize BalanceNotFoundException.
        
        Args:
            message: Error message describing which balance is missing
            missing_sheets: List of worksheet names that were not found
            available_sheets: List of worksheet names that are available in the file
        """
        self.message = message
        self.missing_sheets = missing_sheets or []
        self.available_sheets = available_sheets or []
        super().__init__(self.message)
    
    def __str__(self):
        """Return detailed error message."""
        error_msg = self.message
        if self.missing_sheets:
            error_msg += f"\nOnglets manquants: {', '.join(self.missing_sheets)}"
        if self.available_sheets:
            error_msg += f"\nOnglets disponibles: {', '.join(self.available_sheets)}"
        return error_msg


class InvalidBalanceFormatException(Exception):
    """
    Exception raised when a balance sheet has an invalid format.
    
    This exception is raised when the balance sheet is missing required columns
    or has an unexpected structure that prevents proper processing.
    
    Attributes:
        message (str): Explanation of the error
        missing_columns (list): List of missing column names
        expected_columns (list): List of expected column names
        sheet_name (str): Name of the problematic worksheet
    """
    
    def __init__(self, message: str, missing_columns: list = None, 
                 expected_columns: list = None, sheet_name: str = None):
        """
        Initialize InvalidBalanceFormatException.
        
        Args:
            message: Error message describing the format issue
            missing_columns: List of column names that are missing
            expected_columns: List of column names that are expected
            sheet_name: Name of the worksheet with invalid format
        """
        self.message = message
        self.missing_columns = missing_columns or []
        self.expected_columns = expected_columns or []
        self.sheet_name = sheet_name
        super().__init__(self.message)
    
    def __str__(self):
        """Return detailed error message."""
        error_msg = self.message
        if self.sheet_name:
            error_msg += f"\nOnglet: {self.sheet_name}"
        if self.missing_columns:
            error_msg += f"\nColonnes manquantes: {', '.join(self.missing_columns)}"
        if self.expected_columns:
            error_msg += f"\nColonnes attendues: {', '.join(self.expected_columns)}"
        return error_msg


class InvalidJSONException(Exception):
    """
    Exception raised when a JSON file is invalid or cannot be parsed.
    
    This exception is raised by Mapping_Manager when the correspondances JSON file
    has invalid syntax or structure.
    
    Attributes:
        message (str): Explanation of the error
        file_path (str): Path to the invalid JSON file
        json_error (str): Original JSON parsing error message
    """
    
    def __init__(self, message: str, file_path: str = None, json_error: str = None):
        """
        Initialize InvalidJSONException.
        
        Args:
            message: Error message describing the JSON issue
            file_path: Path to the JSON file that failed to parse
            json_error: Original error message from JSON parser
        """
        self.message = message
        self.file_path = file_path
        self.json_error = json_error
        super().__init__(self.message)
    
    def __str__(self):
        """Return detailed error message."""
        error_msg = self.message
        if self.file_path:
            error_msg += f"\nFichier: {self.file_path}"
        if self.json_error:
            error_msg += f"\nErreur JSON: {self.json_error}"
        return error_msg


class FilePermissionException(Exception):
    """
    Exception raised when file access is denied due to permission issues.
    
    This exception is raised when the system cannot read or write a file
    due to insufficient permissions or file locks.
    
    Attributes:
        message (str): Explanation of the error
        file_path (str): Path to the file with permission issues
        operation (str): Operation that was attempted (read, write, delete)
    """
    
    def __init__(self, message: str, file_path: str = None, operation: str = None):
        """
        Initialize FilePermissionException.
        
        Args:
            message: Error message describing the permission issue
            file_path: Path to the file that cannot be accessed
            operation: Type of operation that failed (read, write, delete)
        """
        self.message = message
        self.file_path = file_path
        self.operation = operation
        super().__init__(self.message)
    
    def __str__(self):
        """Return detailed error message."""
        error_msg = self.message
        if self.file_path:
            error_msg += f"\nFichier: {self.file_path}"
        if self.operation:
            error_msg += f"\nOpération: {self.operation}"
        return error_msg


class EmptyBalanceException(Exception):
    """
    Exception raised when a balance sheet is empty or has no data rows.
    
    This exception is raised when a balance worksheet is found but contains
    no account data to process.
    
    Attributes:
        message (str): Explanation of the error
        sheet_name (str): Name of the empty worksheet
        row_count (int): Number of rows found (excluding headers)
    """
    
    def __init__(self, message: str, sheet_name: str = None, row_count: int = 0):
        """
        Initialize EmptyBalanceException.
        
        Args:
            message: Error message describing the empty balance issue
            sheet_name: Name of the empty worksheet
            row_count: Number of data rows found
        """
        self.message = message
        self.sheet_name = sheet_name
        self.row_count = row_count
        super().__init__(self.message)
    
    def __str__(self):
        """Return detailed error message."""
        error_msg = self.message
        if self.sheet_name:
            error_msg += f"\nOnglet: {self.sheet_name}"
        error_msg += f"\nNombre de lignes: {self.row_count}"
        return error_msg


class InvalidAccountNumberException(Exception):
    """
    Exception raised when an account number has an invalid format.
    
    This exception is raised when an account number does not conform to
    the SYSCOHADA chart of accounts format or contains invalid characters.
    
    Attributes:
        message (str): Explanation of the error
        account_number (str): The invalid account number
        expected_format (str): Description of expected format
        line_number (int): Line number in the balance where the error occurred
    """
    
    def __init__(self, message: str, account_number: str = None, 
                 expected_format: str = None, line_number: int = None):
        """
        Initialize InvalidAccountNumberException.
        
        Args:
            message: Error message describing the invalid account number
            account_number: The account number that is invalid
            expected_format: Description of the expected format
            line_number: Line number in the balance file
        """
        self.message = message
        self.account_number = account_number
        self.expected_format = expected_format
        self.line_number = line_number
        super().__init__(self.message)
    
    def __str__(self):
        """Return detailed error message."""
        error_msg = self.message
        if self.account_number:
            error_msg += f"\nNuméro de compte: {self.account_number}"
        if self.expected_format:
            error_msg += f"\nFormat attendu: {self.expected_format}"
        if self.line_number:
            error_msg += f"\nLigne: {self.line_number}"
        return error_msg


# Export all exceptions
__all__ = [
    'BalanceNotFoundException',
    'InvalidBalanceFormatException',
    'InvalidJSONException',
    'FilePermissionException',
    'EmptyBalanceException',
    'InvalidAccountNumberException'
]
