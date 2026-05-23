# Contributing to NHRMS

## 1. Development Setup

### Prerequisites
- Python 3.13+
- Node.js 22+
- Docker Desktop (with WSL2 on Windows)
- Git
- PostgreSQL 16 (or use Docker)
- Redis 7 (or use Docker)

### Quick Start (one command)
```bash
docker compose up --build
```
This starts PostgreSQL, Redis, the API (hot-reload), worker, and frontend.

### Manual Dev Setup
```bash
# Backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r backend/requirements.txt
pip install -r backend/dev-requirements.txt   # ruff, pytest, httpx

# Frontend
cd frontend && npm install

# Database
docker compose up postgres redis -d

# Environment
cp .env.example .env   # edit DATABASE_URL for your setup

# Migrations
alembic upgrade head

# Seed demo data
python scripts/seed.py

# Run
cd backend
uvicorn backend.app.main:app --reload --port 8000   # API at :8000
cd frontend && npm run dev                           # UI at :5173
```

### Verification Checklist
```bash
pytest tests/ -v                                    # All tests pass
ruff check backend/                                  # No lint errors
cd frontend && npm run build                         # Frontend builds
python scripts/deploy_check.py                       # All checks green
```

---

## 2. Git Workflow (Trunk-Based with Short-Lived Feature Branches)

### Branching Model
```
main         ← production, protected, auto-deploys to Render
develop      ← staging, protected, auto-deploys to staging Render
feat/*       ← feature branches, branch from develop, PR to develop
fix/*        ← bug fixes
refactor/*   ← code improvements
ops/*        ← DevOps, CI/CD, infrastructure
security/*   ← security patches
docs/*       ← documentation only
```

### Branch Naming
```
feat/candidate-scoring     # New feature
fix/checkin-timezone       # Bug fix
ops/upgrade-postgres       # DevOps change
security/jwt-refresh-token # Security fix
```
Use kebab-case, under 50 characters.

### Branch Protection Rules (enforced on GitHub)
| Rule | `main` | `develop` |
|------|--------|-----------|
| Require PR before merge | ✅ | ✅ |
| Required approvals | 1 | 1 |
| Dismiss stale reviews | ✅ | ✅ |
| Require status checks | lint, test, build-frontend | lint, test |
| Require up-to-date branch | ✅ | ❌ |
| Enforce for admins | ✅ | ❌ |
| Restrict direct pushes | ✅ | ✅ |

### Commit Conventions (Semantic Commits)
```
<type>: <imperative description, no period>

[optional body — explain WHY, not what. Wrap at 72 chars.]
```

**Types**: `feat` `fix` `refactor` `test` `docs` `chore` `ops` `security` `perf`

**Good examples:**
```
feat: add candidate filtering by score range
fix: prevent duplicate check-in on same day
refactor: extract payroll engine from route handler
ops: add Render Blueprint staging environment
```

**Bad examples:**
```
fix bug
update stuff
WIP
```

---

## 3. Pull Request Workflow

