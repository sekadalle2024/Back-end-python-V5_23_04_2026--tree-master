"""
Performance Optimizations for Calcul Notes Annexes System

This module provides optimized versions of key operations to improve performance.
Implements:
- Balance caching with dictionary lookup (O(1) access)
- Vectorized pandas operations
- Template caching for HTML/Excel generation
- Batch processing optimizations

Requirements: 12.1, 12.2, 12.3, 12.4
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
import numpy as np


class OptimizedBalanceCache:
    """
    Optimized balance cache with dictionary-based O(1) account lookup.
    
    Instead of filtering DataFrames repeatedly, converts balances to dictionaries
    for instant account access.
    """
    
    def __init__(self, balance_n: pd.DataFrame, balance_n1: pd.DataFrame, 
                 balance_n2: Optional[pd.DataFrame] = None):
        """
        Initialize cache with balance DataFrames.
        
        Args:
            balance_n: Balance for exercise N
            balance_n1: Balance for exercise N-1
            balance_n2: Balance for exercise N-2 (optional)
        """
        self.balance_n = balance_n
        self.balance_n1 = balance_n1
        self.balance_n2 = balance_n2
        
        # Create dictionary indexes for O(1) lookup
        self._index_n = self._create_index(balance_n)
        self._index_n1 = self._create_index(balance_n1)
        self._index_n2 = self._create_index(balance_n2) if balance_n2 is not None else {}
        
        # Cache for account root lookups
        self._root_cache: Dict[Tuple[str, str], Dict[str, float]] = {}
    
    def _create_index(self, balance: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Create dictionary index from balance DataFrame.
        
        Args:
            balance: Balance DataFrame
            
        Returns:
            Dictionary mapping account number to account values
        """
        index = {}
        
        for _, row in balance.iterrows():
            numero = str(row['Numéro']).strip()
            index[numero] = {
                'ant_debit': float(row.get('Ant Débit', 0) or 0),
                'ant_credit': float(row.get('Ant Crédit', 0) or 0),
                'mvt_debit': float(row.get('Débit', 0) or 0),
                'mvt_credit': float(row.get('Crédit', 0) or 0),
                'solde_debit': float(row.get('Solde Débit', 0) or 0),
                'solde_credit': float(row.get('Solde Crédit', 0) or 0)
            }
        
        return index
    
    def get_account(self, numero_compte: str, exercice: str = 'N') -> Dict[str, float]:
        """
        Get account values with O(1) lookup.
        
        Args:
            numero_compte: Account number
            exercice: Exercise ('N', 'N-1', or 'N-2')
            
        Returns:
            Dictionary with account values (zeros if not found)
        """
        index = {
            'N': self._index_n,
            'N-1': self._index_n1,
            'N-2': self._index_n2
        }.get(exercice, self._index_n)
        
        return index.get(numero_compte, {
            'ant_debit': 0.0,
            'ant_credit': 0.0,
            'mvt_debit': 0.0,
            'mvt_credit': 0.0,
            'solde_debit': 0.0,
            'solde_credit': 0.0
        })
    
    def get_accounts_by_root(self, racine: str, exercice: str = 'N') -> Dict[str, float]:
        """
        Get aggregated values for all accounts starting with root.
        Uses caching for repeated lookups.
        
        Args:
            racine: Account root (e.g., "211")
            exercice: Exercise ('N', 'N-1', or 'N-2')
            
        Returns:
            Dictionary with aggregated values
        """
        cache_key = (racine, exercice)
        
        if cache_key in self._root_cache:
            return self._root_cache[cache_key]
        
        index = {
            'N': self._index_n,
            'N-1': self._index_n1,
            'N-2': self._index_n2
        }.get(exercice, self._index_n)
        
        # Aggregate all accounts starting with root
        result = {
            'ant_debit': 0.0,
            'ant_credit': 0.0,
            'mvt_debit': 0.0,
            'mvt_credit': 0.0,
            'solde_debit': 0.0,
            'solde_credit': 0.0
        }
        
        for numero, values in index.items():
            if numero.startswith(racine):
                for key in result:
                    result[key] += values[key]
        
        self._root_cache[cache_key] = result
        return result
    
    def get_multiple_roots(self, racines: List[str], exercice: str = 'N') -> Dict[str, float]:
        """
        Get aggregated values for multiple account roots.
        
        Args:
            racines: List of account roots
            exercice: Exercise ('N', 'N-1', or 'N-2')
            
        Returns:
            Dictionary with aggregated values
        """
        result = {
            'ant_debit': 0.0,
            'ant_credit': 0.0,
            'mvt_debit': 0.0,
            'mvt_credit': 0.0,
            'solde_debit': 0.0,
            'solde_credit': 0.0
        }
        
        for racine in racines:
            values = self.get_accounts_by_root(racine, exercice)
            for key in result:
                result[key] += values[key]
        
        return result


