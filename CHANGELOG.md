# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

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

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-24

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
