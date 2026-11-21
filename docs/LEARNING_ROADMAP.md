# WindConfig AI Learning Roadmap

## Learning Goal

The goal is not only to build a project, but to understand it well enough to explain every major part in an interview. Each milestone should produce working software and a clear mental model.

## Milestone 1: Project Setup

Learn:
- What a monorepo is and why frontend, backend, and infrastructure can live together.
- How Vite creates a fast React development environment.
- How FastAPI starts an API server.
- How Docker Compose runs local services together.
- How environment variables keep local configuration flexible.

You should be able to explain:
- Why this project is local-first.
- Why the project is split into frontend and backend.
- What Docker Compose gives you during development.

## Milestone 2: Backend Foundation

Learn:
- FastAPI routers and route handlers.
- Dependency injection in FastAPI.
- Pydantic schemas for validating request and response data.
- SQLAlchemy model basics.
- Database session management.
- Why API versioning starts with `/api/v1`.

You should be able to explain:
- The difference between an API schema and a database model.
- Why validation belongs on the backend.
- How a request flows through FastAPI.

## Milestone 3: Database and Seed Data

Learn:
- PostgreSQL basics for relational application data.
- SQLAlchemy relationships.
- Alembic migrations.
- Synthetic seed data design.
- How domain entities connect: contracts, wind farms, turbines, groups, alarms, drafts, and configurations.

You should be able to explain:
- Why PostgreSQL is better than JSON files alone for this app.
- What Alembic migrations do.
- How seed data helps demos and tests.

## Milestone 4: Frontend Dashboard

Learn:
- React component structure.
- TypeScript interfaces for API data.
- Tailwind CSS utility styling.
- shadcn/ui component usage.
- TanStack Query for fetching, caching, loading states, errors, and mutations.

You should be able to explain:
- Why TanStack Query is used instead of storing server data in Redux.
- How the dashboard maps backend data into user-facing status.
- How UI state differs from server state.

## Milestone 5: Availability Configuration Wizard

Learn:
- Multi-step form design.
- Form state and validation.
- Saving partial progress.
- Editing and prepopulating existing data.
- Modeling user workflows in frontend routes and components.

You should be able to explain:
- Why a wizard fits this domain.
- How draft prepopulation works.
- How the UI helps prevent configuration mistakes.

## Milestone 6: Draft and Publish Workflow

Learn:
- Draft state versus published state.
- JSON snapshots.
- Version comparison.
- Business validation before publish.
- Auditability and traceability.

You should be able to explain:
- Why draft JSON snapshots are useful.
- Why publish should be stricter than save draft.
- Why deterministic rules are safer than relying on AI for correctness.

## Milestone 7: Local AI and RAG Assistant

Learn:
- What Ollama does.
- How local LLMs differ from paid hosted APIs.
- What embeddings are.
- What vector search is.
- What Chroma stores.
- What RAG means: retrieval augmented generation.
- How prompts are grounded with retrieved context.
- How to handle AI unavailability gracefully.

You should be able to explain:
- Why this is not just a chatbot.
- How the AI answer is grounded in local documents.
- Why the AI explains and summarizes, while backend validation decides correctness.
- Why no paid API keys are required.

## Milestone 8: Testing and CI

Learn:
- pytest for backend unit and API tests.
- Playwright for frontend end-to-end tests.
- Test data setup.
- GitHub Actions workflow basics.
- What should be tested at unit, integration, and end-to-end levels.

You should be able to explain:
- Which flows are most important to test.
- Why CI matters for a portfolio project.
- How tests increase confidence when adding AI features.

## Milestone 9: Resume and Interview Polish

Learn:
- How to write project documentation for recruiters and engineers.
- How to explain architecture clearly.
- How to turn implementation details into resume bullets.
- How to prepare a demo script.

You should be able to explain:
- The product problem.
- The target users.
- The full technical flow.
- The practical AI use cases.
- Tradeoffs and limitations.

## Study Method

For each milestone:
- Build the smallest useful version.
- Read the code after it works.
- Update session notes.
- Write three interview questions and answers.
- Commit the stable state.

This keeps learning attached to working software instead of disconnected theory.
