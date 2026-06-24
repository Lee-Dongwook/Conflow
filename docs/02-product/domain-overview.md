---
title: Conflow 도메인 통합 개요 (Domain Overview)
최종 업데이트: 2026-06-24
상태: draft v1
독자: PM, 백엔드, AI 엔지니어, 보안
---

# 도메인 통합 개요

> 이 문서는 [`positioning.md`](../00-vision/positioning.md) 차별화 축 1·2·4, [`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 1·2·3, [`jtbd.md`](../01-market/jtbd.md) Big Job #1·#2, [`pricing-strategy.md`](../01-market/pricing-strategy.md) Tier 게이팅을 **단일 데이터 모델 + 단일 권한 모델 + A2UI 인터페이스**라는 한 그림 위에서 봉합한다.
> 도메인별 상세 기능 명세는 여기에 쓰지 않는다 — 이 문서는 다음 4개 문서(`domain-pm`, `domain-comms`, `domain-hr`, `domain-documents`)의 **계약**이다.

---

## 이 문서로 내릴 결정

1. **4도메인 경계**: PM / Comms / HR / Documents가 어디까지 책임지고 어디부터 안 들어가는지 — 영업 압력이 새 기능을 욱여넣을 때 거절 기준.
2. **공유 핵심 엔티티 (Shared Core)**: `Workspace`, `Member`, `Role`, `AuditLog`, `EntityLink` 5개. 이 5개가 단일 데이터 모델 약속의 실체. 도메인은 이걸 **참조만** 하고 소유하지 않는다.
3. **도메인 간 통신은 이벤트 우선**: 직접 호출(동기 SQL JOIN, REST 호출) 최소화. 도메인은 이벤트 카탈로그를 통해서만 서로를 안다.
4. **A2UI는 도메인 위의 Tool 카탈로그**: 모든 도메인 비즈니스 로직은 헤드리스 함수 + Zod Input/Output Schema로 노출. 도메인 횡단 쿼리는 Tool의 합성으로만 표현된다.
5. **도메인 문서 4개가 받아갈 인터페이스**: 책임 / 비-책임 / 엔티티 3-5개 / 발행·구독 이벤트 / 노출 Tool / Phase 출시 범위 / JTBD P0 매핑.

---

## 4도메인 경계

각 도메인은 **3-4문장 책임 정의 + 명시적 비-책임**으로 닫는다. 모호한 경계는 코드 결정도 망친다.

### PM (Product Management)

**책임**: 이슈(Issue), 스프린트(Sprint), 백로그(Backlog), 보드(Board), 릴리스 로그를 소유한다. 이슈는 작업의 단위이자 의사결정의 추적 단위다. 키보드 단축키·검색 속도는 Linear 벤치마크 ([`jtbd.md`](../01-market/jtbd.md) USR-1).

**비-책임**:

- 이슈에 대한 **대화**는 PM이 소유하지 않는다 — 코멘트는 Comms의 메시지 모델을 참조한다 (`EntityLink`).
- 작업자 **개인의 인사 정보**는 PM이 갖지 않는다 — `Member` 참조만.
- 외부 발급용 **문서**(예: 스프린트 보고서 PDF)는 Documents 도메인이 만든다.

### Comms (Communication)

**책임**: 채널(Channel), DM, 메시지(Message), 멘션, 반응, 스레드, Huddle(Phase 2) 세션을 소유한다. 메시지는 "대화의 단위"이며 **결정의 발생 지점**이다 — 결정은 PM 이슈로 승격될 수 있어야 한다 (USR-2).

**비-책임**:

- **이메일 / SMS / 외부 챗봇 통합은 Phase 4까지 안 한다** — Slack/Teams와 정면 충돌하는 영역만 한다.
- **HR 1:1 노트**는 Comms가 아니다 — DM이 비공식 대화라면, 1:1은 HR의 공식 기록이다.
- 메시지 **무제한 영구 보관**은 약속하지 않는다 — Tier별 보관 기간 ([`pricing-strategy.md`](../01-market/pricing-strategy.md)).

### HR (People Operations)

**책임**: 인사 DB(Employee Profile), 입퇴사 워크플로우(Onboarding/Offboarding), 1:1 노트, 인사평가(Phase 3+), 휴가·근태, 4대 보험 데이터(Phase 3+)를 소유한다. **`Member`의 인사 측면 메타데이터**의 정본(source of truth).

**비-책임**:

- **법적 효력 있는 문서 발급**(근로계약서, 재직증명서)은 HR이 데이터를 제공하되 Documents가 만든다.
- **개인 성과 평가가 PM 이슈에 직접 묶이는 자동 계산**은 안 한다 — A2UI가 합성할 수 있게 데이터를 노출만 하고, 자동 평가 로직은 도메인에 박지 않는다 (윤리·법적 리스크).
- **외부 채용 ATS**는 안 한다 — Phase 4 이후 검토.

### Documents (Documents & Compliance)

**책임**: 노무·세무·재직 관련 **정형 문서**의 생성, 템플릿, 워크플로우(제출 → 검토 → 승인 → 발급), 전자서명(Phase 4 KISA), 국세청 ezTax 연동(Phase 4)을 소유한다. 노무사 외부 협업자가 들어오는 도메인의 주 무대.

**비-책임**:

- **일반 협업 문서**(미팅 노트, 위키, 페이지) — Phase 4까지 안 한다. Notion 정면 충돌은 피한다 ([`product-vision.md`](../00-vision/product-vision.md) Anti-Vision "5번째 도메인 확장 금지").
- **PM 스프린트 보고서 PDF 자동 생성**은 Documents가 템플릿만 제공, 데이터 소스는 PM/HR.
- **파일 스토리지 일반 기능**(드라이브) — 안 한다. 정형 문서만.

---

## 공유 핵심 엔티티 (Shared Core) — 단일 데이터 모델의 실체

이 5개 엔티티가 **모든 도메인이 참조하지만 어느 도메인도 소유하지 않는 공유 코어**다. `server/src/app/core/` 하위에 위치하며, 도메인 모듈은 이걸 **읽기/참조**만 한다.

### `Workspace` — 단일 테넌트 경계

| 항목        | 내용                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------ |
| 핵심 필드   | `id`, `name`, `slug`, `tier` (free/team/business/enterprise), `region` (kr/jp), `billing_account_id`, `created_at` |
| 읽는 도메인 | 4도메인 + Auth + Billing                                                                                           |
| 쓰는 도메인 | Billing (Tier 변경), Admin (생성/삭제)                                                                             |
| 권한 진입점 | `Workspace.tier`가 A2UI 도메인 횡단 Tool의 게이트 (Business+)                                                      |

**원칙**: 모든 도메인의 모든 테이블에 `workspace_id` 컬럼이 있다. 한 워크스페이스의 데이터가 다른 워크스페이스에 새는 순간 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 2) 무너진다.

### `Member` — 한 사람 = 한 워크스페이스 1회

| 항목        | 내용                                                                                                                 |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| 핵심 필드   | `id`, `workspace_id`, `user_id` (Supabase), `display_name`, `email`, `status` (active/invited/disabled), `joined_at` |
| 읽는 도메인 | 4도메인 전부 (담당자, 작성자, 멘션, 1:1 대상)                                                                        |
| 쓰는 도메인 | Auth (가입), HR (입퇴사 시 status 동기화)                                                                            |
| 권한 진입점 | `Member.id`가 `RoleAssignment`의 키. 4도메인이 모두 같은 ID 사용                                                     |

**원칙**: PM의 `assignee_id`, Comms의 `author_id`, HR의 `employee_id`는 **전부 `Member.id`**. 이름이 다른 별도 테이블 만들면 단일 데이터 모델 약속이 깨진다.

### `Role` / `RoleAssignment` — 단일 권한 모델

| 항목                         | 내용                                                                                                                       |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 핵심 필드 (`Role`)           | `id`, `workspace_id`, `name` (owner/admin/member/guest/external), `scope_type` (workspace/resource), `permissions` (JSONB) |
| 핵심 필드 (`RoleAssignment`) | `id`, `member_id`, `role_id`, `resource_type?`, `resource_id?`                                                             |
| 읽는 도메인                  | 4도메인 전부 (모든 read/write 진입에서 권한 체크)                                                                          |
| 쓰는 도메인                  | Admin, HR(외부 협업자 초대), Documents(노무사 권한)                                                                        |
| 권한 진입점                  | 모든 도메인의 service 레이어 시작점. SCIM(Phase 3)이 여기에 매핑                                                           |

**원칙**: 도메인별 권한 테이블 금지. PM에 별도 `pm_permissions`를 만드는 순간 단일 권한 모델이 깨진다. "PM의 보드는 누가 보는가"는 `RoleAssignment.resource_type='pm_board'`로만 표현.

### `AuditLog` — 4도메인 통합 감사

| 항목        | 내용                                                                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 핵심 필드   | `id`, `workspace_id`, `actor_member_id`, `domain` (pm/comms/hr/documents), `action`, `resource_type`, `resource_id`, `metadata` (JSONB), `occurred_at`, `trace_id` |
| 읽는 도메인 | Admin, Security, A2UI (감사 질의 응답 시)                                                                                                                          |
| 쓰는 도메인 | 4도메인 전부 (모든 mutation은 AuditLog 발생)                                                                                                                       |
| 권한 진입점 | 워크스페이스 Owner/Admin만 조회. Tier별 보관 기간 (Team 90일 / Business 1년 / Enterprise 무제한)                                                                   |

**원칙**: 도메인별 audit 테이블 만들지 않는다. SOC2 Type II(Phase 3) 인증 자료가 단일 테이블이어야 통과 가능.

### `EntityLink` — 도메인 횡단 참조의 표준 메커니즘

| 항목        | 내용                                                                                                                                                                          |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 핵심 필드   | `id`, `workspace_id`, `source_type`, `source_id`, `target_type`, `target_id`, `link_kind` (references/derived_from/blocks/mentioned_in), `created_by_member_id`, `created_at` |
| 읽는 도메인 | A2UI 합성 시 / 사용자가 "관련 항목" 탐색 시                                                                                                                                   |
| 쓰는 도메인 | 4도메인 전부 (예: PM 이슈가 Comms 메시지로부터 생성됨 → `derived_from` 링크)                                                                                                  |
| 권한 진입점 | source / target 양쪽 권한 모두 확인 후 노출 — **편도 가시성 보장**                                                                                                            |

**원칙**: PM 테이블에 `source_message_id` 같은 도메인 횡단 외래키를 박지 않는다. 그건 도메인 경계 침식. `EntityLink`를 거친다.

> 위 엔티티의 **전체 ERD와 인덱스 / 샤딩 전략**은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md)에서 상세.

---

## 도메인 간 의존 다이어그램

```
                       +-----------------------------+
                       |  Shared Core                |
                       |  Workspace / Member / Role  |
                       |  AuditLog / EntityLink      |
                       +--------------+--------------+
                                      ^
                                      | (read-only 참조)
            +-------------+-----------+-----------+-------------+
            |             |                       |             |
            v             v                       v             v
       +--------+    +---------+            +---------+    +-----------+
       |   PM   |<==>|  Comms  |            |   HR    |<---|Documents  |
       +--------+    +---------+            +---------+    +-----------+
            ^             ^                       ^             ^
            |  events     |  events               |  events     |  events
            +-------------+----------+------------+-------------+
                                     |
                              +------v------+
                              | Event Bus   |
                              | (Postgres / |
                              |  Kafka P3+) |
                              +------+------+
                                     |
                              +------v------+
                              | A2UI Tool   |
                              | Registry    |
                              |(LangGraph)  |
                              +-------------+
```

규칙:

- **모든 도메인은 Shared Core를 read-only로 참조**한다. 도메인이 `Workspace`나 `Member`를 직접 mutate 하지 않는다.
- **PM ↔ Comms는 양방향**: 메시지 → 이슈, 이슈 → 채널 알림. 단, **이벤트로만**. 직접 SQL JOIN 금지.
- **Documents → HR 단방향**: 문서가 HR 데이터를 참조해 발급한다. HR이 Documents 내부를 알지 않는다.
- **HR → Member 단방향 쓰기**: 입퇴사 시 `Member.status`를 변경하는 유일한 도메인.
- **순환 의존 금지**: A → B 이벤트가 다시 A로 즉시 돌아오면 큐 폭주. 이벤트 핸들러는 idempotent + 같은 트랜잭션에서 자기 도메인 이벤트 재발행 금지.

---

## 이벤트 모델 (Event Bus)

도메인 간 통신은 **이벤트 우선**. 직접 호출은 같은 도메인 내부 또는 Shared Core 읽기에만 허용.

### 이벤트 카탈로그 v1

| Event Name                    | 발행 도메인 | 구독 도메인                | 페이로드 핵심 필드                                                        | Phase |
| ----------------------------- | ----------- | -------------------------- | ------------------------------------------------------------------------- | ----- |
| `pm.issue.created`            | PM          | Comms, A2UI                | `issue_id`, `workspace_id`, `reporter_id`, `assignee_id`, `sprint_id?`    | 1     |
| `pm.issue.blocked`            | PM          | Comms, HR, A2UI            | `issue_id`, `assignee_id`, `blocked_since`, `reason`                      | 1     |
| `pm.issue.resolved`           | PM          | Comms, A2UI                | `issue_id`, `resolver_id`, `resolved_at`, `cycle_time_hours`              | 1     |
| `pm.sprint.ended`             | PM          | Comms, HR, A2UI            | `sprint_id`, `velocity`, `blocker_count`, `member_stats`                  | 1     |
| `comms.message.posted`        | Comms       | A2UI, PM(스레드 링크 시)   | `message_id`, `channel_id`, `author_id`, `mentions[]`                     | 1     |
| `comms.decision.detected`     | Comms       | PM, A2UI                   | `message_id`, `decision_text`, `participants[]`, `confidence`             | 2     |
| `comms.huddle.ended`          | Comms       | A2UI                       | `huddle_id`, `participants[]`, `duration_sec`, `recording_uri?`           | 2     |
| `hr.member.onboarded`         | HR          | PM, Comms, Documents, A2UI | `member_id`, `start_date`, `team_ids[]`, `manager_id`                     | 2     |
| `hr.member.offboarded`        | HR          | PM, Comms, Documents, Auth | `member_id`, `end_date`, `data_retention_policy`                          | 2     |
| `hr.one_on_one.recorded`      | HR          | A2UI (only)                | `one_on_one_id`, `manager_id`, `member_id`, `keywords[]` (요약만, 원문 X) | 2     |
| `hr.evaluation.cycle_started` | HR          | Comms, A2UI                | `cycle_id`, `period`, `evaluator_assignments[]`                           | 3     |
| `documents.contract.signed`   | Documents   | HR, A2UI, AuditLog         | `document_id`, `signer_member_id`, `signed_at`, `document_type`           | 4     |
| `documents.payroll.processed` | Documents   | HR, A2UI                   | `payroll_run_id`, `period`, `member_count`, `total_amount`                | 4     |

### 이벤트 스토리지 결정

**Phase 1-2: PostgreSQL outbox 패턴 + LISTEN/NOTIFY**

- 근거: 워크스페이스 100-500개 / 이벤트율 < 100 events/sec 수준에서는 Kafka 운영 부담이 가치보다 큼. `transactional outbox`로 atomicity 보장.
- 트레이드오프: 처리량 한계 ~1k events/sec. 멀티 컨슈머 그룹 패턴은 어색.

**Phase 3+: Kafka (또는 Redpanda) 전환**

- 트리거: 워크스페이스 1,000개 초과 또는 A2UI 도메인 횡단 쿼리가 분당 1k건 초과.
- 마이그레이션: outbox 이벤트 → Kafka 토픽으로 dual-write 6주, 점진 전환.

상세 결정은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md), [`04-architecture/tech-stack.md`](../04-architecture/tech-stack.md).

### 이벤트 ↔ A2UI 관계

**모든 이벤트는 A2UI 에이전트의 트리거가 될 수 있어야 한다.**

- 예시: `pm.sprint.ended` → LangGraph `retro_insights` 에이전트 자동 실행 → 회고 초안 생성.
- 예시: `hr.member.onboarded` → `onboarding_assistant` 에이전트가 4도메인 권한·채널·1:1 일정 자동 생성.
- 원칙: 이벤트 페이로드는 A2UI Tool의 입력 Schema와 정렬되어야 한다. 이름·필드를 바꾸려면 Tool 카탈로그를 동시에 갱신.

---

## A2UI가 4도메인을 보는 방법

> 이 절이 **차별화 축 2** ([`positioning.md`](../00-vision/positioning.md))의 운명을 결정한다. 도메인 횡단 쿼리가 가능한 유일한 협업 툴이라는 약속.

### 헤드리스 비즈니스 로직 원칙

CLAUDE.md "Headless logic: 비즈니스 로직은 React 라이프사이클과 분리"와 [`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 3과 정렬.

규칙:

- 모든 도메인 service 함수는 **React에 의존하지 않는 순수 비즈니스 함수**. (`server/src/app/{domain}/service.py`)
- 모든 service 함수는 **Zod-equivalent Pydantic Input/Output Schema**를 가진다.
- service 함수의 **부분집합**이 A2UI Tool로 등록된다. 등록 기준: 도메인 횡단 쿼리에서 합성 가능성 + 권한 안전성 검증 통과.
- UI 컴포넌트는 service 함수를 **호출만** 한다. UI에 비즈니스 로직 박는 순간 A2UI 약속이 깨진다 (영업이 단발성 UI 기능 박을 때의 압력).

### A2UI Tool 카탈로그 v1

| Tool                            | 도메인    | Input Schema 키                                      | Output Schema 키                                       | Tier 노출               |
| ------------------------------- | --------- | ---------------------------------------------------- | ------------------------------------------------------ | ----------------------- |
| `pm.search_issues`              | PM        | `filters`(status, assignee, sprint), `pagination`    | `issues[]`, `total`                                    | Free+                   |
| `pm.create_issue`               | PM        | `title`, `description`, `assignee_id?`, `sprint_id?` | `issue_id`, `url`                                      | Team+                   |
| `pm.get_sprint_summary`         | PM        | `sprint_id`                                          | `velocity`, `blockers[]`, `member_stats[]`             | Team+                   |
| `pm.identify_blockers`          | PM        | `since`, `min_blocked_hours`                         | `blocked_issues[]` with `assignee_id`                  | Team+                   |
| `comms.search_messages`         | Comms     | `query`, `channel_ids?`, `date_range`                | `messages[]`                                           | Free+                   |
| `comms.summarize_channel`       | Comms     | `channel_id`, `since`, `style`                       | `summary`, `action_items[]`                            | Team+                   |
| `comms.extract_decisions`       | Comms     | `channel_id`, `date_range`                           | `decisions[]` with confidence                          | Business+ (도메인 횡단) |
| `comms.message_to_issue`        | Comms→PM  | `message_id`, `assignee_id?`                         | `issue_id`, `link_id`                                  | Team+                   |
| `hr.get_member_context`         | HR        | `member_id`                                          | `profile`, `team`, `manager`, `recent_1on1_keywords[]` | Business+               |
| `hr.list_onboarding`            | HR        | `status` (in_progress/completed)                     | `onboardings[]` with `progress_pct`                    | Business+               |
| `hr.list_one_on_ones`           | HR        | `member_id?`, `manager_id?`, `date_range`            | `one_on_ones[]` (메타데이터만, 원문은 권한 체크 후)    | Business+               |
| `hr.start_offboarding`          | HR        | `member_id`, `end_date`, `reason`                    | `offboarding_id`                                       | Business+ Admin only    |
| `documents.list_pending_review` | Documents | `reviewer_member_id?`                                | `documents[]`                                          | Business+               |
| `documents.generate_contract`   | Documents | `template_id`, `member_id`, `variables`              | `document_id`, `pdf_url`                               | Business+               |
| `documents.request_signature`   | Documents | `document_id`, `signer_member_ids[]`                 | `signature_request_id`                                 | Enterprise (Phase 4)    |
| `a2ui.cross_domain_query`       | A2UI      | `intent`, `domains[]`, `context`                     | `composed_answer`, `tool_trace[]`                      | **Business+**           |

### 도메인 횡단 쿼리 — 데이터 흐름 3개

**예시 1**: "지난 스프린트 블로커 멤버와 그 멤버의 1:1 피드백" ([`positioning.md`](../00-vision/positioning.md) 차별화 축 2의 정식 데모)

```
Agent: a2ui.cross_domain_query(intent="last sprint blockers + their 1:1 feedback")
  └→ pm.identify_blockers(since=last_sprint_start)
       returns: [{assignee_id: M1, blocked_hours: 72}, {assignee_id: M2, blocked_hours: 48}]
  └→ for each assignee:
       hr.get_member_context(member_id=M1)
       hr.list_one_on_ones(member_id=M1, date_range=last_30_days)
         returns: keywords=["bandwidth", "design review delay"]
  └→ 합성: "M1이 3일째 블로커. 최근 1:1 키워드 'bandwidth'와 일치"
  Permission check: caller가 M1의 1:1을 볼 권한 있는가? (매니저/Admin만) 없으면 keyword 마스킹.
```

**예시 2**: "이번달 신입 5명 온보딩 진행률 + 1:1 일정 잡힘 여부"

```
Agent: a2ui.cross_domain_query(intent="this month's onboarding progress + 1:1 scheduled")
  └→ hr.list_onboarding(status="in_progress", filter: start_date in this_month)
       returns: [{member_id: M3, progress_pct: 60}, ...]
  └→ hr.list_one_on_ones(member_id=M3, date_range=next_14_days)
       returns: scheduled=true/false
  └→ 합성 표
```

**예시 3**: "지난주 Slack에서 결정된 것 중 Jira 티켓에 안 옮겨진 것"

```
Agent: a2ui.cross_domain_query(intent="decisions in comms not converted to issues")
  └→ comms.extract_decisions(channel_id=*, date_range=last_7_days)
       returns: [{message_id: ms1, decision_text: "..."}, ...]
  └→ for each decision:
       check EntityLink(source_type='comms.message', source_id=ms1, link_kind='derived_from', target_type='pm.issue')
         empty → "안 옮겨짐"으로 분류
  └→ 합성: 미전환 결정 리스트 + "이슈로 만들기" 액션 제안
```

### 권한 모델과의 통합

**A2UI Tool은 호출자(Member)의 권한을 상속한다.**

- Tool 실행 시 LangGraph supervisor가 `caller_member_id`를 강제 주입 → 각 도메인 service가 `RoleAssignment` 체크.
- **도메인 횡단 쿼리에서 권한 누수 방지**: 예시 1에서 호출자가 M1의 매니저가 아니면 1:1 노트 키워드도 못 본다. 합성 단계에서가 아니라 **각 sub-tool 호출 단계에서** 권한이 적용된다.
- 보류 — [`04-architecture/a2ui-strategy.md`](../04-architecture/a2ui-strategy.md)에서 LangGraph 권한 전파 패턴 상세.

### Tier 게이팅 — 어디서 강제되는가

**Tool Registry 한 곳에서 강제한다.** 코드에 흩어지면 안 된다.

- 메커니즘: `tool_registry.yaml` (또는 동등한 DB 테이블)에 Tool마다 `min_tier` 필드. LangGraph supervisor가 Tool 호출 전 `Workspace.tier`와 비교.
- 도메인 횡단 Tool (`a2ui.cross_domain_query`, `comms.extract_decisions` 등)은 `min_tier: business`.
- 자체 호스팅 / 한국 리전 Tool은 `min_tier: enterprise`.
- Watch List: Tier 체크가 service 함수 안에 박히기 시작하면 차별화 깨짐 신호 (아래 절 참조).

---

## 권한 모델 통합 (Single Permission Model)

### Role 정의

| Role                  | 범위      | PM                     | Comms                    | HR                        | Documents               |
| --------------------- | --------- | ---------------------- | ------------------------ | ------------------------- | ----------------------- |
| **Owner**             | Workspace | full                   | full                     | full                      | full                    |
| **Admin**             | Workspace | full                   | full                     | full (1:1 노트 제외)      | full                    |
| **Member**            | Workspace | full read, own write   | own channels + DMs       | own profile, own 1:1      | own documents           |
| **Guest**             | Resource  | invited resources only | invited channels only    | none                      | invited documents only  |
| **External (노무사)** | Resource  | none                   | assigned channel(s) only | assigned member docs only | assigned documents only |

**원칙**: 도메인별 권한이 아니라 **리소스별 권한 + 도메인 가시성 행렬**. Member는 PM 전체를 보지만 HR은 본인 데이터만 — 이게 같은 `RoleAssignment` 테이블에서 표현된다.

### 외부 협업자 (노무사) 모델

- 별도 워크스페이스 가입 없이 **특정 리소스에 한정된 `RoleAssignment`**로 접근. ([`pricing-strategy.md`](../01-market/pricing-strategy.md) "노무사 외부 시트 무료" 정책)
- 노무사의 `Member.status='external'`, `RoleAssignment.resource_type='hr.document_review'` 같은 형태.
- 노무사는 자기 워크스페이스(노무법인)와 클라이언트 워크스페이스에 동시에 다른 ID로 존재 — 한 사람 한 워크스페이스 1회 원칙은 **워크스페이스 단위**다.

### SCIM (Phase 3)

- SSO 그룹 ↔ Role 매핑은 `scim_mappings` 테이블. IdP의 그룹 변경 → Webhook → `RoleAssignment` 자동 갱신.
- 보류 — [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md).

---

## 데이터 격리 (Multi-tenancy 결정)

**결정 (v1 가설)**: **같은 테이블 + `workspace_id` 컬럼**.

| 옵션                           | 운영 단순성 | 격리 강도              | 마이그레이션 | Phase 4 적합성                 |
| ------------------------------ | ----------- | ---------------------- | ------------ | ------------------------------ |
| 워크스페이스별 별도 DB         | 낮음        | 매우 강함              | 어려움       | Enterprise 한정 옵션           |
| 별도 스키마                    | 중간        | 강함                   | 중간         | 1k 워크스페이스 시 스키마 폭발 |
| **같은 테이블 + workspace_id** | 높음        | RLS + 쿼리 규율로 보장 | 쉬움         | Phase 4까지 충분               |

**근거**:

- Phase 1-3 운영 단순성 우선. PostgreSQL Row Level Security(RLS)로 `workspace_id` 누락 시 자동 차단.
- Enterprise(Phase 4+)에서 망분리·한국 리전 요구 시 **별도 클러스터 옵션** 검토 — 단일 데이터 모델은 유지하되 물리 격리만 추가.

**격리 깨짐 탐지 — 어떻게 알아내는가**:

1. **모든 쿼리에 `workspace_id` 필수**: PostgreSQL RLS 정책으로 강제. RLS 우회 쿼리는 super 권한만 가능.
2. **린트 규칙**: SQLAlchemy 모델의 모든 query에 `.filter(Model.workspace_id == ctx.workspace_id)`가 있는지 정적 분석. `server/src/app/core/db.py`에 `WorkspaceScopedSession` mixin.
3. **테스트 강제**: pytest fixture로 워크스페이스 2개 만들고 cross-tenant read 시도 → 모두 차단되는지 contract test.
4. **AuditLog 모니터링**: `workspace_id`와 `actor_member_id.workspace_id` 불일치 발견 시 즉시 알람.

상세는 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md), [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md).

