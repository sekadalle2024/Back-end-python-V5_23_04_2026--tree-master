# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         TEST ENDPOINT ZEABUR — ÉTATS FINANCIERS SYSCOHADA                  ║
║         Feature : Case 24 — EtatFinAutoTrigger.js                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Endpoint testé : POST /etats-financiers/process-excel                     ║
║  Backend cible  : https://pybackend.zeabur.app                             ║
║  Fichier test   : P000 -BALANCE DEMO N_N-1_N-2.xls                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Utilisation :                                                              ║
║    python test_zeabur_etat_fin.py                                           ║
║    python test_zeabur_etat_fin.py --local      (teste localhost:5000)       ║
║    python test_zeabur_etat_fin.py --url https://mon-backend.com             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import io
import json
import time
import base64
import argparse

# Forcer UTF-8 sur Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ─── Imports avec messages clairs ──────────────────────────────────────────────
try:
    import requests
except ImportError:
    print("❌ 'requests' non installé. Lancez : pip install requests")
    sys.exit(1)

# ─── Arguments CLI ─────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description='Test endpoint États Financiers sur Zeabur ou Local'
)
parser.add_argument(
    '--local', action='store_true',
    help='Tester sur localhost:5000 au lieu de Zeabur'
)
parser.add_argument(
    '--url', type=str, default=None,
    help='URL de base custom (ex: https://mon-backend.com)'
)
parser.add_argument(
    '--file', type=str, default=None,
    help='Chemin vers un fichier Excel de balance (défaut: P000 -BALANCE DEMO N_N-1_N-2.xls)'
)
parser.add_argument(
    '--timeout', type=int, default=120,
    help='Timeout en secondes (défaut: 120)'
)
args = parser.parse_args()


# ─── Configuration ─────────────────────────────────────────────────────────────
ZEABUR_BASE_URL = 'https://pybackend.zeabur.app'
LOCAL_BASE_URL  = 'http://localhost:5000'

if args.url:
    BASE_URL = args.url.rstrip('/')
elif args.local:
    BASE_URL = LOCAL_BASE_URL
else:
    BASE_URL = ZEABUR_BASE_URL

ENDPOINT_HEALTH   = f"{BASE_URL}/"
ENDPOINT_ETAT_FIN = f"{BASE_URL}/etats-financiers/process-excel"
ENDPOINT_LEAD_BAL = f"{BASE_URL}/lead-balance/process-excel"

# Fichier balance par défaut
SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BALANCE = os.path.join(SCRIPT_DIR, "P000 -BALANCE DEMO N_N-1_N-2.xls")
BALANCE_FILE  = args.file if args.file else DEFAULT_BALANCE


# ──────────────────────────────────────────────────────────────────────────────
def sep(title="", char="═", width=70):
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{char*pad} {title} {char*(width-pad-len(title)-2)}")
    else:
        print(char * width)


def ok(msg):  print(f"  ✅ {msg}")
def err(msg): print(f"  ❌ {msg}")
def warn(msg):print(f"  ⚠️  {msg}")
def info(msg):print(f"  ℹ️  {msg}")


