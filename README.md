# NHRMS — HR SaaS Platform

Multi-tenant HR platform with ATS, payroll, attendance, and AI-powered candidate scoring.

**Stack:** FastAPI · React + Vite · PostgreSQL · Redis · Docker · Render

---

## Quick Start (5 minutes)

```bash
# 1. Clone
git clone https://github.com/YOUR_ORG/nhrms.git
cd nhrms

# 2. Environment
cp .env.example .env

# 3. Start infrastructure
docker compose up -d postgres redis

# 4. Backend
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows
pip install -r backend/requirements.txt
alembic upgrade head
uvicorn backend.app.main:app --reload --port 8000

# 5. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

**App:** http://localhost:5173 · **API:** http://localhost:8000/api/docs

---

## Prerequisites

| Tool | Version | Why |
|------|---------|-----|
| Python | 3.12+ | FastAPI runtime |
| Node.js | 20+ | Vite + React build |
| Docker | Latest | PostgreSQL + Redis locally |
| Git | Latest | Version control |

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  React SPA  │────▶│  FastAPI API  │────▶│ PostgreSQL │
│  (Vite)     │     │  (Uvicorn)    │     │            │
└─────────────┘     └──────┬───────┘     └────────────┘
                           │
                    ┌──────▼───────┐     ┌────────────┐
                    │  ARQ Worker  │────▶│   Redis    │
                    │  (async)     │     │   (Queue)  │
                    └──────────────┘     └────────────┘
```

- **Backend** — FastAPI with SQLAlchemy + Alembic migrations
- **Frontend** — React 19 + Vite 6 + TanStack Query + Tailwind
- **Database** — PostgreSQL (SQLite fallback for CI/quick dev)
- **Worker** — ARQ (async task queue via Redis)
- **Auth** — JWT access + refresh tokens, RBAC (5 roles)
- **AI** — LLM adapter for CV scoring (OpenAI/Anthropic or rule-based)

---

## Environment Variables

```env
# Required
DATABASE_URL=postgresql://nhrms:nhrms_dev@localhost:5432/nhrms
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(32))">

# Optional — sensible defaults
DEBUG=true
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com

# Optional — enable features
SENTRY_DSN=            # Error tracking
SMTP_SERVER=            # Email notifications
OPENAI_API_KEY=         # AI scoring via GPT-4o
ANTHROPIC_API_KEY=      # AI scoring via Claude-3
```

---

## Project Structure

```
nhrms/
├── backend/
│   ├── app/
│   │   ├── main.py                 # App factory + middleware
│   │   ├── config.py               # Settings from env
│   │   ├── database/               # SQLAlchemy models + setup
│   │   ├── routes/                 # API endpoints (auth, employees, etc.)
│   │   ├── services/               # Business logic (Excel-based)
│   │   ├── ats/                    # ATS module (SQLAlchemy)
│   │   ├── interviews/             # Interview scheduling
│   │   ├── notifications/          # In-app + email + WebSocket
│   │   └── utils/                  # Security, helpers
│   ├── alembic/                    # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── features/               # Login, ATS, Payroll, etc.
│   │   ├── components/             # Layout, Sidebar, Topbar
│   │   ├── lib/                    # Axios, roles
│   │   └── types/                  # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── data/                           # Legacy Excel files (gitignored)
├── uploads/                        # Employee docs + CVs (gitignored)
├── docker-compose.yml              # PostgreSQL + Redis
├── render.yaml                     # Render Blueprint IaC
└── .github/workflows/ci.yml        # CI/CD pipeline
```

---

## Development Workflow

### Branch Strategy

```
main         ─── Production (Render auto-deploys)
  └── develop ─── Staging (Render auto-deploys)
       ├── feat/ats-dashboard
       ├── feat/payroll-export
       ├── fix/attendance-bug
       └── chore/deps-update
```

### Making Changes

```bash
# 1. Sync latest
git checkout develop
git pull

# 2. Create feature branch
git checkout -b feat/my-feature

# 3. Make changes, commit often
git add -p                    # Review changes interactively
git commit -m "feat: add candidate filtering by score"

# 4. Push and create PR
git push -u origin feat/my-feature
# → Open PR on GitHub: develop ← feat/my-feature
```

### Commit Convention

| Prefix | Example |
|--------|---------|
| `feat:` | `feat: add bulk candidate CSV export` |
| `fix:` | `fix: prevent double-booking on interview schedule` |
| `refactor:` | `refactor: extract scoring engine from ATS service` |
| `test:` | `test: add edge cases for payroll calculation` |
| `docs:` | `docs: update API endpoint table in README` |
| `chore:` | `chore: bump fastapi to 0.115` |
| `ops:` | `ops: reduce uvicorn workers in staging` |
| `security:` | `security: rotate SECRET_KEY in GitHub Secrets` |

---

## API Documentation

Once running:
- **Swagger UI** — http://localhost:8000/api/docs
- **ReDoc** — http://localhost:8000/api/redoc
- **Health** — `GET /api/health`

---

## Testing

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_auth.py -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=backend/app --cov-report=term-missing
```

---

## Deployment

Deployment is automatic via Render Blueprint (`render.yaml`):

| Branch | Environment | URL |
|--------|-------------|-----|
| `main` | Production | `https://nhrms.onrender.com` |
| `develop` | Staging | `https://nhrms-staging.onrender.com` |

Push to trigger:
```bash
git push origin develop    # → deploys staging
git push origin main       # → deploys production
```

---

## FAQ

**Q: Can I develop without Docker?**
Yes. Set `DATABASE_URL=sqlite:///data/saas.db` in `.env` — SQLite works for local dev without any infrastructure.

**Q: How do I reset the database?**
```bash
rm data/saas.db                    # SQLite
# or
docker compose down -v postgres    # PostgreSQL
alembic upgrade head               # Re-run migrations
```

**Q: How do I add a new dependency?**
```bash
pip install <package>
pip freeze > backend/requirements.txt
```

**Q: I see "SECRET_KEY not set"**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output to `SECRET_KEY` in `.env`.

---

## License

MIT
