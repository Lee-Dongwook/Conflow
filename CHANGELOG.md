# Changelog

All notable changes to the Conflow project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

#### Product Strategy

- **엔터프라이즈 피벗 결정 (2026-06-24)**: 타깃을 "대학생 · 스터디 팀"에서 **SMB(10-200명) → 미드마켓(200-2000명) PLG**로 전면 전환. 도메인 범위를 PM(Jira 스타일) + Comms(Slack/Huddle) + HR + 문서발급 4개로 확장.
- **루트 `README.md` 소개부 교체**: 새 태그라인 ("PM · Comms · HR · 문서발급을 하나로 잇는 엔터프라이즈 협업 OS"), Problem/Solution 표를 ICP-1 챔피언(COO/Head of Ops)의 페인 포인트로 재작성.

#### Documentation

- **`docs/` 전체 아카이브**: 기존 문서를 `docs/_archive/2026-06-24-pre-enterprise-pivot/`로 이동 (git rename으로 히스토리 보존).
- **신규 `docs/` 작성 시작** (draft v1):
  - `docs/README.md` — 문서 맵 + 다음 작성 순서
  - `docs/00-vision/positioning.md` — 한 문장 포지셔닝 + 차별화
  - `docs/00-vision/competitive-landscape.md` — Jira / Linear / Slack / Monday / Workday 대비 분석
  - `docs/01-market/icp.md` — ICP-1 (한국 30-80명 IT 회사 beachhead) → ICP-2 → ICP-3 단계별 정의, 자격 기준, 비-ICP 목록

### TODO (Next)

- `02-product/domain-documents.md` (4도메인 문서 중 마지막)
- `01-market/gtm-strategy.md`
- `03-roadmap/` (MoSCoW + Phase 0→4)
- `04-architecture/` (멀티테넌트 데이터 모델, A2UI 전략, SOC2/K-ISMS 로드맵)
- 루트 `README.md` 나머지 섹션 (Tech Stack, Roadmap, Wireframe, ERD) 정리 — Phase 0 문서 확정 후 일괄

## [0.3.1] - 2026-06-24 -- Enterprise Pivot Docs (Vision → Market → Product/4-Domain)

엔터프라이즈 피벗(0.3) 직후 문서 라인 확장. 비전/시장/제품 3개 계층을 한 번에 채워 도메인 설계의 입력을 확정.

### Added

#### Documentation — Vision

- **`docs/00-vision/product-vision.md`** (draft v1, 295줄): 5년 청사진. 2031년 North Star("한국 IT SMB 유료 워크스페이스 12-18% / 1,500개 / 평균 ACV 4천만원", 도달 실패 확률 30-40% 정직 표기), Phase 0→4 타임라인(각 Phase 빌드 목표/**안 빌드하는 것**/종료 조건), 불변 원칙 5개(단일 데이터 모델 / 단일 권한 모델 / A2UI 우선 / KR-first / Linear 벤치마크 UX), 변동 영역 표 5개, 비전-레벨 Watch List 6개, Anti-Vision 6항(카테고리 창조 금지 / 5번째 도메인 금지 / 2030년 이전 영미권 진출 금지 등).

#### Documentation — Market

- **`docs/01-market/jtbd.md`** (draft v1, 347줄): Bob Moesta 식 JTBD 프레임. Big Job 2개("회사 운영의 단일 화면" + "회사가 커져도 도구를 안 갈아엎기")에 각각 4 Forces(Push/Pull/Anxiety/Habit) 부착, 페르소나(COO/CEO/사용자/IT)별 Functional Job + P0-P3 우선순위(P0 10개), Emotional Jobs / Social Jobs, Switch Trigger 6개(Atlassian 가격 인상 / Slack Connect 권한 / 노무 이슈 카톡 유출 / 신입 4명 동시 입사 / CEO ChatGPT 시도 / 시리즈 B 마이그레이션 견적), Job → 4도메인 매핑표 5개를 **02-product/ 도메인 문서의 직접 입력**으로 박음.
- **`docs/01-market/pricing-strategy.md`** (draft v1, 377줄): PLG 4-Tier 가격 (Free 0원 / Team 시트당 월 12,000원·연 10,000원 / Business 22,000원·18,000원 / Enterprise 35,000원+ Custom, KRW 부가세 별도), 경쟁사 가격 비교(30/80/200/500명 4구간), AI/A2UI 가격 모델(메시지 cap + 도메인 횡단은 Business+), 한국 결제 디테일(카드/세금계산서/연계약/부가세), 가격 안티패턴 6가지, Phase별 출시 순서, 재무 모델 가정. **A2UI over-cap 단가 / Enterprise floor / Phase 4 노무 프리미엄 인상 폭**은 metrics.md로 검증 책임 이전.

#### Documentation — Product (4-Domain Architecture)

