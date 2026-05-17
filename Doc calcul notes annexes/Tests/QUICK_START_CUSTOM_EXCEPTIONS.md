# Quick Start - Custom Exceptions

## Overview

This guide shows how to use the custom exceptions defined for the Calcul Notes Annexes system.

## Available Exceptions

### 1. BalanceNotFoundException
Raised when required balance worksheets are missing.

```python
from Modules.custom_exceptions import BalanceNotFoundException

raise BalanceNotFoundException(
    "Onglet BALANCE N manquant",
    missing_sheets=["BALANCE N"],
    available_sheets=["BALANCE N-1", "BALANCE N-2"]
)
```

### 2. InvalidBalanceFormatException
Raised when balance format is invalid.

```python
from Modules.custom_exceptions import InvalidBalanceFormatException

raise InvalidBalanceFormatException(
    "Colonnes manquantes dans la balance",
    missing_columns=["Débit", "Crédit"],
    expected_columns=["Numéro", "Intitulé", "Débit", "Crédit", "Solde Débit", "Solde Crédit"],
    sheet_name="BALANCE N"
)
```

### 3. InvalidJSONException
Raised when JSON file is invalid.

```python
from Modules.custom_exceptions import InvalidJSONException

raise InvalidJSONException(
    "Fichier JSON invalide",
    file_path="correspondances_syscohada.json",
    json_error="Expecting property name enclosed in double quotes"
)
```

### 4. FilePermissionException
Raised when file access is denied.

```python
from Modules.custom_exceptions import FilePermissionException

raise FilePermissionException(
    "Accès refusé au fichier",
    file_path="balance.xlsx",
    operation="read"
)
```

### 5. EmptyBalanceException
Raised when balance has no data.

```python
from Modules.custom_exceptions import EmptyBalanceException

raise EmptyBalanceException(
    "Balance vide",
    sheet_name="BALANCE N",
    row_count=0
)
```

### 6. InvalidAccountNumberException
Raised when account number is invalid.

```python
from Modules.custom_exceptions import InvalidAccountNumberException

raise InvalidAccountNumberException(
    "Numéro de compte invalide",
    account_number="ABC123",
    expected_format="Numérique (ex: 211, 2811)",
    line_number=15
)
```

## Usage in Modules

### Balance_Reader Example

```python
from Modules.custom_exceptions import BalanceNotFoundException, InvalidBalanceFormatException

class BalanceReader:
    def charger_balances(self):
        try:
            # Try to load worksheets
            if "BALANCE N" not in self.sheet_names:
                raise BalanceNotFoundException(
                    "Onglet BALANCE N manquant",
                    missing_sheets=["BALANCE N"],
                    available_sheets=self.sheet_names
                )
        except BalanceNotFoundException as e:
            print(f"Erreur: {e}")
            raise
```

### Mapping_Manager Example

```python
from Modules.custom_exceptions import InvalidJSONException
import json

class MappingManager:
    def charger_correspondances(self):
        try:
            with open(self.fichier_json, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidJSONException(
                "Impossible de parser le fichier JSON",
                file_path=self.fichier_json,
                json_error=str(e)
            )
```

## Error Handling Best Practices

### 1. Catch Specific Exceptions

```python
try:
    balance_reader.charger_balances()
except BalanceNotFoundException as e:
    print(f"Balance manquante: {e}")
    # Handle missing balance
except InvalidBalanceFormatException as e:
    print(f"Format invalide: {e}")
    # Handle format error
```

### 2. Log Exceptions

```python
import logging

try:
    balance_reader.charger_balances()
except BalanceNotFoundException as e:
    logging.error(f"Balance non trouvée: {e}")
    logging.error(f"Onglets manquants: {e.missing_sheets}")
    logging.error(f"Onglets disponibles: {e.available_sheets}")
    raise
```

### 3. Provide User-Friendly Messages

```python
try:
    balance_reader.charger_balances()
except BalanceNotFoundException as e:
    user_message = f"Erreur: Le fichier Excel ne contient pas tous les onglets requis.\n"
    user_message += f"Onglets manquants: {', '.join(e.missing_sheets)}\n"
    user_message += f"Veuillez vérifier que votre fichier contient les onglets BALANCE N, N-1 et N-2."
    print(user_message)
```

## Testing Exceptions

Run the test file to verify all exceptions work correctly:

```bash
python -m pytest py_backend/Doc\ calcul\ notes\ annexes/Tests/test_custom_exceptions.py -v
```

## Requirements Validated

This implementation validates:
- **Error Handling Requirements**: All 6 custom exceptions defined
- **Requirement 1.3**: BalanceNotFoundException for missing worksheets
- **Requirement 1.4**: InvalidBalanceFormatException for format errors
- **Requirement 7.6**: InvalidJSONException for JSON parsing errors
- **Requirement 8.5**: Proper error messages with context

## Next Steps

1. Update existing modules to use these exceptions
2. Add exception handling in all calculateur scripts
3. Implement warning system (Task 28.3)
4. Add graceful degradation (Task 28.4)