class VectorizedCalculations:
    """
    Vectorized calculations using pandas/numpy for better performance.
    
    Replaces row-by-row calculations with vectorized operations.
    """
    
    @staticmethod
    def calculate_movements_vectorized(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate movements for all accounts using vectorized operations.
        
        Args:
            df: DataFrame with balance data
            
        Returns:
            DataFrame with calculated movements
        """
        result = df.copy()
        
        # Vectorized calculations (much faster than row-by-row)
        result['Solde Ouverture'] = result['Ant Débit'] - result['Ant Crédit']
        result['Augmentations'] = result['Débit']
        result['Diminutions'] = result['Crédit']
        result['Solde Clôture'] = result['Solde Débit'] - result['Solde Crédit']
        
        # Vectorized coherence check
        result['Écart'] = (
            result['Solde Clôture'] - 
            (result['Solde Ouverture'] + result['Augmentations'] - result['Diminutions'])
        )
        result['Cohérent'] = np.abs(result['Écart']) < 0.01
        
        return result
    
    @staticmethod
    def calculate_vnc_vectorized(df_brut: pd.DataFrame, 
                                df_amort: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate VNC for all accounts using vectorized operations.
        
        Args:
            df_brut: DataFrame with gross values
            df_amort: DataFrame with depreciation values
            
        Returns:
            DataFrame with VNC calculations
        """
        result = df_brut.copy()
        
        # Merge depreciation data
        result = result.merge(
            df_amort[['Numéro', 'Solde Débit', 'Solde Crédit']],
            on='Numéro',
            how='left',
            suffixes=('_brut', '_amort')
        )
        
        # Fill NaN with 0
        result = result.fillna(0)
        
        # Vectorized VNC calculations
        result['Amort Ouverture'] = result['Solde Crédit_amort'] - result['Solde Débit_amort']
        result['Amort Clôture'] = result['Solde Crédit_amort'] - result['Solde Débit_amort']
        result['VNC Ouverture'] = result['Solde Ouverture'] - result['Amort Ouverture']
        result['VNC Clôture'] = result['Solde Clôture'] - result['Amort Clôture']
        
        # Validate VNC >= 0
        result['VNC Valide'] = (result['VNC Ouverture'] >= 0) & (result['VNC Clôture'] >= 0)
        
        return result
    
    @staticmethod
    def aggregate_by_roots(df: pd.DataFrame, 
                          racines: List[str]) -> pd.DataFrame:
        """
        Aggregate accounts by roots using vectorized operations.
        
        Args:
            df: DataFrame with account data
            racines: List of account roots
            
        Returns:
            DataFrame with aggregated values
        """
        # Create mask for accounts matching any root
        mask = df['Numéro'].str.startswith(tuple(racines), na=False)
        filtered = df[mask]
        
        # Vectorized aggregation
        numeric_cols = filtered.select_dtypes(include=[np.number]).columns
        aggregated = filtered[numeric_cols].sum()
        
        return pd.DataFrame([aggregated])


class TemplateCacheManager:
    """
    Cache manager for HTML and Excel templates.
    
    Caches compiled templates to avoid repeated parsing.
    """
    
    def __init__(self):
        self._html_templates: Dict[str, str] = {}
        self._excel_formats: Dict[str, Dict] = {}
    
    @lru_cache(maxsize=128)
    def get_html_template(self, template_type: str) -> str:
        """
        Get cached HTML template.
        
        Args:
            template_type: Type of template (e.g., 'note_standard', 'note_immobilisations')
            
        Returns:
            HTML template string
        """
        if template_type not in self._html_templates:
            self._html_templates[template_type] = self._load_html_template(template_type)
        
        return self._html_templates[template_type]
    
    def _load_html_template(self, template_type: str) -> str:
        """Load HTML template from file or generate default"""
        # Default template structure
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {css}
            </style>
        </head>
        <body>
            <h1>{titre}</h1>
            <table>
                {content}
            </table>
        </body>
        </html>
        """
    
    @lru_cache(maxsize=128)
    def get_excel_format(self, format_type: str) -> Dict:
        """
        Get cached Excel format configuration.
        
        Args:
            format_type: Type of format (e.g., 'header', 'data', 'total')
            
        Returns:
            Format configuration dictionary
        """
        if format_type not in self._excel_formats:
            self._excel_formats[format_type] = self._load_excel_format(format_type)
        
        return self._excel_formats[format_type]
    
    def _load_excel_format(self, format_type: str) -> Dict:
        """Load Excel format configuration"""
        formats = {
            'header': {
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            },
            'data': {
                'border': 1,
                'num_format': '#,##0'
            },
            'total': {
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1,
                'num_format': '#,##0'
            }
        }
        
        return formats.get(format_type, {})


class BatchProcessor:
    """
    Batch processor for efficient multi-note calculations.
    
    Processes multiple notes in optimized batches.
    """
    
    def __init__(self, balance_cache: OptimizedBalanceCache):
        self.cache = balance_cache
        self.results: Dict[str, pd.DataFrame] = {}
    
    def process_immobilisation_notes(self, notes_config: List[Dict]) -> Dict[str, pd.DataFrame]:
        """
        Process multiple immobilisation notes in batch.
        
        Args:
            notes_config: List of note configurations
            
        Returns:
            Dictionary mapping note number to calculated DataFrame
        """
        results = {}
        
        for config in notes_config:
            note_num = config['numero']
            comptes_brut = config['comptes_brut']
            comptes_amort = config['comptes_amort']
            
            # Batch extract all accounts for this note
            lignes = []
            
            for i, (brut_root, amort_root) in enumerate(zip(comptes_brut, comptes_amort)):
                # Get values from cache (O(1) lookup)
                brut_n = self.cache.get_accounts_by_root(brut_root, 'N')
                brut_n1 = self.cache.get_accounts_by_root(brut_root, 'N-1')
                amort_n = self.cache.get_accounts_by_root(amort_root, 'N')
                amort_n1 = self.cache.get_accounts_by_root(amort_root, 'N-1')
                
                ligne = {
                    'Libellé': config['libelles'][i],
                    'Brut Ouverture': brut_n1['solde_debit'] - brut_n1['solde_credit'],
                    'Augmentations': brut_n['mvt_debit'],
                    'Diminutions': brut_n['mvt_credit'],
                    'Brut Clôture': brut_n['solde_debit'] - brut_n['solde_credit'],
                    'Amort Ouverture': amort_n1['solde_credit'] - amort_n1['solde_debit'],
                    'Dotations': amort_n['mvt_credit'],
                    'Reprises': amort_n['mvt_debit'],
                    'Amort Clôture': amort_n['solde_credit'] - amort_n['solde_debit']
                }
                
                # Calculate VNC
                ligne['VNC Ouverture'] = ligne['Brut Ouverture'] - ligne['Amort Ouverture']
                ligne['VNC Clôture'] = ligne['Brut Clôture'] - ligne['Amort Clôture']
                
                lignes.append(ligne)
            
            results[note_num] = pd.DataFrame(lignes)
        
        return results


# Global cache instance (singleton pattern)
_global_cache: Optional[OptimizedBalanceCache] = None
_template_cache: Optional[TemplateCacheManager] = None


def get_balance_cache() -> Optional[OptimizedBalanceCache]:
    """Get global balance cache instance"""
    return _global_cache


def set_balance_cache(cache: OptimizedBalanceCache) -> None:
    """Set global balance cache instance"""
    global _global_cache
    _global_cache = cache


def get_template_cache() -> TemplateCacheManager:
    """Get global template cache instance"""
    global _template_cache
    if _template_cache is None:
        _template_cache = TemplateCacheManager()
    return _template_cache