---

## 각 도메인 문서가 받아갈 인터페이스

> 다음 4개 문서(`domain-pm.md`, `domain-comms.md`, `domain-hr.md`, `domain-documents.md`)는 이 4개 표를 **계약**으로 받는다. 표에 없는 책임을 추가하려면 이 문서를 먼저 갱신.

### `domain-pm.md` 계약

| 항목         | 내용                                                                                                                                            |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 책임         | Issue, Sprint, Backlog, Board, Release Note                                                                                                     |
| 비-책임      | 이슈 코멘트 대화(Comms), 인사 정보(HR), 발급 문서(Documents)                                                                                    |
| 핵심 엔티티  | `Issue`, `Sprint`, `Board`, `BacklogItem`, `Label`                                                                                              |
| 발행 이벤트  | `pm.issue.created`, `pm.issue.blocked`, `pm.issue.resolved`, `pm.sprint.ended`                                                                  |
| 구독 이벤트  | `comms.decision.detected` (메시지 → 이슈 변환 후보), `hr.member.onboarded` (담당 가능자 풀에 추가), `hr.member.offboarded` (이슈 재할당 트리거) |
| 노출 Tool    | `pm.search_issues`, `pm.create_issue`, `pm.get_sprint_summary`, `pm.identify_blockers`                                                          |
| Phase 출시   | 정식 Phase 1 (Linear 벤치마크 속도)                                                                                                             |
| JTBD P0 매핑 | USR-1, USR-2, COO-1, COO-2 + Jira/Linear 임포터                                                                                                 |