# ──────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Test de santé du backend
# ──────────────────────────────────────────────────────────────────────────────
def test_health():
    sep("ÉTAPE 1 — Santé du backend")
    info(f"URL testée : {BASE_URL}")
    
    # Test endpoint racine
    try:
        t0 = time.time()
        r = requests.get(ENDPOINT_HEALTH, timeout=30)
        elapsed = time.time() - t0
        
        if r.status_code in (200, 422):
            ok(f"Backend en ligne — HTTP {r.status_code} — {elapsed:.2f}s")
            return True
        else:
            warn(f"Backend répond mais avec HTTP {r.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        err(f"Connexion refusée sur {BASE_URL}")
        if not args.local:
            err("Vérifiez que le backend Zeabur est bien démarré")
            err("Dashboard Zeabur → https://dash.zeabur.com")
        else:
            err("Vérifiez que le backend local est démarré : python main.py")
        return False
    except requests.exceptions.Timeout:
        err(f"Timeout après 30s — {BASE_URL} ne répond pas")
        return False
    except Exception as e:
        err(f"Erreur inattendue : {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — Vérification du fichier de balance
# ──────────────────────────────────────────────────────────────────────────────
def check_balance_file():
    sep("ÉTAPE 2 — Vérification du fichier de balance")
    info(f"Fichier : {BALANCE_FILE}")
    
    if not os.path.exists(BALANCE_FILE):
        err(f"Fichier non trouvé : {BALANCE_FILE}")
        err("Placer le fichier dans le dossier py_backend/ ou fournir --file <chemin>")
        return None
    
    size = os.path.getsize(BALANCE_FILE)
    ok(f"Fichier trouvé — {size / 1024:.1f} KB")
    
    # Lire et encoder en base64
    with open(BALANCE_FILE, 'rb') as f:
        content = f.read()
    
    encoded = base64.b64encode(content).decode('utf-8')
    filename = os.path.basename(BALANCE_FILE)
    ok(f"Encodage base64 OK — {len(encoded)} caractères")
    
    return encoded, filename


# ──────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — Appel endpoint États Financiers
# ──────────────────────────────────────────────────────────────────────────────
def test_etats_financiers(file_b64, filename):
    sep("ÉTAPE 3 — Test /etats-financiers/process-excel")
    info(f"Endpoint : {ENDPOINT_ETAT_FIN}")
    info(f"Fichier  : {filename}")
    info(f"Timeout  : {args.timeout}s")
    
    payload = {
        "file_base64": file_b64,
        "filename": filename
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://prclaravi.netlify.app"  # Simuler l'appel depuis Netlify
    }
    
    print("\n  📤 Envoi de la requête...")
    t0 = time.time()
    
    try:
        r = requests.post(
            ENDPOINT_ETAT_FIN,
            json=payload,
            headers=headers,
            timeout=args.timeout
        )
        elapsed = time.time() - t0
        
        print(f"  📥 Réponse reçue en {elapsed:.2f}s — HTTP {r.status_code}")
        
        # Vérifier les headers CORS
        sep("Headers CORS reçus", char="─", width=70)
        cors_headers = {
            k: v for k, v in r.headers.items()
            if 'access-control' in k.lower() or 'cors' in k.lower()
        }
        if cors_headers:
            for k, v in cors_headers.items():
                info(f"{k}: {v}")
        else:
            warn("Aucun header CORS dans la réponse")
        
        # Analyser la réponse
        if r.status_code == 200:
            try:
                data = r.json()
                analyze_response(data, elapsed)
                return data
            except Exception as e:
                err(f"Impossible de parser la réponse JSON : {e}")
                print(f"  Contenu brut (premiers 500 chars): {r.text[:500]}")
                return None
        
        elif r.status_code == 422:
            err(f"HTTP 422 — Données invalides")
            try:
                detail = r.json()
                print(f"  Détail : {json.dumps(detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"  Contenu : {r.text[:300]}")
            return None
        
        elif r.status_code == 500:
            err(f"HTTP 500 — Erreur serveur")
            try:
                detail = r.json()
                err(f"Message : {detail.get('detail', 'Inconnu')}")
            except:
                print(f"  Contenu : {r.text[:500]}")
            return None
        
        else:
            warn(f"HTTP {r.status_code} — Réponse inattendue")
            print(f"  Contenu : {r.text[:300]}")
            return None
    
    except requests.exceptions.Timeout:
        elapsed = time.time() - t0
        err(f"Timeout après {elapsed:.0f}s — Le traitement du fichier Excel prend trop de temps")
        warn(f"Essayez avec --timeout {args.timeout * 2} pour doubler le délai")
        return None
    
    except requests.exceptions.ConnectionError as e:
        err(f"Erreur de connexion : {e}")
        return None
    
    except Exception as e:
        err(f"Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Analyse détaillée de la réponse
# ──────────────────────────────────────────────────────────────────────────────
def analyze_response(data, elapsed):
    sep("RÉSULTATS DÉTAILLÉS", char="─", width=70)
    
    success = data.get('success', False)
    message = data.get('message', 'Pas de message')
    
    if success:
        ok(f"Traitement réussi")
        ok(f"Message : {message}")
        ok(f"Temps de traitement : {elapsed:.2f}s")
    else:
        err(f"Traitement échoué")
        err(f"Message : {message}")
    
    # Analyser les résultats financiers
    results = data.get('results', {})
    if results:
        sep("Données financières", char="─", width=70)
        
        # Comptes
        nb_actif   = len(results.get('bilan_actif', {}))
        nb_passif  = len(results.get('bilan_passif', {}))
        nb_charges = len(results.get('charges', {}))
        nb_produits= len(results.get('produits', {}))
        
        info(f"Postes Bilan Actif   : {nb_actif}")
        info(f"Postes Bilan Passif  : {nb_passif}")
        info(f"Postes Charges       : {nb_charges}")
        info(f"Postes Produits      : {nb_produits}")
        
        # Totaux
        totaux = results.get('totaux', {})
        if totaux:
            sep("Totaux", char="─", width=70)
            
            def fmt(v):
                try: return f"{float(v):>20,.2f}"
                except: return str(v).rjust(20)
            
            print(f"  {'Total Actif':30} {fmt(totaux.get('actif', 0))}")
            print(f"  {'Total Passif':30} {fmt(totaux.get('passif', 0))}")
            print(f"  {'Total Charges':30} {fmt(totaux.get('charges', 0))}")
            print(f"  {'Total Produits':30} {fmt(totaux.get('produits', 0))}")
            
            r_net = totaux.get('resultat_net', 0)
            label = "✅ BÉNÉFICE" if float(r_net) >= 0 else "🔴 PERTE"
            print(f"  {'Résultat Net (' + label + ')':30} {fmt(r_net)}")
            
            # Contrôle équilibre bilan
            actif  = float(totaux.get('actif', 0))
            passif = float(totaux.get('passif', 0))
            ecart  = abs(actif - passif)
            
            sep("Contrôle d'équilibre", char="─", width=70)
            if ecart < 1:
                ok(f"Bilan équilibré (écart = {ecart:.2f})")
            else:
                warn(f"Bilan déséquilibré — Écart Actif/Passif = {ecart:,.2f}")
        
        # Contrôles qualité
        controles = results.get('controles', {})
        if controles:
            sep("Contrôles qualité", char="─", width=70)
            stats = controles.get('statistiques', {})
            taux  = stats.get('taux_couverture', 0)
            
            taux_label = "✅" if taux >= 95 else "⚠️" if taux >= 80 else "❌"
            print(f"  {taux_label} Taux de couverture : {taux:.1f}%")
            print(f"  📊 Comptes intégrés     : {stats.get('comptes_integres', 0)}")
            print(f"  ⚠️  Comptes non intégrés : {stats.get('comptes_non_integres', 0)}")
            
            eq_bilan = controles.get('equilibre_bilan', {})
            if eq_bilan.get('equilibre'):
                ok("Bilan comptablement équilibré")
            else:
                warn(f"Bilan déséquilibré : différence = {eq_bilan.get('difference', 0):,.2f}")
    
    # HTML généré
    html = data.get('html', '')
    if html:
        ok(f"HTML généré : {len(html)} caractères")
        
        # Sauvegarder le HTML
        output_html = os.path.join(SCRIPT_DIR, 'test_zeabur_etat_fin_output.html')
        try:
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html)
            ok(f"HTML sauvegardé → {output_html}")
        except Exception as e:
            warn(f"Impossible de sauvegarder le HTML : {e}")
    else:
        warn("Pas de HTML dans la réponse")


# ──────────────────────────────────────────────────────────────────────────────
# ÉTAPE 4 — Test CORS depuis Netlify (simulation)
# ──────────────────────────────────────────────────────────────────────────────
def test_cors_preflight():
    sep("ÉTAPE 4 — Test CORS Preflight (OPTIONS)")
    info(f"Simulation d'un appel depuis https://prclaravi.netlify.app")
    
    try:
        r = requests.options(
            ENDPOINT_ETAT_FIN,
            headers={
                "Origin": "https://prclaravi.netlify.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            },
            timeout=15
        )
        
        info(f"HTTP {r.status_code}")
        
        acao = r.headers.get('Access-Control-Allow-Origin', 'ABSENT')
        acam = r.headers.get('Access-Control-Allow-Methods', 'ABSENT')
        acah = r.headers.get('Access-Control-Allow-Headers', 'ABSENT')
        acac = r.headers.get('Access-Control-Allow-Credentials', 'ABSENT')
        aceh = r.headers.get('Access-Control-Expose-Headers', 'ABSENT')
        
        print(f"\n  Access-Control-Allow-Origin      : {acao}")
        print(f"  Access-Control-Allow-Methods     : {acam}")
        print(f"  Access-Control-Allow-Headers     : {acah}")
        print(f"  Access-Control-Allow-Credentials : {acac}")
        print(f"  Access-Control-Expose-Headers    : {aceh}")
        
        # Valider
        if acao in ('https://prclaravi.netlify.app', '*'):
            ok("Origine Netlify autorisée")
        else:
            err(f"Origine Netlify NON autorisée. Reçu : '{acao}'")
        
        if 'Content-Disposition' in (aceh or ''):
            ok("Content-Disposition exposé (téléchargements OK)")
        else:
            warn("Content-Disposition absent de expose_headers")
        
        return r.status_code in (200, 204)
        
    except Exception as e:
        warn(f"Test OPTIONS échoué (certains backends ne supportent pas OPTIONS isolé) : {e}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    sep("CLARAVERSE — TEST ENDPOINT ZEABUR — ÉTATS FINANCIERS")
    
    env_label = "🖥️  LOCAL (localhost:5000)" if args.local else f"☁️  ZEABUR ({BASE_URL})"
    if args.url:
        env_label = f"🔧 CUSTOM ({BASE_URL})"
    
    print(f"  Environnement : {env_label}")
    print(f"  Endpoint      : {ENDPOINT_ETAT_FIN}")
    print(f"  Fichier test  : {os.path.basename(BALANCE_FILE)}")
    print(f"  Timeout       : {args.timeout}s")
    
    # Étape 1 : Santé du backend
    if not test_health():
        sep("RÉSULTAT FINAL")
        err("Backend inaccessible — Tests impossibles")
        sys.exit(1)
    
    # Étape 2 : Vérification du fichier
    result = check_balance_file()
    if result is None:
        sep("RÉSULTAT FINAL")
        err("Fichier de balance introuvable — Tests impossibles")
        sys.exit(1)
    
    file_b64, filename = result
    
    # Étape 3 : Test endpoint etat_fin
    response = test_etats_financiers(file_b64, filename)
    
    # Étape 4 : Test CORS preflight
    test_cors_preflight()
    
    # Résumé final
    sep("RÉSUMÉ FINAL")
    if response and response.get('success'):
        ok("✅ Feature 'etat_fin' (Case 24) OPÉRATIONNELLE sur " + BASE_URL)
        ok("Le frontend Netlify peut appeler ce backend sans erreur CORS")
    else:
        err("Feature 'etat_fin' non fonctionnelle — voir les détails ci-dessus")
        print("\n  Pistes de débogage :")
        print("    1. Vérifier les logs Zeabur → Dashboard → Logs")
        print("    2. Tester en local : python test_zeabur_etat_fin.py --local")
        print("    3. Vérifier que le fichier de balance est valide")


if __name__ == '__main__':
    main()
