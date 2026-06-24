---
title: PM 도메인 상세 (Product Management)
최종 업데이트: 2026-06-24
상태: draft v1
독자: PM, 백엔드, 프론트엔드, 디자인
---

# PM 도메인 (Product Management)

> 이 문서는 [`domain-overview.md`](./domain-overview.md)의 PM 계약표를 시작점으로, [`jtbd.md`](../01-market/jtbd.md) USR-1/USR-2/COO-1/COO-2와 [`positioning.md`](../00-vision/positioning.md) 차별화 축 2(도메인 횡단 AI)·축 4(마이그레이션 비용)를 PM 도메인의 **결정 카탈로그**로 풀어낸다.
> [`product-vision.md`](../00-vision/product-vision.md) Phase 1의 **주력 도메인**이며, ICP-1([`icp.md`](../01-market/icp.md))이 첫 도입 시 평가하는 영역이다. Linear/Jira의 대안으로 평가받는다.
> 데이터 모델 ERD, RLS, 인덱스, 권한 전파 패턴 같은 구현 결정은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md), [`04-architecture/a2ui-strategy.md`](../04-architecture/a2ui-strategy.md).

---

## 이 문서로 내릴 결정

1. **Phase 1 P0 범위**: Issue / Sprint / Board / Backlog / Project / Label / Comment + 키보드 단축키 + 빠른 검색 + Jira/Linear 임포터까지. **Milestone / Roadmap / OKR / Time tracking은 Phase 1에 안 빌드**.
2. **PM 도메인 엔티티 경계**: PM이 소유하는 것 6개(Issue / Sprint / Project / Board / Backlog / Label) + PM 영역 코멘트(Comment) — 단, "이슈에 대한 대화의 본문"은 Comms로 인용·참조한다.
3. **A2UI가 PM을 보는 방식**: Tool 카탈로그 8개 (검색·생성·전이·요약·블로커·스프린트 관리·코멘트·임포트 트리거) — 단일 도메인 Tool은 Team+, 도메인 횡단 합성 Tool은 Business+.
4. **다른 도메인과의 연결점**: Comms (메시지 → 이슈 전환 + 채널 알림), HR (입퇴사 시 담당자 풀 갱신 + 이슈 재할당), Documents (스프린트 보고서 PDF 데이터 소스만 제공).
5. **임포터 우선순위**: Jira(Phase 1 필수, Atlassian 공략) > Linear(Phase 1 권장, PLG 전환층) > Notion(Phase 2) — 임포트 정확도 90% 미만이면 차별화 깨짐 신호.

---

## 도메인 책임

### PM이 책임지는 것

- **Issue**: 작업 / 티켓 / 태스크. 의사결정의 추적 단위. PM 도메인의 핵심 aggregate.
- **Sprint**: 시간 박스(Linear의 Cycle 개념과 동등). 계획→실행→완료 라이프사이클.
- **Board**: 칸반 / 스크럼 / 커스텀 보드 뷰. 이슈의 **표현 레이어**(이슈가 아니다).
- **Backlog**: 정렬된 이슈 큐. 우선순위와 그룹화의 작업 공간.
- **Project**: 이슈 그룹화 단위(Linear의 Project 개념). Epic의 상위 호환.
- **Label**: 분류 메타데이터. 워크스페이스 공통 + 프로젝트 로컬.
- **Comment**: 이슈 컨텍스트 안의 코멘트(PM이 소유). Comms 메시지와는 다른 모델.

### PM이 안 책임지는 것 (경계)

- **이슈에 대한 대화의 본문**: Comms 도메인 소유. PM은 `EntityLink(link_kind='mentioned_in')`로 메시지를 참조만.
- **개인의 인사 정보**: HR 소유. PM은 `Member.id`만 안다 (직책·평가·1:1 노트는 안 본다).
- **외부 발급 문서**: 스프린트 보고서 PDF는 Documents가 발급. PM은 **데이터 소스**만 제공.
- **OKR / 목표 추적**: Phase 3로 미룸 (아래 의도적 보류 참조).
- **Time tracking / 공수 입력**: Phase 3로 미룸.
- **자동화 룰 풀 기능**: Phase 2 기초만, 풀 기능은 Phase 3.

### 경계 모호한 케이스 — 결정

| 케이스               | 결정                                                        | 근거                                                                                                                  |
| -------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 스프린트 회고(Retro) | **PM 소유**. Comms는 회고 대화 데이터 참조 제공.            | 회고 결과는 다음 스프린트의 Issue·Project로 환류된다. Comms는 발생 지점일 뿐 결과의 정본이 아니다.                    |
| 이슈 코멘트          | **PM 소유** (`Comment` 모델 별도). Comms 메시지와 다른 LWE. | 이슈 컨텍스트 안 코멘트는 검색·필터·알림 라우팅이 이슈 도메인과 강결합. Comms 메시지로 만들면 권한 행렬이 어색해진다. |
| 이슈 멘션 알림       | Comms가 알림 라우팅 담당, PM이 멘션 이벤트 발행             | 알림은 모든 도메인이 Comms로 모은다 (단일 알림 채널 정책).                                                            |
| Release Note         | **Phase 2부터 PM 소유**. Phase 1은 안 만든다.               | 차별화 축 4에 직결되지 않음. Phase 1 스코프 절제.                                                                     |
| 이슈의 첨부파일      | PM이 메타데이터 소유, 스토리지는 공통 인프라                | Documents가 아니다 — Documents는 정형 발급 문서 한정.                                                                 |

---

## 핵심 엔티티

전체 ERD와 인덱스 / RLS는 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 책임·핵심 필드·상태·권한·이벤트.

### `Issue` — 작업 단위, PM 도메인의 핵심 aggregate

- **책임 한 줄**: 회사가 하기로 결정한 일 1건. 의사결정의 추적 단위.
- **핵심 필드**: `id`, `workspace_id`, `project_id`, `sprint_id?`, `title`, `description`, `status`, `priority` (urgent/high/medium/low), `assignee_id?`, `reporter_id`, `due_date?`, `created_at`, `updated_at`
- **상태 머신**: `backlog → todo → in_progress → blocked ↔ in_progress → done` (또는 `cancelled`). 상세는 아래 다이어그램.
- **권한 모델 진입점**:
  - 읽기: 워크스페이스 Member 이상. Project가 `private`이면 해당 Project 멤버만.
  - 쓰기: 작성자(reporter) 본인 + 담당자(assignee) + Project Maintainer + Workspace Admin.
  - 삭제: Project Maintainer + Workspace Admin만. 일반 Member는 삭제 불가(soft delete).