### `domain-comms.md` 계약

| 항목         | 내용                                                                                                                        |
| ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| 책임         | Channel, DM, Message, Mention, Reaction, Thread, Huddle (Phase 2)                                                           |
| 비-책임      | 이메일, 외부 챗봇, HR 1:1 노트, 무제한 영구 보관                                                                            |
| 핵심 엔티티  | `Channel`, `Message`, `Mention`, `HuddleSession`                                                                            |
| 발행 이벤트  | `comms.message.posted`, `comms.decision.detected` (Phase 2), `comms.huddle.ended` (Phase 2)                                 |
| 구독 이벤트  | `pm.issue.blocked` (관련 채널 알림), `pm.sprint.ended` (회고 채널 자동 게시), `hr.member.onboarded` (입사자 채널 자동 추가) |
| 노출 Tool    | `comms.search_messages`, `comms.summarize_channel`, `comms.extract_decisions` (Business+), `comms.message_to_issue`         |
| Phase 출시   | 기본 Phase 1 (채널/DM/검색), Huddle + 결정 추출 Phase 2                                                                     |
| JTBD P0 매핑 | USR-2, USR-3, COO-2 (도메인 횡단 AI 알파), Slack 임포터(Phase 2)                                                            |

### `domain-hr.md` 계약

| 항목         | 내용                                                                                                               |
| ------------ | ------------------------------------------------------------------------------------------------------------------ |
| 책임         | Employee Profile, Onboarding/Offboarding 워크플로우, 1:1 노트, Evaluation(Phase 3+), 휴가·근태, 4대 보험(Phase 3+) |
| 비-책임      | 법적 효력 문서 발급(Documents), 성과 자동 평가 로직, 외부 채용 ATS                                                 |
| 핵심 엔티티  | `EmployeeProfile`, `OnboardingFlow`, `OneOnOne`, `LeaveRequest`, `EvaluationCycle`                                 |
| 발행 이벤트  | `hr.member.onboarded`, `hr.member.offboarded`, `hr.one_on_one.recorded`, `hr.evaluation.cycle_started` (Phase 3)   |
| 구독 이벤트  | `pm.sprint.ended` (멤버 통계 평가 자료로 노출), `documents.contract.signed` (입사 절차 완료 트리거)                |
| 노출 Tool    | `hr.get_member_context`, `hr.list_onboarding`, `hr.list_one_on_ones`, `hr.start_offboarding`                       |
| Phase 출시   | 알파 Phase 2 (인사 DB, 입퇴사, 1:1) / 정식 Phase 3 (평가, 4대 보험, 노무사 협업)                                   |
| JTBD P0 매핑 | COO-3(Phase 2), COO-4(Phase 3), USR-7(Phase 2/3), CEO-4(Phase 3)                                                   |

