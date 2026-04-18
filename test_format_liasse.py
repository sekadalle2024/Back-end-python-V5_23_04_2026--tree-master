"""
Script de test pour le nouveau format liasse officielle
"""

import pandas as pd
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(__file__))

from etats_financiers import load_tableau_correspondance
from etats_financiers_v2 import (
    process_balance_to_liasse_format,
    generate_section_html_liasse,
    generate_css_liasse,
    format_montant_liasse
)

def test_format_liasse():
    """Test du format liasse officielle"""
    print("=" * 80)
    print("TEST FORMAT LIASSE OFFICIELLE")
    print("=" * 80)
    
    # Charger les balances
    print("\n1. Chargement des balances...")
    try:
        excel_file = "BALANCES_N_N1_N2.xlsx"
        balance_n = pd.read_excel(excel_file, sheet_name="Balance N (2024)")
        balance_n1 = pd.read_excel(excel_file, sheet_name="Balance N-1 (2023)")
        print(f"   ✅ Balance N: {len(balance_n)} lignes")
        print(f"   ✅ Balance N-1: {len(balance_n1)} lignes")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    # Charger les correspondances
    print("\n2. Chargement des correspondances...")
    try:
        correspondances = load_tableau_correspondance()
        print(f"   ✅ Correspondances chargées")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    # Traiter les balances
    print("\n3. Traitement des balances au format liasse...")
    try:
        results = process_balance_to_liasse_format(balance_n, balance_n1, correspondances)
        print(f"   ✅ Traitement terminé")
        print(f"   - Compte de Résultat: {len(results['compte_resultat'])} postes")
        print(f"   - Bilan Actif: {len(results['bilan_actif'])} postes")
        print(f"   - Bilan Passif: {len(results['bilan_passif'])} postes")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Afficher un échantillon du Compte de Résultat
    print("\n4. Échantillon Compte de Résultat (10 premiers postes):")
    print("-" * 80)
    print(f"{'REF':<6} {'LIBELLÉ':<50} {'NOTE':<6} {'N':>15} {'N-1':>15}")
    print("-" * 80)
    
    for poste in results['compte_resultat'][:10]:
        ref = poste['ref']
        libelle = poste['libelle'][:48]
        note = poste.get('note', '')
        montant_n = format_montant_liasse(poste['montant_n'])
        montant_n1 = format_montant_liasse(poste['montant_n1'])
        print(f"{ref:<6} {libelle:<50} {note:<6} {montant_n:>15} {montant_n1:>15}")
    
    # Afficher les postes de totalisation
    print("\n5. Postes de Totalisation:")
    print("-" * 80)
    totaux = [p for p in results['compte_resultat'] if p['ref'].startswith('X')]
    for poste in totaux:
        ref = poste['ref']
        libelle = poste['libelle'][:48]
        montant_n = format_montant_liasse(poste['montant_n'])
        montant_n1 = format_montant_liasse(poste['montant_n1'])
        print(f"{ref:<6} {libelle:<50} {montant_n:>15} {montant_n1:>15}")
    
    # Générer le HTML
    print("\n6. Génération du HTML...")
    try:
        html = generate_css_liasse()
        html += "<div class='etats-fin-container'>"
        html += generate_section_html_liasse(
            "compte_resultat",
            "📊 COMPTE DE RÉSULTAT",
            results['compte_resultat'],
            "EXERCICE N",
            "EXERCICE N-1"
        )
        html += generate_section_html_liasse(
            "bilan_actif",
            "🏢 BILAN - ACTIF",
            results['bilan_actif'],
            "EXERCICE N",
            "EXERCICE N-1"
        )
        html += generate_section_html_liasse(
            "bilan_passif",
            "🏛️ BILAN - PASSIF",
            results['bilan_passif'],
            "EXERCICE N",
            "EXERCICE N-1"
        )
        html += "</div>"
        
        # Sauvegarder le HTML
        output_file = "test_format_liasse.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Format Liasse Officielle</title>
    {html}
</head>
<body>
    <h1 style="text-align: center; color: #1e3a8a;">Test Format Liasse Officielle</h1>
    {html}
    
    <script>
    // Script pour les accordéons
    document.querySelectorAll('.section-header-ef').forEach(header => {{
        header.addEventListener('click', function() {{
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            content.classList.toggle('active');
        }});
    }});
    </script>
</body>
</html>
            """)
        
        print(f"   ✅ HTML généré: {output_file}")
        print(f"   📂 Taille: {len(html)} caractères")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("✅ TEST TERMINÉ AVEC SUCCÈS")
    print("=" * 80)


if __name__ == "__main__":
    test_format_liasse()
