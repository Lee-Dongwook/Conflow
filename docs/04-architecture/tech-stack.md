---
title: 기술 스택 결정 + Phase별 진화 경로
최종 업데이트: 2026-06-24
상태: draft v1
독자: 백엔드, 프론트, AI 엔지니어, 인프라/SRE, CTO
---

# 기술 스택 결정 + Phase별 진화 경로

> 이 문서는 [`domain-overview.md`](../02-product/domain-overview.md) "Open Decisions"의 기술 선택 부분과 [`phases.md`](../03-roadmap/phases.md) "Phase 간 마이그레이션 결정 시점"을 통합한 **의사결정 문서**다. 도메인 기능 명세가 아니다.

> **draft v1 가설 주의**: 아래 기술 선택은 2026-06-24 시점의 가설이다. 각 마이그레이션 결정 시점에 데이터 기반 재평가한다. 절대값으로 박지 말고 "방향 + 임계치"로 읽을 것.

---

## 이 문서로 내릴 결정

1. **각 영역의 기본 기술 스택을 박는다** — Frontend / Backend / Data / Messaging / AI / Infra / Observability 7개 영역. CLAUDE.md의 현재 스택을 정답으로 채택, 진화 경로만 보강.
2. **"왜 그 기술인가"의 트레이드오프를 박는다** — 영업·디자인·신규 입사자가 "Next.js 왜 안 써요" "Kafka 왜 안 써요" 물을 때 한 화면으로 답할 수 있는 근거.
3. **Phase 1→2→3→4 진화 시 무엇이 바뀌고 무엇이 안 바뀌는가** — 가장 큰 결정 (Event Bus PG outbox → Kafka, Docker Compose → k8s, 한국 리전 자체 호스팅)의 결정 분기 / 실행 분기 / 트리거 임계치를 [`phases.md`](../03-roadmap/phases.md) 마이그레이션 표와 동기화.
4. **AI 인프라의 4-모드 구조를 박는다** — Agent Mode `mock`/`llm`/`ollama`/`vllm`이 모두 필요한 이유. 벤더 잠금 회피 + 엔터프라이즈 자체 호스팅 옵션 보장.
5. **도입하지 않을 기술 (Anti-Stack)을 박는다** — Microservices, GraphQL, MongoDB, 커스텀 CRDT, 별도 Vector DB 등. "지루한 기술" 원칙 위반 시 거절 근거.
6. **관측가능성·보안·결제 인프라의 Phase별 진입 시점을 박는다** — OTel(Phase 2), SOC2(Phase 3), KISA(Phase 4), 한국 리전 자체 호스팅(Phase 4).

---

## 선택 원칙 (Technology Selection Principles)

기술 선택은 다음 6가지 원칙을 모두 통과해야 한다. 하나라도 깨지면 의사결정 회의 재소집.

### 1. "지루한 기술"을 기본값으로 (Boring tech first)

[McKinley, *Choose Boring Technology*]의 정신. 새 기술은 **"이게 없으면 못 만든다"**를 입증해야 도입한다.

- PostgreSQL이 우리의 "지루한 기본값" — RDB, FTS, pgvector, JSONB, RLS 모두 한 엔진에서.
- 새 기술 도입 시 3가지 답 강제: (1) 기존 스택으로 안 되는 이유, (2) 운영 부담 누가 지는가, (3) 6개월 후 잘 안 되면 빠질 수 있는가.

### 2. Phase별 진화: 처음부터 분산 시스템 만들지 않는다