### `domain-documents.md` 계약

| 항목         | 내용                                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| 책임         | 정형 문서 템플릿, 발급 워크플로우(제출→검토→승인→발급), 전자서명(Phase 4 KISA), ezTax(Phase 4)               |
| 비-책임      | 일반 협업 문서(Notion 영역), 파일 드라이브, PM 보고서의 데이터 소스                                          |
| 핵심 엔티티  | `DocumentTemplate`, `DocumentInstance`, `ReviewWorkflow`, `Signature`, `PayrollRun` (Phase 4)                |
| 발행 이벤트  | `documents.contract.signed` (Phase 4), `documents.payroll.processed` (Phase 4), `documents.review.completed` |
| 구독 이벤트  | `hr.member.onboarded` (근로계약서 템플릿 자동 인스턴스화), `hr.member.offboarded` (퇴직 관련 문서 생성)      |
| 노출 Tool    | `documents.list_pending_review`, `documents.generate_contract`, `documents.request_signature` (Phase 4)      |
| Phase 출시   | 기본 워크플로우 Phase 2 (노무 검토) / KISA + ezTax Phase 4                                                   |
| JTBD P0 매핑 | COO-4 (노무사 협업), COO-5 (보고서 자동 요약), Compliance P3 (Phase 4)                                       |

