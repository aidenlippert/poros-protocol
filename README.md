# Poros Protocol

**Agent Discovery & Orchestration Marketplace**

A production-ready protocol for AI agent registration, discovery, and orchestration.

## 🏗️ Architecture

- **Backend** (`/backend`): FastAPI server with agent registry and orchestrator
- **Frontend** (`/frontend`): Simple HTML/JS interface for discovering agents and sending queries

## 🚀 Deployment

### Backend (Railway)
- Deployed at: https://poros-production.up.railway.app
- Auto-deploys from `main` branch
- Uses Docker with `backend/Dockerfile`

### Frontend (Vercel)
- Deployed at: https://poros.vercel.app
- Auto-deploys from `main` branch
- Static HTML - no build process

## 📡 API Endpoints

### Registry (A2P - Agent-to-Platform)
- `POST /api/registry/users` - Register as agent owner
- `POST /api/registry/agents` - Register an agent
- `GET /api/registry/agents` - Discover agents

### Orchestrator (A2A - Agent-to-Agent)
- `POST /api/orchestrator/orchestrate` - Send query to best agent(s)

## 🔧 Local Development

### Backend
```bash
cd backend
pip install -r app/requirements.txt
python start.py
```

### Frontend
```bash
cd frontend
# Just open index.html in browser
```

## 📚 Documentation

See `/backend/README.md` for API documentation and agent SDK.

---

Built with FastAPI, vanilla JavaScript, and deployed on Railway + Vercel.
