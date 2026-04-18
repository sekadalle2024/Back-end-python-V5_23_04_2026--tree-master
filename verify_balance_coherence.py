# -*- coding: utf-8 -*-
"""
Script pour vérifier la cohérence des balances N, N-1, N-2
Vérifie que les variations sont cohérentes et logiques
"""
import pandas as pd
import sys

# Forcer l'encodage UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verify_balance_coherence():
    """Vérifie la cohérence des balances"""
    
    try:
        # Charger les balances
        balance_n = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N (2024)')
        balance_n1 = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N-1 (2023)')
        balance_n2 = pd.read_excel('BALANCES_N_N1_N2.xlsx', sheet_name='Balance N-2 (2022)')
        
        print("="*80)
        print("VÉRIFICATION DE LA COHÉRENCE DES BALANCES")
        print("="*80)
        
        # Fonction pour convertir les montants
        def to_float(val):
            try:
                return float(str(val).replace(' ', '').replace(',', '.'))
            except:
                return None
        
        # Analyser les colonnes de montants
        amount_cols = []
        for col in balance_n.columns:
            col_lower = str(col).lower()
            if 'solde' in col_lower or 'débit' in col_lower or 'crédit' in col_lower:
                if 'ant' not in col_lower:  # Exclure les antérieurs
                    amount_cols.append(col)
        
        print(f"\nColonnes de montants analysées: {amount_cols}")
        print(f"Nombre de comptes: {len(balance_n)}")
        
        # Vérifier la cohérence pour chaque compte
        print("\n" + "="*80)
        print("ANALYSE DE COHÉRENCE PAR COMPTE")
        print("="*80)
        
        coherence_issues = []
        growth_rates = []
        
        for idx in range(min(10, len(balance_n))):  # Analyser les 10 premiers comptes
            account_name = balance_n.iloc[idx, 0] if len(balance_n.columns) > 0 else f"Compte {idx}"
            
            print(f"\n{'─'*60}")
            print(f"Compte {idx + 1}: {account_name}")
            print(f"{'─'*60}")
            
            for col in amount_cols:
                val_n = to_float(balance_n.iloc[idx][col])
                val_n1 = to_float(balance_n1.iloc[idx][col])
                val_n2 = to_float(balance_n2.iloc[idx][col])
                
                if val_n is not None and val_n1 is not None and val_n2 is not None:
                    # Calculer les taux de croissance
                    if val_n1 != 0:
                        growth_n_n1 = ((val_n - val_n1) / abs(val_n1)) * 100
                    else:
                        growth_n_n1 = 0
                    
                    if val_n2 != 0:
                        growth_n1_n2 = ((val_n1 - val_n2) / abs(val_n2)) * 100
                    else:
                        growth_n1_n2 = 0
                    
                    print(f"\n  {col}:")
                    print(f"    N-2 (2022): {val_n2:>15,.2f}")
                    print(f"    N-1 (2023): {val_n1:>15,.2f}  (croissance: {growth_n1_n2:>6.2f}%)")
                    print(f"    N   (2024): {val_n:>15,.2f}  (croissance: {growth_n_n1:>6.2f}%)")
                    
                    # Vérifier la cohérence
                    if abs(growth_n_n1 - growth_n1_n2) > 50:  # Écart > 50% entre les deux croissances
                        coherence_issues.append({
                            'account': account_name,
                            'column': col,
                            'growth_n1_n2': growth_n1_n2,
                            'growth_n_n1': growth_n_n1,
                            'issue': 'Croissance incohérente'
                        })
                        print(f"    ⚠️  ALERTE: Croissance incohérente!")
                    
                    growth_rates.append({
                        'account': account_name,
                        'column': col,
                        'growth_n1_n2': growth_n1_n2,
                        'growth_n_n1': growth_n_n1
                    })
        
        # Résumé
        print("\n" + "="*80)
        print("RÉSUMÉ DE LA COHÉRENCE")
        print("="*80)
        
        if growth_rates:
            avg_growth_n1_n2 = sum(g['growth_n1_n2'] for g in growth_rates) / len(growth_rates)
            avg_growth_n_n1 = sum(g['growth_n_n1'] for g in growth_rates) / len(growth_rates)
            
            print(f"\nCroissance moyenne N-2 → N-1: {avg_growth_n1_n2:.2f}%")
            print(f"Croissance moyenne N-1 → N:   {avg_growth_n_n1:.2f}%")
        
        if coherence_issues:
            print(f"\n⚠️  {len(coherence_issues)} problèmes de cohérence détectés:")
            for issue in coherence_issues[:5]:  # Afficher les 5 premiers
                print(f"  - {issue['account']} ({issue['column']})")
                print(f"    Croissance N-2→N-1: {issue['growth_n1_n2']:.2f}%")
                print(f"    Croissance N-1→N:   {issue['growth_n_n1']:.2f}%")
        else:
            print("\n✓ Aucun problème de cohérence majeur détecté")
        
        print("\n" + "="*80)
        
    except FileNotFoundError:
        print("Erreur: Le fichier BALANCES_N_N1_N2.xlsx n'existe pas")
        print("Exécutez d'abord: python create_balances_multi_exercices.py")
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_balance_coherence()