---

## 차별화 깨짐 신호 (Watch List)

| #   | 신호                                                                       | 그러면 무엇을 한다                                                                                                               |
| --- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 도메인 간 직접 SQL JOIN이 PR에서 증가 (예: PM이 `hr_employee` 테이블 JOIN) | 도메인 경계 침식. 즉시 `EntityLink` + 이벤트로 리팩토링 강제. 코드 리뷰 체크리스트에 추가.                                       |
| 2   | A2UI Tool 카탈로그에서 Tier 게이팅이 service 함수 안에 흩어짐              | Tool Registry 한 곳에서만 강제하는 원칙 깨짐. 모든 게이팅을 registry로 이전 + 정적 분석 룰 추가.                                 |
| 3   | 새 도메인 추가 압력 (CRM, BI, 마케팅 자동화 등)                            | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision "5번째 도메인 확장 금지" 위반. 거절 + 영업에 안티-비전 재전달. |
| 4   | `workspace_id` 없는 쿼리가 머지됨                                          | 데이터 격리 깨짐. 핫픽스 + RLS 정책 강화 + 사후 audit로 누수 범위 확인.                                                          |
| 5   | 도메인 service 함수가 React 컴포넌트를 import                              | 헤드리스 원칙 깨짐. UI 결합도가 A2UI Tool 등록 불가능하게 만듦. 즉시 리팩토링.                                                   |
| 6   | A2UI 도메인 횡단 Tool이 권한 체크 우회 (super user 모드로 동작)            | 권한 누수. 즉시 회로 차단(circuit breaker)로 Tool 정지 + 사후 audit.                                                             |
| 7   | 도메인별 `audit_*` 테이블 신설                                             | 통합 `AuditLog` 약속 깨짐. SOC2 Type II 인증 위협. 즉시 통합.                                                                    |
| 8   | 노무사 외부 협업자가 본인 영역 외 데이터에 접근 가능                       | [`jtbd.md`](../01-market/jtbd.md) Trigger 2 / 3 약속 깨짐. 권한 모델 재설계 + 외부 협업자 모드 회귀 테스트 추가.                 |

