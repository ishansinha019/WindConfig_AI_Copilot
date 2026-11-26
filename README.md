# WindConfig AI Copilot

Local AI copilot for wind farm contract and turbine configuration management.

This project is designed as a resume-ready, local-first full-stack application. It models contract cards, turbine configuration, production periods, alarm categories, availability settings, draft saves, publishing, and AI-assisted review.

The project uses synthetic domain-inspired data only. It does not use proprietary company data.

## Milestone Status

- Milestone 1: Project setup in progress.
- Milestone 2: Backend foundation next.
- Milestone 3+: Database, frontend workflow, draft/publish, local AI, testing, and interview polish.

## Tech Stack

Frontend:
- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- shadcn/ui later in the UI milestone

Backend:
- FastAPI
- Pydantic
- SQLAlchemy later in Milestone 2
- Alembic later in Milestone 2
- uv for Python dependency management

Local services:
- PostgreSQL
- Chroma later in the AI milestone
- Ollama as a local LLM runtime later in the AI milestone

Testing:
- pytest
- Playwright later in the frontend testing milestone

## Project Structure

```txt
WindConfig_AI_Copilot/
  backend/
    app/
      api/v1/
      core/
      schemas/
      main.py
    tests/
    pyproject.toml
    Dockerfile
  frontend/
    src/
      components/
      pages/
      lib/
    package.json
    Dockerfile
  docs/
  infra/
  docker-compose.yml
```

## Local Development

### Prerequisites

Install these locally:
- Node.js 20 or newer
- npm
- Python 3.12
- uv
- Docker Desktop

### Backend

From `backend`:

```bash
uv sync
uv run alembic upgrade head
uv run python -m app.db.seed
uv run fastapi dev app/main.py
```

Health endpoint:

```txt
http://localhost:8000/api/v1/health
```

### Frontend

From `frontend`:

```bash
npm install
npm run dev
```

Frontend URL:

```txt
http://localhost:5173
```

### Docker Compose

From the project root:

```bash
docker compose up --build
```

This starts:
- PostgreSQL on port `5432`
- Backend on port `8000`
- Frontend on port `5173`

On backend startup, the container applies the Alembic migrations and seeds six
synthetic demo contracts, with contract-specific turbines, alarm categories
and configurations. Restarting the stack does not duplicate that seed data.
An upgrade keeps the original fleets and saved versions; use a separate fresh
database to see the expanded demo fleets without deleting the original data.

Available backend endpoints:

```txt
GET /api/v1/health
GET /api/v1/contracts
GET /api/v1/contracts/{contract_id}
```

## Environment

Backend environment variables are documented in `backend/.env.example`.

The default local database URL is:

```txt
postgresql+psycopg://windconfig:windconfig@localhost:5432/windconfig
```

Inside Docker Compose, the backend uses:

```txt
postgresql+psycopg://windconfig:windconfig@postgres:5432/windconfig
```

## Current Demo Flow

The current foundation provides:
- A contract home page and separate detail page, with a backend health check.
- PostgreSQL-backed contracts with separate configuration histories and
  contract-specific turbines and nested alarms.
- Automatic migration and synthetic demo-data seeding in Docker Compose.
- Backend tests that run without Docker: `uv run --extra dev pytest` from `backend`.

The existing draft/publish API still operates on each contract's default
configuration. Editing multiple configurations, the carousel, the wizard,
and local AI are later milestones.

## Documentation

Start here:
- `docs/AVAILABILITY_CONFIG_MILESTONES.md` (active work plan and agent handoff)
- `docs/PROJECT_ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/LEARNING_ROADMAP.md`
- `docs/INTERVIEW_STORY.md`
- `docs/SESSION_NOTES.md`
