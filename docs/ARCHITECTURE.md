# WindConfig AI Architecture

## Architecture Goal

WindConfig AI is a local-first full-stack application. The architecture should be simple enough to run on a personal desktop, but structured enough to demonstrate professional engineering judgment.

The system separates deterministic business correctness from AI assistance. Backend validation decides whether a configuration is valid. The AI assistant helps users understand, summarize, compare, and investigate configurations.

## High-Level Components

Frontend:
- React for UI.
- TypeScript for type safety.
- Vite for fast local development.
- Tailwind CSS and shadcn/ui for a polished enterprise interface.
- TanStack Query for server state, caching, loading states, and mutation handling.
- Playwright for end-to-end testing.

Backend:
- FastAPI for APIs.
- Pydantic for request and response schemas.
- SQLAlchemy for database models and queries.
- Alembic for migrations.
- uv for Python dependency and environment management.
- pytest for backend tests.

Database:
- PostgreSQL stores structured application data such as contracts, wind farms, turbines, alarm categories, availability configurations, drafts, and published states.

Vector Store:
- Chroma stores embeddings for local knowledge base documents and selected configuration summaries.
- Chroma is preferred over FAISS for this project because persistence and local development ergonomics matter.

LLM:
- Ollama runs a local model such as Qwen, Llama, Gemma, or Mistral.
- The project should support model configuration through environment variables.
- No paid API key should be required.

Embeddings:
- Use a local embedding model such as Nomic or BGE.
- Embeddings are used for retrieval over synthetic alarm guidance, availability rules, and configuration help documents.

Runtime:
- Docker Compose coordinates PostgreSQL, Chroma, backend, and frontend.
- Ollama can run either through Docker or as a local desktop service, depending on the machine setup.

## Core User Flow

1. User opens the frontend dashboard.
2. Frontend fetches contract cards from the FastAPI backend.
3. User selects a contract.
4. Frontend loads contract details, turbines, alarm categories, draft state, and configuration progress.
5. User opens the availability configuration wizard.
6. User fills four steps: Basic Details, Turbines and Production Periods, Formula and Alarm Categories, Details and Optional Extras.
7. Frontend sends save requests to the backend.
8. Backend validates input with Pydantic and business rules.
9. Backend stores structured data in PostgreSQL.
10. Backend stores draft snapshots as JSON for version comparison and prepopulation.
11. User asks the AI assistant for a summary, explanation, or readiness review.
12. Backend retrieves relevant context from Chroma and sends a grounded prompt to Ollama.
13. Backend returns the AI response to the frontend.

## Data Ownership

PostgreSQL owns:
- Contracts (including order reason, sales document number, customer list).
- Wind farms, turbine groups, and contract-scoped turbines.
- Production periods, alarm categories, and nested alarms.
- Availability configurations (`availability_configurations` headers by GUID, `created_by` / `updated_by`).
- Versioned configuration snapshots (`configuration_versions` JSONB v2 payloads, checksums, and publish state).

Chroma owns:
- Embedded knowledge base chunks.
- Optional embedded summaries of contract configuration snapshots.

Ollama owns:
- Local LLM inference only.
- It should not be treated as the system of record.

The frontend owns:
- UI state.
- Form state.
- Query cache.
- User interactions.

## AI Responsibilities

The AI assistant can:
- Summarize a contract configuration.
- Explain why validation errors matter.
- Compare two draft snapshots in plain English.
- Answer domain questions using local retrieved context.
- Produce a publish-readiness report.
- Convert technical configuration JSON into business-readable language.

The AI assistant must not:
- Decide that an invalid configuration is valid.
- Mutate data without explicit user action.
- Replace backend validation.
- Invent proprietary rules.
- Require paid APIs.

## Backend Validation Responsibilities

The backend should enforce rules such as:
- Contract end date must be after start date.
- Required basic details must be present before publish.
- Every turbine must belong to a group before publish.
- Required production periods must exist.
- Required alarm categories must be selected.
- Optional extras must include dependent fields when enabled.
- Published configurations must not have blocking validation errors.

## API Shape

API groups:
- `/api/v1/health`
- `/api/v1/catalog` and `/api/v1/users`
- `/api/v1/contracts` and `/api/v1/contracts/{contract_id}`
- `/api/v1/contracts/{contract_id}/availability-configurations` (create, list, get, delete by GUID)
- `/api/v1/contracts/{contract_id}/availability-configurations/{acid}/drafts` (OCC save)
- `/api/v1/contracts/{contract_id}/availability-configurations/{acid}/versions` (history, readiness, publish)
- `/api/v1/contracts/{contract_id}/availability-configurations/{acid}/diff`
- `/api/v1/contracts/{contract_id}/ai/summary` (Milestone 7)
- `/api/v1/contracts/{contract_id}/ai/readiness` (Milestone 7)
- `/api/v1/contracts/{contract_id}/ai/compare-drafts` (Milestone 7)
- `/api/v1/ai/chat` (Milestone 7)

Exact schemas will be finalized when backend models are implemented.

## Local Development Principle

The project should always have a non-AI path. If Ollama or Chroma is not running, the core contract dashboard, wizard, draft save, and publish validation should still work.

This makes the project easier to demo and shows that AI is integrated responsibly rather than being a fragile dependency.