---

## 의도적 보류 (Open Decisions → 책임 이전)

다음 결정들은 이 문서에서 **하지 않는다**. 도메인 문서 4개를 작성하기 위해 필요한 만큼만 정의했다.

| 결정                                                           | 어디로 미루는가                                                                                      |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 전체 ERD, 인덱스, 샤딩 전략, RLS 정책 SQL                      | [`04-architecture/data-model.md`](../04-architecture/data-model.md)                                  |
| LangGraph supervisor → Tool 권한 전파 패턴, Tool Registry 구현 | [`04-architecture/a2ui-strategy.md`](../04-architecture/a2ui-strategy.md)                            |
| Event Bus 기술 선택 (PostgreSQL outbox vs Kafka vs NATS) 최종  | [`04-architecture/tech-stack.md`](../04-architecture/tech-stack.md)                                  |
| SCIM ↔ Role 매핑 정의, SOC2 Type II 인증 자료 구조             | [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md)                |
| 도메인별 P0-P3 기능 명세, UX 와이어프레임                      | `02-product/domain-{pm,comms,hr,documents}.md`                                                       |
| Phase별 출시 일정 (분기 OKR)                                   | [`03-roadmap/phases.md`](../03-roadmap/phases.md), [`03-roadmap/moscow.md`](../03-roadmap/moscow.md) |

