# -*- coding: utf-8 -*-
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, '.')

# Import direct sans FastAPI
exec(open('tableau_flux_tresorerie.py').read())
exec(open('annexes_liasse.py').read())

print('Test export complet - En cours de développement')
print('Utilisez: python test_etats_financiers_standalone.py')
