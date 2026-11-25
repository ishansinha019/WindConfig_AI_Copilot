# WindConfig AI Project Roadmap

## Project Goal

Build a local-first AI copilot for wind farm contract and turbine configuration management. The product models a realistic enterprise workflow: contract cards, turbine grouping, production periods, alarm categories, availability settings, draft saving, publishing, and AI-assisted review.

The project must be free to run locally. It should not require paid API keys or cloud services.

## Product Summary

WindConfig AI helps TPMs, site managers, contract managers, and operations analysts configure wind farm availability rules with fewer mistakes. Users can manage contracts, organize turbines into sections, apply production periods, select alarm categories, configure availability rules, save drafts, publish configurations, and ask a local AI assistant for summaries, validation explanations, and draft comparisons.

## Milestone 1: Project Setup

Purpose: create a clean full-stack foundation that is easy to run locally.

Build:
- Monorepo structure with `frontend`, `backend`, `docs`, and later `infra`.
- React + TypeScript + Vite frontend.
- FastAPI backend managed with `uv`.
- Docker Compose with PostgreSQL, backend, frontend, Chroma, and optional Ollama connection.
- Basic README with local setup commands.

Success criteria:
- Frontend starts locally.
- Backend health endpoint responds.
- Docker Compose can start PostgreSQL.
- Documentation explains how to run the project.

## Milestone 2: Backend Foundation

Purpose: establish the backend patterns before adding business complexity.

Build:
- FastAPI app structure with routers, services, schemas, models, and database session management.
- Pydantic request and response schemas.
- SQLAlchemy database models.
- Alembic migration setup.
- Health endpoint and basic API versioning under `/api/v1`.

Success criteria:
- Backend has a clear layered structure.
- Database connection works.
- First migration can create tables.
- pytest can run at least one backend test.

Status: completed for the contracts foundation. The API has layered routing,
service, schema, model, session, migration, seed, and test coverage for
contracts. Additional domain models belong to Milestone 3.

## Milestone 3: Database and Seed Data

Purpose: create realistic synthetic data without using proprietary information.

Build:
- Contract model.
- Wind farm model.
- Turbine model.
- Turbine group or section model.
- Production period model.
- Alarm category model.
- Availability configuration model.
- Draft snapshot model storing structured JSON.
- Synthetic seed data for multiple contracts, wind farms, turbines, and alarm categories.

Success criteria:
- Local database can be seeded.
- API can list contracts and contract details.
- Seed data is clearly synthetic and domain-inspired.

Current scope: contracts now have seeded wind farms, turbine groups, turbines,
production periods, and alarm categories. Availability configurations and draft
snapshots remain intentionally deferred to the configuration-workflow milestones.

## Milestone 4: Frontend Dashboard

Purpose: make the product feel like a real enterprise workflow, not a generic demo.

Build:
- Contract dashboard with card or compact grid view.
- Contract status indicators such as draft, published, needs review, and missing data.
- Contract detail page.
- Turbine overview with table and simple map-like layout or operational grid.
- TanStack Query setup for API fetching and caching.
- shadcn/ui component foundation.

Success criteria:
- User can see multiple contracts.
- User can open one contract.
- UI shows turbines, status, and key configuration progress.
- Server data is fetched through TanStack Query.

## Milestone 5: Availability Configuration Wizard

Detailed plan: see `docs/AVAILABILITY_CONFIG_MILESTONES.md` (milestones A1–A9),
which supersedes the bullet list below and reworks Milestone 6 versioning to be
per availability configuration instead of per contract.

Purpose: model the main domain workflow in a way that resembles real contract configuration.

Build:
- Step 1: Basic Details.
- Step 2: Turbines and Production Periods.
- Step 3: Formula and Alarm Categories.
- Step 4: Details and Optional Extras.
- Left navigation pane showing the four steps.
- Form validation and save state per step.
- Data prepopulation when editing an existing draft.

Success criteria:
- User can move through all four steps.
- User can edit and review configuration data.
- Existing draft data prepopulates the wizard.
- Required fields are visibly validated.

## Milestone 6: Draft and Publish Workflow

Status: Completed. Hybrid JSONB versioning, OCC conflict handling, deterministic readiness validation, and diffing engine are implemented, migrated in Postgres, tested with pytest, and integrated into the frontend dashboard.

Purpose: show enterprise-grade state handling and traceability.

Build:
- Save as draft.
- Publish configuration.
- Store draft snapshots as JSON.
- Track draft versions.
- Compare latest draft with previous draft.
- Backend validation rules before publish.

Success criteria:
- Drafts persist and reload correctly.
- Published configuration cannot have blocking validation errors.
- User can compare two draft versions.
- Backend owns deterministic validation logic.

## Milestone 7: Local AI and RAG Assistant

Purpose: add practical AI features without paid APIs.

Build:
- Ollama integration for local LLM calls.
- Local embedding model integration, preferably Nomic or BGE.
- Chroma vector store for persistent local retrieval.
- Knowledge base documents for synthetic alarm rules, availability concepts, and configuration guidance.
- AI assistant panel inside the contract/configuration experience.

AI capabilities:
- Summarize a contract configuration.
- Explain validation errors in plain English.
- Answer questions using retrieved knowledge base context.
- Compare draft versions and explain changes.
- Generate a publish-readiness report.

Success criteria:
- AI works locally through Ollama.
- RAG answers include retrieved context.
- AI does not replace backend validation.
- App still works when AI is unavailable, with graceful messaging.

## Milestone 8: Testing and CI

Purpose: make the project credible as an engineering portfolio project.

Build:
- pytest backend tests for API endpoints, validation rules, and draft workflow.
- Playwright frontend tests for dashboard and wizard flows.
- GitHub Actions workflow for linting and tests.
- Example test data and test database configuration.

Success criteria:
- Tests run locally.
- CI runs on pull request or push.
- Critical product paths are covered.

## Milestone 9: Resume and Interview Polish

Purpose: turn the project into a story that helps in screening and interviews.

Build:
- Strong README with architecture diagram, screenshots, local setup, and demo flow.
- Resume bullet points.
- Interview explanation.
- Technical decision record.
- Short demo script.

Success criteria:
- You can explain the project in 60 seconds.
- You can explain each technology choice.
- You can answer why local AI, RAG, PostgreSQL, Chroma, Docker, tests, and CI were used.

## Build Rhythm

Each milestone should end with:
- Working code or completed documentation.
- Updated `docs/SESSION_NOTES.md`.
- Updated learning notes.
- A short explanation of what was built and why.
- A Git commit once the milestone is stable.
