# WindConfig AI Session Notes

## Current Status

Milestone 1 project setup has been scaffolded and verified. The project now has a frontend shell, backend health endpoint, Docker Compose file, environment examples, setup README, and working local container stack.

## Completed Decisions

- The project will be created as a new sibling folder named `WindConfig_AI_Copilot`.
- It will remain separate from the existing `Predictive_Part_Failure_Dashboard`.
- The project will be local-first and free to run.
- No paid API keys or cloud services are required.
- All data will be synthetic and domain-inspired.
- The AI assistant will explain, summarize, compare, and support validation review.
- Backend deterministic rules will own correctness.
- PostgreSQL will store structured data.
- Chroma will store vector embeddings.
- Ollama will run the local LLM.
- Local embedding models such as Nomic or BGE will be used.
- Milestone 1 uses a clean monorepo structure with `frontend`, `backend`, `infra`, and `docs`.
- The first backend endpoint is `/api/v1/health`.
- The first frontend screen is an app shell that checks backend health through TanStack Query.

## Documentation Added

- `docs/PROJECT_ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/LEARNING_ROADMAP.md`
- `docs/INTERVIEW_STORY.md`
- `docs/SESSION_NOTES.md`

## Milestone 1 Files Added

- `README.md`
- `docker-compose.yml`
- `backend/pyproject.toml`
- `backend/Dockerfile`
- `backend/.env.example`
- `backend/app/main.py`
- `backend/app/api/v1/health.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/Dockerfile`
- `frontend/.dockerignore`
- `frontend/.env.example`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/components/HealthStatus.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/styles.css`
- `backend/.dockerignore`

## Next Build Step

Milestone 2: Backend Foundation.

Planned tasks:
- Begin SQLAlchemy, Alembic, database session, and API layering in Milestone 2.
- Add backend dependency verification through Docker or local `uv`.
- Add first database migration.
- Add a contracts router placeholder backed by synthetic data or database models.

## Commands Used

- `New-Item -ItemType Directory -Force ...` to create project structure.
- `apply_patch` to add Milestone 1 files.
- `npm.cmd install` to install frontend dependencies and create lockfile.
- `npm.cmd run lint` passed.
- `npm.cmd run build` passed when run outside the sandbox.
- `docker compose config` passed.
- `docker compose build` passed.
- `docker compose build frontend` passed after adding Docker ignore files and switching frontend Dockerfile to `npm ci`.
- `docker compose up -d` passed.
- `Invoke-RestMethod http://localhost:8000/api/v1/health` returned `status=ok` and `service=windconfig-ai-backend`.
- `Invoke-WebRequest http://localhost:5173` returned HTTP 200.
- `docker compose down` stopped and removed the Milestone 1 containers.

## Open Questions

- Which local Ollama model should be the default for the first AI milestone?
- Should Ollama run through Docker Compose or as an already-installed desktop service?
- Should the first UI use a table-heavy enterprise layout or a more visual wind farm dashboard?
- Python launcher exists, but the detected Python 3.14 installation does not have pip available.
- `uv` was not found in the quick PATH check. Install or expose `uv` before local backend dependency setup, or use Docker for backend execution.
- npm reported two audit findings after frontend install. Do not run forced audit fixes without reviewing breaking changes.

Recommended defaults:
- Start with a lightweight Ollama model that runs comfortably on the local machine.
- Treat Ollama as an external local service at first.
- Build an enterprise-style dashboard first, then add a simple visual turbine layout.

## Handoff Note

If this chat context is compacted or a new thread is started, read this file first, then read:

1. `docs/PROJECT_ROADMAP.md`
2. `docs/ARCHITECTURE.md`
3. `docs/LEARNING_ROADMAP.md`
4. `docs/INTERVIEW_STORY.md`

Then continue with Milestone 1.