[`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 1 (단일 데이터 모델) + [`phases.md`](../03-roadmap/phases.md) Phase 0-4 점진 진화.

- **Phase 1-2**: 단일 PostgreSQL + transactional outbox로 충분. 워크스페이스 100-500개 / 이벤트율 < 100 events/sec.
- **Phase 3+**: 워크스페이스 1,000개 / 미드마켓 진입 / SOC2 Type II 통과 시점에 분산 인프라 진입 (Kafka, k8s 정식, OTel APM).
- Phase 4 한국 리전 옵션은 단일 데이터 모델을 유지한 채 **물리 격리만** 추가.

### 3. AI 모드 전환 가능성 (mock / llm / ollama / vllm) — 벤더 잠금 회피

CLAUDE.md `CONFLOW_AGENT_MODE` 네 가지. [`product-vision.md`](../00-vision/product-vision.md) 변동 영역 "AI 모드 / LLM 제공자" 정렬.

- **mock**: 결정론적 스텁. 테스트·CI에서 OpenAI 비용 없이 워크플로우 검증.
- **llm**: 운영 (OpenAI gpt-4o-mini 기본).
- **ollama**: 로컬 개발 / 자체 호스팅 PoC.
- **vllm**: OpenAI 호환 vLLM 엔드포인트 — Phase 4 한국 리전 / 미드마켓 자체 호스팅.
- 모드 전환은 **`.env` 한 줄**. `server/src/app/core/llm_factory.py`가 추상화.

### 4. 헤드리스 + Schema-first (Zod / Pydantic) — A2UI 호환성

[`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 3 + [`domain-overview.md`](../02-product/domain-overview.md) "헤드리스 비즈니스 로직 원칙".

- 모든 도메인 service 함수는 **Pydantic Input/Output Schema**를 가진다 (TypeScript는 Zod, Python은 Pydantic V2).
- service 함수의 부분집합이 A2UI Tool 카탈로그로 등록 — UI 결합 금지.
- 외부 입력 (REST, WebSocket, LLM 출력) 모두 Schema 검증 강제.

### 5. 한국 시장 우선 (한국 리전 / ezTax / KISA — Phase 4)

[`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 4 + [`positioning.md`](../00-vision/positioning.md) 차별화 축 3.

- Phase 1-3은 글로벌 클라우드 (AWS/GCP) 단일 리전.
- Phase 4 Enterprise는 **한국 리전 자체 호스팅 옵션** — NHN Cloud / KT Cloud / Naver Cloud 비교.
- KISA 전자서명 / ezTax 연동 / K-ISMS 인증은 Phase 4 빌드 ([`moscow.md`](../03-roadmap/moscow.md) Could → Phase 4 정식).

### 6. 운영 단순성 vs 처리량의 트레이드오프 명시

같은 기술의 두 옵션 중 **운영 단순성이 항상 1순위**다 (Phase 3까지). 단, 다음 임계치 초과 시 처리량 우선으로 전환:

- 이벤트율 > 1,000 events/sec → Kafka 검토
- 워크스페이스 > 1,000개 → k8s 정식 검토
- 동시 WebSocket 연결 > 10,000개 → SFU 분산 검토
- A2UI 도메인 횡단 쿼리 > 분당 1k건 → 캐싱 / Read replica 검토

각 임계치는 [`phases.md`](../03-roadmap/phases.md) 마이그레이션 표에 결정 분기 박혀 있음.

---

## 스택 한눈에 (현재 + Phase별 진화)

| 영역              | Phase 0-1 (2026 Q3 – 2027 Q2)                        | Phase 2 (2027 Q3 – 2028 Q2)                     | Phase 3 (2028 Q3 – 2029 Q2)                                | Phase 4 (2029 Q3+)                                      |
| ----------------- | ---------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------- |
| **프론트엔드**    | Vite 8 + React 18 + Tailwind 4 + TS 5.7 (FSD)        | 동일 + 모바일 풀 기능 (RN 또는 Capacitor)       | 동일 + 미드마켓 RBAC UI                                    | 동일 + 다국어 (영문) UI                                 |
| **백엔드**        | FastAPI + SQLAlchemy 2 async + Pydantic V2 (Python 3.13) | 동일 + Celery 워커 확장                       | 동일 + Modular Monolith → 일부 서비스 분리 검토 (보류)     | 동일 + 한국 리전 인스턴스                               |
| **데이터**        | PostgreSQL 16 + pgvector + Redis (single instance)   | + Read Replica (Phase 2 종료 시점)              | + Multi-AZ + Connection pooling (PgBouncer) + S3 호환 스토리지 | + 한국 리전 클러스터 (Enterprise 한정) + KMS 통합       |
| **메시징**        | PostgreSQL outbox + LISTEN/NOTIFY                    | 동일 (부하 시뮬레이션 + Kafka 의사결정 자료 수집) | **Kafka(또는 Redpanda) 전환** (dual-write 6주 → 점진)     | Kafka 정식 + 멀티 컨슈머 그룹                           |
| **AI / 에이전트** | mock + llm (OpenAI gpt-4o-mini) + LangGraph supervisor | A2UI 첫 출시 (PM ↔ Comms) + Sandbox 강화      | A2UI 3도메인 횡단 (PM ↔ Comms ↔ HR)                       | A2UI 4도메인 횡단 + vllm 자체 호스팅 옵션               |
| **RAG**           | packages/rag/ (FastAPI 포트 8001) + pgvector         | + Decision 추출 임베딩 본격                     | + 도메인 횡단 임베딩                                       | + 다국어 임베딩 (영문)                                  |
| **인프라**        | Docker Compose (단일 호스트)                         | k8s 알파 (managed: GKE 또는 EKS)                | k8s 정식 + Multi-AZ + SOC2 Type II 통제                    | 멀티 리전 (KR/JP) + 한국 리전 자체 호스팅 옵션          |
| **CI/CD**         | GitHub Actions + Docker Hub                          | + Preview 환경 + canary 배포                    | + blue-green + 단계 롤아웃                                 | + 한국 리전 분리 파이프라인                             |
| **관측**          | Structured logs (JSON) + 기본 Prometheus + Sentry    | + OpenTelemetry 도입 (trace_id 전파)            | + OTel + APM (Datadog/Honeycomb 결정) + SLO 약속           | + K-ISMS audit log + 한국 리전 격리 로그                |
| **인증**          | Supabase Auth (Google/Microsoft OAuth)               | + Magic link 강화                               | + SSO/SAML 정식 + SCIM 자동 프로비저닝                     | + KISA 인증서 기반 서명자 인증                          |
| **보안**          | TLS 1.3 + 기본 WAF (Cloudflare)                      | + Rate limit / Idempotency (Redis)              | + mTLS 내부 서비스 + WAF 정식 + DLP 골격                   | + KISA 서명 + K-ISMS 인증 + 한국 리전 키 관리           |
| **결제**          | Stripe (글로벌) + 토스페이먼츠/PortOne (한국)        | 동일 + 한국 세금계산서 정식                     | + Enterprise 견적 / PO 발행                                | + KISA 인증 청구서 + ezTax 연동                         |

**핵심 관찰**

- 프론트엔드 / 백엔드 / 데이터 코어는 Phase 1-4 내내 **거의 안 바뀐다**. 큰 변화는 메시징(outbox → Kafka), 인프라(Compose → k8s), 한국 리전 추가.
- AI 모드 4개는 Phase 1부터 다 존재. **모드 전환은 `.env` 한 줄**이라 점진 진화가 아니라 옵션 추가.
- 관측가능성은 단계적으로 깊어진다 — Phase 1 로그·메트릭 → Phase 2 OTel → Phase 3 APM·SLO → Phase 4 K-ISMS audit.

---

## 프론트엔드 (Vite + React 18 + Tailwind 4 + FSD)

### 선택 근거

| 후보                  | 채택 여부 | 이유                                                                                                                                                                                                                       |
| --------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Vite + React (현재)** | O         | SPA에 최적. HMR 속도, 번들 크기, TypeScript 통합 모두 1급. 모노레포 (Turborepo)와 궁합. Linear 수준 UX 벤치마크 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 5)에 필수.                              |
| Next.js               | X         | SSR/RSC가 우리 시나리오에 과잉. 협업 앱은 **로그인 후 SPA**가 80% — SEO 필요 영역(랜딩, 가격)만 SSR 필요. 랜딩은 별도 정적 사이트(Astro/Hugo)로 분리 (Phase 1 후반 검토). 풀스택 프레임워크 잠금 회피.                  |
| Remix                 | X         | 데이터 로딩 패턴은 좋지만 협업 앱의 WebSocket 중심 흐름과 어색한 결합. TanStack Query로 충분.                                                                                                                              |
| SvelteKit             | X         | 한국 채용 풀 / FSD 적용 자료 / Tailwind 통합 모두 React 대비 약함. ICP 출시 속도 우선.                                                                                                                                     |

### FSD (Feature-Sliced Design) 레이어

CLAUDE.md `apps/web/` + 사용자 메모리 ([`MEMORY.md`](../../.claude/projects/-Users-dlehddnr0713-Desktop-conflow/memory/MEMORY.md)) 정렬.

```
src/
├── app/       — 앱 진입, 글로벌 provider
├── pages/     — 라우트 단위 페이지
├── widgets/   — 페이지를 구성하는 큰 블록
├── features/  — 사용자 시나리오 단위 (예: features/consent/)
├── entities/  — 비즈니스 엔티티 단위 (예: entities/issue/, entities/member/)
└── shared/    — 공용 UI / 유틸 / API 클라이언트
```

- Import 규칙: **상위 레이어 → 하위 레이어만**. `entities`가 `features`를 import 금지.
- 경로 alias: `app/*` → `src/*` (vite.config.ts + tsconfig.json).
- Cross-layer는 절대 경로 `app/`, 같은 슬라이스는 상대 경로.

### 상태관리 결정

| 후보                   | 채택 | 근거                                                                                                                                                |
| ---------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Zustand**            | O    | 학습 곡선 낮음, 보일러플레이트 없음, A2UI Tool에서 호출되는 헤드리스 store 패턴과 궁합. ICP 출시 속도 우선.                                          |
| Redux Toolkit (RTK)    | X    | 미드마켓 진입 시 (Phase 3) 재검토 가능. 현재는 보일러플레이트 비용 > 가치.                                                                          |
| Jotai                  | X    | 원자 단위 상태는 매력적이나 Zustand가 더 명시적. 팀 학습 일관성 우선.                                                                                |
| **TanStack Query**     | O    | 서버 상태 전용. Zustand는 클라이언트 상태만. 명확한 책임 분리.                                                                                      |

**원칙**: 서버 상태는 무조건 TanStack Query. 클라이언트 상태는 Zustand. URL 상태는 React Router. **세 가지를 섞지 않는다**.

### 빌드 / 패키징

- **Turborepo + pnpm 9**: 모노레포 빌드 캐시, 워크스페이스 의존성 자동 추적.
- **packages/core/**: Axios 클라이언트, Zod 검증, 날짜/문자열 유틸.
- **packages/ui/**: 원자 컴포넌트 (Button, Card, Avatar...).
- 의존성 흐름: `apps/web` → `packages/ui` → `packages/core` (역방향 금지).

### 모바일 결정 (Phase 2 빌드 목표)

| 후보                  | 결정 시점          | 결정 기준                                                                                       |
| --------------------- | ------------------ | ---------------------------------------------------------------------------------------------- |
| **React Native (RN)** | 2027 Q3 (Phase 2)  | 코드 공유 ~60%, 네이티브 UX 정합. 단, RN 운영 부담 있음.                                       |
| Capacitor             | 2027 Q3 (Phase 2)  | 웹뷰 기반. 코드 공유 ~95%, 출시 속도 빠름. UX는 RN보다 약함.                                   |
| Expo                  | 2027 Q3 (Phase 2)  | RN의 운영 부담 완화 옵션.                                                                       |

**현재 가설 (보류)**: Phase 1 종료 시점 (2027 Q2) 모바일 사용 패턴 데이터 + 인력 상황 보고 결정. 결정 분기는 [`phases.md`](../03-roadmap/phases.md) 2027 Q2 OKR.

### 안티패턴 (도입 안 함)

| 안티패턴                    | 이유                                                                                                              |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| SSR 무리하게 도입           | 로그인 후 SPA가 80%. SSR은 랜딩 페이지(Astro 별도)로 분리.                                                        |
| CSS-in-JS (styled-components, Emotion) | Tailwind 4가 우리의 답. 런타임 비용 + 번들 크기 + TypeScript 추론 부담 모두 회피.                              |
| Custom UI 프레임워크         | shadcn/ui 패턴(복사 + 수정) + Tailwind로 충분. 자체 디자인 시스템은 packages/ui로 천천히 빌드.                    |
| Module Federation            | 모노레포 + pnpm 워크스페이스로 충분. 마이크로 프론트엔드는 우리 규모에 과잉.                                      |

---

## 백엔드 (FastAPI + SQLAlchemy 2 async + PostgreSQL 16)

### 선택 근거

| 후보                | 채택 | 이유                                                                                                                                                                                                                  |
| ------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FastAPI**         | O    | Pydantic V2 통합, async 1급, OpenAPI 자동 생성 → A2UI Tool 카탈로그와 직결. Python AI/LangGraph 생태계 정합. CLAUDE.md 채택.                                                                                          |
| Django + DRF        | X    | 동기 ORM이 async LangGraph와 어색. Django Channels로 WebSocket은 되지만 첫 진입 비용 큼. 관리자 페이지의 매력은 인정하나 Pydantic V2 + 헤드리스 원칙과 결합 어려움.                                                  |
| Ruby on Rails       | X    | 한국 채용 풀 약함. AI/LangGraph 생태계 거의 없음. Rails magic이 헤드리스 원칙과 충돌.                                                                                                                                |
| NestJS              | X    | TypeScript 풀스택의 매력은 있으나 AI 생태계 (LangChain, LangGraph)가 Python 1급. Pydantic ↔ Zod 이중화 부담은 작게 — 둘 다 Schema 우선이라.                                                                          |
| Spring Boot         | X    | Java 생태계 깊이는 인정. 단, AI 생태계 (LangGraph 등) 빈약. 한국 SaaS 스타트업 채용 풀 좁음. 운영 비용 큼.                                                                                                            |
| **SQLAlchemy 2 (async)** | O    | Python ORM의 사실상 표준. async 패턴 1급, Alembic 마이그레이션 안정. 동기/비동기 혼용 가이드 필요.                                                                                                              |

### 도메인 모듈 구조

CLAUDE.md `server/src/app/{domain}/` 패턴. [`domain-overview.md`](../02-product/domain-overview.md) 4도메인과 정렬.

```
server/src/app/
├── core/              — 인프라 (db, security, llm_factory, middlewares, config)
│                        + Shared Core 엔티티 (Workspace, Member, Role, AuditLog, EntityLink)
├── agent/             — LangGraph supervisor + 워커 그래프
├── sandbox/           — AI 에이전트 실행 격리
├── common/            — 횡단 (idempotency, circuit breaker, caching, storage)
├── websockets/        — 실시간 (Huddle, DM signaling)
│
├── pm/                — 도메인: api.py / model.py / schemas.py / service.py
├── comms/             — 동일 패턴
├── hr/                — 동일 패턴
├── documents/         — 동일 패턴
│
└── (기존 sprint/, backlog/, board/, inbox/, week/, retro/, planning/, user/, team/, consent/)
   → Phase 1 종료까지 domain 모듈로 정리 통합
```

- 각 도메인 모듈은 `api.py` (FastAPI 라우터) + `model.py` (SQLAlchemy) + `schemas.py` (Pydantic) + `service.py` (헤드리스 비즈니스 로직).
- `service.py`는 **A2UI Tool 등록 후보**. FastAPI 라우트와 LangGraph Tool 양쪽이 같은 service 함수를 호출.

### 마이그레이션 / 라우터 패턴

- **Alembic**: 모든 스키마 변경. `autogenerate` 사용하되 PR 리뷰에서 검토 필수.
- **라우터 등록**: `app.include_router(router)` + `app.include_router(router, prefix="/api")` 더블 등록 패턴 ([`MEMORY.md`](../../.claude/projects/-Users-dlehddnr0713-Desktop-conflow/memory/MEMORY.md)).
- **AutoUUIDMixin**: User 모델 등에서 UUID 자동 생성. 모든 mutable 엔티티는 UUID 1순위.

### 비동기 / 동기 혼용 가이드

원칙: **I/O는 async, 순수 계산은 sync**. 혼용 카오스 방지.

| 시나리오                                       | 패턴                                                                  |
| ---------------------------------------------- | --------------------------------------------------------------------- |
| FastAPI 라우트                                 | `async def` 강제. sync 라우트는 Celery 위임이 필요할 때만.            |
| DB 호출                                        | `AsyncSession` 강제. sync session 금지.                               |
| 외부 API 호출 (OpenAI, Supabase, 결제)         | `httpx.AsyncClient` 강제.                                             |
| 무거운 계산 (PDF 렌더링, 임베딩 배치)          | Celery 태스크로 위임. async 이벤트 루프 막힘 방지.                    |
| 헤드리스 service 함수                          | `async def` 기본. A2UI Tool에서 호출 시 async 일관성 보장.            |

### Pydantic V2 / Zod 짝

[`domain-overview.md`](../02-product/domain-overview.md) "헤드리스 비즈니스 로직 원칙" — Input/Output Schema 강제.

- 백엔드: Pydantic V2 (validation 빠르고 strict mode).
- 프론트엔드: Zod (런타임 검증 + TypeScript 추론).
- OpenAPI 스펙 → TypeScript 클라이언트 자동 생성 (Phase 1 후반 정리).
- 외부 데이터 (LLM 출력 포함) 모두 Schema 검증 강제. **schema 없는 외부 데이터는 절대 도메인에 진입 안 함**.

### 안티패턴

| 안티패턴                                    | 이유 / 대안                                                                                                                       |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| ORM 우회한 raw SQL 남발                     | 가독성 / 마이그레이션 정합 / RLS 강제 모두 깨짐. 복잡 쿼리는 SQLAlchemy Core 또는 stored function. raw SQL은 분석 쿼리 한정.        |
| sync / async 혼용 카오스                    | I/O는 async, 계산은 sync. 라우트 진입은 항상 async. Celery 위임이 sync 진입 유일한 정당 경로.                                      |
| 도메인별 별도 `audit_*` 테이블 신설         | [`domain-overview.md`](../02-product/domain-overview.md) Watch List #7 직접 위반. 단일 `AuditLog` 강제.                            |
| service 함수에 React/UI 컴포넌트 import     | [`domain-overview.md`](../02-product/domain-overview.md) Watch List #5 직접 위반. 헤드리스 원칙 깨짐.                              |
| 도메인 간 직접 SQL JOIN                     | Watch List #1 직접 위반. `EntityLink` + 이벤트로 우회.                                                                            |

---

## 데이터 계층 (PostgreSQL 16 + pgvector + Redis)

### 선택 근거

| 후보                     | 채택 | 이유                                                                                                                                                                                                                                                  |
| ------------------------ | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PostgreSQL 16**         | O    | RDB / FTS / pgvector / JSONB / RLS 모두 단일 엔진. 단일 데이터 모델 약속의 물리적 보장. 운영 단순성 1순위.                                                                                                                                            |
| MySQL/MariaDB            | X    | JSONB / FTS / RLS 모두 PostgreSQL 대비 약함. pgvector 같은 즉시 도입 가능한 AI 생태계 부재.                                                                                                                                                            |
| **pgvector**              | O    | Postgres 확장. 단일 데이터 모델 약속을 깨지 않고 임베딩 저장 가능. RAG / Decision 추출 임베딩 ([`domain-comms.md`](../02-product/domain-comms.md) Decision 추출).                                                                                       |
| Pinecone / Weaviate / Qdrant | X    | 별도 Vector DB는 단일 데이터 모델 약속 깨짐 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 1). Phase 3+ 처리량 초과 시 재검토하되, 그때도 pgvector 샤딩 / 별도 클러스터가 1차 옵션.                                                  |
| **Redis**                 | O    | Idempotency 키 저장 ([`MEMORY.md`](../../.claude/projects/-Users-dlehddnr0713-Desktop-conflow/memory/MEMORY.md)), 캐싱, Pub/Sub (Phase 1-2 LISTEN/NOTIFY 보완), Celery 브로커.                                                                       |
| KeyDB / Dragonfly         | X    | Redis 호환은 매력적이나 운영 자료·관리형 서비스 빈약. Phase 4까지 보류.                                                                                                                                                                                |

### PostgreSQL 16 — 단일 데이터 모델의 실체

[`domain-overview.md`](../02-product/domain-overview.md) "공유 핵심 엔티티" + "데이터 격리 (Multi-tenancy 결정)" 정렬.

- **모든 테이블에 `workspace_id` 컬럼 + RLS 정책** — 단일 테이블 + 행 단위 격리.
- **JSONB 활용**: `Role.permissions`, `AuditLog.metadata` 등 스키마 진화 빈번한 필드.
- **FTS (Full-Text Search)**: 한글 풀텍스트 검색 — 키워드 검색은 PostgreSQL FTS, 시맨틱 검색은 pgvector (이중 인덱스).
- **RLS (Row Level Security)**: `workspace_id` 누락 쿼리 자동 차단. 보안 마지막 방어선.

### pgvector — RAG + Decision 추출

- **packages/rag/** (FastAPI 포트 8001): 임베딩 생성·검색 엔드포인트. CLAUDE.md 채택.
- 임베딩 모델: OpenAI text-embedding-3-small 기본 (Phase 2). Phase 4 한국어 특화 모델 검토.
- 인덱스: HNSW (속도 우선) — 워크스페이스별 분리 인덱스가 단일 인덱스 + RLS보다 빠를지 Phase 3에서 결정.

### Redis — 다목적

| 용도               | 사용 패턴                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Idempotency        | `server/src/app/common/idempotency.py` ([`MEMORY.md`](../../.claude/projects/-Users-dlehddnr0713-Desktop-conflow/memory/MEMORY.md)). API 멱등성 키. |
| 캐싱               | A2UI Tool 결과 캐시 (입력 hash 기반 short TTL).                                                                    |
| Pub/Sub            | Phase 1-2 LISTEN/NOTIFY 보완 — 대규모 채널 fanout 시.                                                              |
| Celery 브로커      | 비동기 작업 큐 (PDF 렌더링, 임베딩 배치).                                                                          |
| APScheduler 상태   | 분산 스케줄러 락 (단일 호스트에서는 불필요, Phase 2 k8s 알파에서 도입).                                            |

### 스토리지 — Supabase Storage vs S3 호환 (Phase 2 결정)

| 옵션                  | Phase 1                  | Phase 2 결정 시점                                                                          |
| --------------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| Supabase Storage      | 기본 채택 (auth와 통합)  | 200MB 파일 / 워크스페이스당 100GB 임계치 초과 시 S3 호환 (Cloudflare R2 / AWS S3) 분리      |
| Cloudflare R2         | 보류                     | egress 비용 우위. Phase 2 후반 검토.                                                       |
| AWS S3 / GCS          | 보류                     | Multi-AZ 안정성. Phase 3 SOC2 Type II 시점에 채택 가능.                                    |

### Phase 4 한국 리전 선택지

| 클라우드           | 장점                                              | 단점                                              |
| ------------------ | ------------------------------------------------- | ------------------------------------------------- |
| **NHN Cloud**      | KISA 인증 기본 제공, 정부/공공 진입 자료 있음     | 글로벌 도구 통합 약함                             |
| KT Cloud           | 망분리 옵션 강함, 통신사 안정성                   | 한국 SaaS 스타트업 채용 풀의 친숙도 낮음          |
| Naver Cloud        | 한국 SaaS에서 가장 친숙, 관리 도구 우수           | KISA 인증 / 정부 진입은 NHN/KT 대비 약함          |
| AWS Seoul (현재)   | 가장 친숙, 미드마켓 영업 자료 풍부                | 데이터 주권 우려 (Phase 4 Enterprise 요구)        |

**Phase 4 가설**: AWS Seoul 유지 + Enterprise 한정 NHN/KT 옵션 추가. 결정 분기 [`phases.md`](../03-roadmap/phases.md) 2030 Q1.

### 안티패턴

| 안티패턴                          | 이유                                                                                                              |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| NoSQL 흩뿌리기 (MongoDB, DynamoDB) | 단일 데이터 모델 약속 깨짐. JSONB로 충분.                                                                          |
| 별도 Vector DB (Pinecone 등)      | Watch List 동일. pgvector + 워크스페이스 단위 인덱스로 Phase 4까지 충분.                                          |
| GraphQL (Phase 1-3)               | 권한 매핑 복잡 ([`domain-overview.md`](../02-product/domain-overview.md) RLS와 정합 어려움). REST + OpenAPI + Pydantic 스키마로 충분. Phase 4에서 외부 API 통합 시 게이트웨이 검토. |
| 도메인별 별도 DB / 별도 스키마    | [`domain-overview.md`](../02-product/domain-overview.md) "데이터 격리 결정" 명시 — 같은 테이블 + workspace_id.   |

---

## Event Bus 결정 (가장 큰 결정)

[`domain-overview.md`](../02-product/domain-overview.md) "이벤트 스토리지 결정"의 확장. [`phases.md`](../03-roadmap/phases.md) "Phase 간 마이그레이션 결정 시점" Event Bus 전환과 동기화.

### Phase 1-2: PostgreSQL Outbox 패턴 + LISTEN/NOTIFY

**메커니즘**

1. 트랜잭션 안에서 도메인 상태 변경 + `outbox` 테이블에 이벤트 행 삽입.
2. `pg_notify('outbox_channel', event_id)` 호출.
3. 별도 worker (Celery 또는 FastAPI background)가 LISTEN으로 받아 처리 + outbox row를 `processed`로 표시.
4. 처리 실패 시 재시도 (idempotent 강제).

**근거**

- **Atomicity 보장**: 도메인 mutation과 이벤트 발행이 같은 트랜잭션. 별도 메시지 큐는 dual-write 문제.
- **운영 단순성**: PostgreSQL만 운영. Kafka/ZooKeeper 인프라 부담 없음.
- **처리량 충분**: Phase 1-2 워크스페이스 100-500개 / 이벤트율 < 100 events/sec 수준에서 outbox 처리는 무리 없음.

**한계 (Phase 3+ 전환의 트리거)**

- **처리량 한계**: ~1,000 events/sec. 미드마켓 진입 + A2UI 도메인 횡단 활성화 시 임박.
- **멀티 컨슈머 그룹 패턴 어색**: A2UI / Comms 알림 / Documents 자동 발급 세 컨슈머가 같은 이벤트를 다르게 처리할 때 outbox는 어색.
- **이벤트 재처리 비용**: 전체 outbox 스캔. Kafka의 offset 기반 재처리 대비 비효율.
- **분산 워커 조정**: k8s 정식 진입 (Phase 3) 시 Redis 락 + outbox 워커 동시성 관리 복잡.

### Phase 3 전환 결정 (2028 Q2 결정 분기)

[`phases.md`](../03-roadmap/phases.md) 2028 Q2 KR4: "Event Bus 전환 결정". 결정 기준은 다음 4개 시그널 중 **2개 이상** 초과 시 전환 Go.

| 시그널                                | 트리거 임계치                  | 측정 방법                                                                |
| ------------------------------------- | ------------------------------ | ------------------------------------------------------------------------ |
| 워크스페이스 수                        | > 1,000개                      | DB 카운트                                                                |
| 이벤트율                              | > 1,000 events/sec (피크)     | outbox 삽입율 + LISTEN throughput                                        |
| A2UI 도메인 횡단 쿼리율               | > 분당 1k건                    | `a2ui.cross_domain_query` Tool 호출 메트릭                              |
| 부하 시뮬레이션 결과                  | PoC 환경에서 outbox 폴링 지연 P99 > 5초 | Phase 3 SCIM/SSO 동시성 시뮬레이션 ([`phases.md`](../03-roadmap/phases.md) 2028 Q2) |

### 대안 비교 (Phase 3 전환 시점)

| 후보                  | 장점                                                                                                                  | 단점                                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Kafka (managed: MSK/Confluent)** | 산업 표준. 멀티 컨슈머 그룹 1급. 운영 자료 풍부. 영업/IT 자료 강점.                                          | 운영 부담 큼. 매니지드 비용 큼. 학습 곡선.                                                                  |
| **Redpanda**          | Kafka API 호환, ZooKeeper 불필요, 운영 부담 절반. 단일 바이너리.                                                       | 매니지드 생태계 Kafka 대비 약함. 미드마켓 영업 자료의 친숙도 낮음.                                          |
| NATS JetStream        | 가볍고 빠름. KV 스토리지까지.                                                                                          | 멀티 컨슈머 그룹 패턴 자료 약함. 산업 표준 아님. 미드마켓 채용 자료 약함.                                  |
| RabbitMQ              | 안정적, AMQP 표준                                                                                                      | 스트림 처리 / 재처리는 Kafka 대비 약함. 우리는 이벤트 스트림이 1순위라 RabbitMQ 부적합.                     |

**현재 가설**: **Redpanda 1차 검토 → Kafka 폴백**. Redpanda의 운영 부담 절감이 우리 SaaS 규모에 fits. 자체구축 vs 매니지드는 Phase 3 진입 시점에 결정.

### 마이그레이션 단계 (PG outbox → Kafka)

1. **사전 (Phase 2 후반, 2028 Q1)**: Kafka 토픽 설계 (도메인별 또는 이벤트별), 컨슈머 그룹 정의, 부하 시뮬레이션 환경 구축.
2. **Dual-write (Phase 3 진입, 2028 Q3, 6주)**: 도메인 service가 outbox + Kafka 양쪽에 발행. 컨슈머는 outbox만 처리.
3. **점진 전환 (Phase 3 중반, 2028 Q4, 4주)**: 컨슈머별로 Kafka 구독으로 전환. 우선순위: A2UI > Comms 알림 > Documents 자동 발급.
4. **Outbox deprecation (Phase 3 후반, 2029 Q1)**: 모든 컨슈머가 Kafka 전환 완료 후 outbox 발행 제거. outbox 테이블은 90일 보존 후 drop.

### Phase 3-4: Kafka (또는 Redpanda)

**토픽 설계 원칙**

- **도메인 단위 토픽**: `conflow.pm.events`, `conflow.comms.events`, `conflow.hr.events`, `conflow.documents.events`.
- **이벤트별 분리는 Phase 4 처리량 초과 시**: 토픽 폭증보다 컨슈머 측 필터링이 1차 답.
- **파티션 키**: `workspace_id` (워크스페이스 단위 순서 보장).
- **보존 정책**: 7일 (재처리 용도). Audit Log는 별도 PostgreSQL 보존.

**멀티 컨슈머 그룹**

| 컨슈머 그룹                | 처리 이벤트                          | SLA                              |
| -------------------------- | ------------------------------------ | -------------------------------- |
| `a2ui-supervisor`          | 모든 도메인 이벤트                   | Phase 3 SLO P99 < 5초            |
| `comms-notifier`           | `pm.*`, `hr.*` (알림 트리거)         | P99 < 2초                        |
| `documents-auto-generator` | `hr.member.onboarded`, `*.signed` 등 | P99 < 30초                       |
| `audit-log-writer`         | 모든 이벤트                          | At-least-once, 누락 금지         |

---

## AI / 에이전트 인프라

### Agent Mode 4종 (mock / llm / ollama / vllm)

CLAUDE.md `CONFLOW_AGENT_MODE` 4 모드. 모드 전환은 **`.env` 한 줄** — `server/src/app/core/llm_factory.py`가 추상화.

| 모드     | 용도                                          | 의존성                | Phase 진입         |
| -------- | --------------------------------------------- | --------------------- | ------------------ |
| `mock`   | CI/CD 테스트, A2UI 워크플로우 결정론적 검증   | 없음 (스텁 응답)      | Phase 0부터        |
| `llm`    | 운영 (OpenAI gpt-4o-mini 기본)                | OPENAI_API_KEY        | Phase 0부터        |
| `ollama` | 로컬 개발, 자체 호스팅 PoC                    | 로컬 Ollama 서버      | Phase 1 후반       |
| `vllm`   | Phase 4 한국 리전 / 미드마켓 Enterprise 자체 호스팅 | vLLM 엔드포인트 (사내) | Phase 4            |

**왜 4종이 다 필요한가**

- **mock**: OpenAI 비용 없이 LangGraph 워크플로우 unit/integration 테스트. CI 시간 단축. A2UI 회귀 테스트의 핵심.
- **llm**: 운영. 가격·지연·품질의 현재 최적. Phase 1-3 기본.
- **ollama**: 개발자 노트북에서 LangGraph 전체 흐름 디버깅. 인터넷 차단 환경 PoC.
- **vllm**: Enterprise / 한국 리전 / K-ISMS 자체 호스팅 요구 대응. OpenAI 호환 API라 코드 변경 0.

### LangGraph Supervisor 패턴

`server/src/app/agent/graphs/supervisor_graph.py` (CLAUDE.md 채택).

**구조**

```
User intent
   ↓
[supervisor_graph] ─ caller_member_id 강제 주입
   ├─→ [meeting_summary worker]
   ├─→ [blocker_triage worker]
   ├─→ [retro_insights worker]
   ├─→ [user_query worker]
   └─→ [file_analysis worker]
   ↓
[Tool Registry] ─ Tier / 권한 / 도메인 체크
   ↓
도메인 service 함수 (헤드리스)
   ↓
[Response synthesis] ─ 권한 누수 방지 마스킹
```

**워커 (Phase 1-2)**

- `meeting_summary`: Huddle / 회의록 요약
- `blocker_triage`: PM 블로커 자동 분류 + 알림
- `retro_insights`: Sprint 종료 회고 초안 생성
- `user_query`: 자연어 질의 → A2UI Tool 합성
- `file_analysis`: 파일 분석 + 메타 추출

**Phase 3+ 워커 확장**

- `onboarding_assistant`: `hr.member.onboarded` 트리거 → 4도메인 자동 액션
- `compliance_reviewer`: `documents.*.submitted` → 노무사 검토 큐 라우팅
- `payroll_validator`: Phase 4 ezTax 연동 검증

**상세는 보류** — [`a2ui-strategy.md`](./a2ui-strategy.md)에서 권한 전파 / Tool Registry / supervisor 라우팅 규칙 상세.

### LLM Factory (`server/src/app/core/llm_factory.py`)

- 모델 선택 추상화: `get_llm(mode, model_name?)`
- Phase 4 멀티 프로바이더: OpenAI / Anthropic / 한국 리전 vLLM
- 비용·지연 메트릭 자동 기록 (관측가능성 절 참조)

### RAG (`packages/rag/`, FastAPI 포트 8001)

- **분리 이유**: Python 의존성 (sentence-transformers, langchain) 무거움 + 배포 사이클 분리.
- **pgvector 임베딩 저장**: 단일 데이터 모델 약속 유지.
- **Decision 추출 임베딩**: Comms 메시지 → 임베딩 → 의미 검색 → Decision 후보 추출 ([`domain-comms.md`](../02-product/domain-comms.md) Phase 2 P1).
- **임베딩 모델 (Phase 2)**: OpenAI text-embedding-3-small.
- **Phase 4**: 한국어 특화 임베딩 모델 검토 (KLUE, KR-SBERT 등).

### Sandbox (`server/src/app/sandbox/`)

CLAUDE.md "Runtime security for AI agent execution".

- **현재 통제**: syscall 차단, path validation, 시간 제한.
- **Phase 3+ 강화**: 외부 코드 실행 (Tool calling 확장) 시 컨테이너 격리 (gVisor 또는 Firecracker 검토).
- **Phase 4**: K-ISMS 인증 요구 시 sandbox 감사 로그 별도 보존.

### 비용 / 지연 / 한국어 품질 모니터링

[`product-vision.md`](../00-vision/product-vision.md) 변동 영역 "AI 모드 / LLM 제공자" 트리거 신호.

| 메트릭                       | 임계치                                | 액션                                          |
| ---------------------------- | ------------------------------------- | --------------------------------------------- |
| LLM 비용 / 활성 워크스페이스 | > $50/월                              | 모델 다운그레이드 또는 ollama 자체 호스팅 검토 |
| LLM 응답 P95 지연            | > 8초                                 | Streaming + Tool 캐싱 강화                    |
| 한국어 Decision 추출 정밀도  | < 70%                                 | 모델 변경 또는 KR 특화 fine-tuning            |
| OpenAI API 가용성            | 월 가용성 < 99.5%                     | 멀티 프로바이더 (Anthropic) 폴백 도입         |

---

## 인프라 / 배포

### Phase 0-1: Docker Compose (단일 호스트)

CLAUDE.md `docker compose up` 채택.

- 서비스: `db` (PostgreSQL), `backend` (FastAPI), `rag` (packages/rag), `frontend` (Vite preview).
- 단일 호스트 — 모든 운영 인스턴스에서 동작. 알파 / 베타 단계 충분.
- 모니터링: 호스트 단위 docker logs + Sentry.

**한계**: 무중단 배포 안 됨, 수평 확장 안 됨, Multi-AZ 안 됨. Phase 1 종료 (유료 워크스페이스 100개) 시점에 k8s 알파로 이전 시작.

### Phase 2: k8s 알파 (managed: GKE 또는 EKS)

- **결정 시점**: [`phases.md`](../03-roadmap/phases.md) 2027 Q3 (Phase 2 진입).
- **GKE vs EKS**: AWS Seoul 리전 활용 강점 → EKS 1차. GCP는 Phase 4 멀티 클라우드 시 검토.
- **Workload**: backend, rag, agent worker, celery worker, websocket gateway 별도 deployment.
- **DB는 RDS / Cloud SQL 매니지드** — k8s에 DB 직접 운영 금지.
- **Helm chart 작성**: 미드마켓 자체 호스팅 옵션 (Phase 4) 사전 준비.

### Phase 3: k8s 정식 + Multi-AZ + SOC2 통제

- **Multi-AZ**: PostgreSQL Primary + Replica + Standby. RTO < 30분, RPO < 5분.
- **HPA + VPA**: 워크스페이스 활성도 기반 자동 스케일.
- **Network policy**: 도메인 모듈 간 통신 제한 (mTLS 검토).
- **SOC2 Type II 통제**: 액세스 로그, 변경 관리, 백업 검증 자동화 ([`phases.md`](../03-roadmap/phases.md) 2028 Q3 KR3).

### Phase 4: 멀티 리전 (KR/JP) + 한국 리전 자체 호스팅

- **Phase 4 진입 (2029 Q3)**: 한국 본부 클러스터 + 일본 알파 클러스터.
- **한국 리전 자체 호스팅 옵션 (Enterprise 한정)**:
  - 옵션 A: 우리가 NHN/KT/Naver Cloud에서 운영 (managed Conflow).
  - 옵션 B: 고객사 사내 k8s에 Helm chart 배포 (자체 호스팅 진정한 의미).
  - 결정 분기: [`phases.md`](../03-roadmap/phases.md) 2030 Q1 ("한국 리전 자체 호스팅 vs 멀티 클라우드").
- **데이터 격리 모드**: 같은 테이블 + workspace_id 유지하되, **물리 클러스터 분리** ([`domain-overview.md`](../02-product/domain-overview.md) "데이터 격리" 결정과 정합).

### CI/CD

- **Phase 1**: GitHub Actions (테스트, 빌드, Docker Hub push). 매뉴얼 배포.
- **Phase 2**: GitHub Actions + Preview 환경 (PR마다 1개) + canary 배포 (10% 트래픽 1시간 관찰).
- **Phase 3**: blue-green 배포 + 단계 롤아웃 (10% → 50% → 100%) + 자동 롤백 (오류율 1%+ 시).
- **Phase 4**: 한국 리전 별도 파이프라인 (regulation 분리).

### Secrets 관리

| Phase     | 도구                                            | 비고                                          |
| --------- | ----------------------------------------------- | --------------------------------------------- |
| Phase 1-2 | `.env` + GitHub Secrets                         | 매뉴얼 로테이션. 알파 단계 충분.              |
| Phase 3+  | AWS Secrets Manager + KMS (또는 HashiCorp Vault) | 자동 로테이션 + SOC2 Type II 요구.            |
| Phase 4   | + 한국 리전 KMS (KISA 인증 키 관리)              | 한국 리전 자체 호스팅은 사내 Vault 사용.      |

---

## 관측가능성 (Observability)

### 로그 (Logs)

- **Phase 1부터**: 구조화 로그 (JSON), 모든 로그에 `trace_id` 전파 ([`domain-overview.md`](../02-product/domain-overview.md) AuditLog의 `trace_id` 컬럼과 정합).
- **Phase 1-2**: stdout → Cloudwatch Logs / Stackdriver.
- **Phase 3+**: 중앙 집계 (Datadog Logs / OpenSearch).
- **Phase 4**: K-ISMS 감사 요구 시 한국 리전 별도 로그 저장.

### 메트릭 (Metrics)

- **Phase 1부터**: Prometheus + Grafana. 기본 메트릭 (요청율, 오류율, 지연, DB 연결, Redis 활용).
- **Phase 2**: 도메인별 메트릭 (PM 이슈 생성율, Comms 메시지율, A2UI Tool 호출율).
- **Phase 3**: SLO 약속 — 미드마켓 진입 시 가용성 / 지연 SLO 계약. APM (Datadog 또는 Honeycomb) 통합.

### Tracing (분산 추적)

- **Phase 2**: OpenTelemetry 도입. FastAPI / SQLAlchemy / LangGraph / Celery 모두 trace_id 전파.
- **Phase 3**: APM Tool과 연동. A2UI Tool 호출 trace가 도메인 service 호출까지 자연스럽게 이어짐.
- **Phase 4**: 한국 리전 자체 호스팅 환경에 OTel Collector 자체 운영.

### APM

| 후보              | 채택 시점     | 비고                                                                                       |
| ----------------- | ------------- | ------------------------------------------------------------------------------------------ |
| **Sentry**         | Phase 1부터   | Frontend + Backend 오류 추적. PLG 단계에 충분.                                              |
| **Datadog**        | Phase 3 결정 | 풀 스택 APM + SLO + 한국 리전 지원. 비용 큼.                                                |
| Honeycomb         | Phase 3 결정 | High-cardinality tracing 1급. OTel 친화. 한국 리전 자체 호스팅 시 보류.                    |
| New Relic         | Phase 3 결정 | 가격 모델 변경 잦음. 보류.                                                                  |

**결정 분기**: [`phases.md`](../03-roadmap/phases.md) 2028 Q3 (Phase 3 진입, SOC2 Type II 감사 시작 시점).

### SLO (Service Level Objective)

Phase 3+ 미드마켓 진입 시 Enterprise 약속의 일부.

| SLO                       | Target        | 측정                                  |
| ------------------------- | ------------- | ------------------------------------- |
| API 가용성                | 99.9% (월)    | Synthetic monitoring + RUM            |
| API P95 지연              | < 500ms       | 라우트 단위 / 워크스페이스 단위 집계   |
| WebSocket 연결 안정성     | 99.5% (월)    | DM / Huddle 신호 연결률                |
| A2UI Tool P95 응답        | < 8초         | Tool 별 메트릭                        |
| 이벤트 처리 지연 P99      | < 5초         | outbox/Kafka 폴링 + 컨슈머 처리        |

---

## 보안 인프라 (요약, 상세는 security-compliance.md)

이 절은 기술 스택 관점만. 권한 모델 / SCIM / SOC2 자료 / KISA 인증 디테일은 [`security-compliance.md`](./security-compliance.md) 위임.

| 영역                      | Phase 1-2                            | Phase 3                              | Phase 4                                       |
| ------------------------- | ------------------------------------ | ------------------------------------ | --------------------------------------------- |
| TLS                       | TLS 1.3 (Cloudflare front)           | + 인증서 자동 갱신 (cert-manager)    | + 한국 리전 인증서 분리                       |
| 내부 서비스 통신          | HTTP (단일 호스트)                   | mTLS (k8s 정식) — istio 또는 linkerd | + 한국 리전 mTLS 별도 CA                      |
| WAF                       | Cloudflare 기본                      | WAF 정식 룰셋 + DLP 골격            | + KISA 트래픽 분류 + K-ISMS 통제              |
| Rate Limit                | FastAPI middleware + Redis           | + L7 게이트웨이 (Cloudflare / Envoy) | + 한국 리전 분리 제한                         |
| 키 관리                   | env vars                             | AWS Secrets Manager + KMS            | + KISA 서명 키 (한국 리전 KMS)                |
| 감사 로그                 | PostgreSQL `AuditLog` 테이블         | + SIEM 통합 (선택)                   | + K-ISMS 5년 보존 + 한국 리전 분리            |
| 데이터 암호화 (at rest)   | DB 디스크 암호화 (RDS 기본)          | + JSONB 민감 필드 컬럼 암호화        | + 한국 리전 별도 키                           |
| 데이터 암호화 (in transit) | TLS 1.3                              | + mTLS 내부                          | (동일)                                         |

---

## 결제 / 빌링

[`pricing-strategy.md`](../01-market/pricing-strategy.md) Free / Team / Business / Enterprise 4-Tier.

| Phase     | Stripe (글로벌)        | 토스페이먼츠 / PortOne (한국)               | Enterprise 견적                                    |
| --------- | ---------------------- | ------------------------------------------- | -------------------------------------------------- |
| Phase 1   | Free / Team / Business | 카드 + 세금계산서 + 연 청구서               | 미출시                                              |
| Phase 2   | 동일                   | + 한국 세금계산서 자동 발급                 | 미출시                                              |
| Phase 3   | 동일                   | + PO 발행 / 분기 청구                       | **Enterprise 견적 / PO** ([`phases.md`](../03-roadmap/phases.md) 2029 Q1) |
| Phase 4   | 동일                   | + KISA 인증 청구서                          | + ezTax 연동 청구서 자동화                         |

**선택 근거**: 듀얼 결제. Stripe는 글로벌 표준 + 개발자 친화. 토스페이먼츠/PortOne은 한국 결제 수단 (카드/계좌이체/카카오페이/세금계산서) 1급. 한국 ICP는 토스페이먼츠가 영업 신뢰 1순위.

---

## 도입하지 않을 것 (Anti-Stack)

영업/디자인/외부 PoC가 요구해도 거절. 거절 시 다음 표가 1차 응답.

| 기술                           | 안 도입 이유                                                                                                                  | 우리 답 (대안)                                                                              |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Kubernetes (Phase 0-1)**     | 운영 부담. 알파 워크스페이스 30개 수준에서 k8s는 과잉.                                                                        | Docker Compose. Phase 2 종료 시점에 k8s 알파 진입.                                          |
| **GraphQL (Phase 1-3)**        | 권한 매핑 복잡. RLS와 정합 어려움. 미드마켓 보안 검토에서 잠재적 위험.                                                       | REST + OpenAPI + Pydantic 스키마. TypeScript 클라이언트 자동 생성으로 GraphQL의 DX 이점 흡수. |
| **Microservices (Phase 1-2)**  | 분산 운영 비용. Phase 1 팀 규모에 부적합. 도메인 경계 침식 위험.                                                              | Modular Monolith. `server/src/app/{domain}/` 모듈 분리로 미래 분리 가능성만 보존.            |
| **별도 Vector DB (Pinecone, Weaviate)** | 단일 데이터 모델 약속 깨짐 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 1).                       | pgvector + 워크스페이스별 인덱스 분리. Phase 4까지 충분.                                    |
| **MongoDB / DynamoDB**         | 단일 RDBMS 원칙. JSONB로 충분. 단일 데이터 모델 약속 깨짐.                                                                    | PostgreSQL JSONB.                                                                            |
| **Web3 / 블록체인**            | KR-first 비전 어긋남. 컴플라이언스 시장 (HR/Documents)과 정반대.                                                              | -                                                                                            |
| **Custom CRDT (협업 실시간)**  | 운영 부담 큼. Linear / Notion 수준 협업은 우리 우선순위 아님 (Phase 1-3).                                                    | Phase 1-3: last-write-wins + 보드 실시간 (Optimistic UI). Phase 4 평가.                     |
| **Federated learning**         | ROI 낮음. 미드마켓 / 엔터프라이즈 시장에서 요구 거의 없음.                                                                    | -                                                                                            |
| **자체 캘린더**                | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision "자체 캘린더 안 만듦". 4도메인 외부.                       | Google Calendar / Outlook 통합 (Phase 3+).                                                  |
| **자체 OCR / 번역 SaaS**       | [`moscow.md`](../03-roadmap/moscow.md) Won't (영구). 외부 (Google Document AI / DeepL) 위임.                                | -                                                                                            |
| **5번째 도메인 (CRM, BI, Marketing Auto)** | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision. 4도메인 깊이 우선.                                 | -                                                                                            |
| **Module Federation (마이크로 프론트엔드)** | 모노레포 + pnpm 워크스페이스로 충분.                                                                                  | Turborepo.                                                                                   |
| **CSS-in-JS (styled-components, Emotion)** | 런타임 비용 + 번들 크기 + TypeScript 추론 부담.                                                                       | Tailwind CSS 4.                                                                              |
| **Next.js (Phase 1-3)**        | SSR/RSC가 협업 SPA에 과잉. 풀스택 프레임워크 잠금.                                                                            | Vite + React SPA + (랜딩은 별도 정적 사이트 Phase 1 후반).                                  |

---

## Phase별 마이그레이션 일정 (phases.md와 동기화)

[`phases.md`](../03-roadmap/phases.md) "Phase 간 마이그레이션 결정 시점" 표를 기술 스택 관점으로 재정렬.

| 마이그레이션                       | 결정 분기        | 실행 분기         | 사전 신호 메트릭                                          | 측정 정의 위임                                  |
| ---------------------------------- | ---------------- | ----------------- | --------------------------------------------------------- | ----------------------------------------------- |
| PG outbox → Kafka(또는 Redpanda)   | 2028 Q2          | 2028 Q3-Q4        | events/sec > 1k, 워크스페이스 > 1,000개, A2UI 횡단 분당 > 1k | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| Docker Compose → k8s 알파          | 2027 Q3          | 2027 Q4           | 가용성 SLA 요구 시작, 무중단 배포 요구                    | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| k8s 알파 → 정식 (Multi-AZ + SOC2)  | 2028 Q3          | 2028 Q3 ~ 2029 Q2 | 미드마켓 진입, SOC2 Type II 감사 시작                     | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| RN/Capacitor 모바일 정식           | 2027 Q2          | 2027 Q4           | DAU 모바일 비중, 알파 사용자 모바일 요구                  | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| Supabase Storage → S3 호환         | 2028 Q1          | 2028 Q2           | 파일 / 워크스페이스당 100GB 초과 비율                     | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| OpenTelemetry 도입                 | 2027 Q3          | 2027 Q4           | 도메인 횡단 디버깅 시간 증가, A2UI trace 필요              | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| APM 정식 (Datadog/Honeycomb 결정)  | 2028 Q3          | 2028 Q4           | SLO 약속 시작, SOC2 통제 요구                              | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| Sentry → 정식 APM 통합             | 2028 Q3          | 2028 Q4           | Enterprise 견적 시작                                       | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| Secrets Manager + KMS 도입         | 2028 Q3          | 2028 Q3           | SOC2 Type II 통제 요구                                     | [`security-compliance.md`](./security-compliance.md) |
| 한국 리전 자체 호스팅 옵션         | 2030 Q1          | 2030 Q2           | Enterprise 한국 리전 요구 비율 > 30%                       | [`metrics.md`](../03-roadmap/metrics.md) 위임   |
| KISA 자체구축 vs 모두싸인 OEM      | 2029 Q1-Q2       | 2029 Q3           | 자체구축 12-18개월 비용 vs OEM 어댑터 비용·정확도          | [`security-compliance.md`](./security-compliance.md) |
| vLLM 자체 호스팅 / 멀티 프로바이더 | 2029 Q4 ~ 2030 Q1 | 2030 Q2           | LLM 비용 / 활성 워크스페이스 > $50/월, 한국어 품질 신호    | [`metrics.md`](../03-roadmap/metrics.md) 위임   |

각 마이그레이션은 **이전 Phase 종료 분기에 결정**, **다음 Phase 진입과 동시에 실행** ([`phases.md`](../03-roadmap/phases.md) 원칙 정렬).

---

## 의도적 보류 (책임 이전)

이 문서가 **다루지 않는** 것 — 다른 문서로 위임.

| 결정                                                              | 위임                                                                                                              |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 데이터 모델 ERD, 인덱스, 샤딩 전략, RLS 정책 SQL                  | [`data-model.md`](./data-model.md)                                                                                |
| Tool Registry 구현, LangGraph supervisor 권한 전파 패턴, Tool 카탈로그 상세 | [`a2ui-strategy.md`](./a2ui-strategy.md)                                                                  |
| SCIM ↔ Role 매핑, SOC2 Type II 인증 자료 구조, KISA / K-ISMS 인증 디테일 | [`security-compliance.md`](./security-compliance.md)                                                              |
| 분기 KR 측정 정의 (events/sec, P99 지연 등 임계치)                | [`metrics.md`](../03-roadmap/metrics.md)                                                                          |
| 도메인별 service 함수 시그니처 / API 라우트 / 이벤트 페이로드     | [`domain-pm.md`](../02-product/domain-pm.md), [`domain-comms.md`](../02-product/domain-comms.md), [`domain-hr.md`](../02-product/domain-hr.md), [`domain-documents.md`](../02-product/domain-documents.md) |
| Phase별 출시 일정 / 분기 OKR                                      | [`phases.md`](../03-roadmap/phases.md), [`moscow.md`](../03-roadmap/moscow.md)                                    |
| 가격 / Tier 게이팅 결제 메커니즘                                  | [`pricing-strategy.md`](../01-market/pricing-strategy.md)                                                         |
| ICP별 영업 자료 / GTM 채널                                        | [`gtm-strategy.md`](../01-market/gtm-strategy.md) (TODO)                                                          |

---

## 관련 문서

- [`../02-product/domain-overview.md`](../02-product/domain-overview.md) — 4도메인 경계, 공유 엔티티, 이벤트 카탈로그, A2UI Tool, 데이터 격리 결정
- [`../03-roadmap/phases.md`](../03-roadmap/phases.md) — Phase 0-4 분기 OKR, Phase 간 마이그레이션 결정 시점
- [`../03-roadmap/moscow.md`](../03-roadmap/moscow.md) — Must/Should/Could/Won't (Anti-Stack의 정렬 근거)
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — 5가지 불변 원칙 (단일 데이터 모델, 단일 권한 모델, 헤드리스, KR-first, Linear UX)
- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 4축 (KR-first 차별화 표는 Phase 4 종료 조건 근거)
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — Tier 게이팅 / 결제 인프라
- [`./data-model.md`](./data-model.md) — 단일 데이터 모델 ERD, RLS, 샤딩 (작성 예정)
- [`./a2ui-strategy.md`](./a2ui-strategy.md) — LangGraph 헤드리스 아키텍처, Tool Registry, 권한 전파 (작성 예정)
- [`./security-compliance.md`](./security-compliance.md) — SCIM, SOC2, KISA, K-ISMS, 권한 모델 구현 (작성 예정)
- [`../03-roadmap/metrics.md`](../03-roadmap/metrics.md) — Phase별 KR 측정 정의, 마이그레이션 트리거 임계치 (작성 예정)

---

## 변경 정책

이 문서는 **4개 트리거** 시 갱신한다.

1. **분기 GTM 리뷰**: [`phases.md`](../03-roadmap/phases.md) "Phase 간 마이그레이션 결정 시점" 표의 결정 분기 도래 시 — 결정 자료 / 비교 / Go-Hold 회의 결과를 본 문서에 반영.
2. **Phase 종료**: 각 Phase 종료 시점에 다음 Phase의 스택 진화 표 / 마이그레이션 일정 재정의.
3. **Watch List 신호 발견**: [`product-vision.md`](../00-vision/product-vision.md) Watch List 6개 / [`domain-overview.md`](../02-product/domain-overview.md) Watch List 8개 중 기술 관련 신호 발견 시 분기 기다리지 않음.
4. **임계치 초과 메트릭 발견**: "운영 단순성 vs 처리량 트레이드오프" 임계치 (events/sec, 워크스페이스 수, A2UI 호출율) 1개 이상 초과 시.

**금지 사항**

- 영업/디자인 압력만으로 Anti-Stack 항목 도입 — 거절. 표준 답변: "기술 스택 결정 문서 Anti-Stack 절을 보세요."
- 새 기술 도입 시 "이게 없으면 못 만든다" 입증 없이 PoC 진행 — 금지.
- Phase 1-2 단계에 Phase 3+ 인프라(k8s 정식, Kafka, mTLS) 미리 도입 — 금지. 자원 분산 + 운영 부담 폭증.
- 한 분기에 2개 이상 큰 마이그레이션 동시 실행 — 금지. PG outbox → Kafka + Docker Compose → k8s 동시는 위험.

**책임자**: Backend Architect (1차) + CTO (Phase 마이그레이션 Go-Hold 결정) + SRE (관측·운영 측면). 갱신 시 변경 이력을 본 파일 하단에 추가.

---

## 변경 이력

| 날짜       | 버전     | 변경 요약                                                                                                                       | 작성자             |
| ---------- | -------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| 2026-06-24 | draft v1 | 최초 작성. CLAUDE.md 현재 스택 + domain-overview.md "이벤트 스토리지 결정" + phases.md "마이그레이션 결정 시점" 통합. Anti-Stack 14개 박음. | Backend Architect  |
