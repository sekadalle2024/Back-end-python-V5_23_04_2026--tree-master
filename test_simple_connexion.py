import socket

# Test de connexion simple
print("Test de connexion au port 5000...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    
    if result == 0:
        print("✅ Port 5000 est ouvert et accessible")
    else:
        print(f"❌ Port 5000 n'est pas accessible (code: {result})")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test avec requests
print("\nTest avec requests...")
try:
    import requests
    print("✅ Module requests disponible")
    
    response = requests.get("http://127.0.0.1:5000/health", timeout=5)
    print(f"✅ Réponse reçue: {response.status_code}")
except ImportError:
    print("❌ Module requests non installé")
except Exception as e:
    print(f"❌ Erreur: {e}")