- **이벤트 발행**: `pm.issue.created`, `pm.issue.updated`, `pm.issue.blocked` (status → blocked 전이 시), `pm.issue.resolved` (status → done), `pm.issue.cancelled`

### `Sprint` — 시간 박스 (Linear의 Cycle)

- **책임 한 줄**: 시작일·종료일이 정해진 작업 묶음. 속도(velocity) 측정의 단위.
- **핵심 필드**: `id`, `workspace_id`, `project_id?` (Project별 스프린트 또는 워크스페이스 공통), `name`, `start_date`, `end_date`, `phase` (planned/active/completed), `velocity?` (완료 후 계산), `created_at`
- **상태 머신**: `planned → active → completed`. `completed`에서 재시작 불가(새 Sprint 생성).
- **권한 모델 진입점**:
  - 생성·전이: Project Maintainer + Workspace Admin.
  - 읽기: 워크스페이스 Member 이상.
- **이벤트 발행**: `pm.sprint.started`, `pm.sprint.ended` (velocity·blocker 통계 포함)

### `Project` — 이슈 그룹화 (Epic의 상위 호환)

- **책임 한 줄**: 목표·기한·소유자가 있는 작업 묶음. Linear의 Project 개념.
- **핵심 필드**: `id`, `workspace_id`, `name`, `slug`, `lead_member_id`, `visibility` (private/internal/public-in-workspace), `target_date?`, `status` (planned/in_progress/paused/completed/cancelled), `created_at`
- **상태 머신**: `planned → in_progress → completed` (또는 `paused`, `cancelled`).
- **권한 모델 진입점**:
  - `visibility='private'`: 명시적으로 추가된 Member만.
  - `visibility='internal'`: 워크스페이스 Member 전부, Guest 제외.
  - `visibility='public-in-workspace'`: Guest 포함 워크스페이스 전체.
  - 삭제: Workspace Admin만.
- **이벤트 발행**: `pm.project.created`, `pm.project.status_changed`

### `Board` — 표현 레이어 (뷰)

- **책임 한 줄**: 이슈의 칸반/리스트/타임라인 뷰 정의. 이슈를 소유하지 않는다.
- **핵심 필드**: `id`, `workspace_id`, `project_id?`, `name`, `type` (kanban/list/timeline), `filter_spec` (JSONB: status, assignee, label 필터), `column_spec` (JSONB: 칸반 컬럼 정의), `created_by_member_id`
- **상태 머신**: 없음 (단순 CRUD).
- **권한 모델 진입점**:
  - 개인 보드: 작성자만.
  - 공유 보드: 워크스페이스 Member 전체 읽기, 작성자·Admin이 수정.
- **이벤트 발행**: 없음 (Board는 뷰이므로 도메인 이벤트 안 발생).

### `BacklogItem` — 정렬된 이슈 큐

- **책임 한 줄**: 백로그 안 이슈의 순서 정의. Issue ↔ Backlog 관계 + position.
- **핵심 필드**: `id`, `workspace_id`, `backlog_id`, `issue_id`, `position` (float 또는 fractional indexing), `added_at`
- **권한 모델 진입점**: 해당 Project Maintainer + Admin이 순서 변경. Member는 읽기만.
- **이벤트 발행**: `pm.backlog.reordered` (선택적, Phase 2 — 실시간 보드용)

### `Label` — 분류

- **책임 한 줄**: 이슈 분류 메타데이터. 워크스페이스 공통 또는 프로젝트 로컬.
- **핵심 필드**: `id`, `workspace_id`, `scope_type` (workspace/project), `scope_id?`, `name`, `color`, `description?`
- **권한 모델 진입점**: 생성·삭제는 Admin/Maintainer, 적용은 모든 Member.
- **이벤트 발행**: 없음 (Phase 1 기준).

### `Comment` — 이슈 코멘트 (PM 소유)

- **책임 한 줄**: 이슈 컨텍스트 안의 코멘트. Comms 메시지와 별도 모델.
- **핵심 필드**: `id`, `workspace_id`, `issue_id`, `author_member_id`, `body` (markdown), `parent_comment_id?` (스레드), `mentions[]` (Member ID 배열), `created_at`, `edited_at?`
- **권한 모델 진입점**: Issue 읽기 권한과 동일. 수정/삭제는 작성자 본인 + Admin.
- **이벤트 발행**: `pm.comment.added`, `pm.comment.mentioned` (멘션 알림용 — Comms가 구독)

> **명시적으로 안 만드는 엔티티** (Phase 1): `Milestone`, `Roadmap`, `OKR`, `TimeEntry`, `Dependency`(이슈 간 명시적 의존성 그래프). 모두 Phase 2+ 또는 Phase 3.

---

## 상태 머신 다이어그램

### Issue 상태 전이

```
                   ┌──────────────────────────────────┐
                   │                                  │
                   v                                  │
    [backlog] ──> [todo] ──> [in_progress] <─┬──> [blocked]
                    │             │           │
                    │             v           │
                    │           [done]        │
                    │                         │
                    └────────> [cancelled] <──┘

   전이 트리거 → 발행 이벤트:
     * → blocked                  : pm.issue.blocked
     blocked → in_progress        : pm.issue.unblocked   (Phase 2)
     * → done                     : pm.issue.resolved
     * → cancelled                : pm.issue.cancelled
     backlog → todo               : pm.issue.scheduled   (스프린트 배정 시 동시 발생 가능)
     create                       : pm.issue.created
```

규칙:

