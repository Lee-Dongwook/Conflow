# Changelog

All notable changes to the Conflow project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.2.0] - 2026-05-31

### Added

#### Frontend

- **Landing page** 초기 구현 (`c22b95a`)
- **Login workflow**: 로그인 모달, 미인증 시 overlay trigger, 회원가입 연동 (`096f793`, `6a825b9`, `709da45`, `b3d9674`)
- **Logout + 세션 관리** (`1730a58`)
- **프로필 편집 API 연동** (`4b2b9af`)
- **Dashboard skeleton UI** 로딩 상태 추가 (`763f8e5`)
- **Dashboard schema** 초기 설계 및 ERD 업데이트 (`00620c1`, `862a8e4`)
- **Theme provider** (다크/라이트 모드) (`085e8d5`)
- **SEO 최적화** 초기 설정 (`0569a2a`)
- **모바일 대응** 초기 구현 (`c08c45e`)
- **Consent/Legal**: 이용약관, 개인정보처리방침, 동의 시스템 (`44135a9`)

#### Backend

- **Sprint CRUD** API 및 팀 Sprint 속성 추가 (`bc7ea96`, `0dc125f`)
- **Backlog CRUD** API 및 기능 연동 (`d164f64`, `74023d5`)
- **Board 데이터 연동** (`2b3a1de`)
- **Team-User 관계** 모델 추가 (`f5e3aa2`)
- **API v1 목록** 정리 (`455e9fa`)
- **Meeting summary 스크립트** — LangGraph 시나리오 테스트용 (`fcb2a87`)
- **Health check endpoint** 배포 준비 (`2907424`, `9a1ea7e`)
- **Team membership CRUD** 및 user-team 관계 관리 (`57437f5`)
- **OAuth 설정** — Supabase 인증 연동 (`3bbaa72`)

#### Infrastructure

- **GitHub Actions** — lint checker + e2e 테스트 파이프라인 (`7c23250`)
- **Changeset v1** 도입 (`2b70d96`)

### Changed

- **Frontend → Feature-Sliced Design (FSD)** 아키텍처 전환 (`cefb23d`)
  - Vite/TypeScript path alias (`app/*` → `src/*`)
  - Mock data를 domain-specific `src/entities/*/model/types.ts`로 이동
  - 각 entity별 barrel exports (`index.ts`) 추가
  - `styles.css` → `src/app/` layer 이동, `index.html` entry point 변경
  - cross-layer import를 절대경로 `app/` prefix로 통일
- Docs와 서비스 expose 분리 (`d90c99b`)

### Fixed

- Sprint 목록 로딩 실패 수정 (`b5829c4`)
- Backlog items enum 값 수정 (`c009ce0`)
- Team connection mismatch 수정 (`551fb8a`)
- Sprint ConfigDict 연결 누락 수정 (`a7b9679`)
- Model import 누락 수정 (`a71fb15`)
- 로그인 모달 동작 수정 (`6a825b9`)
- User API 데이터 핸들링 수정 (`91318af`)
- User-team member 관계 생성 수정 (`e4a4645`)
- WebSocket 관련 연결 수정 (`1c084ea`)
- Health check endpoint 라우팅 수정 (`9a1ea7e`)
- pnpm workspace prefix 수정 (`bb7472c`)
- 배포 의존성 업데이트 (`3832b0f`, `8778f5f`)

### Documentation

- Settings page 기획 문서 (`1788d71`)
- CLAUDE.md 업데이트 (`2f300fd`)
- Docusaurus 문서 사이트 추가 (`c433558`)

### Infrastructure

- Prettier 적용 (`e720a3c`)
- ESLint/lint 적용 (`8bf6d6d`)
- Alembic 마이그레이션 업데이트 — user-team, board 데이터 (`06385a0`, `181d355`)

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

[Unreleased]: https://github.com/dlehddnr0713/conflow/compare/c22b95a...HEAD
[0.2.0]: https://github.com/dlehddnr0713/conflow/compare/cefb23d...c22b95a
[0.1.0]: https://github.com/dlehddnr0713/conflow/commits/cefb23d
