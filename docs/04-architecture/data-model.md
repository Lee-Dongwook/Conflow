---
title: 단일 데이터 모델 v1 (ERD + RLS + 마이그레이션)
최종 업데이트: 2026-06-24
상태: draft v1
독자: 백엔드, 데이터 엔지니어, 보안
---

# 단일 데이터 모델 v1

> 이 문서는 [`domain-overview.md`](../02-product/domain-overview.md)의 "Shared Core 5 엔티티"와 도메인 문서 4개([`domain-pm.md`](../02-product/domain-pm.md) / [`domain-comms.md`](../02-product/domain-comms.md) / [`domain-hr.md`](../02-product/domain-hr.md) / [`domain-documents.md`](../02-product/domain-documents.md))의 "핵심 엔티티"를 **한 ERD 위에 봉합**한다. [`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 1·2 ("단일 데이터 모델", "워크스페이스 격리")가 Phase 1-4 내내 깨지지 않게 만든다.
>
> 이 문서가 봉인하는 결정: Shared Core 5개 엔티티의 정확한 컬럼 + 인덱스, 도메인 4개 × 핵심 엔티티 v1 스키마, RLS 정책 SQL 패턴, EntityLink 도메인 횡단 참조, 이벤트 outbox 테이블, Phase별 진화, Alembic 마이그레이션 규칙, JSONB vs 별도 테이블 결정.

> **draft v1 가설 주의** — Phase 0 Q3 데이터 모델 합의([`phases.md`](../03-roadmap/phases.md) 2026 Q3 KR1)의 기반. 실제 마이그레이션 적용 전에는 Phase 0 알파에서 검증해야 한다. 컬럼/인덱스 디테일은 Alembic 1차 머지 후 점진 조정.

---

## 이 문서로 내릴 결정

1. **Shared Core 5개 엔티티의 정확한 컬럼·인덱스·RLS 정책** — `workspaces` / `members` / `roles` + `role_assignments` / `audit_logs` / `entity_links`. 모든 도메인은 이걸 **read-only로 참조**한다.
2. **도메인 4개의 핵심 엔티티 v1 스키마** — PM 7개 / Comms 8개 / HR 13개 / Documents 13개. 각 엔티티의 컬럼 + 인덱스 prefix 규칙 + 이벤트 outbox 연결.
3. **RLS 정책 SQL 패턴** — 모든 테이블에 `workspace_id` 컬럼 + 세션 변수 강제. `workspace_id` 누락 쿼리는 PostgreSQL이 자동 차단. 외부 협업자(노무사·세무사)는 `resource_scope` 보조 정책.
4. **이벤트 outbox + Kafka 전환 규칙** — Phase 1-2는 PostgreSQL `event_outbox` + LISTEN/NOTIFY, Phase 3는 Kafka dual-write 6주, Phase 3+에서 outbox.published_at 의미 변경. [`domain-overview.md`](../02-product/domain-overview.md) "이벤트 스토리지 결정" 봉인.
5. **JSONB vs 별도 테이블 결정 기준** — 도메인 외부 스키마(AuditLog.metadata, Role.permissions, DocumentTemplate.variables_schema)만 JSONB. 도메인 직접 소유 필드(Issue.custom_fields, Workspace.settings)는 별도 테이블.
6. **Phase별 데이터 모델 진화 마일스톤** — v1 Phase 0-1 (Shared Core + PM/Comms), v2 Phase 2 (HR/Documents 알파 + 권한 세분화), v3 Phase 3 (SCIM/외부 협업자 + Event Bus 전환), v4 Phase 4 (KISA/ezTax/PayrollRun + 멀티 리전). Alembic 다운타임 0 원칙.

---

## 설계 원칙

1. **Shared Core 5개 엔티티는 4도메인 모두 read-only 참조**. 도메인은 `Workspace` / `Member` / `Role` 등을 직접 mutate 하지 않는다. mutate 진입점은 Auth / Billing / Admin / HR(입퇴사) 한정.
2. **`workspace_id` 컬럼이 모든 테이블에** — PostgreSQL RLS로 강제. 누락된 쿼리는 자동 차단. [`domain-overview.md`](../02-product/domain-overview.md) 다중 테넌트 격리 결정 1번.
3. **도메인 횡단 참조는 `entity_links` 거침** (직접 FK 금지) — PM `issues`에 `source_message_id` 같은 횡단 외래키 금지. EntityLink + 이벤트로만.
4. **ID는 UUID v7** — 시간 순서(인덱스 친화) + 분산 환경(샤딩 / Phase 4 멀티 리전) 동시 지원. PostgreSQL 16 `uuidv7()` 함수 또는 애플리케이션 측 생성. 알파 단계 단순화 위해 application-level 생성으로 시작.
5. **Soft delete (`deleted_at TIMESTAMPTZ NULL`) 기본** — hard delete는 보존 정책 만료 잡 + 법정 익명화에 한정. 보존 기간은 도메인 결정(HR 3년, Documents 카테고리별, Comms Tier별).
6. **시간 컬럼은 `*_at TIMESTAMPTZ`, UTC 저장** — 표시 시점에 Workspace.region timezone 변환. Python `datetime.now(UTC)` 패턴(ruff `UP017` 자동 수정 정렬).
7. **JSONB는 "스키마가 도메인 외부 결정"인 경우만** — AuditLog.metadata, Role.permissions, DocumentTemplate.variables_schema, Board.filter_spec 같이 카테고리별·인스턴스별 스키마가 다른 경우. 도메인이 직접 소유한 정형 필드에는 JSONB 금지.
8. **인덱스: `workspace_id`를 모든 복합 인덱스 prefix로** — RLS와 정합. 쿼리 플래너가 `workspace_id` 필터 후 부수 컬럼을 처리.
9. **마이그레이션 다운타임 0** — Alembic + 호환 변경 (ADD COLUMN NULL → backfill → SET NOT NULL의 3단계 분할). DROP COLUMN / 이름 변경 금지(Phase 종료 시 일괄).

---

## 명명 / 형식 컨벤션

| 대상 | 규칙 | 예시 |
| ---- | ---- | ---- |
| 테이블 | snake_case 복수형 | `workspaces`, `members`, `issues`, `document_instances` |
| PK | `id UUID` | `id UUID PRIMARY KEY` |
| FK | `{entity}_id` | `workspace_id`, `assignee_member_id`, `template_id` |
| 시간 | `*_at TIMESTAMPTZ` | `created_at`, `deleted_at`, `signed_at` |
| 불리언 | `is_*` (또는 `has_*`) | `is_archived`, `has_signature` |
| enum | PostgreSQL native ENUM | `member_status`, `workspace_tier`, `issue_status` |
| 인덱스 | `idx_{table}_{cols}` | `idx_issues_workspace_status`, `idx_messages_workspace_channel_created` |
| 유니크 인덱스 | `uq_{table}_{cols}` | `uq_workspaces_slug`, `uq_members_workspace_email` |
| RLS 정책 | `rls_{table}_workspace_isolation` | `rls_issues_workspace_isolation` |
| 외부 협업자 RLS | `rls_{table}_external_scope` | `rls_document_instances_external_scope` |
| 이벤트 outbox | `event_outbox`, 이벤트명 `{domain}.{noun}.{verb}` | `pm.issue.created`, `hr.member.onboarded` |

**원칙**: 이름이 컨벤션을 벗어나는 순간 정적 분석 룰(다음 절)이 실패하도록 한다. [`domain-overview.md`](../02-product/domain-overview.md) 다중 테넌트 격리 결정 2번(SQLAlchemy 정적 분석).

---

## Shared Core ERD

### `workspaces` — 단일 테넌트 경계

| 컬럼 | 타입 | 제약 | 설명 |
| ---- | ---- | ---- | ---- |
| `id` | UUID | PK | UUID v7 |
| `name` | TEXT | NOT NULL | 표시명 |
| `slug` | TEXT | UNIQUE NOT NULL | URL slug |
| `tier` | workspace_tier ENUM | NOT NULL DEFAULT 'free' | free / team / business / enterprise |
| `region` | workspace_region ENUM | NOT NULL DEFAULT 'kr' | kr / jp (Phase 4+) |
| `billing_account_id` | UUID | NULL | Billing 모듈 참조 (Phase 1) |
| `settings_id` | UUID | NULL | 워크스페이스 설정 별도 테이블 참조 (JSONB 무한 확장 금지) |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULL | soft delete |

**ENUM**:
```sql
CREATE TYPE workspace_tier AS ENUM ('free', 'team', 'business', 'enterprise');
CREATE TYPE workspace_region AS ENUM ('kr', 'jp');
```

**인덱스**:
- `uq_workspaces_slug` (UNIQUE on `slug`)
- `idx_workspaces_tier` (`tier`) — Tier 게이팅 조회용
- `idx_workspaces_region_tier` (`region`, `tier`) — Phase 4 멀티 리전 분기

**RLS**: super 권한만 (전체 워크스페이스 조회). 일반 mutation은 Workspace Owner.

### `members` — 한 사람 = 한 워크스페이스 1회

| 컬럼 | 타입 | 제약 | 설명 |
| ---- | ---- | ---- | ---- |
| `id` | UUID | PK | UUID v7 |
| `workspace_id` | UUID | NOT NULL FK → workspaces | 격리 단위 |
| `user_id` | UUID | NULL | Supabase auth.users.id (외부 협업자는 NULL 가능) |
| `display_name` | TEXT | NOT NULL | |
| `email` | TEXT | NOT NULL | |
| `status` | member_status ENUM | NOT NULL DEFAULT 'invited' | active / invited / disabled / external |
| `joined_at` | TIMESTAMPTZ | NULL | active 진입 시점 |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULL | soft delete (퇴사 / 외부 협업자 회수) |

**ENUM**:
```sql
CREATE TYPE member_status AS ENUM ('active', 'invited', 'disabled', 'external');
```

**인덱스**:
- `uq_members_workspace_email` (UNIQUE on `workspace_id, email`) — 한 워크스페이스에 같은 email 1회
- `idx_members_workspace_status` (`workspace_id`, `status`)
- `idx_members_workspace_user` (`workspace_id`, `user_id`) — SSO 매핑 조회

**RLS**: 워크스페이스 격리. 외부 협업자(`status='external'`)는 별도 `role_assignments`로 리소스 단위 권한.

**원칙**: 한 사람이 여러 워크스페이스에 동시 존재 가능 — **각 워크스페이스마다 별도 `members.id`**. 노무사가 여러 클라이언트사에 외부 협업자로 가입하는 경우 ([`domain-hr.md`](../02-product/domain-hr.md))의 기반.

### `roles` — 권한 정의

| 컬럼 | 타입 | 제약 | 설명 |
| ---- | ---- | ---- | ---- |
| `id` | UUID | PK | |
| `workspace_id` | UUID | NOT NULL FK → workspaces | |
| `name` | role_name ENUM | NOT NULL | owner / admin / member / guest / external |
| `scope_type` | role_scope_type ENUM | NOT NULL | workspace / resource |
| `permissions` | JSONB | NOT NULL DEFAULT '{}' | 도메인별 권한 비트맵 (예: `{"pm.issue.write": true, "hr.evaluation.read": false}`) |
| `is_system` | BOOLEAN | NOT NULL DEFAULT FALSE | 기본 시스템 role 여부 |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |

**ENUM**:
```sql
CREATE TYPE role_name AS ENUM ('owner', 'admin', 'member', 'guest', 'external');
CREATE TYPE role_scope_type AS ENUM ('workspace', 'resource');
```

**인덱스**:
- `idx_roles_workspace_name` (`workspace_id`, `name`)
- `idx_roles_workspace_scope` (`workspace_id`, `scope_type`)

### `role_assignments` — 권한 부여

| 컬럼 | 타입 | 제약 | 설명 |
| ---- | ---- | ---- | ---- |
| `id` | UUID | PK | |
| `workspace_id` | UUID | NOT NULL FK → workspaces | |
| `member_id` | UUID | NOT NULL FK → members | |
| `role_id` | UUID | NOT NULL FK → roles | |
| `resource_type` | TEXT | NULL | 예: `pm.project`, `comms.channel`, `documents.review`, `hr.employee_profile_group` |
| `resource_id` | UUID | NULL | 해당 리소스 PK |
| `granted_by_member_id` | UUID | NULL FK → members | 누가 부여했는지 |
| `expires_at` | TIMESTAMPTZ | NULL | 외부 협업자 / 임시 권한 만료 |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `revoked_at` | TIMESTAMPTZ | NULL | 1-click 회수 시점 |

**인덱스**:
- `idx_role_assignments_workspace_member` (`workspace_id`, `member_id`) — caller 권한 조회의 핫 패스
- `idx_role_assignments_workspace_resource` (`workspace_id`, `resource_type`, `resource_id`) — 리소스 단위 권한자 조회
- `idx_role_assignments_member_active` (`member_id`) WHERE `revoked_at IS NULL` — 활성 권한만

**원칙**: 외부 협업자(노무사) 권한 회수는 `revoked_at` 갱신 + WebSocket 연결 종료 + `audit_logs` 발생. 5초 이내 access 차단 약속 ([`domain-hr.md`](../02-product/domain-hr.md)).

### `audit_logs` — 4도메인 통합 감사

| 컬럼 | 타입 | 제약 | 설명 |
| ---- | ---- | ---- | ---- |
| `id` | UUID | PK | UUID v7 (시간 순서) |
| `workspace_id` | UUID | NOT NULL | (FK 생략 — 파티션 성능) |
| `actor_member_id` | UUID | NULL | NULL = system actor (retention 잡 등) |
| `domain` | audit_domain ENUM | NOT NULL | pm / comms / hr / documents / core |
| `action` | TEXT | NOT NULL | 예: `issue.created`, `member.offboarded` |
| `resource_type` | TEXT | NOT NULL | 예: `pm.issue`, `documents.instance` |
| `resource_id` | UUID | NULL | |
| `metadata` | JSONB | NOT NULL DEFAULT '{}' | 도메인별 추가 정보 |
| `is_external_collaborator` | BOOLEAN | NOT NULL DEFAULT FALSE | 외부 협업자(노무사·세무사) 액션 마킹 |
| `trace_id` | TEXT | NULL | OpenTelemetry trace |
| `occurred_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 파티션 키 |

**ENUM**:
```sql
CREATE TYPE audit_domain AS ENUM ('pm', 'comms', 'hr', 'documents', 'core');
```

**파티셔닝**:
- `occurred_at` 기준 **월 단위 RANGE 파티셔닝** (PostgreSQL native).
- 매월 자동 생성 잡 (`pg_partman` 또는 자체 잡). 보존 기간 만료 파티션은 detach + 아카이브.
- Phase 3+ 파티션 수 > 60개 (5년) 시 TimescaleDB 전환 검토.

**인덱스** (각 파티션):
- `idx_audit_workspace_occurred` (`workspace_id`, `occurred_at DESC`) — 핫 패스
- `idx_audit_workspace_domain_action` (`workspace_id`, `domain`, `action`)
- `idx_audit_workspace_actor` (`workspace_id`, `actor_member_id`, `occurred_at DESC`)
- `idx_audit_external` (`workspace_id`, `is_external_collaborator`, `occurred_at DESC`) WHERE `is_external_collaborator = TRUE`

**Tier별 보관**:
- Free: 30일 / Team: 90일 / Business: 1년 / Enterprise: 무제한 (또는 협상).
- 만료 파티션은 `cold storage`(S3 Parquet) 아카이브 후 detach. Enterprise는 무제한 유지.

**원칙**: 도메인별 `audit_*` 테이블 만들지 않는다 — SOC2 Type II 인증 자료가 단일 테이블이어야 통과 가능 ([`domain-overview.md`](../02-product/domain-overview.md) 원칙).

### `entity_links` — 도메인 횡단 참조

| 컬럼 | 타입 | 제약 | 설명 |
| ---- | ---- | ---- | ---- |
| `id` | UUID | PK | |
| `workspace_id` | UUID | NOT NULL FK → workspaces | |
| `source_type` | TEXT | NOT NULL | 예: `comms.message`, `pm.issue` |
| `source_id` | UUID | NOT NULL | |
| `target_type` | TEXT | NOT NULL | 예: `pm.issue`, `documents.instance` |
| `target_id` | UUID | NOT NULL | |
| `link_kind` | entity_link_kind ENUM | NOT NULL | references / derived_from / blocks / mentioned_in / subtask_of |
| `created_by_member_id` | UUID | NULL FK → members | |
| `metadata` | JSONB | NOT NULL DEFAULT '{}' | 링크별 부가 정보 (예: 컨버전 신뢰도) |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULL | |

**ENUM**:
```sql
CREATE TYPE entity_link_kind AS ENUM (
  'references',     -- 단순 참조 (PM 이슈가 Comms 메시지를 인용)
  'derived_from',   -- 변환 출처 (PM 이슈가 Comms 결정 → 변환됨)
  'blocks',         -- 차단 관계 (이슈 A가 이슈 B를 막음)
  'mentioned_in',   -- 멘션 (이슈가 채널에 멘션됨)
  'subtask_of'      -- 부모-자식 (Jira sub-task 임포트, Phase 2)
);
```

**인덱스** (양방향 필요):
- `idx_entity_links_workspace_source` (`workspace_id`, `source_type`, `source_id`)
- `idx_entity_links_workspace_target` (`workspace_id`, `target_type`, `target_id`, `link_kind`)
- `idx_entity_links_workspace_kind_created` (`workspace_id`, `link_kind`, `created_at DESC`) — A2UI "comms 결정 중 PM 미전환" 쿼리

**원칙 (편도 가시성 보장)**: source / target **양쪽 권한 모두** 확인 후 노출. 한쪽 권한만 있으면 링크 자체가 안 보임. service 진입점에서 caller_member_id로 양쪽 권한 검증. 검증 누락은 [`domain-overview.md`](../02-product/domain-overview.md) Watch List #6 직결.

### `event_outbox` — Phase 1-2 이벤트 버스

| 컬럼 | 타입 | 제약 | 설명 |
| ---- | ---- | ---- | ---- |
| `id` | UUID | PK | UUID v7 |
| `workspace_id` | UUID | NOT NULL | (FK 생략 — 파티션) |
| `event_name` | TEXT | NOT NULL | 예: `pm.issue.created`, `hr.member.onboarded` |
| `payload` | JSONB | NOT NULL | 이벤트 페이로드 |
| `headers` | JSONB | NOT NULL DEFAULT '{}' | trace_id / idempotency_key / actor 등 |
| `occurred_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 생성 시점 |
| `published_at` | TIMESTAMPTZ | NULL | worker 발행 완료 시점 |
| `published_attempts` | INT | NOT NULL DEFAULT 0 | 재시도 횟수 |
| `last_error` | TEXT | NULL | 마지막 재시도 실패 메시지 |
| `trace_id` | TEXT | NULL | |

**인덱스**:
- `idx_event_outbox_unpublished` (`occurred_at`) WHERE `published_at IS NULL` — worker 폴링 핫 패스 (PARTIAL INDEX로 작게)
- `idx_event_outbox_workspace_name_occurred` (`workspace_id`, `event_name`, `occurred_at DESC`)

**작동 방식 (Phase 1-2)**:
1. 도메인 service가 트랜잭션 안에서 mutation + `INSERT event_outbox`를 함께 커밋(transactional outbox 패턴).
2. PostgreSQL `LISTEN/NOTIFY`로 worker 깨움 + 폴링 fallback (LISTEN 누락 대비).
3. Worker가 `published_at IS NULL` 행을 가져와 발행(WebSocket / 도메인 핸들러). 성공 시 `published_at` 세팅.
4. 재시도 정책: exponential backoff, 10회 실패 시 DLQ 테이블 이동.

**Phase 3 Kafka 전환 메커니즘**:
- 6주간 dual-write: outbox + Kafka 동시 발행. consumer 측 idempotency_key로 중복 흡수.
- Phase 3 종료 시 outbox는 audit/recovery 용도로만 유지. `published_at` 의미는 "Kafka 발행 시점"으로 변경.
- 전환 트리거: 워크스페이스 1,000개 초과 또는 이벤트율 > 1k/sec ([`domain-overview.md`](../02-product/domain-overview.md) 이벤트 스토리지 결정).

---

## 도메인 엔티티 v1 ERD

각 도메인 엔티티는 [`domain-{pm,comms,hr,documents}.md`](../02-product/) 의 "핵심 엔티티" 절을 시작점으로 한다. 여기서는 컬럼·인덱스·이벤트 발행을 봉인.

### PM 도메인 (7 엔티티)

#### `projects`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `name` | TEXT | NOT NULL |
| `slug` | TEXT | NOT NULL |
| `lead_member_id` | UUID | NULL FK → members |
| `visibility` | project_visibility ENUM | NOT NULL DEFAULT 'internal' |
| `status` | project_status ENUM | NOT NULL DEFAULT 'planned' |
| `target_date` | DATE | NULL |
| `created_at`, `updated_at`, `deleted_at` | TIMESTAMPTZ | 표준 |

**ENUM**:
```sql
CREATE TYPE project_visibility AS ENUM ('private', 'internal', 'public_in_workspace');
CREATE TYPE project_status AS ENUM ('planned', 'in_progress', 'paused', 'completed', 'cancelled');
```

**인덱스**: `uq_projects_workspace_slug`, `idx_projects_workspace_status`, `idx_projects_workspace_lead`.

#### `sprints`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `project_id` | UUID | NULL FK → projects |
| `name` | TEXT | NOT NULL |
| `start_date`, `end_date` | DATE | NOT NULL |
| `phase` | sprint_phase ENUM | NOT NULL DEFAULT 'planned' |
| `velocity` | INT | NULL (completed 후 계산) |
| `created_at`, `updated_at`, `deleted_at` | TIMESTAMPTZ | 표준 |

**ENUM**: `CREATE TYPE sprint_phase AS ENUM ('planned', 'active', 'completed');`

**인덱스**: `idx_sprints_workspace_phase`, `idx_sprints_workspace_project_dates` (`workspace_id`, `project_id`, `start_date`, `end_date`).

#### `issues`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `project_id` | UUID | NOT NULL FK → projects |
| `sprint_id` | UUID | NULL FK → sprints |
| `title` | TEXT | NOT NULL |
| `description` | TEXT | NULL |
| `status` | issue_status ENUM | NOT NULL DEFAULT 'backlog' |
| `priority` | issue_priority ENUM | NOT NULL DEFAULT 'medium' |
| `reporter_member_id` | UUID | NOT NULL FK → members |
| `assignee_member_id` | UUID | NULL FK → members |
| `due_date` | DATE | NULL |
| `blocked_since` | TIMESTAMPTZ | NULL (status=blocked 시점) |
| `blocked_reason` | TEXT | NULL |
| `external_source` | TEXT | NULL (jira / linear / notion) |
| `external_source_id` | TEXT | NULL (임포트 추적) |
| `created_at`, `updated_at`, `deleted_at` | TIMESTAMPTZ | 표준 |

**ENUM**:
```sql
CREATE TYPE issue_status AS ENUM ('backlog', 'todo', 'in_progress', 'blocked', 'done', 'cancelled');
CREATE TYPE issue_priority AS ENUM ('urgent', 'high', 'medium', 'low');
```

**인덱스**:
- `idx_issues_workspace_status_created` (`workspace_id`, `status`, `created_at DESC`)
- `idx_issues_workspace_assignee_status` (`workspace_id`, `assignee_member_id`, `status`)
- `idx_issues_workspace_project_sprint` (`workspace_id`, `project_id`, `sprint_id`)
- `idx_issues_workspace_blocked` (`workspace_id`, `blocked_since`) WHERE `status = 'blocked'` — `pm.identify_blockers` Tool 핫 패스
- `idx_issues_external_source` (`workspace_id`, `external_source`, `external_source_id`) — 임포트 idempotency
- 풀텍스트: `idx_issues_title_fts` (GIN tsvector_kor + tsvector_eng on `title`, `description`)

**이벤트 발행**: `pm.issue.created` / `pm.issue.updated` / `pm.issue.blocked` (status → blocked) / `pm.issue.unblocked` (Phase 2) / `pm.issue.resolved` / `pm.issue.cancelled`.

#### `boards`, `backlog_items`, `labels`, `issue_labels` (M:N), `comments`

| 테이블 | 핵심 컬럼 | 인덱스 |
| ----- | -------- | ----- |
| `boards` | `id`, `workspace_id`, `project_id?`, `name`, `type` (kanban/list/timeline), `filter_spec JSONB`, `column_spec JSONB`, `created_by_member_id` | `idx_boards_workspace_project` |
| `backlog_items` | `id`, `workspace_id`, `project_id`, `issue_id`, `position FLOAT` | `uq_backlog_workspace_project_issue`, `idx_backlog_workspace_project_position` |
| `labels` | `id`, `workspace_id`, `scope_type` (workspace/project), `scope_id?`, `name`, `color`, `description?` | `uq_labels_workspace_scope_name` |
| `issue_labels` | `issue_id`, `label_id`, `workspace_id` | PK (`issue_id`, `label_id`), `idx_issue_labels_workspace_label` |
| `comments` | `id`, `workspace_id`, `issue_id`, `author_member_id`, `body TEXT`, `parent_comment_id?`, `mentions UUID[]`, `created_at`, `edited_at`, `deleted_at` | `idx_comments_workspace_issue_created` |

**이벤트**: `pm.project.created` / `pm.project.status_changed` / `pm.sprint.started` / `pm.sprint.ended` / `pm.backlog.reordered` (Phase 2) / `pm.comment.added` / `pm.comment.mentioned` / `pm.import.completed`.

### Comms 도메인 (8 엔티티)

#### `channels`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `name` | TEXT | NOT NULL |
| `type` | channel_type ENUM | NOT NULL |
| `topic` | TEXT | NULL |
| `is_archived` | BOOLEAN | NOT NULL DEFAULT FALSE |
| `archived_at` | TIMESTAMPTZ | NULL |
| `created_by_member_id` | UUID | NOT NULL FK → members |
| `created_at`, `updated_at`, `deleted_at` | TIMESTAMPTZ | 표준 |

**ENUM**: `CREATE TYPE channel_type AS ENUM ('public', 'private', 'dm', 'external');`

**인덱스**: `uq_channels_workspace_name` (`workspace_id`, `name`) WHERE `type IN ('public','private')`, `idx_channels_workspace_type` (`workspace_id`, `type`).

#### `channel_members` (M:N)

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `channel_id` | UUID | NOT NULL FK |
| `member_id` | UUID | NOT NULL FK |
| `workspace_id` | UUID | NOT NULL |
| `joined_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() |
| `left_at` | TIMESTAMPTZ | NULL |
| `last_read_message_id` | UUID | NULL |

PK: (`channel_id`, `member_id`). 인덱스: `idx_channel_members_workspace_member`, `idx_channel_members_workspace_channel_active` (`workspace_id`, `channel_id`) WHERE `left_at IS NULL`.

#### `messages`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK (UUID v7, 시간 순) |
| `workspace_id` | UUID | NOT NULL FK |
| `channel_id` | UUID | NOT NULL FK |
| `thread_root_id` | UUID | NULL (스레드 루트면 NULL) |
| `author_member_id` | UUID | NOT NULL FK |
| `body` | TEXT | NOT NULL |
| `attachments` | JSONB | NOT NULL DEFAULT '[]' (파일 메타: URI, MIME, size) |
| `mentions` | UUID[] | NOT NULL DEFAULT '{}' (멤버 ID 배열) |
| `decision_flag` | decision_flag ENUM | NULL (Phase 2) |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() |
| `edited_at` | TIMESTAMPTZ | NULL |
| `deleted_at` | TIMESTAMPTZ | NULL |

**ENUM**: `CREATE TYPE decision_flag AS ENUM ('candidate', 'confirmed', 'dismissed');`

**인덱스**:
- `idx_messages_workspace_channel_created` (`workspace_id`, `channel_id`, `created_at DESC`) — 채널 메시지 조회 핫 패스
- `idx_messages_workspace_thread` (`workspace_id`, `thread_root_id`, `created_at`)
- `idx_messages_workspace_author_created` (`workspace_id`, `author_member_id`, `created_at DESC`)
- `idx_messages_mentions` (GIN on `mentions`) — `@member` 멘션 조회
- 풀텍스트: `idx_messages_body_fts` (GIN tsvector_kor on `body`) — 한국어 형태소 분석기 `mecab-ko` 또는 동등.

**파티셔닝 (Phase 3+)**: `created_at` 월 단위. 메시지 수 > 1억 건 시 권장.

#### `mentions`, `reactions`, `huddle_sessions` (Phase 2), `decisions` (Phase 2), `notifications`

| 테이블 | 핵심 컬럼 | 인덱스 |
| ----- | -------- | ----- |
| `mentions` | `id`, `workspace_id`, `message_id`, `mentioned_member_id`, `created_at` | `idx_mentions_workspace_member_created` |
| `reactions` | `id`, `workspace_id`, `message_id`, `member_id`, `emoji_code`, `created_at` | `uq_reactions_message_member_emoji` |
| `huddle_sessions` | `id`, `workspace_id`, `channel_id`, `started_by_member_id`, `phase` (scheduled/active/ended/archived), `participants UUID[]`, `started_at`, `ended_at?`, `recording_uri?`, `transcript_uri?`, `summary?` | `idx_huddles_workspace_channel_started` |
| `decisions` | `id`, `workspace_id`, `source_message_id?`, `source_huddle_id?`, `decision_text`, `participants UUID[]`, `confidence FLOAT`, `state` (detected/confirmed/converted_to_issue/dismissed), `confirmed_by_member_id?`, `converted_issue_id?`, `created_at` | `idx_decisions_workspace_state_created`, `idx_decisions_workspace_confidence` (`workspace_id`, `confidence DESC`) WHERE `state='detected'` |
| `notifications` | `id`, `workspace_id`, `recipient_member_id`, `source_type`, `source_id`, `payload JSONB`, `read_at?`, `dismissed_at?`, `created_at` | `idx_notifications_workspace_recipient_unread` (WHERE `read_at IS NULL`) |

**이벤트 발행**: `comms.message.posted` / `comms.message.edited` / `comms.message.deleted` / `comms.thread.replied` / `comms.mention.created` / `comms.channel.created` / `comms.channel.archived` / `comms.member.joined_channel` / `comms.member.left_channel` / `comms.huddle.started` / `comms.huddle.ended` / `comms.decision.detected` / `comms.decision.confirmed`.

### HR 도메인 (13 엔티티)

#### `employee_profiles`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `member_id` | UUID | NOT NULL UNIQUE FK → members (1:1) |
| `employee_no` | TEXT | NULL |
| `title` | TEXT | NULL |
| `org_unit_id` | UUID | NULL FK → org_units |
| `employment_type` | employment_type ENUM | NOT NULL |
| `hired_at` | DATE | NULL |
| `manager_member_id` | UUID | NULL FK → members |
| `birth_date` | DATE | NULL (**HR-only 계층**) |
| `phone` | TEXT | NULL (**HR-only 계층**) |
| `tenure_status` | tenure_status ENUM | NOT NULL DEFAULT 'candidate' |
| `leave_balance_days` | NUMERIC(5,2) | NULL (**Manager-visible 계층**) |
| `insurance_consent_at` | TIMESTAMPTZ | NULL (Phase 3) |
| `contract_signed_at` | TIMESTAMPTZ | NULL (Phase 2, Documents 구독) |
| `data_retention_expires_at` | TIMESTAMPTZ | NULL (offboarded 후 법정 보존 만료) |
| `created_at`, `updated_at`, `deleted_at` | TIMESTAMPTZ | 표준 |

**ENUM**:
```sql
CREATE TYPE employment_type AS ENUM ('regular', 'contract', 'outsourced', 'intern');
CREATE TYPE tenure_status AS ENUM (
  'candidate', 'pre_hire', 'active', 'on_leave',
  'pre_offboarding', 'offboarded', 'archived_legal'
);
```

**인덱스**:
- `uq_employee_profiles_workspace_member` (`workspace_id`, `member_id`)
- `idx_employee_profiles_workspace_tenure` (`workspace_id`, `tenure_status`)
- `idx_employee_profiles_workspace_org_unit` (`workspace_id`, `org_unit_id`)
- `idx_employee_profiles_workspace_manager` (`workspace_id`, `manager_member_id`)

**프라이버시 4계층 컬럼 메타데이터** (Phase 2 v2 마이그레이션에서 추가):
- `column_privacy_layer` 별도 메타 테이블 또는 SQLAlchemy 모델 메타데이터로 표시.
- 예: `birth_date.privacy=hr_only`, `title.privacy=public`, `leave_balance_days.privacy=manager_visible`.
- service 레이어에서 응답 직렬화 시 caller_member_id의 권한 계층과 컬럼 메타 비교 → 응답 마스킹.

#### `org_units`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `parent_org_unit_id` | UUID | NULL FK (self-ref) |
| `name` | TEXT | NOT NULL |
| `manager_member_id` | UUID | NULL FK → members |
| `kind` | org_unit_kind ENUM | NOT NULL |
| `cost_center_code` | TEXT | NULL (Phase 4) |
| `is_archived` | BOOLEAN | NOT NULL DEFAULT FALSE |
| `created_at`, `updated_at`, `deleted_at` | TIMESTAMPTZ | 표준 |

**ENUM**: `CREATE TYPE org_unit_kind AS ENUM ('department', 'team', 'squad');`

**인덱스**: `idx_org_units_workspace_parent`, `idx_org_units_workspace_manager`.

#### `onboarding_workflows`, `onboarding_steps`, `offboarding_workflows`

| 테이블 | 핵심 컬럼 |
| ----- | -------- |
| `onboarding_workflows` | `id`, `workspace_id`, `target_member_id`, `template_id?`, `phase` (pending/in_progress/completed/cancelled), `started_at?`, `completed_at?`, `progress_pct INT`, `assigned_buddy_member_id?` |
| `onboarding_steps` | `id`, `workflow_id`, `workspace_id`, `kind` (account_provision/channel_join/equipment/document_sign/training/kpi_setup), `target_domain?` (pm/comms/documents), `target_payload JSONB`, `status` (pending/in_progress/done/skipped), `due_date?`, `responsible_member_id?`, `order` |
| `offboarding_workflows` | `id`, `workspace_id`, `target_member_id`, `reason_code` (resignation/agreed_termination/dismissal/contract_end/retirement), `requires_labor_review BOOLEAN`, `effective_date`, `phase`, `final_payment_status?`, `data_retention_policy TEXT` |

**인덱스**: 모두 `workspace_id` prefix. 추가 `idx_onboarding_workflows_workspace_phase`, `idx_offboarding_workflows_workspace_requires_labor_review` (WHERE TRUE).

#### `one_on_ones` (HR-only 권한 — Admin 조회 차단)

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `manager_member_id` | UUID | NOT NULL FK |
| `report_member_id` | UUID | NOT NULL FK |
| `scheduled_at` | TIMESTAMPTZ | NOT NULL |
| `held_at` | TIMESTAMPTZ | NULL |
| `notes_md` | TEXT | NULL |
| `action_items` | JSONB | NOT NULL DEFAULT '[]' |
| `mood` | TEXT | NULL (Phase 3) |
| `visibility` | one_on_one_visibility ENUM | NOT NULL DEFAULT 'manager_and_report' |
| `created_at`, `updated_at` | TIMESTAMPTZ | 표준 |

**ENUM**: `CREATE TYPE one_on_one_visibility AS ENUM ('manager_and_report', 'report_only_after_session');`

**인덱스**: `idx_one_on_ones_workspace_manager_report_scheduled` (`workspace_id`, `manager_member_id`, `report_member_id`, `scheduled_at DESC`).

**RLS 특수 정책** — Admin / Owner도 자동 SELECT 차단:
```sql
CREATE POLICY rls_one_on_ones_participant_only ON one_on_ones
USING (
  workspace_id = current_setting('app.workspace_id')::UUID
  AND (
    manager_member_id = current_setting('app.member_id')::UUID
    OR report_member_id = current_setting('app.member_id')::UUID
    OR current_setting('app.audit_mode', true) = 'true'  -- 감사 모드 (양당사자 동의 시만)
  )
);
```

**이벤트**: `hr.one_on_one.recorded` — 페이로드는 **키워드 / 테마만** (원문 X). 다른 도메인 구독 금지 (A2UI 한정).

#### `leave_requests`, `attendance_records`, `evaluation_cycles` (Phase 3), `insurance_enrollments` (Phase 3), `labor_documents` (Phase 3), `payroll_records` (Phase 4), `kpi_notes`

| 테이블 | 핵심 컬럼 | Phase |
| ----- | -------- | ----- |
| `leave_requests` | `id`, `workspace_id`, `requester_member_id`, `leave_type` (annual/sick/family/compensatory/public/parental/maternity), `start_date`, `end_date`, `half_day BOOLEAN`, `reason_md`, `attachments JSONB`, `status` (draft/submitted/approved/rejected/consumed/cancelled), `approver_member_id?` | 2 |
| `attendance_records` | `id`, `workspace_id`, `member_id`, `work_date`, `check_in_at?`, `check_out_at?`, `overtime_minutes INT`, `policy_id?`, `anomaly_flag?` | 3 |
| `evaluation_cycles` | `id`, `workspace_id`, `name`, `period_start`, `period_end`, `phase` (scheduled/self_review/manager_review/calibration/closed), `participants JSONB`, `template_id` | 3 |
| `insurance_enrollments` | `id`, `workspace_id`, `employee_profile_id`, `insurance_type` (national_pension/health/employment/industrial_accident), `event_kind` (enroll/unenroll/monthly_salary_change), `effective_date`, `monthly_compensation NUMERIC`, `status`, `labor_advisor_review_id? FK → labor_documents`, `external_submission_id?` | 3 |
| `labor_documents` | `id`, `workspace_id`, `employee_profile_id`, `kind` (employment_contract/resignation/agreed_termination/dismissal_notice/harassment_report/wage_statement), `document_instance_id FK → document_instances`, `labor_advisor_review_state`, `confidential_level` (hr_only/advisor_visible) | 3 |
| `payroll_records` | `id`, `workspace_id`, `employee_profile_id`, `period TEXT (YYYY-MM)`, `gross_amount NUMERIC`, `net_amount NUMERIC`, `withholding_tax NUMERIC`, `insurance_deductions JSONB`, `source` (manual/adp_import/flex_import/labor_advisor_system), `document_instance_id?`, `state` | 4 |
| `kpi_notes` | `id`, `workspace_id`, `subject_member_id`, `author_member_id`, `kind` (praise/coaching/concern), `body_md`, `visibility` (subject_and_author/hr_admin_too) | 3 |

**인덱스 패턴**: 모두 `workspace_id` prefix. `leave_requests`는 `idx_leave_requests_workspace_requester_status_dates`. `attendance_records`는 `uq_attendance_workspace_member_date`. `insurance_enrollments`는 `idx_insurance_workspace_profile_type_event`. `labor_documents`는 `idx_labor_documents_workspace_profile_kind`. `payroll_records`는 `uq_payroll_workspace_profile_period`.

**이벤트 발행**: `hr.member.onboarded` / `hr.member.offboarded` / `hr.profile.updated` / `hr.org_unit.changed` / `hr.onboarding.*` / `hr.offboarding.*` / `hr.one_on_one.recorded` / `hr.leave.*` / `hr.evaluation.*` / `hr.insurance.*` / `hr.labor_document.*` / `hr.labor_compliance.alert` / `hr.attendance.anomaly_detected` / `hr.payroll.*`.

### Documents 도메인 (13 엔티티)

#### `document_templates`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `name` | TEXT | NOT NULL |
| `category` | document_category ENUM | NOT NULL |
| `subtype` | TEXT | NOT NULL (예: employment_contract, wage_statement) |
| `body_md` | TEXT | NOT NULL |
| `variables_schema` | JSONB | NOT NULL DEFAULT '[]' (변수 명세) |
| `default_review_workflow_id` | UUID | NULL |
| `default_retention_policy_id` | UUID | NOT NULL FK → retention_policies |
| `requires_signature` | BOOLEAN | NOT NULL DEFAULT FALSE |
| `version` | TEXT | NOT NULL (semver) |
| `state` | template_state ENUM | NOT NULL DEFAULT 'draft' |
| `published_at` | TIMESTAMPTZ | NULL |
| `created_by_member_id` | UUID | NOT NULL FK |
| `created_at`, `updated_at`, `deleted_at` | TIMESTAMPTZ | 표준 |

**ENUM**:
```sql
CREATE TYPE document_category AS ENUM ('labor', 'tax', 'internal_issuance', 'external_submission', 'report');
CREATE TYPE template_state AS ENUM ('draft', 'published', 'deprecated');
```

**인덱스**: `idx_document_templates_workspace_category_subtype` (`workspace_id`, `category`, `subtype`), `idx_document_templates_workspace_state`.

#### `document_instances`

| 컬럼 | 타입 | 제약 |
| ---- | ---- | ---- |
| `id` | UUID | PK |
| `workspace_id` | UUID | NOT NULL FK |
| `template_id` | UUID | NOT NULL FK |
| `template_version` | TEXT | NOT NULL |
| `subject_member_id` | UUID | NULL FK |
| `requester_member_id` | UUID | NOT NULL FK |
| `variables_snapshot` | JSONB | NOT NULL (발급 시점 데이터 동결) |
| `rendered_pdf_uri` | TEXT | NULL |
| `state` | instance_state ENUM | NOT NULL DEFAULT 'draft' |
| `review_workflow_id` | UUID | NULL FK |
| `signature_request_id` | UUID | NULL FK |
| `retention_policy_id` | UUID | NOT NULL FK → retention_policies |
| `retention_expires_at` | TIMESTAMPTZ | NULL |
| `issued_at` | TIMESTAMPTZ | NULL |
| `void_reason` | TEXT | NULL |
| `created_at`, `updated_at` | TIMESTAMPTZ | 표준 |

**ENUM**:
```sql
CREATE TYPE instance_state AS ENUM (
  'draft', 'pending_review', 'approved', 'signed',
  'issued', 'archived', 'archived_legal_only', 'void'
);
```

**인덱스**:
- `idx_document_instances_workspace_state` (`workspace_id`, `state`)
- `idx_document_instances_workspace_subject_state` (`workspace_id`, `subject_member_id`, `state`)
- `idx_document_instances_workspace_template_created` (`workspace_id`, `template_id`, `created_at DESC`)
- `idx_document_instances_retention_due` (`retention_expires_at`) WHERE `state IN ('issued', 'archived')` — 만료 잡 핫 패스
- `idx_document_instances_workspace_category` (조인 후 사용, `template_id` → `category`) — 매개 view 또는 denormalized `category` 컬럼 옵션

#### `document_versions`, `review_workflows`, `review_steps`, `review_comments`

| 테이블 | 핵심 컬럼 |
| ----- | -------- |
| `document_versions` | `id`, `instance_id`, `workspace_id`, `version_no INT`, `body_snapshot TEXT`, `rendered_at`, `rendered_by_member_id`, `change_summary?` (append-only) |
| `review_workflows` | `id`, `workspace_id`, `instance_id`, `steps_count INT`, `current_step_index INT`, `state` (pending/in_progress/approved/rejected) |
| `review_steps` | `id`, `workflow_id`, `workspace_id`, `order INT`, `reviewer_role` (hr_admin/labor_advisor/legal/subject_self/signer), `reviewer_member_id?`, `requires_approval BOOLEAN`, `state` (pending/in_progress/approved/rejected/skipped), `acted_at?`, `comment_md?`, `parallel_group?` |
| `review_comments` | `id`, `workflow_id`, `step_id?`, `workspace_id`, `author_member_id`, `body_md`, `anchor JSONB?`, `parent_comment_id?`, `resolved_at?`, `created_at` |

**인덱스**: `idx_review_workflows_workspace_instance`, `idx_review_steps_workflow_order`, `idx_review_steps_workspace_reviewer_pending` (`workspace_id`, `reviewer_member_id`, `state`) WHERE `state IN ('pending','in_progress')` — `documents.list_pending_review` Tool 핫 패스.

#### `signature_requests`, `signers`, `kisa_signatures` (Phase 4)

| 테이블 | 핵심 컬럼 | Phase |
| ----- | -------- | ----- |
| `signature_requests` | `id`, `workspace_id`, `instance_id`, `mode` (sequential/parallel), `state` (draft/sent/in_progress/completed/cancelled/expired), `sent_at?`, `completed_at?`, `expires_at?`, `provider` (internal_simple_phase3 / kisa_self_phase4 / modusign_oem_phase4) | 3 |
| `signers` | `id`, `signature_request_id`, `workspace_id`, `signer_member_id?`, `signer_external_email?`, `role` (employee/employer/witness/labor_advisor/counterparty), `order INT`, `state` (waiting/notified/viewed/signed/declined), `signed_at?`, `signature_artifact_uri?`, `ip_address INET?`, `device_info JSONB?` | 3 |
| `kisa_signatures` | `id`, `signer_id`, `workspace_id`, `certificate_serial TEXT`, `issuer_dn TEXT`, `subject_dn TEXT`, `signing_algorithm TEXT`, `signed_hash BYTEA`, `timestamp_token BYTEA` (RFC 3161), `validation_state` (valid/revoked/expired/unverifiable), `provider_response_blob JSONB`, `verified_at?` | 4 |

**인덱스**: `idx_signature_requests_workspace_instance`, `idx_signers_request_order`, `idx_signers_workspace_member_state` (signer 큐 조회), `idx_kisa_signatures_workspace_validation_state`.

#### `retention_policies`, `eztax_filings` (Phase 4), `payroll_runs` (Phase 4), `reports`

| 테이블 | 핵심 컬럼 | Phase |
| ----- | -------- | ----- |
| `retention_policies` | `id`, `workspace_id`, `name`, `category`, `subtype?`, `retention_years INT`, `retention_basis` (creation/issuance/employment_end/fiscal_year_end), `on_expiry` (delete/anonymize/archive_legal_only), `legal_basis_ref TEXT` | 2 |
| `eztax_filings` | `id`, `workspace_id`, `filing_kind` (withholding_monthly/year_end_settlement/business_income), `period TEXT`, `subject_employee_profile_ids UUID[]`, `document_instance_ids UUID[]`, `state` (draft/prepared/submitted_to_eztax/acknowledged/rejected/void), `eztax_submission_id?`, `acknowledged_at?`, `error_blob JSONB?` | 4 |
| `payroll_runs` | `id`, `workspace_id`, `period TEXT (YYYY-MM)`, `source_payroll_record_ids UUID[]`, `document_instance_ids UUID[]`, `state` (draft/generated/delivered/sealed), `delivered_at?`, `total_count INT`, `error_count INT` | 4 |
| `reports` | `id`, `instance_id`, `workspace_id`, `report_kind` (sprint_report/investor_monthly/hr_quarterly/labor_compliance/eztax_year_end), `period_start`, `period_end`, `data_source_trace JSONB`, `regenerable BOOLEAN` | 2 |

**인덱스**: `idx_retention_policies_workspace_category_subtype`, `idx_eztax_filings_workspace_period_kind`, `idx_payroll_runs_workspace_period`, `idx_reports_workspace_kind_period`.

**이벤트 발행**: `documents.template.*` / `documents.instance.*` / `documents.review.*` / `documents.signature.*` / `documents.signer.*` / `documents.contract.signed` / `documents.kisa.*` / `documents.retention.*` / `documents.eztax.*` / `documents.payroll.*` / `documents.report.generated`.

---

## RLS (Row Level Security) 정책

### 기본 정책 — 모든 도메인 테이블에 동일 형식

PostgreSQL 16 RLS로 `workspace_id` 격리를 강제한다. 모든 도메인 테이블에 다음 형식 정책을 적용:

```sql
-- 예: issues 테이블
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE issues FORCE ROW LEVEL SECURITY;  -- 테이블 소유자도 우회 X

CREATE POLICY rls_issues_workspace_isolation ON issues
  USING (workspace_id = current_setting('app.workspace_id')::UUID)
  WITH CHECK (workspace_id = current_setting('app.workspace_id')::UUID);
```

**세션 변수 주입 패턴** — 모든 요청 시작 시:
```sql
SET LOCAL app.workspace_id = '...';
SET LOCAL app.member_id = '...';
SET LOCAL app.role_names = 'member,project_maintainer';  -- 쉼표 구분
```

**SQLAlchemy 통합** — `server/src/app/core/db.py`에 `WorkspaceScopedSession` mixin:
```python
@event.listens_for(Session, "after_begin")
def _inject_workspace_context(session, transaction, connection):
    ctx = current_workspace_context.get()
    connection.execute(text("SET LOCAL app.workspace_id = :ws"), {"ws": str(ctx.workspace_id)})
    connection.execute(text("SET LOCAL app.member_id = :m"), {"m": str(ctx.member_id)})
```

`workspace_id` 누락 쿼리는 `current_setting('app.workspace_id')` 미설정 → PostgreSQL이 자동 차단(NULL 비교). [`domain-overview.md`](../02-product/domain-overview.md) 다중 테넌트 격리 결정 1번.

### 외부 협업자 (노무사 / 세무사) 정책

외부 협업자는 `members.status='external'` + `role_assignments`에 `resource_type/resource_id` 지정. 추가 RLS 정책으로 다른 클라이언트사 / 다른 사원의 문서 차단:

```sql
-- 예: document_instances 외부 협업자 정책
CREATE POLICY rls_document_instances_external_scope ON document_instances
  USING (
    workspace_id = current_setting('app.workspace_id')::UUID
    AND (
      -- 내부 멤버는 카테고리별 기존 권한 체크 (service 레이어)
      current_setting('app.member_status') != 'external'
      OR
      -- 외부 협업자는 명시적 RoleAssignment 지정된 인스턴스만
      EXISTS (
        SELECT 1 FROM role_assignments ra
        WHERE ra.workspace_id = document_instances.workspace_id
          AND ra.member_id = current_setting('app.member_id')::UUID
          AND ra.resource_type = 'documents.review'
          AND ra.resource_id = document_instances.id
          AND ra.revoked_at IS NULL
          AND (ra.expires_at IS NULL OR ra.expires_at > NOW())
      )
    )
  );
```

[`domain-hr.md`](../02-product/domain-hr.md) Switch Trigger #3 약속의 RLS 측 표현. 누수 발견 = Watch List #1.

### Super 우회 (마이그레이션 / 운영)

Alembic 마이그레이션 / cron 만료 잡 / 백업 잡 등 시스템 작업은 RLS 우회 필요:

```sql
-- 시스템 service role에는 BYPASSRLS 권한 부여
ALTER ROLE conflow_system BYPASSRLS;
```

**우회 사용 시 audit 강제**:
- 시스템 service role로 mutation 시 `audit_logs.actor_member_id = NULL`, `actor_kind = 'system'`.
- 우회 사용 모든 쿼리에 `application_name` 마킹 (`SET application_name = 'retention_expire_job'`) — pg_stat_activity에서 추적.

### 외부 협업자 ↔ 외부 협업자 DM 금지

[`domain-comms.md`](../02-product/domain-comms.md) 정책의 RLS 측 표현 — `channels.type='dm'` 채널 가입 시 `channel_members` 트리거로 외부↔외부 조합 검사:

```sql
CREATE TRIGGER trigger_block_external_to_external_dm
BEFORE INSERT ON channel_members
FOR EACH ROW EXECUTE FUNCTION fn_block_external_to_external_dm();

-- 함수: DM 채널이고 추가하려는 member가 external이며
--      이미 external 멤버가 있으면 RAISE EXCEPTION
```

---

## 인덱스 전략

### 핵심 원칙

1. **복합 인덱스의 첫 컬럼은 무조건 `workspace_id`** — RLS 필터 후 부수 컬럼 처리. PostgreSQL 쿼리 플래너가 RLS 정책으로 추가하는 `workspace_id = ?` 조건과 정합.
2. **시간순 조회는 `(workspace_id, created_at DESC)`** — 메시지 / 이슈 / 알림 등 "최신 N건" 패턴.
3. **상태 필터는 PARTIAL INDEX** — 예: `WHERE state IN ('pending','in_progress')`로 인덱스 크기 축소.
4. **외부 ID 임포트 idempotency는 UNIQUE 인덱스** — `(workspace_id, external_source, external_source_id)`.

### 풀텍스트 검색 (Phase 1)

- PostgreSQL `tsvector` + `pg_trgm` 보조.
- 한국어 형태소: `mecab-ko-dic` 또는 `pgsearch` 확장. Phase 1 가설은 mecab-ko, PoC에서 정확도 검증.
- 영어 / 한국어 분리 인덱스:
  ```sql
  ALTER TABLE messages ADD COLUMN tsvector_kor tsvector
    GENERATED ALWAYS AS (to_tsvector('korean_mecab', body)) STORED;
  CREATE INDEX idx_messages_tsvector_kor ON messages USING GIN (tsvector_kor);
  ```
- 권한 필터 정합: 검색 쿼리에 `channel_id IN (caller가 멤버인 channels)` 강제 필터 ([`domain-comms.md`](../02-product/domain-comms.md) 권한 누수 방지).

### 시맨틱 검색 / 벡터 (Phase 2)

- `pgvector` 확장. 1536차원 (text-embedding-3-small) 또는 768차원 (한국어 fine-tune 옵션).
- 인덱스 선택:
  - **ivfflat** — 대규모, 빠른 빌드, ~95% recall. 메시지 수 1억+ 적합.
  - **hnsw** — 더 정확, 느린 빌드 / 큰 메모리. Phase 2 알파에는 hnsw 권장.
- 예:
  ```sql
  CREATE TABLE message_embeddings (
    message_id UUID PRIMARY KEY,
    workspace_id UUID NOT NULL,
    embedding vector(1536) NOT NULL,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  );
  CREATE INDEX idx_message_embeddings_hnsw ON message_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WHERE workspace_id IS NOT NULL;
  ```

### 샤딩 (Phase 4+ 검토)

- Phase 1-3는 단일 PostgreSQL 클러스터로 충분 (워크스페이스 < 1,000개 / 데이터 < 1TB 가설).
- Phase 4+ 워크스페이스 > 1,000개 또는 메시지 1억 건 초과 시:
  - **`workspace_id` hash 샤딩** — Citus 또는 자체 라우팅. 한 워크스페이스의 모든 도메인 테이블은 같은 샤드.
  - **Enterprise 한정 별도 클러스터** — 한국 리전 / 망분리 요구 시. 단일 데이터 모델은 유지, 물리 격리만 추가.
- 결정 시점은 [`tech-stack.md`](./tech-stack.md) 위임 (Phase 3 종료 시점 데이터 기반).

---

## EntityLink 패턴 — 도메인 횡단 참조

### 사용 예시

**예 1: Comms 메시지 → PM 이슈 변환**
```sql
-- Comms 도메인 service에서 트랜잭션:
INSERT INTO issues (id, workspace_id, project_id, title, description, ...) VALUES (...);
INSERT INTO entity_links (
  workspace_id, source_type, source_id, target_type, target_id, link_kind, created_by_member_id
) VALUES (
  $ws, 'comms.message', $message_id, 'pm.issue', $issue_id, 'derived_from', $caller_id
);
INSERT INTO event_outbox (workspace_id, event_name, payload, ...) VALUES
  ($ws, 'pm.issue.created', '{...}'),
  ($ws, 'comms.decision.confirmed', '{...}');
```

**예 2: A2UI "Slack 결정 중 Jira 미전환" 쿼리**
```sql
SELECT d.id, d.decision_text, m.body
FROM decisions d
JOIN messages m ON m.id = d.source_message_id
WHERE d.workspace_id = $ws
  AND d.state = 'detected'
  AND NOT EXISTS (
    SELECT 1 FROM entity_links el
    WHERE el.workspace_id = d.workspace_id
      AND el.source_type = 'comms.message'
      AND el.source_id = m.id
      AND el.target_type = 'pm.issue'
      AND el.link_kind = 'derived_from'
  );
```

### 권한 양방향 체크 (편도 가시성 보장)

EntityLink 조회 시 **source / target 양쪽 권한 모두 필요**. service 레이어 패턴:

```python
def list_links(workspace_id: UUID, source: tuple[str, UUID], caller: Member) -> list[EntityLink]:
    links = db.query(EntityLink).filter(
        EntityLink.workspace_id == workspace_id,
        EntityLink.source_type == source[0],
        EntityLink.source_id == source[1],
    ).all()
    # 양방향 권한 체크
    visible = []
    for link in links:
        if not _can_access(caller, link.source_type, link.source_id):
            continue
        if not _can_access(caller, link.target_type, link.target_id):
            continue
        visible.append(link)
    return visible
```

한쪽 권한만 있으면 link 자체가 안 보임. [`domain-overview.md`](../02-product/domain-overview.md) Watch List #6 직결. 회귀 테스트 필수.

---

## 다중 테넌트 격리 — 깨짐 탐지

[`domain-overview.md`](../02-product/domain-overview.md)의 4가지 메커니즘을 데이터 모델 측면에서 구현:

### 1. RLS 강제

- 모든 도메인 테이블에 `workspace_id` 컬럼 + RLS 정책 (위 절).
- `FORCE ROW LEVEL SECURITY`로 테이블 소유자도 우회 X.
- migration 시 정책 적용 누락 검출: `pg_policies` 시스템 카탈로그 조회 + CI 검사.

### 2. SQLAlchemy 정적 분석 룰

- ruff custom rule 또는 사전 작성된 모델 메타 검사:
  - 모든 `Model.__table__.columns`에 `workspace_id` 존재 검사 (제외: `workspaces` 자체 + 시스템 테이블).
  - 모든 `session.query(Model)` 또는 `select(Model)` 패턴에 `.filter(Model.workspace_id == ctx.workspace_id)` 또는 `WorkspaceScopedSession` 사용 검사.
- 누락 시 빌드 실패.

### 3. Pytest contract test

```python
# tests/contract/test_workspace_isolation.py
def test_cross_tenant_read_blocked(db_session):
    ws_a, ws_b = create_workspaces()
    issue_a = create_issue(workspace=ws_a)
    # ws_b 컨텍스트로 조회 시도
    with workspace_context(ws_b):
        result = db_session.query(Issue).filter(Issue.id == issue_a.id).first()
        assert result is None, "cross-tenant read leak!"
```

모든 도메인 모델에 동일 패턴 contract test 필수. CI에서 매번 실행.

### 4. AuditLog cross-tenant 알람

cron 잡 (시간당) — `audit_logs.actor_member_id`의 워크스페이스와 `audit_logs.workspace_id` 불일치 검사:

```sql
SELECT a.id, a.workspace_id, m.workspace_id AS actor_workspace_id
FROM audit_logs a
JOIN members m ON m.id = a.actor_member_id
WHERE a.workspace_id != m.workspace_id
  AND a.occurred_at > NOW() - INTERVAL '1 hour';
```

결과 1건이라도 발견 시 즉시 보안 Admin 알람 + circuit breaker로 cross-tenant 가능 service 정지.

---

## JSONB 사용 기준

### ✅ JSONB 적합

| 컬럼 | 이유 |
| ---- | ---- |
| `audit_logs.metadata` | 도메인마다 다른 부가 정보 (예: PM은 `from_status/to_status`, Documents는 `template_id/category`) |
| `roles.permissions` | 스코프별 다른 권한 비트맵 (예: workspace scope vs resource scope) |
| `document_templates.variables_schema` | 템플릿마다 변수 개수·타입 다름 |
| `boards.filter_spec`, `boards.column_spec` | 사용자 정의 보드 — 도메인이 의미 해석 안 함 |
| `event_outbox.payload`, `event_outbox.headers` | 이벤트마다 스키마 다름 |
| `entity_links.metadata` | 링크별 부가 정보 (예: AI 변환 신뢰도) |
| `signers.device_info` | 서명 시점 디바이스 메타 (개수·필드 가변) |
| `kisa_signatures.provider_response_blob` | 외부 KISA 사업자 응답 원본 (감사·재검증 위해 그대로 보존) |
| `one_on_ones.action_items` | 액션 아이템 배열 (member_id, due_date, description) — 검색 / 조인 안 함 |

### ❌ JSONB 부적합

| 패턴 | 대신 |
| ---- | ---- |
| `issues.custom_fields` | PM이 직접 소유하는 정형 필드 → 별도 `issue_custom_field_values` 테이블 + `issue_custom_fields` 정의 (Phase 3+) |
| `workspaces.settings` 무한 확장 | 별도 `workspace_settings` 테이블 (1:1 또는 카테고리별) |
| `employee_profiles.payroll_history` | 별도 `payroll_records` 테이블 (집계 / 조인 필요) |
| `messages.tags` | 별도 `message_tags` 테이블 (M:N, 검색 필요) |

**판단 기준**:
- 도메인이 의미를 해석하는가? YES → 별도 테이블. NO (보존·통과만) → JSONB 가능.
- 조인 / 집계 / GIN 인덱스로 검색해야 하는가? YES → 별도 테이블 권장.
- 스키마가 인스턴스별로 다른가? YES → JSONB 가능.

---

## Alembic 마이그레이션 규칙

### 디렉토리 구조

- 위치: `server/alembic/versions/`
- 명명: `YYYYMMDD_HHMM_{slug}.py` (예: `20271015_1430_add_decisions_table.py`)
- 한 마이그레이션 = 한 논리 변경 (테이블 추가 / 컬럼 추가 / 인덱스 추가 등 묶기 가능, 단 롤백 가능해야 함).

### 다운타임 0 원칙

**ADD COLUMN 패턴 (3단계 분할)**:
1. **마이그레이션 N**: ADD COLUMN nullable, DEFAULT NULL.
2. **마이그레이션 N+1**: backfill 잡 (별도 배치 — 큰 테이블은 chunk 단위) + 코드가 양쪽 모두 지원하도록 배포.
3. **마이그레이션 N+2**: SET NOT NULL + DEFAULT 제거. 코드가 새 컬럼만 쓰도록 배포.

**DROP COLUMN 금지** (Phase 1-2): 일단 unused 후 Phase 종료 시점에 일괄 제거 마이그레이션.

**이름 변경 금지** (Phase 1-3): 새 컬럼 만들고 dual-write로 cutover 후 옛 컬럼 unused.

**ENUM 값 추가**: PostgreSQL `ALTER TYPE ... ADD VALUE`는 안전. **값 제거 / 변경은 금지** — 새 ENUM 만들고 cutover.

### 큰 마이그레이션 — 별도 배치 잡

`workspace_id` backfill 같은 큰 변경은 Alembic 스크립트 안에서 직접 실행 X. 대신:
1. Alembic으로 컬럼 추가 + 잡 ID 발급.
2. Celery 배치 잡으로 chunk 단위 backfill (1만 행씩).
3. 완료 후 Alembic post-step으로 NOT NULL 적용.

### 정책 / RLS 마이그레이션

테이블 추가 시 RLS 정책 동시 마이그레이션 의무:

```python
def upgrade():
    op.create_table('decisions', ...)
    op.execute("ALTER TABLE decisions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE decisions FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY rls_decisions_workspace_isolation ON decisions
        USING (workspace_id = current_setting('app.workspace_id')::UUID)
        WITH CHECK (workspace_id = current_setting('app.workspace_id')::UUID)
    """)
```

CI에서 `pg_policies` 카탈로그 조회 — 새 테이블에 정책 누락 시 빌드 실패.

### 롤백 정책

- `downgrade()` 반드시 구현. 다만 `DROP COLUMN` / `DROP TABLE` 롤백은 데이터 손실 가능 — 운영 환경에서는 별도 백업 후 실행.
- 인덱스 추가는 `CREATE INDEX CONCURRENTLY` 사용 (테이블 락 회피).

---

## Phase별 진화

### v1 (Phase 0 – Phase 1) — Shared Core 5 + PM/Comms 핵심

- **2026 Q3 ([`phases.md`](../03-roadmap/phases.md))**: Shared Core 5개 + PM 7개 + Comms 8개(Huddle/Decisions 제외) 1차 마이그레이션.
- **2027 Q1-Q2**: 임포터 추적 컬럼 (`external_source`, `external_source_id`) 추가. WebSocket presence 테이블 (Phase 2 예약).
- **컬럼·테이블 추가 가능, 호환 변경만**.
- **이벤트 outbox 가동** — PostgreSQL LISTEN/NOTIFY.

### v2 (Phase 2) — HR/Documents 알파 + 권한 세분화

- **2027 Q3-Q4**: HR 6개 (employee_profiles, org_units, onboarding_*, one_on_ones, leave_requests) + Documents 7개 (document_templates, document_instances, document_versions, review_*, retention_policies) 추가.
- Comms `huddle_sessions`, `decisions` 추가.
- `role_assignments`에 `resource_type/resource_id` 본격 사용 — Project별 권한, 채널별 권한.
- HR 프라이버시 4계층 컬럼 메타데이터 도입 — 별도 `column_privacy` 메타 테이블 또는 SQLAlchemy 모델 메타.
- `one_on_ones` 특수 RLS 정책 (참가자만, Admin 차단).
- **2028 Q2 결정 게이트** ([`phases.md`](../03-roadmap/phases.md) Phase 2 종료): [`domain-overview.md`](../02-product/domain-overview.md)의 권한 모델 확장이 미드마켓 진입에 충분한가 — 미충족 시 v3 진입 전 권한 모델 v2 추가 빌드.

### v3 (Phase 3) — SCIM / 노무사 외부 협업자 + Event Bus 전환

- **2028 Q3-Q4**: HR 추가 6개 (`evaluation_cycles`, `insurance_enrollments`, `labor_documents`, `attendance_records`, `kpi_notes`) + Documents 추가 (`signature_requests`, `signers`).
- `scim_mappings` 테이블 추가 — IdP 그룹 ↔ Role 매핑.
- 외부 협업자 본격 가동 — `members.status='external'` + `role_assignments.resource_*` + 외부 협업자 RLS 정책 활성화.
- **PG outbox → Kafka 전환** (6주 dual-write):
  - 이벤트 outbox 테이블 유지 (audit / recovery 용도).
  - 새 이벤트는 Kafka가 1차, outbox.published_at은 "Kafka 발행 시점" 의미로 변경.
  - Consumer는 idempotency_key로 중복 흡수.

### v4 (Phase 4) — KISA / ezTax / PayrollRun + 멀티 리전

- **2029 Q3+**: Documents 추가 (`kisa_signatures`, `eztax_filings`, `payroll_runs`) + HR `payroll_records`.
- `audit_logs` 파티션 수 60개+ — TimescaleDB 전환 검토.
- `workspaces.region` 활용 본격 — 한국 리전 Enterprise는 별도 클러스터 옵션:
  - 단일 데이터 모델 유지, 물리 격리만 추가.
  - 워크스페이스별 connection routing (`workspace_id → region → cluster`).
- KISA 인증서 메타는 한국 리전 강제 — `kisa_signatures` 테이블은 KR 리전 클러스터만 존재.

### 마이그레이션 의무 갱신 트리거

| 트리거 | 갱신 |
| ----- | ---- |
| 도메인 문서에서 새 엔티티 추가 | 이 문서 ERD 절 갱신 → Alembic 마이그레이션 작성 |
| Phase 종료 | Phase별 진화 마일스톤 절 갱신 + 다음 Phase ENUM 값 사전 정의 |
| 법령 개정 (근로기준법 / 세법) | `retention_policies` seed 데이터 갱신 (`legal_basis_ref`) |
| Watch List 신호 1개 이상 | 즉시 갱신 (분기 기다리지 않음) |

---

## 안티패턴 / Watch List (데이터 모델 관련)

[`domain-overview.md`](../02-product/domain-overview.md) Watch List 8개 중 데이터 모델 직결 항목:

| # | 신호 | 그러면 무엇을 한다 |
| - | --- | ----------------- |
| 1 | 도메인 간 직접 FK (예: `issues.source_message_id`) | `entity_links` 우회로 강제 리팩토링. CI 정적 분석에 도메인 횡단 FK 금지 룰 추가 |
| 2 | `workspace_id` 없는 컬럼 / 쿼리 머지됨 | 핫픽스 + RLS 정책 강화 + CI 룰 검토 (왜 통과했는지) |
| 3 | 도메인별 `audit_*` 테이블 신설 | 통합 `audit_logs` 약속 깨짐. 즉시 통합 + SOC2 Type II 영향 분석 |
| 4 | `private` Project / private 채널 / HR 1:1 데이터가 다른 워크스페이스로 노출 | 즉시 회로 차단 + cross-tenant audit 잡 강화 |
| 5 | RLS 정책 누락된 테이블 발견 | 마이그레이션 적용 + `pg_policies` 자동 검사 강화 |
| 6 | JSONB 컬럼이 도메인 직접 소유 필드를 흡수 (예: `issue.metadata.custom_fields`) | 별도 테이블로 분리. JSONB 사용 기준 위반 |
| 7 | 인덱스 첫 컬럼이 `workspace_id` 아닌 신규 인덱스 | 쿼리 플래너가 RLS 필터 비효율. 인덱스 재정의 |
| 8 | `event_outbox.published_at = NULL` 행이 10분 이상 적체 | worker 장애. 알람 + 큐 모니터링 강화 |

---

## 의도적 보류 (책임 이전)

| 결정 | 어디로 미루는가 |
| ---- | ------------- |
| 이벤트 카탈로그 페이로드 스키마 상세 | [`domain-overview.md`](../02-product/domain-overview.md) 이벤트 카탈로그 + 각 도메인 문서 |
| 인덱스 튜닝 / 슬로우 쿼리 분석 | 분기 데이터 리뷰 (운영 단계) |
| 백업 / 복원 / DR / RPO / RTO | [`tech-stack.md`](./tech-stack.md), [`security-compliance.md`](./security-compliance.md) |
| KISA / ezTax 외부 키 관리 (HSM, KMS) | [`security-compliance.md`](./security-compliance.md) |
| SCIM 매핑 상세 (Azure AD / Okta / Google Workspace) | [`security-compliance.md`](./security-compliance.md) |
| pgvector vs 외부 벡터 DB (Pinecone / Weaviate) 결정 | [`tech-stack.md`](./tech-stack.md) Phase 2 |
| Kafka vs Redpanda vs NATS 최종 선택 | [`tech-stack.md`](./tech-stack.md) Phase 2 종료 시점 |
| WebSocket 인프라 (Postgres LISTEN/NOTIFY vs Redis Pub/Sub vs NATS) | [`tech-stack.md`](./tech-stack.md) |
| 샤딩 전략 구체 (Citus vs 자체 라우팅) | [`tech-stack.md`](./tech-stack.md) Phase 3 종료 시점 |
| 한국 리전 자체 호스팅 인프라 (NCP / KT Cloud / 자체 IDC) | [`tech-stack.md`](./tech-stack.md), [`security-compliance.md`](./security-compliance.md) Phase 4 |
| K-ISMS 인증 자료 자동 생성 잡 구현 | [`security-compliance.md`](./security-compliance.md) Phase 4 |
| LangGraph supervisor → service 권한 전파 패턴 | [`a2ui-strategy.md`](./a2ui-strategy.md) |

---

## 관련 문서

- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — 불변 원칙 1·2 (단일 데이터 모델 + 워크스페이스 격리)
- [`../02-product/domain-overview.md`](../02-product/domain-overview.md) — Shared Core 5개 + 이벤트 카탈로그 + 다중 테넌트 결정 (이 문서의 시작점)
- [`../02-product/domain-pm.md`](../02-product/domain-pm.md) — PM 7 엔티티 + Phase별 출시
- [`../02-product/domain-comms.md`](../02-product/domain-comms.md) — Comms 8 엔티티 + 권한 누수 방지
- [`../02-product/domain-hr.md`](../02-product/domain-hr.md) — HR 13 엔티티 + 프라이버시 4계층 + 노무사 외부 협업자
- [`../02-product/domain-documents.md`](../02-product/domain-documents.md) — Documents 13 엔티티 + 보존 정책 매트릭스 + KISA/ezTax
- [`../03-roadmap/phases.md`](../03-roadmap/phases.md) — Phase 0 Q3 데이터 모델 v1 합의 마일스톤, Phase별 진화 시점
- `./tech-stack.md` — 인프라 결정 (PostgreSQL / Kafka / pgvector / WebSocket / 한국 리전), 작성 예정
- `./a2ui-strategy.md` — LangGraph 권한 전파, Tool Registry 구현, 작성 예정
- `./security-compliance.md` — RLS 운영, SCIM, SOC2 Type II, K-ISMS, KISA 키 관리, 작성 예정

---

## 문서 변경 정책

이 문서는 **5개 트리거** 시 갱신한다.

1. **도메인 문서 4개 중 하나가 새 엔티티 / 컬럼을 추가할 때** — 도메인 문서를 먼저 갱신 후 이 문서에 Alembic 마이그레이션 계획 동기화.
2. **[`domain-overview.md`](../02-product/domain-overview.md) Shared Core가 바뀔 때** — overview를 먼저 갱신 후 이 문서 동기.
3. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음. 데이터 모델 안티패턴 발견 = 즉시 핫픽스 + 문서 갱신.
4. **Phase 종료 시점** — 다음 Phase의 진화 마일스톤 확정과 동시에 갱신.
5. **법령 개정 시** — 근로기준법 / 세법 / 개인정보보호법 / 전자서명법. `retention_policies` seed + 관련 ENUM 갱신.

문서 책임자: backend-architect + data engineer + security lead. 갱신 시 변경 이력을 본 파일 하단에 추가.

---

## 변경 이력

| 날짜 | 버전 | 변경 | 작성자 |
| ---- | ---- | ---- | ------ |
| 2026-06-24 | draft v1 | 최초 작성. Shared Core 5 + 도메인 41개 엔티티(PM 7 / Comms 8 / HR 13 / Documents 13) 1차 ERD 봉인. RLS 정책 SQL 패턴 + 외부 협업자 정책 정의. 이벤트 outbox + Kafka 전환 규칙. Phase 0-4 진화 마일스톤. Alembic 다운타임 0 원칙. | Backend Architect |
