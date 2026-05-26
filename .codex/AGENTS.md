# AGENTS.md — Conflow (OpenCode High-Signal Repo Guidance)

**Do not blindly rewrite. Only update if something high-signal has changed; remove anything outdated or generic.**

---

## Essential Repo Facts — If you miss these, you'll break things

- **Monorepo flow is strict:**
  - `apps/web` (UI/routing) → `packages/business` (logic) → `packages/ui` (dumb UI) → `packages/core` (infra, adapters, utils, no logic)
  - No business logic in `core` or `ui` packages. Do not import up the layer chain.
  - `core`: NO UI, NO business logic. Only infra, adapters, stateless util.
  - `ui`: NO logic, NO data fetch, only display. Pure atomic component library.
  - `business`: Entities/ (zod domain schemas and state only), Features/ (user actions, logic, A2UI requirements).
- **Frontend is TanStack Start (SSR).** Use server functions for any data mutation or DB/API call. Never do such work on the client.
- **Every feature in `business/features/` must:**
  - Be lifecycle-agnostic (headless, callable outside UI)
  - Export strict Input/Output Zod schemas for AI interoperability
  - Log context for all main actions (feature id, runtime, status)
- **Strict Immutability & Purity:**
  - NO `let` (disable), use `const` everywhere; rely on functional transforms (`map`, `filter`, `reduce`)
  - NO `any`; use `unknown` or explicit types
  - Self-documenting types, max one-liner comments (no filler)
- **SSR First & Preloading:**
  - Always preload dashboard data in Loaders. Never allow layout shift (fetch only once, at load time).
- **Event boundaries:**
  - ALWAYS use skeleton + error boundary on all dashboard widgets so one crash doesn't take out the whole app
- **State:** TanStack Query only. Never mutate state directly.
- **Do NOT create or run any install/build/lint/test commands:** Only output the suggested command as a code block for review. User must run it. Never modify system state.
- **Workspace commands:**
  - Always run from repo root unless editing only the backend (`server/`) (see below).
  - Top-level package manager is `pnpm` (no npm, no yarn), with Turbo for scripts.
  - Strict node/engine versioning: see package.json `engines`.
  - **Common top-level commands:**
    - `pnpm install`
    - `pnpm dev`, `pnpm build`, `pnpm test`, `pnpm lint`, `pnpm typecheck` — all routed via Turbo
  - To run only the web/frontend: `cd apps/web && pnpm dev` (for SSR/dev server)
  - To run only tests/lint on a subpackage, use Turbo or direct script from that package.

---

## Backend/Agent (Python/FastAPI/LangGraph — server/)

- Work in `server/`, not repo root; use `uv` for all Python commands.
- Entrypoint: `server/main.py` (`uvicorn main:app`)
- Test: `uv run pytest` (or `uv run pytest <file>`)
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Migrate: `uv run alembic <cmd>`
- Install: `uv sync --group agent --group dev`
- Place all AI/agent code under `src/app/agent/`; use typed, documented Pydantic models at boundaries; mock LLM mode (`CONFLOW_AGENT_MODE=mock`) is default for local/dev validation and demo (LLM/inference is only used if key and explicit override given).
- Agent graphs:
  - Well-known: `meeting_summary`, `user_query`, `blocker_triage`, `retro_insights`, `file_analysis`, `search` (see docs/agent-purpose.md and multi-agent-guide.md for field shapes)
  - See scripts/smoke\_\*.py for rapid pipeline/graph contract checks (no API/init overhead)
- Use `.env.example` for required configuration; never record real credentials or secrets.

---

## How instructions propagate

- **If project structure or boundaries change, update THIS file.**
- Any major convention (feature isolation, workspace command discipline, agent boundaries, execution mode, LLM-mocking, CI quirks) must be captured HERE or in referenced main docs. If in doubt, preserve context here and point to source.

---

## References for deep context

- Real/Complete README: `README.md`
- Multi-agent/worker/LLM design: `docs/agent-purpose.md`, `docs/multi-agent-guide.md`
- Backend dev rules: `.codex/skills/back/SKILL.md`
- API/entity/relationship schemas: `docs/database-table-relationships.md`, see also Zod types

---

## Omitted: Anything that can be inferred

- Do not restate obvious language/framework/library facts (React, FastAPI, Zod usage, pnpm basics, etc.).
- Only list style rules and workflows that differ from defaults, cannot be found in official docs, or that _must_ be obeyed for this repo.
- Examples and generic best practices are for referenced skill files, not here.

---

# Summary

If you need more than this file and the above references, re-audit the monorepo boundary and main doc files. When in doubt, prefer explicit over guess or template.
