# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Conflow is a **pnpm + Turbo monorepo** — an IT collaboration platform for university study teams providing meeting summarization, blocker detection, and sprint management. It uses an **A2UI-ready** (AI-to-UI) architecture where business logic is headless and invocable by LangGraph agents.

## Common Commands

### Monorepo (root)

- `pnpm dev` — run all services via Turborepo
- `pnpm build` — build all packages/apps
- `pnpm test` — run all tests
- `pnpm typecheck` — TypeScript type checking
- `pnpm lint` — lint all packages

### Frontend (apps/web)

- `pnpm --filter @conflow/web dev` — start Vite dev server (port 3000)
- `pnpm --filter @conflow/web build` — production build
- `pnpm --filter @conflow/web typecheck` — type check frontend only

### Backend (server/)

- `cd server && uv run uvicorn main:app --reload` — start FastAPI dev server (port 8000)
- `cd server && uv run pytest` — run all Python tests
- `cd server && uv run pytest tests/test_health.py` — run a single test file
- `cd server && uv run ruff check .` — lint Python code
- `cd server && uv run ruff format .` — format Python code
- `cd server && uv sync --group agent --group dev` — install all dependency groups

### Docker

- `docker compose up db` — start PostgreSQL only
- `docker compose up` — start all services (db, backend, rag, frontend)

### Database Migrations

- `cd server && uv run alembic upgrade head` — apply migrations
- `cd server && uv run alembic revision --autogenerate -m "description"` — create migration

## Architecture

### Monorepo Layout

```
apps/web/          — Vite + React 18 + Tailwind CSS frontend
packages/core/     — Shared infra: Axios client, Zod validation, date/string utils
packages/ui/       — Atomic React components (Button, Card, Avatar, etc.)
packages/rag/      — Python RAG service (FastAPI, port 8001) with pgvector
server/            — FastAPI backend + LangGraph multi-agent system
docs/              — Architecture docs, wireframes, agent guides
```

**Dependency flow**: `apps/web` → `packages/ui` → `packages/core`

### Backend Structure (server/src/app/)

- **core/**: Infrastructure — database (async SQLAlchemy + PostgreSQL), security (JWT), LLM factory, middlewares, config
- **agent/graphs/**: LangGraph agents — `supervisor_graph.py` routes to specialized workers: `meeting_summary`, `blocker_triage`, `retro_insights`, `user_query`, `file/analysis_file`
- **sandbox/**: Runtime security for AI agent execution (syscall blocking, path validation)
- **Domain modules**: `user/`, `team/`, `sprint/`, `backlog/`, `board/`, `inbox/`, `week/`, `retro/`, `planning/` — each with `api.py`, `model.py`, `schemas.py`, `service.py`
- **websockets/**: Real-time signaling (Huddle, DM)
- **common/**: Cross-cutting — idempotency (Redis), circuit breaker, caching, storage

### Agent Modes

Set via `CONFLOW_AGENT_MODE` env var:

- `mock` — deterministic stubs, no API calls (for testing)
- `llm` — real OpenAI calls
- `ollama` — local Ollama server
- `vllm` — OpenAI-compatible vLLM endpoint

### Key Tech Stack

- **Frontend**: Vite 8, React 18, Tailwind CSS 4, TypeScript 5.7
- **Backend**: FastAPI, SQLAlchemy 2 (async), PostgreSQL 16 + pgvector, Supabase auth
- **AI/Agents**: LangGraph, LangChain, OpenAI (gpt-4o-mini default)
- **Infra**: Docker Compose, uv (Python), pnpm 9 + Turborepo, Redis, Celery + APScheduler
- **Python**: 3.13+, ruff for linting/formatting, pytest for testing

## Coding Standards

From `.cursorrules`:

- **Immutability**: No `let` — always `const`. Use `map`/`filter`/`reduce`.
- **No `any`**: Use `unknown` or strict interfaces.
- **Zod validation**: Mandatory for all external data (API responses, AI outputs).
- **Layer isolation**: No circular dependencies between packages.
- **Headless logic**: Features in business layer must be decoupled from React lifecycle for A2UI agent invocation.
- **Schema-first**: Every feature needs defined Input/Output Schema (Zod) for AI interoperability.
- **Python**: ruff with `line-length = 100`, target `py313`, select rules `E, F, I, UP`.

## Environment Variables

Key variables (see `.env.example`):

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` — PostgreSQL connection
- `SUPABASE_URL`, `SUPABASE_KEY` — authentication
- `OPENAI_API_KEY` — LLM provider
- `CONFLOW_AGENT_MODE` — agent execution mode (mock/llm/ollama/vllm)
- `REDIS_URL` — for idempotency/caching (optional)
- `CORS_ALLOWED_ORIGINS` — frontend origin allowlist
