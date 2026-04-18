import sys
sys.path.append('.')
from export_liasse import remplir_liasse_officielle
import datetime

results = {
    'bilan_actif': [
        {'ref': 'AD', 'brut': 1000, 'amort_deprec': 200, 'montant_n': 800, 'montant_n1': 700},
        {'ref': 'AE', 'brut': 5000, 'amort_deprec': 1000, 'montant_n': 4000, 'montant_n1': 3500}
    ],
    'bilan_passif': [
        {'ref': 'DA', 'montant_n': 4000, 'montant_n1': 4000},
        {'ref': 'DB', 'montant_n': 800, 'montant_n1': 200}
    ],
    'compte_resultat': [
        {'ref': 'RA', 'montant_n': 10000, 'montant_n1': 9000},
        {'ref': 'TA', 'montant_n': -4000, 'montant_n1': -3000}
    ],
    'tft': [
        {'ref': 'ZA', 'montant_n': 1000, 'montant_n1': 500}
    ]
}

print("Appel de remplir_liasse_officielle...")
try:
    xlsx_bytes = remplir_liasse_officielle(results, "TEST_ENTREPRISE", "2026")
    with open("TEST_LIASSE.xlsx", "wb") as f:
        f.write(xlsx_bytes)
    print("Fichier TEST_LIASSE.xlsx généré avec succès!")
except Exception as e:
    import traceback
    traceback.print_exc()
