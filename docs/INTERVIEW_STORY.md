# WindConfig AI Interview Story

## Elevator Pitch

WindConfig AI is a local-first AI copilot for wind farm contract and turbine configuration management. It models a realistic enterprise workflow where users manage contracts, group turbines, define production periods, configure alarm categories, set availability rules, save drafts, publish configurations, and use a local AI assistant to summarize, validate, compare, and explain configurations.

The project is designed to show practical AI integration in a domain workflow, not just a generic chatbot.

## Target Users

TPMs:
- Coordinate contract setup and review.
- Track draft and published configuration state.
- Use AI to summarize configurations and identify missing information before publish.

Site Managers:
- Understand turbine grouping, production periods, alarms, and downtime options.
- Use AI to explain configuration gaps in plain language.

Contract Managers:
- Review contract dates, customer visibility, availability percentage, downtime rules, and optional extras.
- Use AI to generate business-readable summaries.

Operations Analysts:
- Investigate alarm categories and turbine configuration status.
- Use RAG search to answer questions from local synthetic knowledge documents.

## Practical Business Value

The product helps users handle complex configuration data with fewer mistakes.

Without the copilot, a user may manually inspect many turbines, groups, production periods, alarm categories, optional downtime settings, and draft JSON snapshots. This is slow and error-prone.

With the copilot, the user can ask:
- Is this contract ready to publish?
- Which turbines are missing production periods?
- What changed since the previous draft?
- Summarize this contract for a site manager.
- Explain why this alarm category matters.

The system can respond with a plain-English explanation while backend validation remains responsible for correctness.

## Technical Architecture Explanation

Frontend:
- React, TypeScript, Vite, Tailwind CSS, and shadcn/ui provide the user interface.
- TanStack Query manages server state, loading states, caching, and mutations.

Backend:
- FastAPI exposes REST APIs.
- Pydantic validates request and response data.
- SQLAlchemy maps Python models to PostgreSQL tables.
- Alembic manages database schema migrations.
- pytest verifies backend behavior.

Data:
- PostgreSQL stores structured business data.
- Draft configurations are stored as JSON snapshots for reload and comparison.

AI:
- Ollama runs a local LLM such as Qwen, Llama, Gemma, or Mistral.
- Local embeddings such as Nomic or BGE convert documents into vectors.
- Chroma stores vector embeddings for local retrieval.
- The backend retrieves relevant context and sends grounded prompts to the local model.

Runtime:
- Docker Compose runs the local services.
- The app does not require paid APIs or external cloud services.

## Why The Architecture Is Resume-Worthy

This project demonstrates:
- Full-stack development with React and FastAPI.
- Type-safe frontend development with TypeScript.
- Backend validation and database modeling.
- PostgreSQL, SQLAlchemy, and Alembic.
- Local AI integration through Ollama.
- RAG architecture with local embeddings and Chroma.
- Docker-based local development.
- Automated testing with pytest and Playwright.
- CI/CD basics with GitHub Actions.
- Domain-driven product thinking.

## Example Interview Explanation

"I built WindConfig AI as a local-first AI copilot for wind farm contract configuration. The idea was to model a realistic enterprise workflow from the wind domain: contract cards, turbines, production periods, alarm categories, availability rules, draft saves, and publishing. The AI layer helps users summarize configurations, explain validation errors, compare draft versions, and answer questions from a local knowledge base. I used FastAPI, Pydantic, SQLAlchemy, PostgreSQL, React, TypeScript, TanStack Query, Chroma, local embeddings, and Ollama. I intentionally kept the system free and local, with no paid APIs."

## Likely Interview Questions

### Why did you build this project?

I wanted to build an AI project that connects to a real enterprise workflow instead of creating a generic chatbot. Since I understand wind domain workflows, I modeled contract and turbine configuration and added AI where it has practical value: explanation, summarization, draft comparison, and knowledge retrieval.

### Why use local AI instead of a hosted API?

The project is designed to run for free on a local desktop without paid API keys. Local AI also makes sense for enterprise-style workflows where data sensitivity matters. Even though this project uses synthetic data, the architecture demonstrates privacy-aware AI design.

### What does RAG mean in this project?

RAG means retrieval augmented generation. The app stores local knowledge documents as embeddings in Chroma. When the user asks a question, the backend retrieves relevant document chunks and sends them to the local LLM as context. This grounds the answer in project-specific knowledge.

### Why not let AI validate everything?

AI is useful for explanation, but deterministic backend rules should decide correctness. For example, contract end date validation, required fields, turbine grouping, and publish blockers should be enforced by backend logic. The AI can explain those errors in plain English.

### What happens if Ollama is not running?

The core app should still work. Users can manage contracts, save drafts, and publish valid configurations. AI features should show a clear unavailable message rather than breaking the main workflow.

### How is this different from a chatbot?

The AI is embedded inside a real workflow. It has access to contract state, draft versions, validation results, and local knowledge documents. It supports specific user tasks instead of acting as a general conversation tool.

## Resume Bullet Drafts

- Built a local-first AI copilot for wind farm contract configuration using React, TypeScript, FastAPI, PostgreSQL, Chroma, and Ollama.
- Implemented draft and publish workflows with backend validation, JSON snapshots, and AI-assisted configuration summaries.
- Designed a RAG pipeline with local embeddings and Chroma to answer domain-specific questions without paid APIs.
- Added AI-assisted draft comparison and publish-readiness reporting for complex turbine availability configurations.
- Containerized the application with Docker Compose and planned automated validation through pytest, Playwright, and GitHub Actions.