- **`docs/02-product/domain-overview.md`** (draft v1, 476줄): 4도메인(PM/Comms/HR/Documents) 통합 그림. 도메인별 책임/비-책임 + 공유 핵심 엔티티 5개(`Workspace`·`Member`·`Role/RoleAssignment`·`AuditLog`·`EntityLink` — 외래키 대신 EntityLink로 도메인 횡단 참조 표준화), 도메인 의존 다이어그램, **이벤트 카탈로그 13개** + Phase 도입 시점, **A2UI Tool 카탈로그 16개** + Tier 게이팅을 `tool_registry.yaml` 한 곳에서 강제하는 원칙, 데이터 격리 결정(같은 테이블 + `workspace_id` + RLS, Phase 4+ Enterprise 별도 클러스터 옵션), 도메인 횡단 쿼리 3개 시나리오 검증, **도메인 문서 4개가 받아갈 계약표 5개**.
- **`docs/02-product/domain-pm.md`** (draft v1, 633줄): PM 도메인 상세. 핵심 엔티티 7개(Issue/Sprint/Project/Board/BacklogItem/Label/Comment, Milestone·Roadmap·OKR·Dependency는 Phase 2+ 보류), Phase 1 P0 14개(Issue CRUD / Sprint / Project / Backlog / Board / Label / Comment / 키보드 단축키 / Cmd+K / 실시간 보드 / Optimistic UI / Jira·Linear 임포터 / REST+Webhook), **A2UI Tool 10개**(search / create / transition / comment / sprint_summary / blockers / start_sprint / end_sprint / import / release_note), 횡단 시나리오 2개(회고 자동 생성 / 메시지→이슈, Business+ 게이트), 임포터 우선순위(Jira > Linear > Notion), 정확도 < 90%는 Watch List 신호. External(노무사)은 PM 0건 노출 명시. 영구 안 함: 게임화 / 커스텀 status / Confluence급 위키.
- **`docs/02-product/domain-comms.md`** (draft v1, 712줄): Comms 도메인 상세. 엔티티 8개(Channel/Message/Thread/Reaction/Huddle/**Decision**/Notification/SearchIndex), Phase 1 P0 12개, **A2UI Tool 9개**(search_messages / post_message / summarize_channel / **detect_decisions** / confirm_decision / **message_to_issue** / summarize_huddle / list_unread_mentions / create_channel). **Decision 추출 차별화** 목표 precision > 80% / recall 50-60% 허용 / 오탐률 < 20% + 1클릭 컨펌 워크플로우. **외부 협업자 권한 모델**(지정 채널만 가시 / 다른 채널 검색 0 노출 / 외부↔외부 DM 금지 / DM은 Admin도 못 봄) — Slack Connect 대비 차별점. Huddle은 Phase 2 BaaS(Daily.co 등) 외주로 시작. 영구 안 함: 이메일 보관·통합 / 자체 캘린더 / Zoom급 화상회의.
- **`docs/02-product/domain-hr.md`** (draft v1, 790줄): HR 도메인 상세, **차별화 축 3(KR-first Compliance) 짊어짐**. 엔티티 13개(EmployeeProfile / OrgUnit / OnboardingWorkflow(+Step) / OffboardingWorkflow / OneOnOne / LeaveRequest / Attendance / EvaluationCycle / InsuranceEnrollment / LaborDocument / PayrollRecord / KpiNote). Phase 분배: Phase 2 알파 P0 10개 / Phase 3 정식 P1 12개(4대 보험 + 노무사 외부 협업자 + 근로기준법 8개 워크플로우 + SCIM + Flex 임포터) / Phase 4 P2 7개(KISA / ezTax / PayrollRecord / K-ISMS / EDI 자동화 / 한국 리전). **A2UI Tool 9개** + 도메인 횡단 시나리오 3개(블로커×1:1 / 신입 온보딩×1:1 / 퇴사자 인수인계). **노무사 외부 협업자 모델**: 무료 시트 / 멀티 클라이언트사 동시 / 1-click 5초 access 회수 / `AuditLog.external_collaborator=true` / 외부↔외부 DM 금지 — Switch Trigger #3("노무 이슈 카톡 유출") 직접 해결. **프라이버시 4계층**: Public / Manager-visible / HR-only / Self-only. **1:1 노트는 Admin도 못 봄**(감사 모드 제외), A2UI 호출자 권한이 sub-tool 단계에서 적용되어 1:1 키워드조차 누수 차단. **근로기준법 8개 워크플로우** 매핑(연차 60조 / 주 52시간 / 권고사직 23조 / 해고 27조 / 임금명세서 48조 / 직장 내 괴롭힘 76조의2 / 출산휴가·육아휴직 / 퇴직금 34조). 영구 안 함: 자체 급여 계산 엔진 / 채용 ATS / LMS / CRM식 영업 평가 / 자체 캘린더. 글로벌 노무는 Phase 4+ 일본만 검토.

### Changed

- **`docs/README.md`**: 작성 상태 표·"어떤 문서를 언제 보는가" 가이드·"다음 작성 순서" 매번 동기화 (7회 업데이트). `02-product/` 폴더 신규 생성.

### Notes

- 7개 문서 / 총 약 3,630줄.
- 모든 문서는 README 작성 규칙 준수: 한국어 / 프론트매터(`title`/`최종 업데이트`/`상태`/`독자`) / 첫 섹션 "이 문서로 내릴 결정" / 백과사전 금지(결정 중심).
- 결정 의도적 보류 다수: ERD·RLS SQL → `04-architecture/data-model.md`, Tool Registry 구현 → `a2ui-strategy.md`, Event Bus 기술 → `tech-stack.md`, SCIM → `security-compliance.md`, Phase OKR → `03-roadmap/phases.md`, A2UI over-cap 단가 → `metrics.md`, KISA 자체구축 vs 모두싸인 OEM → Phase 3 종료 시점 재결정.

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

[Unreleased]: https://github.com/dlehddnr0713/conflow/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/dlehddnr0713/conflow/compare/43f8aed...HEAD
[0.2.0]: https://github.com/dlehddnr0713/conflow/compare/cefb23d...c22b95a
[0.1.0]: https://github.com/dlehddnr0713/conflow/commits/cefb23d
