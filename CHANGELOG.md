# Changelog

All notable changes to the Conflow project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Health check endpoint** for deployment readiness verification
- **Team membership CRUD** operations with user-team relationship management
- **OAuth configuration** for Supabase authentication integration
- **i18n planning** groundwork for future internationalization support

### Changed

- **Frontend restructured to Feature-Sliced Design (FSD)** architecture (`cefb23d`)
  - Added Vite/TypeScript path alias (`app/*` mapped to `src/*`)
  - Moved mock data from `src/data/` into domain-specific `src/entities/*/model/types.ts`
  - Added barrel exports (`index.ts`) for each entity: backlog, board, dashboard, inbox, metrics, retro, session, user, week
  - Moved `styles.css` into `src/app/` layer
  - Updated `index.html` entry point to `src/app/main.tsx`
  - Converted all cross-layer imports to absolute paths using `app/` prefix

### Fixed

- User API modifications for correct data handling
- User-team member relationship creation
- WebSocket-related connection issues
- Health check endpoint routing
- pnpm workspace prefix resolution

### Infrastructure

- Prettier formatting applied across the codebase
- ESLint/lint fixes applied project-wide
- Docusaurus documentation site added

---

## [0.1.0] - 2026-05-03 to 2026-05-22 -- Initial Development

The foundational release of Conflow, establishing the monorepo structure, backend services, frontend wireframes, multi-agent AI system, and infrastructure.

### Added

#### Monorepo and Shared Packages (`packages/`)

- **packages/core**: Axios HTTP client, Zod validation, SSE helper, date/string utilities, adapter pattern, constants, retry logic for backend error responses
- **packages/ui**: Atomic React components (Button, Card, Avatar, etc.) with Tailwind CSS
- **packages/rag**: Python RAG service (FastAPI, port 8001) with pgvector integration

#### Frontend (`apps/web`)

- Vite + React 18 + Tailwind CSS 4 application scaffold
- **Dashboard page** with weekly planner widget
- **Board page** (Kanban-style task management)
- **Backlog page** with task listing and filtering
- **Inbox page** for notifications and messages
- **Metrics page** for sprint analytics
- **Retro page** for retrospective sessions
- **Huddle page** for real-time audio/video collaboration
- **User page** for profile management
- **Direct Message section** mockup
- Sidebar navigation component
- Complete wireframes and wireframe assets

#### Backend (`server/`)

- FastAPI application with async SQLAlchemy 2 and PostgreSQL 16
- **User management**: User and UserProfile models with 1:1 relationship, role-based properties, CRUD API, token-based auth
- **Team organization**: Team model with membership management
- **Sprint management**: Sprint and SprintMetricSnapshot models
- **Backlog system**: Backlog item modeling and schema
- **Database**: Alembic migrations, ERD diagrams, table relationship documentation
- **Authentication**: Supabase integration, JWT verify_token, token API, auth MCP handler
- **Core infrastructure**: Structured logging, middleware stack, OpenAPI setup, error handling, storage service, dotenv configuration
- **WebSocket**: Real-time signaling initiator for Huddle and DM
- **Media processing**: Speech-to-text processor with agent orchestrator integration
- **Session manager** for WebSocket connection lifecycle
- **Idempotency middleware** (Redis-backed) to prevent duplicate submissions
- **Circuit breaker** for resilient external service calls
- **Context compression** for optimized chat history in LLM calls
- **LLM guardrails** for safe AI output validation
- **Slack MCP notifier** for message alert handling (test integration)

#### Multi-Agent AI System (`server/src/app/agent/`)

- **LangGraph** integration with development environment setup
- **Supervisor graph**: Routes user requests to specialized worker agents with mock/LLM/Ollama/vLLM mode support
- **User query agent**: General Q&A with human-in-the-loop approval flow
- **Blocker triage agent**: Identifies and prioritizes sprint blockers, enrolled in supervisor routing
- **Retro insights agent**: Generates retrospective analysis and recommendations
- **File analysis agent**: Processes uploaded files for content extraction
- **Image analysis agent**: Processes images with dedicated node pipeline
- **Sandbox runtime**: Security manager with syscall blocking and path validation for safe agent execution
- **LLM factory**: Stabilized provider abstraction supporting OpenAI, Ollama, and vLLM backends
- LangGraph graph schema documentation

### Infrastructure

- **pnpm 9 + Turborepo** monorepo with workspace dependency management
- **Docker Compose**: PostgreSQL, backend, RAG service, and frontend containers
- **Makefile** for common server operations
- **Ruff** linting and formatting (Python 3.13+, line-length 100)
- **PyTorch GPU** configuration for local ML workloads
- **Husky + commitlint** for conventional commit enforcement
- **ESLint + Prettier** for frontend code quality
- Cursorrules for both frontend and backend development standards

### Documentation

- Project README
- ERD diagrams and table relationship docs
- Multi-agent architecture guide
- AI engineering patterns reference
- Gemini skill agent documentation
- LangGraph graph schema reference
- Architecture documentation with version snapshots

[Unreleased]: https://github.com/dlehddnr0713/conflow/compare/cefb23d...HEAD
[0.1.0]: https://github.com/dlehddnr0713/conflow/commits/cefb23d