### Step-by-Step
1. **Create a feature branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/your-feature
   ```

2. **Make changes** — small, logical commits with semantic messages.

3. **Push and open a PR**:
   ```bash
   git push origin feat/your-feature
   ```
   → Open PR on GitHub: `feat/your-feature → develop`
   → Title must follow commit convention
   → Description: WHAT and WHY, reference issues with "Closes #N"

4. **CI runs automatically**:
   - `lint` — ruff checks (cancels on failure)
   - `test` — pytest with SQLite (only runs if lint passes)
   - `build-frontend` — Vite build (only runs if lint passes)

5. **Request review** from a team member.

6. **Merge** via "Squash and merge" (keeps history clean):
   ```bash
   # Delete remote branch after merge
   git branch -d feat/your-feature
   ```

### PR Checklist
- [ ] Code follows existing patterns and conventions
- [ ] Tests added/updated for new functionality
- [ ] `pytest tests/ -v` passes locally
- [ ] `ruff check backend/` passes
- [ ] Frontend `npm run build` succeeds
- [ ] No secrets, credentials, or hardcoded URLs in code
- [ ] `.env.example` updated if new environment variables added
- [ ] Alembic migration created if models changed: `alembic revision --autogenerate -m "description"`
- [ ] API changes documented in Swagger/OpenAPI
- [ ] Security implications considered (auth, permissions, data exposure)

---

## 4. Issue Workflow

### Issue Labels
| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |
| `tech-debt` | Refactoring, test coverage, code quality |
| `ops` | CI/CD, deployment, infrastructure |
| `security` | Security vulnerability or hardening |
| `good-first-issue` | Beginner-friendly task |
| `blocked` | Waiting on external dependency |

### Triage Process
1. Bug reports → label `bug`, assign priority
2. Feature requests → label `enhancement`, discuss in sprint planning
3. Critical bugs → hotfix branch from `main`, deploy ASAP

---

## 5. Code Standards

### Python / FastAPI
- Use **type hints** on all function signatures
- Follow **FastAPI best practices** (dependency injection, Pydantic models)
- Imports: `stdlib → third-party → local` (grouped with blank lines)
- Use `logger` from `backend.app.utils.helpers` — never `print()`
- No commented-out code
- Docstrings only where public API needs explanation

### TypeScript / React
- Strict TypeScript — no `any`, no `@ts-ignore`
- Functional components with hooks (no class components)
- Use `services/` layer for API calls, not inline fetch
- Import paths: `@/` alias for `src/`

### Testing
- Unit tests in `tests/` using `pytest`
- Test each route with `httpx.AsyncClient`
- Test edge cases (empty data, auth failures, permission denied)
- Aim for 80%+ coverage on new code

---

## 6. Environment / Configuration

### Per-Developer Setup
```bash
cp .env.example .env
```
Edit `.env`:
- `DATABASE_URL`: `sqlite:///data/saas.db` for SQLite (no Docker needed)
- `DATABASE_URL`: `postgresql://nhrms:nhrms_dev@localhost:5432/nhrms` for PostgreSQL
- `SECRET_KEY`: generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Environment Files
| File | Used For | Committed? |
|------|----------|-----------|
| `.env.example` | Documentation of all env vars | ✅ Yes |
| `.env` | Local development | ❌ No (gitignored) |
| Render Env Vars | Production/staging | ❌ Set in dashboard |
| GitHub Secrets | CI/CD | ❌ Set in repo settings |

---

## 7. Deployment Pipeline

### Environments
| Environment | Branch | Deploy Method | URL Pattern |
|-------------|--------|---------------|-------------|
| Development | Local | `uvicorn --reload` | `localhost:8000` |
| Staging | `develop` | Auto-deploy (CI) | `*.onrender.com` |
| Production | `main` | Auto-deploy (CI) | `*.onrender.com` |

### CI/CD Flow
```
Push to develop → CI: lint → test → build-frontend → deploy-staging
Push to main    → CI: lint → test → build-frontend → deploy-production
```

### Deployment Steps (Render Blueprint)
1. Push to `main` → GitHub Actions triggers
2. CI runs lint → test → build-frontend
3. If all pass → Render deploy hook fires
4. Render rebuilds from Blueprint (`render.yaml`)
5. Alembic migrations run on startup
6. Service health checks verify readiness

---

## 8. Security

- **NEVER** commit `.env`, secrets, API keys, or tokens
- All passwords must use bcrypt (handled by `security.py`)
- All API endpoints (except login/register) require JWT auth
- CORS restricted to known origins
- `TrustedHostMiddleware` prevents host header attacks
- Security headers set on every response (HSTS, CSP, XSS, XFO)
- Background worker tasks use least-privilege database user
- Report vulnerabilities via `SECURITY.md`

---

## 9. Multi-Device & Remote Development

### Working from Multiple Machines
```bash
# Machine 1: push your branch
git push origin feat/your-feature

# Machine 2: pull and continue
git pull
git checkout feat/your-feature
```

### Using GitPod / VS Code Remote (Optional)
A `.devcontainer` config can be added for cloud development:
- Pre-installed Python 3.13, Node 22, Docker
- Automatic port forwarding for :8000 and :5173
- PostgreSQL and Redis services in dev container

---

## 10. Need Help?

- Open a GitHub Discussion
- Check `scripts/deploy_check.py` for deployment validation
- Read the API docs at `/api/docs` when running locally
- Review existing PRs for examples of the workflow
