# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — FastAPI/React skeleton with health endpoint

Status: done

Acceptance:
- Backend starts on port 8000 with /health endpoint returning JSON
- Frontend builds with Vite and serves on port 5173
- Docker Compose brings up backend + frontend + Keycloak
- Backend pytest passes, frontend npm test passes

Implementation: `backend/app/main.py`, `backend/app/api/health.py`, `backend/requirements.txt`, `backend/Dockerfile`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/vite.config.ts`, `docker-compose.yaml`, `.env.example`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/pyproject.toml`, `frontend/tsconfig.json`, `frontend/tsconfig.node.json`, `frontend/index.html`, `frontend/src/index.css`, `frontend/nginx.conf`, `frontend/Dockerfile`, `frontend/vitest.config.ts`, `frontend/src/__tests__/setup.ts`

Tests: `backend/tests/test_health.py`, `frontend/src/__tests__/App.test.tsx`

### agent-workflow-engine — Agent workflow orchestration engine

Status: planned

Acceptance:
- POST /api/workflows creates a workflow run with provider-qualified reviewers
- GET /api/workflows/{id} returns status and collected reviews
- Cross-provider dispatch: claude -> codex exec, codex -> claude -p
- Incomplete verdict when any reviewer fails

### hook-effectiveness-analyzer — Hook effectiveness measurement from transcripts

Status: planned

Acceptance:
- Ingest local transcript logs (JSONL)
- Compute opens per 100 prompts for main vs subagent
- Compare before/after hook changes

### oidc-auth — OIDC Keycloak authentication with SPA PKCE

Status: planned

Acceptance:
- Login redirects to Keycloak, callback exchanges code for tokens
- Tokens kept in memory (sessionStorage for verifier/state)
- Bearer-only API with role-based authorization
- Logout clears session

