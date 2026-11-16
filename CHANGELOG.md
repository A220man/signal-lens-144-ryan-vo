# Changelog

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.5.0 — hook-effectiveness-analyzer checkpoint

- **Added**: Hook effectiveness measurement from transcripts
  - `POST /api/hooks/ingest` - Ingest transcript logs (JSONL format)
  - `GET /api/hooks/effectiveness` - Compute opens-per-100-prompts for main vs subagent sessions
  - `TranscriptEntry` model: prompt_id, session_type, event_type, optional metadata
  - `OpensMetrics` model: total_prompts, open_count, opens_per_100, router_count, playbook_count, principle_count
  - In-memory transcript store with `reset_hook_store()` utility
- **Added**: Test suite for hook effectiveness
  - `backend/tests/test_hooks_ingest.py` - Ingest endpoint tests
  - `backend/tests/test_hooks_effectiveness.py` - Effectiveness metrics tests
  - `backend/tests/conftest.py` - Test isolation fixtures
- **Modified**: `backend/app/main.py` - Added hooks router inclusion
- **Modified**: `feature-plan.json` - Updated current_feature to hook-effectiveness-analyzer, added test paths

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added
- FastAPI backend with health endpoint (`/api/health`)
- React + TypeScript + Vite frontend with health dashboard
- Docker Compose with backend, frontend, and Keycloak services
- SQLite persistent storage with SQLAlchemy
- CORS configuration for local development
- Backend pytest test for health endpoint
- Frontend vitest test for App component
- MIT License
- Comprehensive README with architecture diagram
- .env.example with all configuration options
- .gitignore excluding dependencies, build outputs, secrets

### Security
- OIDC Keycloak authentication configured (SPA PKCE flow)
- Demo mode with localhost binding and production refusal
- Non-root Docker users
- Healthchecks on all services

### Changed
- Agent workflow orchestration engine implemented:
  - POST /api/workflows creates a workflow run with provider-qualified reviewers (claude/codex)
  - GET /api/workflows/{id} returns status and collected reviews
  - Cross-provider dispatch: claude -> codex exec, codex -> claude -p
  - Incomplete verdict when any reviewer fails
  - In-memory workflow store with async background execution
- Workflow models: Provider (CLAUDE/CODEX), ReviewStatus, WorkflowStatus, Reviewer, Review, WorkflowCreate, WorkflowRun, WorkflowRunResponse
- Backend tests for workflow endpoints (test_create_workflow, test_get_workflow, test_get_nonexistent_workflow)

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added
- FastAPI backend with health endpoint (`/api/health`)
- React + TypeScript + Vite frontend with health dashboard
- Docker Compose with backend, frontend, and Keycloak services
- SQLite persistent storage with SQLAlchemy
- CORS configuration for local development
- Backend pytest test for health endpoint
- Frontend vitest test for App component
- MIT License
- Comprehensive README with architecture diagram
- .env.example with all configuration options
- .gitignore excluding dependencies, build outputs, secrets

### Security
- OIDC Keycloak authentication configured (SPA PKCE flow)
- Demo mode with localhost binding and production refusal
- Non-root Docker users
- Healthchecks on all services

### Changed
- Agent workflow orchestration engine implemented:
  - POST /api/workflows creates a workflow run with provider-qualified reviewers (claude/codex)
  - GET /api/workflows/{id} returns status and collected reviews
  - Cross-provider dispatch: claude -> codex exec, codex -> claude -p
  - Incomplete verdict when any reviewer fails
  - In-memory workflow store with async background execution
- Workflow models: Provider (CLAUDE/CODEX), ReviewStatus, WorkflowStatus, Reviewer, Review, WorkflowCreate, WorkflowRun, WorkflowRunResponse
- Backend tests for workflow endpoints (test_create_workflow, test_get_workflow, test_get_nonexistent_workflow)

Partial code published for continued development. Known issues: STATUS.md.

## [1.2.0] - 2024-10-24

### Added
- FastAPI backend with health endpoint (`/api/health`)
- React + TypeScript + Vite frontend with health dashboard
- Docker Compose with backend, frontend, and Keycloak services
- SQLite persistent storage with SQLAlchemy
- CORS configuration for local development
- Backend pytest test for health endpoint
- Frontend vitest test for App component
- MIT License
- Comprehensive README with architecture diagram
- .env.example with all configuration options
- .gitignore excluding dependencies, build outputs, secrets

### Security
- OIDC Keycloak authentication configured (SPA PKCE flow)
- Demo mode with localhost binding and production refusal
- Non-root Docker users
- Healthchecks on all services
