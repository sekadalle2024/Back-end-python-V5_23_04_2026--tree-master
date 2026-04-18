"""
Modules partagés pour le calcul des notes annexes SYSCOHADA révisé.

Ce package contient les modules réutilisables pour:
- Lecture des balances (Balance_Reader)
- Extraction des comptes (Account_Extractor)
- Calcul des mouvements (Movement_Calculator)
- Calcul des VNC (VNC_Calculator)
- Génération HTML (HTML_Generator)
- Export Excel (Excel_Exporter)
- Gestion des correspondances (Mapping_Manager)
- Validation de cohérence (Coherence_Validator)
- Traçabilité (Trace_Manager)
"""

__version__ = "1.0.0"
__author__ = "Claraverse"

from .balance_reader import BalanceReader
from .account_extractor import AccountExtractor
from .movement_calculator import MovementCalculator
from .vnc_calculator import VNCCalculator
from .html_generator import HTMLGenerator
from .excel_exporter import ExcelExporter
from .mapping_manager import MappingManager
from .coherence_validator import CoherenceValidator
from .trace_manager import TraceManager

__all__ = [
    'BalanceReader',
    'AccountExtractor',
    'MovementCalculator',
    'VNCCalculator',
    'HTMLGenerator',
    'ExcelExporter',
    'MappingManager',
    'CoherenceValidator',
    'TraceManager'
]
