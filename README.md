---
title: Claraverse Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Claraverse Backend API

Backend FastAPI pour l'application Claraverse - Assistant IA pour l'audit et la comptabilité.

## 🚀 Fonctionnalités

- **API REST FastAPI** : API moderne et performante
- **Traitement Excel** : Analyse de balances comptables et fichiers Excel
- **États Financiers SYSCOHADA** : Génération automatique d'états financiers
- **Export Documents** : Export Word et Excel
- **Analyse Pandas** : Traitement avancé de données
- **Lead Balance** : Gestion des balances de vérification
- **Échantillonnage Audit** : Outils d'échantillonnage statistique

## 📡 Endpoints Principaux

### Santé et Documentation
- `GET /health` - Vérification de l'état du service
- `GET /docs` - Documentation interactive Swagger UI
- `GET /redoc` - Documentation ReDoc

### Analyse de Données
- `POST /api/pandas/upload` - Upload et analyse de fichiers Excel
- `POST /api/pandas/analyze` - Analyse de données avec Pandas
- `GET /api/pandas/lead-balance` - Récupération de la lead balance

### États Financiers
- `POST /api/etats-financiers/generer` - Génération d'états financiers SYSCOHADA
- `POST /api/export-liasse/generer` - Export de la liasse fiscale complète

### Export et Rapports
- `POST /api/export-synthese-cac/generer` - Export de la synthèse CAC
- `POST /api/word-export/generer` - Export de documents Word

### Échantillonnage
- `POST /api/echantillonnage/calculer` - Calcul d'échantillons d'audit

## 🔧 Configuration

### Variables d'Environnement

```bash
HOST=0.0.0.0
PORT=7860
PYTHONUNBUFFERED=1
```

### Port

L'application écoute sur le **port 7860** (standard Hugging Face Spaces).

## 🐳 Docker

### Build Local

```bash
docker build -t claraverse-backend .
docker run -p 7860:7860 claraverse-backend
```

### Déploiement sur Hugging Face

Ce backend est conçu pour être déployé sur Hugging Face Spaces avec Docker SDK.

## 📦 Dépendances Principales

- **FastAPI** : Framework web moderne
- **Uvicorn** : Serveur ASGI
- **Pandas** : Analyse de données
- **OpenPyXL** : Manipulation de fichiers Excel
- **Python-docx** : Génération de documents Word
- **PyPDF2** : Traitement de fichiers PDF

## 🚀 Démarrage Rapide

### Installation Locale

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py --host 0.0.0.0 --port 7860
```

### Tester l'API

```bash
# Vérifier la santé
curl http://localhost:7860/health

# Accéder à la documentation
# Ouvrir http://localhost:7860/docs dans votre navigateur
```

## 📚 Documentation Complète

Pour une documentation complète du projet Claraverse, consultez le repository principal.

## 🔐 Sécurité

- CORS configuré pour accepter toutes les origines (à restreindre en production)
- Healthcheck intégré pour monitoring
- Gestion des erreurs globale

## 📊 Monitoring

L'application expose un endpoint `/health` qui retourne :

```json
{
  "status": "healthy",
  "timestamp": "2026-04-18T...",
  "version": "1.0.0",
  "uptime": "..."
}
```

## 🤝 Contribution

Ce projet fait partie de l'écosystème Claraverse. Pour contribuer, consultez le repository principal.

## 📄 License

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Consultez la documentation sur `/docs`
- Vérifiez les logs de l'application
- Contactez l'équipe de développement

---

**Déployé sur Hugging Face Spaces** 🤗
