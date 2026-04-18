#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test des imports pour vérifier que toutes les dépendances sont installées
"""

import sys

def test_imports():
    """Test tous les imports nécessaires"""
    errors = []
    
    # Test FastAPI
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        errors.append(f"✗ FastAPI: {e}")
    
    # Test Pandas
    try:
        import pandas
        print(f"✓ Pandas {pandas.__version__}")
    except ImportError as e:
        errors.append(f"✗ Pandas: {e}")
    
    # Test openpyxl
    try:
        import openpyxl
        print(f"✓ openpyxl {openpyxl.__version__}")
    except ImportError as e:
        errors.append(f"✗ openpyxl: {e}")
    
    # Test PyPDF2
    try:
        import PyPDF2
        print(f"✓ PyPDF2 {PyPDF2.__version__}")
    except ImportError as e:
        errors.append(f"✗ PyPDF2: {e}")
    
    # Test python-docx
    try:
        import docx
        print(f"✓ python-docx")
    except ImportError as e:
        errors.append(f"✗ python-docx: {e}")
    
    # Test beautifulsoup4
    try:
        import bs4
        print(f"✓ beautifulsoup4")
    except ImportError as e:
        errors.append(f"✗ beautifulsoup4: {e}")
    
    # Test numpy
    try:
        import numpy
        print(f"✓ numpy {numpy.__version__}")
    except ImportError as e:
        errors.append(f"✗ numpy: {e}")
    
    if errors:
        print("\nERREURS:")
        for error in errors:
            print(error)
        return 1
    else:
        print("\n✅ Tous les imports sont OK!")
        return 0

if __name__ == "__main__":
    sys.exit(test_imports())