---

## 관련 문서

- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 4축. 축 1·2·4가 이 문서의 직접 입력
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — 불변 원칙 1·2·3, Phase별 도메인 출시 일정
- [`../01-market/jtbd.md`](../01-market/jtbd.md) — Big Job #1·#2, 도메인 입력표 5개
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — Tier 게이팅 (A2UI 도메인 횡단 = Business+, 노무사 무료 시트)
- `./domain-pm.md` — PM 도메인 상세 (이 문서의 PM 계약표가 시작점, 작성 예정)
- `./domain-comms.md` — Comms 도메인 상세 (작성 예정)
- `./domain-hr.md` — HR 도메인 상세 (작성 예정)
- `./domain-documents.md` — Documents 도메인 상세 (작성 예정)
- `../04-architecture/data-model.md` — 단일 데이터 모델 ERD, RLS, 샤딩 (작성 예정)
- `../04-architecture/a2ui-strategy.md` — LangGraph 헤드리스 아키텍처, Tool Registry (작성 예정)
- `../04-architecture/tech-stack.md` — Event Bus, 인프라 기술 선택 (작성 예정)
- `../04-architecture/security-compliance.md` — 권한 모델 구현, SCIM, SOC2 (작성 예정)

---

## 문서 변경 정책

이 문서는 **3개 트리거** 시 갱신한다.

1. **도메인 문서 4개 중 하나가 이 문서의 계약을 벗어나야 할 때** — 도메인 문서를 갱신하기 전에 이 문서를 먼저 변경.
2. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음.
3. **Phase 종료 시점** — 다음 Phase의 도메인 출시 범위 확정과 동시에 갱신.

문서 책임자: backend-architect + product lead. 갱신 시 변경 이력을 본 파일 하단에 추가.
