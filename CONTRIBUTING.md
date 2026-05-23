# Contributing to NHRMS

## Branch Naming

```
feat/short-description     # New features
fix/short-description      # Bug fixes
refactor/short-description # Code improvements
chore/short-description    # Dependencies, tooling
docs/short-description     # Documentation
ops/short-description      # DevOps, CI/CD, deployment
security/short-description # Security fixes
```
Keep names kebab-case, under 50 chars.

## Commit Messages

```
<type>: <imperative description>

[optional body — explain WHY, not what]
```

Types: `feat` `fix` `refactor` `test` `docs` `chore` `ops` `security`

Good:
```
feat: add candidate filtering by score range
fix: prevent duplicate check-in on same day
refactor: extract payroll engine from route handler
```

Avoid:
```
fix bug
update stuff
WIP
```

## Pull Request Workflow

1. Branch from `develop`
2. Make changes with small, logical commits
3. Push and open PR → `develop`
4. Title: `<type>: <description>` (same as commit style)
5. Description: include WHAT and WHY, reference issues
6. Wait for CI checks (lint → test → build) to pass
7. Request review if team member available
8. Merge via "Squash and merge" (keeps history clean)
9. Delete the feature branch

## PR Checklist

- [ ] Code follows existing patterns
- [ ] Tests added/updated
- [ ] `pytest tests/ -v` passes
- [ ] `ruff check backend/` passes
- [ ] Frontend `npm run build` succeeds
- [ ] No secrets or credentials in code
- [ ] `.env.example` updated if new env vars added
- [ ] Alembic migration created if models changed

## Code Standards

- Python: follow FastAPI patterns, use type hints
- TypeScript: use strict types, no `any`
- No commented-out code
- No print/debug statements (use `logger`)
- Imports: stdlib → third-party → local (grouped)