- **모든 전이는 `AuditLog`에 actor·trace_id와 함께 기록**된다.
- `blocked` 전이는 `reason` 필드 필수 — A2UI `pm.identify_blockers` Tool이 reason을 노출.
- `cancelled`는 종결 상태. `cancelled → *` 재오픈 금지 (대신 새 Issue 생성).
- 사용자별 커스텀 상태 추가 기능은 **Phase 1에 안 만든다** (Watch List #4).

### Sprint 라이프사이클

```
   [planned]  ──(start)──>  [active]  ──(end)──>  [completed]
                                                     │
                                                     └─> pm.sprint.ended (velocity, blocker_count 포함)

   active 상태에서만 이슈 sprint_id 할당 가능.
   completed 후 sprint_id 변경 금지 (불변).
```

### Project 라이프사이클

```
   [planned] ──> [in_progress] ──┬──> [completed]
                       ^         │
                       │         └──> [cancelled]
                       │
                   [paused]  <─ in_progress (양방향)
```

---

## Phase별 출시 (P0/P1/P2/P3)

> 모든 기능은 [`jtbd.md`](../01-market/jtbd.md) Job ID에 매핑. ID 없는 기능은 빌드 안 한다.

### Phase 1 (P0) — Beachhead 정식 출시 (2027 H1)

| 기능                     | Phase | JTBD ID      | 우선순위 | 근거                                                         |
| ------------------------ | ----- | ------------ | -------- | ------------------------------------------------------------ |
| Issue CRUD + 상태 전이   | 1     | USR-1, COO-1 | P0       | PM 도메인의 핵심 aggregate. 없으면 도메인 자체가 성립 안 함. |
| Sprint 생성·시작·종료    | 1     | COO-1        | P0       | "월요일 9시" Big Job #1의 데이터 단위.                       |
| Project (이슈 그룹화)    | 1     | USR-1, COO-1 | P0       | Linear의 Project 동등. 50명+ 회사 보드 규율의 최소 단위.     |
| Backlog (정렬 큐)        | 1     | USR-1        | P0       | Linear 벤치마크.                                             |
| Board (칸반 + 리스트 뷰) | 1     | USR-1, COO-1 | P0       | UX 차별화의 1번. 타임라인 뷰는 Phase 2.                      |
| Label                    | 1     | USR-1        | P0       | 분류·필터의 기본.                                            |
| Comment + 멘션           | 1     | USR-2, USR-3 | P0       | 이슈 컨텍스트의 대화. Comms 멘션 라우팅과 통합.              |
| 키보드 단축키 카탈로그   | 1     | USR-1, EMO-5 | P0       | 불변 원칙 5 (Linear UX 벤치마크).                            |
| Cmd+K 빠른 검색          | 1     | USR-1, EMO-5 | P0       | 이슈 / 스프린트 / 멤버 통합.                                 |
| 실시간 보드 (WebSocket)  | 1     | USR-1        | P0       | Linear 동등 — 다른 사용자의 이동이 즉시 보임.                |
| Optimistic UI            | 1     | USR-1, EMO-5 | P0       | 입력 → 응답 체감 속도.                                       |
| Jira 이슈 임포터         | 1     | Trigger 1, 6 | P0       | Atlassian 공략. Habit 해제 무기.                             |
| Linear 이슈 임포터       | 1     | Trigger 1    | P0       | PLG 전환층.                                                  |
| REST API + Webhook 기본  | 1     | IT-2         | P0       | 통합 / IT 검토 통과.                                         |

### Phase 2 (P1) — 통합 (2027 H2 – 2028 H1)

| 기능                               | Phase | JTBD ID      | 우선순위 | 근거                                                             |
| ---------------------------------- | ----- | ------------ | -------- | ---------------------------------------------------------------- |
| A2UI 도메인 횡단 Tool (PM ↔ Comms) | 2     | COO-2, USR-4 | P1       | 차별화 축 2의 외부 데모. Business+ Tier 게이트.                  |
| Milestone (마감 단위)              | 2     | CEO-1        | P1       | 분기 OKR 회고 입력. Phase 1에 안 박은 이유는 Project로 80% 커버. |
| Roadmap 뷰 (타임라인)              | 2     | CEO-2        | P1       | Project × Milestone × Sprint 시각화.                             |
| Notion 페이지 임포터               | 2     | Trigger 1    | P1       | competitive-landscape.md Phase 2 약속.                           |
| Release Note 자동 생성             | 2     | COO-5        | P1       | Sprint 종료 → 릴리스 노트 초안. AI 합성.                         |
| 자동화 룰 기초                     | 2     | USR-1        | P1       | "라벨 X 추가 → 담당자 자동 할당" 수준. 풀 기능은 Phase 3.        |
| 회고(Retro) 흐름 정식              | 2     | CEO-2        | P1       | Sprint 종료 후 회고 워크플로우. Comms 데이터 인용.               |
| 이슈 첨부파일                      | 2     | USR-1        | P1       | Phase 1은 외부 링크만.                                           |
| 모바일 풀 기능                     | 2     | USR-6        | P1       | iOS/Android — Phase 1은 읽기 전용.                               |

### Phase 3 (P2) — 미드마켓 진입 (2028 H2 – 2029 H1)

| 기능                                  | Phase | JTBD ID         | 우선순위 | 근거                                                           |
| ------------------------------------- | ----- | --------------- | -------- | -------------------------------------------------------------- |
| 미드마켓 RBAC (Project별 세분화 권한) | 3     | IT-4, COO-7     | P2       | SCIM·SOC2와 함께.                                              |
| OKR / 목표 추적                       | 3     | CEO-2           | P2       | 미드마켓이 요구. Phase 1-2 의도적 보류.                        |
| 의존성 그래프 (Dependency)            | 3     | USR-1           | P2       | 이슈 간 명시적 blocks/blocked_by. Phase 1은 EntityLink로 우회. |
| Time tracking                         | 3     | (미드마켓 요구) | P2       | 광고대행·외주 미드마켓 회사가 요구. ICP-3 도입 시점.           |
| 자동화 룰 풀 기능 (Workflow Builder)  | 3     | USR-1           | P2       | If-this-then-that 풀 빌더.                                     |
| Sprint 회고 AI 분석 (3도메인 횡단)    | 3     | CEO-2, CEO-4    | P2       | HR 정식 출시 후 가능.                                          |

### Phase 4+ (P3) — 보류 또는 영구 안 함

| 기능                              | 결정       | 근거                                                               |
| --------------------------------- | ---------- | ------------------------------------------------------------------ |
| 게임화 / 리워드 / 포인트          | 영구 안 함 | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision. |
| 포트폴리오 뷰 (다중 워크스페이스) | Phase 4+   | 미드마켓 본부 시장. ICP-3 충족 후.                                 |
| 외부 마켓플레이스 / 플러그인      | Phase 4+   | Atlassian 마켓플레이스 비유. 4도메인 깊이 완성 전에는 분산.        |
| Confluence 수준 위키              | 영구 안 함 | 5번째 도메인 확장 금지 (불변 원칙).                                |

---

## API 표면 (개념 수준)

> 전체 OpenAPI 3.1 스펙은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 엔드포인트 카탈로그.

### REST 엔드포인트

| 메서드 | 경로                                              | 권한         | Phase |
| ------ | ------------------------------------------------- | ------------ | ----- |
| GET    | `/workspaces/{ws}/issues`                         | Member+      | 1     |
| POST   | `/workspaces/{ws}/issues`                         | Member+      | 1     |
| GET    | `/issues/{id}`                                    | Issue Read   | 1     |
| PATCH  | `/issues/{id}`                                    | Issue Write  | 1     |
| POST   | `/issues/{id}/transition`                         | Issue Write  | 1     |
| DELETE | `/issues/{id}`                                    | Maintainer+  | 1     |
| GET    | `/workspaces/{ws}/sprints`                        | Member+      | 1     |
| POST   | `/workspaces/{ws}/sprints`                        | Maintainer+  | 1     |
| POST   | `/sprints/{id}/start`                             | Maintainer+  | 1     |
| POST   | `/sprints/{id}/end`                               | Maintainer+  | 1     |
| GET    | `/sprints/{id}/issues`                            | Member+      | 1     |
| GET    | `/workspaces/{ws}/projects`                       | Member+      | 1     |
| POST   | `/workspaces/{ws}/projects`                       | Maintainer+  | 1     |
| GET    | `/projects/{id}/backlog`                          | Project Read | 1     |
| POST   | `/projects/{id}/backlog/reorder`                  | Maintainer+  | 1     |
| GET    | `/workspaces/{ws}/boards`                         | Member+      | 1     |
| POST   | `/issues/{id}/comments`                           | Issue Read   | 1     |
| GET    | `/issues/{id}/comments`                           | Issue Read   | 1     |
| POST   | `/workspaces/{ws}/importers/jira`                 | Admin        | 1     |
| POST   | `/workspaces/{ws}/importers/linear`               | Admin        | 1     |
| POST   | `/workspaces/{ws}/importers/notion`               | Admin        | 2     |
| GET    | `/workspaces/{ws}/search?q=...&type=issue,sprint` | Member+      | 1     |

### WebSocket / SSE 이벤트 (실시간)

| 이벤트                        | 채널                   | 페이로드                               | Phase |
| ----------------------------- | ---------------------- | -------------------------------------- | ----- |
| `issue.updated`               | `ws:{ws}/project/{id}` | `issue_id`, `delta`                    | 1     |
| `issue.transitioned`          | `ws:{ws}/project/{id}` | `issue_id`, `from_status`, `to_status` | 1     |
| `backlog.reordered`           | `ws:{ws}/project/{id}` | `backlog_id`, `new_order[]`            | 1     |
| `comment.added`               | `ws:{ws}/issue/{id}`   | `comment_id`, `author_id`              | 1     |
| `presence` (누가 같이 보는중) | `ws:{ws}/issue/{id}`   | `member_ids[]`                         | 2     |

규칙:

- 모든 WebSocket 메시지에 `trace_id` 포함 (OpenTelemetry 전파).
- 클라이언트 재연결 시 `since=cursor` 지원 — 누락 이벤트 따라잡기.

---

## A2UI Tool 카탈로그 (PM 전용)

> [`domain-overview.md`](./domain-overview.md) A2UI Tool 카탈로그 v1의 PM Tool 4개를 시작점으로 확장 (8개). 모든 Tool은 헤드리스 service 함수 + Pydantic Input/Output Schema. UI 호출 / 에이전트 호출 동일 진입점.

| Tool                       | Input Schema 핵심 필드                                                                                       | Output Schema 핵심 필드                                            | Tier          | Phase        | JTBD ID      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------- | ------------ | ------------ |
| `pm.search_issues`         | `workspace_id`, `query?`, `filters`(status, assignee_id, sprint_id, project_id, label[]), `pagination`       | `issues[]`, `total`, `facets`                                      | Free+         | 1            | USR-1        |
| `pm.create_issue`          | `workspace_id`, `project_id`, `title`, `description?`, `assignee_id?`, `sprint_id?`, `labels[]`, `priority?` | `issue_id`, `url`, `event`                                         | Team+         | 1            | USR-2        |
| `pm.transition_issue`      | `issue_id`, `to_status`, `reason?` (blocked 시 필수)                                                         | `issue`, `event`                                                   | Team+         | 1            | USR-1        |
| `pm.add_comment`           | `issue_id`, `body`, `mentions[]`, `parent_comment_id?`                                                       | `comment_id`, `event`                                              | Team+         | 1            | USR-2        |
| `pm.get_sprint_summary`    | `sprint_id`                                                                                                  | `velocity`, `blockers[]`, `member_stats[]`, `burnup_series[]`      | Team+         | 1            | COO-1, COO-5 |
| `pm.identify_blockers`     | `workspace_id`, `since`, `min_blocked_hours?`                                                                | `blocked_issues[]` (with `assignee_id`, `blocked_since`, `reason`) | Team+         | 1            | COO-2        |
| `pm.start_sprint`          | `sprint_id`                                                                                                  | `sprint`, `event`                                                  | Team+         | 1            | COO-1        |
| `pm.end_sprint`            | `sprint_id`, `auto_carry_over?`                                                                              | `sprint`, `velocity`, `event`, `carry_over_issues[]`               | Team+         | 1            | COO-1        |
| `pm.trigger_import`        | `workspace_id`, `source` (jira/linear/notion), `credentials_ref`, `mapping?`                                 | `import_job_id`, `dry_run_summary`                                 | Team+ (Admin) | 1 (Notion 2) | Trigger 1    |
| `pm.generate_release_note` | `sprint_id`, `style?`                                                                                        | `markdown`, `issues_included[]`                                    | Business+     | 2            | COO-5        |

### 도메인 횡단 Tool 진입점 (Business+, Phase 2)

PM에서 시작해서 다른 도메인을 호출하는 합성 시나리오. [`domain-overview.md`](./domain-overview.md) A2UI 도메인 횡단 쿼리 절과 정렬.

**시나리오 1: 스프린트 회고 자동 생성** (COO-2, CEO-2)

```
사용자: "이번주 스프린트 끝났어. 회고 초안 만들어줘."

Agent: a2ui.cross_domain_query(intent="sprint retro draft")
  └→ pm.get_sprint_summary(sprint_id)
       returns: velocity=23, blockers=[{issue_id: I7, blocked_hours: 72, assignee_id: M3}]
  └→ pm.identify_blockers(workspace_id, since=sprint_start)
  └→ comms.summarize_channel(channel_id=sprint_channel, since=sprint_start, style="decisions+blockers")
       returns: key_decisions[], unresolved_threads[]
  └→ for each blocker.assignee_id (권한 체크 통과 시):
       hr.get_member_context(member_id) → recent_1on1_keywords (마스킹 가능)
  └→ 합성: 회고 마크다운 초안 (스프린트 통계 + 채널 결정 요약 + 블로커 멤버 컨텍스트 한 줄)
```

**시나리오 2: 메시지 → 이슈 전환** (USR-2, Trigger 5)

```
사용자가 Comms 메시지에 "이슈로 만들기" 단축키 누름.

Agent: comms.message_to_issue(message_id, assignee_id?)
  └→ comms.search_messages(thread containing message_id) → context
  └→ AI 합성: title 추출, description은 thread context 인용
  └→ pm.create_issue(workspace_id, project_id, title, description, assignee_id?)
  └→ EntityLink 생성: source=comms.message, target=pm.issue, link_kind='derived_from'
  └→ 양 도메인 이벤트 발행
```

### Tool Registry 게이팅 — Tier 강제

[`domain-overview.md`](./domain-overview.md) 절차 따름:

- `pm.search_issues` / `pm.add_comment` 등 단일 도메인 Tool: Free 또는 Team+.
- `pm.generate_release_note` / `a2ui.cross_domain_query`로 진입하는 PM Tool: **Business+ Tier 게이트**.
- 게이트는 `tool_registry.yaml` 한 곳에서만 강제. service 함수 안에 박지 않음 (Watch List #2).

---

## 임포터 전략 (Phase 1 핵심)

ICP-1이 Switch 결정의 마지막 30초에 묻는 질문은 항상 같다: **"내 Jira/Linear 데이터를 잃지 않고 옮길 수 있나?"** 임포터는 마케팅 기능이 아니라 Habit 해제 무기다 ([`jtbd.md`](../01-market/jtbd.md) Trigger 1·6).

### Jira 임포터 (Phase 1 필수)

**접근**: Jira Cloud REST API v3 (`/rest/api/3/`). On-prem(Data Center)은 Phase 3까지 안 한다 ([`icp.md`](../01-market/icp.md) 비-ICP).

**매핑 표**:

| Jira 개념                          | Conflow 개념                      | 변환 규칙                                                                                                                 |
| ---------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Project                            | Project                           | 1:1 매핑                                                                                                                  |
| Issue (Standard / Sub-task)        | Issue                             | parent_issue_id는 Phase 1에 안 받음 — flat 구조로 가져옴. 부모-자식은 EntityLink(`link_kind='subtask_of'`)로 Phase 2 전환 |
| Issue Type (Story/Bug/Task/Epic)   | Label (`type:bug` 등)             | Type 자체는 안 만들고 Label로 보존. Epic은 Phase 2에 Project로 승격 옵션                                                  |
| Status (Open/In Progress/Done/...) | status enum                       | 매핑 대화상자 — 사용자가 Jira status → Conflow status 매핑 확정                                                           |
| Sprint                             | Sprint                            | 1:1. Active Sprint 1개까지 보존, 과거 Sprint는 completed 상태로                                                           |
| Assignee / Reporter                | Member                            | 이메일 기반 자동 매핑. 매칭 안 되면 "Unmatched Users" 목록 + 수동 매핑                                                    |
| Comment                            | Comment                           | 1:1. 첨부파일은 Phase 1에 외부 링크로 보존                                                                                |
| Custom Field                       | Label 또는 무시                   | 사용자가 Phase 1에 명시적으로 무시 선택 가능. 자동 변환 안 함                                                             |
| Attachment                         | 외부 링크 (s3 또는 Atlassian URL) | Phase 1: URL만 보존. Phase 2: 자체 스토리지로 이전 옵션                                                                   |
| Workflow Transition Rule           | 무시                              | Phase 1: 안 가져옴. Phase 3에 자동화 룰로 재정의                                                                          |

**한계와 우회**:

- 5,000+ 이슈 워크스페이스는 **dry-run 모드** 필수 (1차 매핑 검증 후 본 임포트).
- Jira 권한 매핑은 1차 자동 + 수동 보정 — 자동 90% 정확도 목표.
- 임포트는 **부분 실패 시 재개 가능** (idempotent job, 이슈별 외부 ID 추적).

### Linear 임포터 (Phase 1 권장)

**접근**: Linear GraphQL API. PLG 전환층이 가장 빠름 ([`competitive-landscape.md`](../00-vision/competitive-landscape.md)).

**매핑 표**:

| Linear 개념                                            | Conflow 개념                 | 변환 규칙                                            |
| ------------------------------------------------------ | ---------------------------- | ---------------------------------------------------- |
| Team                                                   | Project (또는 Project group) | 1:1                                                  |
| Project                                                | Project                      | 1:1                                                  |
| Issue                                                  | Issue                        | 1:1                                                  |
| Cycle                                                  | Sprint                       | 1:1 (Linear Cycle = Conflow Sprint)                  |
| Issue Status (Backlog/Todo/In Progress/Done/Cancelled) | status enum                  | 표준 매핑 자동                                       |
| Label                                                  | Label                        | 1:1                                                  |
| Comment                                                | Comment                      | 1:1                                                  |
| Sub-issue                                              | EntityLink(`subtask_of`)     | flat 구조 + 링크                                     |
| Estimate (point)                                       | priority + custom field      | Phase 1: priority로 근사. Phase 3 estimate 정식 도입 |

**기대 정확도**: 95%+ (Linear 모델이 Conflow와 거의 동형). 임포트 실패 < 5%여야 차별화 깨짐 신호 (Watch List).

### Notion 임포터 (Phase 2)

**접근**: Notion API. **DB 우선 휴리스틱** — 페이지가 DB row면 Issue, 그 외 페이지는 무시(Phase 2).

**한계**:

- Notion의 자유 구조 → 이슈 변환은 본질적으로 손실 있음. 사용자에게 명시.
- "내 Notion DB가 PM 보드처럼 쓰이고 있다"는 경우에 한정 효과.

### 임포트 실패·충돌 처리

| 케이스              | 처리                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| 중복 외부 ID        | upsert 정책. 같은 source_external_id가 이미 있으면 업데이트(필드 단위 diff). 사용자가 "skip" 선택 가능. |
| 매칭 안 되는 Member | "Unmatched Users" 큐. 임포트는 계속 진행, 해당 이슈는 unassigned. 사용자가 사후 매핑.                   |
| 깨진 첨부파일 링크  | 임포트 로그에 기록. 이슈 본문에 `[broken-link]` 주석.                                                   |
| 권한 매핑 충돌      | 보수적 기본값(가장 제한적인 권한). 사용자가 명시적으로 더 넓게 풀어야 함.                               |
| 부분 실패           | job 재개 가능. 실패한 이슈만 재시도 (idempotent).                                                       |

### 도메인 횡단 영향

- 임포트 시 **Member ID 매핑 테이블**은 PM 임포터만 쓰지 않는다 — Comms 임포트 / HR 입퇴사 동기화 시 재사용 (`server/src/app/core/identity_mapping/`).
- Jira 임포터로 만든 Project가 **자동으로 Comms 채널과 매핑되지 않음** — 사용자가 명시적으로 "이 Project에 Comms 채널 연결" 결정. 자동 매핑은 Phase 2 도메인 횡단 자동화 룰로.

---

## UX 차별화 디테일 (Linear 벤치마크)

[`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 5와 [`jtbd.md`](../01-market/jtbd.md) USR-1·EMO-5의 직접 표현.

### 키보드 단축키 카탈로그 (Phase 1 P0)

| 단축키        | 동작                                   | 범위    |
| ------------- | -------------------------------------- | ------- |
| `C`           | 새 이슈                                | 전역    |
| `Cmd+K`       | 빠른 검색 (이슈/스프린트/멤버/Project) | 전역    |
| `G` `I`       | 이슈 목록으로 이동                     | 전역    |
| `G` `S`       | 활성 스프린트로 이동                   | 전역    |
| `G` `B`       | 백로그로 이동                          | 전역    |
| `G` `P`       | 프로젝트 목록으로 이동                 | 전역    |
| `/`           | 현재 뷰 안 검색                        | 뷰 안   |
| `A`           | 담당자 변경                            | 이슈    |
| `S`           | 상태 변경 (transition picker)          | 이슈    |
| `P`           | 우선순위 변경                          | 이슈    |
| `L`           | 라벨 변경                              | 이슈    |
| `D`           | 마감일 변경                            | 이슈    |
| `M`           | 코멘트 작성                            | 이슈    |
| `E`           | 이슈 편집 모드                         | 이슈    |
| `Esc`         | 닫기 / 취소                            | 모달    |
| `J` / `K`     | 다음 / 이전 이슈                       | 리스트  |
| `Cmd+Enter`   | 폼 제출                                | 모든 폼 |
| `Cmd+Shift+P` | 명령 팔레트 (모든 Tool)                | 전역    |
| `?`           | 단축키 도움말                          | 전역    |
| `Cmd+/`       | 멘션 검색 (코멘트 작성 중)             | 코멘트  |

**원칙**:

- Linear와 **충돌하지 않는 매핑** (마이그레이션 사용자의 근육 기억 보존).
- Cmd+Shift+P는 명령 팔레트 — 모든 A2UI Tool 진입점.
- 단축키 도움말은 항상 `?` (Slack/Linear 표준).

### Cmd+K 빠른 검색

- **통합 검색**: 이슈 / 스프린트 / Project / Member / Label.
- **응답 시간 SLO**: p99 < 300ms (Linear 벤치마크 동등).
- **컨텍스트 인식**: 현재 Project 안에서는 해당 Project 결과 우선.
- **최근 항목 캐시**: 클라이언트 메모리에 최근 50개 — 오프라인에서도 즉시 응답.
- **A2UI 진입**: Cmd+K 안에서 "/ai" 입력 시 자연어 쿼리 모드 진입 (Business+).

### 실시간 보드 (WebSocket)

- **Optimistic UI**: 드래그 즉시 UI 반영, 서버 응답 후 reconcile.
- **Presence**: 같은 이슈/보드를 보는 다른 멤버 아바타 표시 (Phase 2).
- **Conflict 처리**: 두 사용자가 동시에 같은 이슈 상태 변경 → last-write-wins + 이전 값 토스트로 알림.
- **재연결**: 끊김 시 자동 재연결 + `since=cursor`로 누락 이벤트 따라잡기.

### Optimistic UI 원칙

| 동작           | Optimistic | 비고                             |
| -------------- | ---------- | -------------------------------- |
| 이슈 상태 전이 | O          | 실패 시 롤백 + 토스트            |
| 라벨 추가/제거 | O          |                                  |
| 담당자 변경    | O          |                                  |
| 이슈 생성      | O          | 임시 ID 부여, 서버 ID로 교체     |
| 이슈 삭제      | X          | 확인 다이얼로그 + 서버 응답 대기 |
| Sprint 종료    | X          | velocity 계산 등 서버 의존도 큼  |

### 모바일 (Phase 1: 읽기 전용 / Phase 2: 정식)

- Phase 1: 이슈 / 스프린트 읽기 + 코멘트 작성까지만 (USR-6 부분 충족).
- Phase 2: 모든 P0 액션 (생성·전이·할당) + Push 알림.

---

## 권한 모델 적용

[`domain-overview.md`](./domain-overview.md)의 Role 5개가 PM에서 어떻게 작동하는가.

### 권한 매트릭스

| 동작                        | Owner | Admin | Member                                  | Guest            | External (노무사) |
| --------------------------- | ----- | ----- | --------------------------------------- | ---------------- | ----------------- |
| Issue 읽기 (workspace 전체) | O     | O     | O (private project 제외)                | 초대된 project만 | **없음**          |
| Issue 생성                  | O     | O     | O                                       | 초대된 project만 | **없음**          |
| Issue 수정 (본인 작성/담당) | O     | O     | O                                       | 초대된 범위만    | **없음**          |
| Issue 삭제                  | O     | O     | X (soft delete만, Maintainer 권한 필요) | X                | **없음**          |
| Sprint 생성·전이            | O     | O     | Maintainer 역할 부여 시                 | X                | **없음**          |
| Project 생성                | O     | O     | X                                       | X                | **없음**          |
| Project 가시성 변경         | O     | O     | Project Lead                            | X                | **없음**          |
| Comment 작성                | O     | O     | O                                       | 초대된 범위만    | **없음**          |
| 임포트 트리거               | O     | O     | X                                       | X                | **없음**          |
| A2UI PM Tool 호출           | O     | O     | Tier 게이트 통과 시                     | 초대 범위 안만   | **없음**          |

**중요 결정**:

- **External(노무사) 역할은 PM 도메인에 아예 진입 불가**. 노무사가 HR/Documents 외부 협업자로 들어와도 PM 데이터 0건 노출 ([`jtbd.md`](../01-market/jtbd.md) Trigger 2·3, EMO-6).
- **Guest는 명시적으로 초대된 Project의 리소스만**. 워크스페이스 전체 이슈 검색 불가.

### Project별 가시성

| visibility            | 노출 범위                                                                     |
| --------------------- | ----------------------------------------------------------------------------- |
| `private`             | 명시적으로 추가된 Member만. Workspace Admin도 자동 진입 안 됨 (요청 후 승인). |
| `internal`            | 워크스페이스 Member 전체. Guest 제외.                                         |
| `public-in-workspace` | 워크스페이스 전체 (Guest 포함). External 제외.                                |

`private` Project의 데이터는 **A2UI Tool 호출 시에도 권한 체크**. [`domain-overview.md`](./domain-overview.md) "도메인 횡단 쿼리에서 권한 누수 방지" 원칙과 정렬.

---

## 이벤트 발행 / 구독

### PM이 발행하는 이벤트

| 이벤트                      | Phase | 페이로드 핵심 필드                                                                    | 구독 도메인                                          |
| --------------------------- | ----- | ------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `pm.issue.created`          | 1     | `issue_id`, `workspace_id`, `project_id`, `reporter_id`, `assignee_id?`, `sprint_id?` | Comms (멘션·알림), A2UI                              |
| `pm.issue.updated`          | 1     | `issue_id`, `delta` (변경된 필드만)                                                   | A2UI (Phase 2 자동화 룰)                             |
| `pm.issue.blocked`          | 1     | `issue_id`, `assignee_id`, `blocked_since`, `reason`                                  | Comms (담당자 알림), HR (Phase 2 1:1 컨텍스트), A2UI |
| `pm.issue.unblocked`        | 2     | `issue_id`, `unblocked_at`                                                            | Comms, A2UI                                          |
| `pm.issue.resolved`         | 1     | `issue_id`, `resolver_id`, `resolved_at`, `cycle_time_hours`                          | Comms, A2UI                                          |
| `pm.issue.cancelled`        | 1     | `issue_id`, `cancelled_by`, `reason?`                                                 | A2UI                                                 |
| `pm.sprint.started`         | 1     | `sprint_id`, `start_date`, `issue_count`                                              | Comms (채널 알림), A2UI                              |
| `pm.sprint.ended`           | 1     | `sprint_id`, `velocity`, `blocker_count`, `member_stats[]`                            | Comms (회고 트리거), HR (멤버 통계), A2UI            |
| `pm.project.created`        | 1     | `project_id`, `lead_member_id`, `visibility`                                          | Comms (채널 자동 생성 후보), A2UI                    |
| `pm.project.status_changed` | 1     | `project_id`, `from`, `to`                                                            | Comms, A2UI                                          |
| `pm.comment.added`          | 1     | `comment_id`, `issue_id`, `author_member_id`, `mentions[]`                            | Comms (멘션 알림 라우팅)                             |
| `pm.import.completed`       | 1     | `import_job_id`, `source`, `issues_imported`, `errors[]`                              | A2UI, AuditLog                                       |

### PM이 구독하는 이벤트

| 이벤트                      | 발행 도메인 | PM의 반응                                                                | Phase |
| --------------------------- | ----------- | ------------------------------------------------------------------------ | ----- |
| `comms.decision.detected`   | Comms       | A2UI가 이슈 생성 후보 제안 (자동 생성 아님 — 사용자 승인 필요)           | 2     |
| `hr.member.onboarded`       | HR          | 담당자 풀에 추가. 해당 멤버에게 기본 Project Member 권한 부여 후보       | 2     |
| `hr.member.offboarded`      | HR          | 해당 멤버의 `in_progress` / `blocked` 이슈를 매니저에게 재할당 후보 알림 | 2     |
| `documents.contract.signed` | Documents   | (PM 직접 반응 없음 — HR 경유)                                            | 4     |

규칙:

- **`comms.decision.detected` → 자동 이슈 생성 금지** (Phase 2 기준). 사용자가 명시적으로 승인해야 생성. 자동 생성은 알림 폭주 위험.
- 이벤트 핸들러는 모두 **idempotent** ([`domain-overview.md`](./domain-overview.md) 규칙).

---

## 차별화 깨짐 신호 (Watch List)

| #   | 신호                                                                               | 그러면 무엇을 한다                                                                                        |
| --- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 1   | 키보드 단축키 / Cmd+K 검색이 Linear 대비 30%+ 느림 (p99 측정)                      | 사용자 페르소나 이탈 가능성. 즉시 성능 스프린트. 불변 원칙 5 위협.                                        |
| 2   | 도메인 횡단 A2UI Tool이 PM 데이터를 단순 SQL 조회 수준으로만 노출 (합성 깊이 부재) | 차별화 축 2 무력화. Tool Registry에 "합성 시나리오 커버리지" 메트릭 추가, Phase 2 PoC 검증에서 정성 평가. |
| 3   | Jira 임포터 정확도 < 90% (5,000+ 이슈 워크스페이스 기준)                           | Atlassian 공략 메시지 좌초. Trigger 1·6 약속 깨짐. 즉시 매핑 규칙 보강 + 사용자 매핑 UX 강화.             |
| 4   | Issue 상태 머신이 워크스페이스별 커스텀 상태로 분기                                | "단순함" 약속 깨짐. Phase 3까지 커스텀 상태 금지 유지. 라벨로 우회.                                       |
| 5   | PM service 함수가 React 컴포넌트 import                                            | 헤드리스 원칙 깨짐. A2UI Tool 등록 불가능. 즉시 리팩토링.                                                 |
| 6   | PM이 HR 테이블 또는 Comms 테이블 직접 JOIN                                         | 도메인 경계 침식. `EntityLink` + 이벤트로 강제 리팩토링.                                                  |
| 7   | `private` Project 데이터가 A2UI Tool 응답에 노출                                   | 권한 누수. circuit breaker로 Tool 정지 + 사후 audit.                                                      |
| 8   | Phase 1 P0 기능에서 P2/P3 기능이 영업 압력으로 끼어듦 (예: OKR, Time tracking)     | 스코프 절제 깨짐. [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision 재전달 + 거절.        |

---

## 의도적 보류 (Open Decisions)

명시적으로 **안 한다** 또는 **누가 묻기 전에 확정한** 결정들.

| 결정                                                                    | 시점                                                                             | 근거                                                               |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 게임화 / 리워드 / 포인트 / 뱃지                                         | 영구 안 함                                                                       | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision. |
| OKR / 목표 추적                                                         | Phase 3로 미룸                                                                   | 미드마켓 진입 시점에 필요. ICP-1은 Project로 80% 커버.             |
| Time tracking / 공수 입력                                               | Phase 3로 미룸                                                                   | 광고대행·외주 미드마켓이 요구. ICP-1은 안 씀.                      |
| 외부 마켓플레이스 / 플러그인                                            | Phase 4+로 미룸                                                                  | 4도메인 깊이 완성 전에는 분산. Atlassian 마켓플레이스 함정 회피.   |
| 의존성 그래프 시각화                                                    | Phase 3로 미룸                                                                   | Phase 1-2는 EntityLink로 우회.                                     |
| 워크스페이스별 커스텀 status 상태                                       | 영구 안 함 (Phase 3 재검토)                                                      | 단순함 약속. 분류는 Label로 대체.                                  |
| Confluence 수준 위키                                                    | 영구 안 함                                                                       | 5번째 도메인 확장 금지.                                            |
| 사용자별 커스텀 워크플로우 (Jira 워크플로우 빌더 동급)                  | 영구 안 함                                                                       | Linear 벤치마크와 충돌. 자동화 룰로 80% 커버 (Phase 3).            |
| 이슈 첨부파일 자체 스토리지                                             | Phase 2                                                                          | Phase 1은 외부 링크만.                                             |
| 모바일 풀 기능                                                          | Phase 2                                                                          | Phase 1은 읽기 전용.                                               |
| Slack 임포터 (PM 영역 — 메시지 → 이슈 일괄 변환)                        | Phase 2                                                                          | Habit 해제 압력 낮음. Comms 도메인 임포터에 위임.                  |
| Jira On-prem / Data Center 임포터                                       | Phase 3 검토                                                                     | ICP-1·2 비-ICP.                                                    |
| 이슈 상태 머신 ERD / RLS / 인덱스 / 샤딩 SQL                            | [`04-architecture/data-model.md`](../04-architecture/data-model.md)로 위임       |
| A2UI Tool Registry 구현 패턴 (LangGraph 권한 전파)                      | [`04-architecture/a2ui-strategy.md`](../04-architecture/a2ui-strategy.md)로 위임 |
| WebSocket 인프라 선택 (Postgres LISTEN/NOTIFY vs Redis Pub/Sub vs NATS) | [`04-architecture/tech-stack.md`](../04-architecture/tech-stack.md)로 위임       |

---

## 관련 문서

- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 축 2(도메인 횡단 AI)·축 4(마이그레이션 비용)
- [`../00-vision/competitive-landscape.md`](../00-vision/competitive-landscape.md) — Atlassian/Linear/Notion 공략·임포터 우선순위
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — Phase 1 PM 정식 출시, 불변 원칙 3·5
- [`../01-market/jtbd.md`](../01-market/jtbd.md) — Big Job #1·#2, PM 도메인 매핑표 (이 문서의 시작점)
- [`../01-market/icp.md`](../01-market/icp.md) — ICP-1 사용자 페르소나 (Linear/Slack 속도 기준)
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — Free/Team/Business Tier 게이팅
- [`./domain-overview.md`](./domain-overview.md) — 4도메인 경계, 공유 엔티티, A2UI Tool 카탈로그 v1 (이 문서의 PM 계약표가 시작점)
- `./domain-comms.md` — Comms 도메인 (PM ↔ Comms 횡단의 반대편, 작성 예정)
- `./domain-hr.md` — HR 도메인 (입퇴사 시 이슈 재할당의 발행자, 작성 예정)
- `./domain-documents.md` — Documents 도메인 (스프린트 보고서 PDF 발급, 작성 예정)
- `../04-architecture/data-model.md` — Issue / Sprint / Project ERD, RLS, 샤딩 (작성 예정)
- `../04-architecture/a2ui-strategy.md` — PM Tool Registry 등록, LangGraph 권한 전파 (작성 예정)
- `../03-roadmap/phases.md` — Phase 1 PM 분기 OKR (작성 예정)
- `../03-roadmap/metrics.md` — 키보드 단축키·검색 속도 SLO, 임포터 정확도 측정 (작성 예정)

---

## 문서 변경 정책

이 문서는 **4개 트리거** 시 갱신한다.

1. **[`domain-overview.md`](./domain-overview.md)의 PM 계약표가 바뀔 때** — overview를 먼저 갱신 후 이 문서 동기.
2. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음.
3. **Phase 종료 시점** — 다음 Phase의 PM 출시 범위 확정과 동시에 갱신.
4. **임포터 정확도 측정 분기 보고** — < 90% 신호 시 매핑 규칙 갱신.

문서 책임자: backend-architect + PM lead. 갱신 시 변경 이력을 본 파일 하단에 추가.
