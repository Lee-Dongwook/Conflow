---
title: A2UI 아키텍처 전략 (헤드리스 + Tool Registry + 권한 전파)
최종 업데이트: 2026-06-24
상태: draft v1
독자: 백엔드, AI 엔지니어, 프론트엔드, 보안
---

# A2UI 아키텍처 전략

> 이 문서는 [`positioning.md`](../00-vision/positioning.md) 차별화 축 2의 "도메인 횡단 AI 협업 인터페이스" 약속의 **구현 결정 문서**다. [`domain-overview.md`](../02-product/domain-overview.md) "A2UI가 4도메인을 보는 방법" 절을 인프라/코드 결정으로 봉인한다.
>
> [`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 3 "A2UI 우선 (모든 기능은 헤드리스부터)" 과 [`pricing-strategy.md`](../01-market/pricing-strategy.md) 원칙 5 "AI/A2UI는 Tier로 차등, 도메인 횡단은 Business+" 의 **운영 가능한 형태**가 여기에 박힌다.
>
> **draft v1 가설 주의**: A2UI 외부 PoC 5개사 검증 ([`phases.md`](../03-roadmap/phases.md) Phase 2 종료 조건, 2028 Q1-Q2) 결과에 따라 v2로 재정의될 수 있다. 현재 시점에서는 Tool Registry 데이터 모델 / 권한 전파 호출 규약 / Agent Mode 추상화 3개를 **잠금**하고, 합성 정확도 임계치는 가설로 박는다.

---

## 이 문서로 내릴 결정

1. **헤드리스 비즈니스 로직 원칙의 구현 강제**: 모든 도메인 service 함수의 시그니처 규칙 5개. React import 정적 분석. Schema-first CI 검증. ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 3, CLAUDE.md "Headless logic" 의 코드 결정 봉인).
2. **Tool Registry 패턴**: `tool_registry.yaml` 또는 동등 DB 테이블 한 곳에서 Tool 메타데이터 / 권한 정책 / Tier 게이팅 / Phase 노출을 강제. service 함수 안에 게이팅을 박는 패턴 금지 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #2).
3. **LangGraph supervisor → 워커 → Tool 호출 흐름**: 현재 `server/src/app/agent/graphs/supervisor_graph.py` 의 워커 5개 (meeting_summary / blocker_triage / retro_insights / user_query / file_analysis) 위에 Phase 2에서 `cross_domain_composer` 노드를 추가. 호출 흐름 / Trace 규약 봉인.
4. **권한 전파 (Permission Propagation)**: supervisor가 `caller_member_id`를 모든 Tool 호출에 강제 주입. 도메인 횡단 권한 누수는 **합성 단계가 아니라 sub-tool 호출 단계에서** 차단한다. 외부 협업자(노무사) 권한은 resource-scoped로만 허용. 권한 회로 차단(circuit breaker) 패턴.
5. **도메인 횡단 합성 정확도 임계치 및 측정**: hallucination < 5%, Decision 추출 정밀도 70%+ (Phase 2) / 80%+ (Phase 3), 외부 PoC 5/3 통과 — 회귀 테스트 인프라 (`eval_dataset`) 결정.
6. **Agent Mode 4종 (mock/llm/ollama/vllm) 스위치 전략**: 모든 모드가 같은 supervisor / 같은 Tool Registry / 같은 권한 전파를 공유. 모드 전환은 `.env` `CONFLOW_AGENT_MODE` 한 줄. service 함수에 LLM provider import 금지.

---

## A2UI 설계 원칙

| # | 원칙 | 의미 |
| --- | --- | --- |
| 1 | **헤드리스 우선** | 모든 비즈니스 로직은 React 라이프사이클에 의존하지 않는 service 함수. UI는 호출만. CLAUDE.md "Headless logic" 의 구현 결정 표현. |
| 2 | **Schema-first** | Zod (프론트) / Pydantic (백엔드) Input/Output Schema가 진실. Tool은 service 함수의 부분집합 + Schema 노출. |
| 3 | **권한은 sub-tool 단계에서 적용** | 합성 단계가 아니라 각 sub-tool 호출에서 caller 권한 체크. 합성 결과의 사후 필터는 신뢰하지 않는다 (LLM이 일부 유출 가능). |
| 4 | **Tool Registry 한 곳에서 Tier 게이팅** | service 함수에 흩어지면 차별화 ([`pricing-strategy.md`](../01-market/pricing-strategy.md) 원칙 5) 깨짐. Watch List #2. |
| 5 | **Agent Mode 추상화** | mock / llm / ollama / vllm 4종 모두 같은 인터페이스 (`llm_factory.py`). 모드 전환은 `.env` 한 줄. |
| 6 | **외부 PoC가 진실** | 도메인 횡단 합성의 정확도/유용성은 5개사 검증 ([`phases.md`](../03-roadmap/phases.md) Phase 2 종료 조건) 통과로 입증. 내부 메트릭만으로 차별화 약속하지 않는다. |

---

## A2UI 한눈에 (계층 그림)

```
+--------------------+
| React UI           |  (UI는 service 호출, A2UI는 ChatInterface로 격리)
| (apps/web)         |
+---------+----------+
          | (REST/SSE, fetch)
+---------v----------+
| FastAPI API Layer  |  (server/src/app/{domain}/api.py)
| - Depends 권한 체크 |
+---------+----------+
          |
+---------v----------+        +---------------------+
| Service Layer      |<------>| LangGraph Supervisor|
| (Headless 비즈니스) |        | (agent/graphs/      |
| - Pydantic Schemas |        |  supervisor_graph)  |
+---------+----------+        +---------+-----------+
          |                              | (caller_member_id 주입)
          |                              | (Tool Registry lookup)
          |                              |
+---------v------------------------------v---------+
| Tool Registry (tool_registry.yaml 또는 DB)        |
| - tool_id / service_fn / schemas                 |
| - min_tier / permission_required / cross_domain  |
| - phase / status                                 |
+---------+----------------------------------------+
          |
+---------v---------+   +-------------+   +---------------+
| Domain Services   |   | Sandbox     |   | LLM Factory   |
| - pm/service.py   |   | (sandbox/   |   | (core/        |
| - comms/...       |   |  syscall    |   |  llm_factory) |
| - hr/...          |   |  block /    |   | mode=         |
| - documents/...   |   |  path val)  |   |  mock/llm/    |
+---------+---------+   +-------------+   |  ollama/vllm  |
          |                               +---------------+
+---------v---------+
| PostgreSQL +      |
| RoleAssignment    |
| (RLS by ws_id)    |
+-------------------+
```

**핵심 흐름**:

1. UI 또는 supervisor가 service 함수 호출 → 같은 진입점.
2. supervisor가 Tool 호출 시 `caller_member_id`를 강제 주입.
3. Tool Registry는 호출 전 Tier / 권한 검증.
4. service 함수는 `RoleAssignment` 체크 → DB 쿼리 (RLS로 `workspace_id` 강제).
5. LLM 호출은 `llm_factory.get_llm(mode=...)` 만 거침. service 함수가 provider 직접 import 금지.

---

## 헤드리스 비즈니스 로직 강제

### service 함수 시그니처 규칙

모든 도메인 service 함수는 다음 5개 규칙을 따른다.

```python
# server/src/app/pm/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.pm.schemas import SearchIssuesInput, SearchIssuesOutput

async def search_issues(
    *,
    workspace_id: UUID,
    caller_member_id: UUID,
    filters: SearchIssuesInput,
    db: AsyncSession,
) -> SearchIssuesOutput:
    """
    PM 이슈 검색 — A2UI Tool과 UI 모두 동일 진입점.

    Args (keyword-only):
        workspace_id: 다중 테넌트 격리의 강제 입력
        caller_member_id: RoleAssignment 권한 체크의 진입점
        filters: Pydantic Input Schema (any 금지)
        db: 트랜잭션 컨텍스트
    """
    # 1) RoleAssignment 체크 (workspace.read)
    # 2) DB 쿼리 (.filter(Issue.workspace_id == workspace_id))
    # 3) Pydantic Output Schema 반환
    ...
```

**규칙 5개**:

| # | 규칙 | 위반 시 |
| --- | --- | --- |
| 1 | 첫 인자에 `workspace_id` 강제 (keyword-only) | 다중 테넌트 격리 깨짐 — [`domain-overview.md`](../02-product/domain-overview.md) Watch List #4 |
| 2 | `caller_member_id` 강제 (keyword-only) | 권한 체크 우회 가능 — [`domain-overview.md`](../02-product/domain-overview.md) Watch List #6 |
| 3 | Pydantic Input/Output Schema 강제 (any 금지) | Tool Registry 등록 불가 — 차별화 축 2 무력화 |
| 4 | React imports 금지 (정적 분석 룰) | 헤드리스 원칙 깨짐 — A2UI Tool 등록 불가 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #5) |
| 5 | FastAPI `Depends` 패턴은 `api.py` 에서만 — service는 순수 | UI / Tool 진입점이 갈라짐 |

### UI ↔ service 경계

- React 컴포넌트 → `useQuery` → `axios.post(/api/...)` → FastAPI `api.py` → service 호출.
- LangGraph 워커 → Tool Registry lookup → service 호출 (`caller_member_id` 강제).
- **service 안에서 UI 상태 / 라우터 / context 참조 금지**.
- 위반 발견 시 코드 리뷰 체크리스트 + ruff 커스텀 룰로 차단.

### Schema-first 검증 (CI)

- 백엔드 빌드 시 Pydantic Schema → JSON Schema 생성.
- 프론트 `packages/core` 의 Zod 스키마와 비교 (드리프트 검출).
- 불일치 시 빌드 실패. PR 머지 차단.
- Tool Registry 의 `input_schema` / `output_schema` 참조도 동일 JSON Schema 사용.

### service 함수 ↔ Tool 등록 결정 규칙

도메인 service 함수가 무조건 Tool로 등록되지는 않는다. **등록 기준 4개**:

1. **합성 가능성**: 도메인 횡단 쿼리에서 의미 있는 sub-tool이 되는가
2. **권한 안전성**: `caller_member_id` 전파만으로 누수 차단 가능한가 (사후 LLM 마스킹 의존 X)
3. **Schema 안정성**: Input/Output이 도메인 내부 구현 변경에 견디는가
4. **검증 통과**: 단위 테스트 + integration 테스트 + permission 누수 테스트 + (cross_domain Tool 한정) eval_dataset 케이스

위 4개 통과한 service 함수만 `tool_registry.yaml` 에 추가. 추가 PR은 `@backend-architect` 리뷰 필수.

---

## Tool Registry

### Registry 데이터 모델 (`tool_registry.yaml` v1)

Phase 1 합의: **YAML 정적 파일**. Phase 3에서 DB 테이블로 마이그레이션 검토 (사용자 정의 Tool 시점, Phase 4+ 일 가능성).

```yaml
# server/src/app/agent/tool_registry.yaml
version: 1
tools:
  - id: pm.search_issues
    domain: pm
    service_fn: app.pm.service.search_issues
    input_schema: app.pm.schemas.SearchIssuesInput
    output_schema: app.pm.schemas.SearchIssuesOutput
    min_tier: free
    permission_required: workspace.read
    cross_domain: false
    phase: 1
    status: stable

  - id: pm.create_issue
    domain: pm
    service_fn: app.pm.service.create_issue
    input_schema: app.pm.schemas.CreateIssueInput
    output_schema: app.pm.schemas.CreateIssueOutput
    min_tier: team
    permission_required: pm.issue.write
    cross_domain: false
    phase: 1
    status: stable

  - id: comms.extract_decisions
    domain: comms
    service_fn: app.comms.service.extract_decisions
    input_schema: app.comms.schemas.ExtractDecisionsInput
    output_schema: app.comms.schemas.ExtractDecisionsOutput
    min_tier: business           # 도메인 횡단 핵심
    permission_required: channel.read
    cross_domain: true
    phase: 2
    status: beta

  - id: hr.summarize_one_on_ones
    domain: hr
    service_fn: app.hr.service.summarize_one_on_ones
    input_schema: app.hr.schemas.SummarizeOneOnOnesInput
    output_schema: app.hr.schemas.SummarizeOneOnOnesOutput
    min_tier: business
    permission_required: hr.one_on_one.read   # 매니저 + 본인만
    cross_domain: true
    phase: 2
    status: alpha
    privacy_layer: manager_visible           # HR 4계층 분류 표시

  - id: hr.draft_offboarding
    domain: hr
    service_fn: app.hr.service.draft_offboarding
    input_schema: app.hr.schemas.DraftOffboardingInput
    output_schema: app.hr.schemas.DraftOffboardingOutput
    min_tier: business
    permission_required: hr.offboarding.write
    role_required: hr_admin                  # Tier + Role 동시 게이트
    cross_domain: true
    phase: 2
    status: alpha

  - id: documents.file_eztax
    domain: documents
    service_fn: app.documents.service.file_eztax
    input_schema: app.documents.schemas.FileEzTaxInput
    output_schema: app.documents.schemas.FileEzTaxOutput
    min_tier: enterprise                     # ACV 1억원+ 근거
    permission_required: documents.eztax.submit
    role_required: hr_admin
    cross_domain: true
    phase: 4
    status: planned

  - id: a2ui.cross_domain_query
    domain: a2ui
    composer: app.agent.composers.cross_domain.compose   # service_fn 대신 composer
    min_tier: business
    permission_required: workspace.read
    cross_domain: true
    phase: 2
    status: beta
```

**필드 의미**:

| 필드 | 의미 | 위반 시 |
| --- | --- | --- |
| `id` | `domain.action` 형식 글로벌 고유. | id 충돌 시 빌드 실패 |
| `service_fn` | 호출될 service 함수 경로 (composer는 별도) | 함수 미존재 시 빌드 실패 |
| `input_schema` / `output_schema` | Pydantic Schema 경로. Zod와 매칭. | Schema 드리프트 시 빌드 실패 |
| `min_tier` | free / team / business / enterprise — supervisor가 호출 전 검증 | 검증 우회 발견 시 Watch List #2 |
| `permission_required` | `RoleAssignment.permissions` 의 키 | 누락 시 service가 호출 차단 |
| `role_required` | (선택) HR Admin 등 추가 Role 요구 | 누락 시 service 단에서 추가 거절 |
| `cross_domain` | 도메인 횡단 합성 sub-tool 인가 | 도메인 횡단 합성 외부 PoC 검증 의무 |
| `phase` | 출시 Phase | 미달 Phase에 호출 시 Registry가 차단 |
| `status` | planned / alpha / beta / stable / deprecated | deprecated는 호출 가능하나 logger 경고 |
| `privacy_layer` | (HR 한정) public / manager_visible / hr_only / self_only | 누락 시 HR Tool 등록 거절 |

### 등록 / 갱신 워크플로우

1. service 함수 PR 머지.
2. `tool_registry.yaml` 에 항목 추가 PR.
3. CI 검증:
   - service_fn / Schema 경로 존재 확인.
   - JSON Schema 드리프트 검사.
   - cross_domain=true 인 경우 eval_dataset 케이스 1개 이상 의무.
   - permission 누수 테스트 케이스 의무.
4. `@backend-architect` 리뷰.
5. 머지 후 supervisor 핫리로드 (Phase 1-2 정적 재로드, Phase 3 동적 검토).

### Tier 게이팅 — Tool Registry 한 곳에서만 강제

supervisor가 Tool 호출 전 다음 순서로 검증:

```
1. ws = Workspace.get(workspace_id)
2. tool = ToolRegistry.lookup(tool_id)
3. if tool.status == "planned" or tool.phase > current_phase:
      raise ToolNotAvailable
4. if not tier_allows(ws.tier, tool.min_tier):
      raise TierGated
      audit_log(actor=caller, tool=tool_id, denied="tier_gated")
5. if not has_permission(caller_member_id, tool.permission_required, ws):
      raise PermissionDenied
      audit_log(actor=caller, tool=tool_id, denied="permission")
6. if tool.role_required and not has_role(caller_member_id, tool.role_required):
      raise RoleDenied
7. tool.service_fn(workspace_id=ws.id, caller_member_id=caller, **input)
```

**원칙**:

- 검증 1-6 은 **registry-driven**. service 함수 안에 같은 검증을 박지 않는다 (중복 + 일관성 위협 + 영업 압력 시 흘림).
- service 함수는 **2차 방어선**으로 `RoleAssignment` 만 체크 (Tier는 안 봄). Tool Registry가 잘못된 호출을 막아주는 신뢰 모델.
- 게이팅이 service 함수 안에 박히기 시작하면 → [`domain-overview.md`](../02-product/domain-overview.md) Watch List #2 발동 → 즉시 Registry로 회수.

### Tool 카탈로그 v1 (한눈에)

[`domain-overview.md`](../02-product/domain-overview.md) "A2UI Tool 카탈로그 v1" 16개 + 도메인 문서 4개의 추가 Tool을 통합. cross_domain=true 표시.

| Tool ID | 도메인 | cross_domain | min_tier | phase | 출처 |
| --- | --- | --- | --- | --- | --- |
| `pm.search_issues` | pm | false | free | 1 | overview / domain-pm |
| `pm.create_issue` | pm | false | team | 1 | overview / domain-pm |
| `pm.transition_issue` | pm | false | team | 1 | domain-pm |
| `pm.add_comment` | pm | false | team | 1 | domain-pm |
| `pm.get_sprint_summary` | pm | true | team | 1 | overview / domain-pm |
| `pm.identify_blockers` | pm | true | team | 1 | overview / domain-pm |
| `pm.start_sprint` | pm | false | team | 1 | domain-pm |
| `pm.end_sprint` | pm | false | team | 1 | domain-pm |
| `pm.trigger_import` | pm | false | team | 1 (Notion 2) | domain-pm |
| `pm.generate_release_note` | pm | true | business | 2 | domain-pm |
| `comms.search_messages` | comms | false | free | 1 | overview / domain-comms |
| `comms.post_message` | comms | false | team | 1 | domain-comms |
| `comms.summarize_channel` | comms | true | team (cross: business) | 2 | overview / domain-comms |
| `comms.extract_decisions` | comms | true | **business** | 2 | overview (도메인 횡단 핵심) |
| `comms.confirm_decision` | comms | false | team | 2 | domain-comms |
| `comms.message_to_issue` | comms→pm | true | team | 2 | overview / domain-comms |
| `comms.summarize_huddle` | comms | true | team (cross: business) | 2 | domain-comms |
| `comms.list_unread_mentions` | comms | false | free | 1 | domain-comms |
| `comms.create_channel` | comms | false | team | 1 | domain-comms |
| `hr.get_member_context` | hr | true | business | 2 | overview / domain-hr |
| `hr.list_onboarding` | hr | true | business | 2 | overview / domain-hr |
| `hr.summarize_one_on_ones` | hr | true | business | 2 | domain-hr (privacy: manager_visible) |
| `hr.draft_offboarding` | hr | true | business (HR Admin) | 2 | domain-hr |
| `hr.check_labor_compliance` | hr | true | business | 3 | domain-hr |
| `hr.list_evaluation_progress` | hr | true | business | 3 | domain-hr |
| `hr.draft_one_on_one_agenda` | hr | true | business | 3 | domain-hr |
| `hr.list_pending_labor_reviews` | hr | true | business | 3 | domain-hr |
| `hr.get_org_chart` | hr | false | team | 2 | domain-hr |
| `documents.list_pending_review` | documents | true | business | 2 | overview / domain-documents |
| `documents.generate_from_template` | documents | true | business | 2 | domain-documents |
| `documents.summarize_instance` | documents | true | business | 2 | domain-documents |
| `documents.generate_report` | documents | true | business | 2 | domain-documents (COO-5) |
| `documents.request_signature` | documents | true | business (simple) / **enterprise** (KISA) | 3 / 4 | overview / domain-documents |
| `documents.search_archive` | documents | true | business | 2 | domain-documents |
| `documents.check_retention_due` | documents | true | business | 3 | domain-documents |
| `documents.file_eztax` | documents | true | **enterprise** | 4 | domain-documents (ACV 1억원+) |
| `a2ui.cross_domain_query` | a2ui | true | **business** | 2 | overview / 본 문서 |

**총 38개 Tool** (Phase 1: 9 / Phase 2 추가: 18 / Phase 3 추가: 8 / Phase 4 추가: 3). 도메인 문서 4개 갱신 시 본 표 동기 의무.

---

## LangGraph Supervisor 흐름

### 현재 supervisor 구조 (Phase 0-1)

CLAUDE.md `server/src/app/agent/graphs/supervisor_graph.py` 의 현재 워커:

| 워커 | 역할 | 상태 |
| --- | --- | --- |
| `meeting_summary` | 회의 요약 (mock 또는 LLM) | Phase 0-1 가동 |
| `blocker_triage` | PM 블로커 분류 | Phase 0-1 가동 |
| `retro_insights` | 스프린트 회고 인사이트 | Phase 0-1 가동 |
| `user_query` | 단일 도메인 자연어 쿼리 | Phase 0-1 가동 |
| `file_analysis` | 파일 분석 (sandbox 적용 대상) | Phase 0-1 가동 |

### Phase 2 추가: `cross_domain_composer` 노드

```
사용자 입력 (Comms 채팅 또는 Cmd+K AI 모드)
        │
        v
+---------------------+
| Router 노드          |
| intent_classify      |
+--------+------------+
         │
   ┌─────┼────────────────┬─────────────────────┐
   │     │                │                     │
   v     v                v                     v
[meeting_   [blocker_     [retro_insights]   [cross_domain_
 summary]    triage]                          composer]   ← Phase 2 추가
                                                  │
                                                  v
                                       +----------+---------+
                                       | 1) Plan: 필요한      |
                                       |    sub-tool 식별    |
                                       | 2) Tool Registry    |
                                       |    조회             |
                                       | 3) 각 sub-tool 호출:|
                                       |    - tier 검증      |
                                       |    - 권한 검증      |
                                       |    - service 호출   |
                                       | 4) 결과 모음        |
                                       | 5) LLM 합성 또는    |
                                       |    결정론적 합성    |
                                       | 6) audit_log + trace|
                                       +---------+----------+
                                                  │
                                                  v
                                           응답 (사용자 + trace)
```

### 호출 흐름 — 예시 (`a2ui.cross_domain_query` Phase 2)

[`domain-overview.md`](../02-product/domain-overview.md) "도메인 횡단 쿼리 — 데이터 흐름 3개" 예시 1을 코드 결정으로 풀어쓰면:

```python
# server/src/app/agent/composers/cross_domain.py (Phase 2 추가)

async def compose(
    *,
    workspace_id: UUID,
    caller_member_id: UUID,
    intent: str,
    context: dict,
    db: AsyncSession,
) -> CrossDomainAnswer:
    # 1. Plan: LLM이 intent에서 필요한 sub-tool 식별
    plan = await llm_factory.get_llm(mode=settings.agent_mode).plan(
        intent=intent,
        available_tools=registry.list_tools(cross_domain=True),
    )
    # plan = [
    #   ("pm.identify_blockers", {"since": last_sprint_start}),
    #   ("hr.summarize_one_on_ones", {"member_id": "M1"}),
    # ]

    # 2. 각 sub-tool 호출 — supervisor가 caller_member_id 강제 주입
    results = []
    trace = []
    for tool_id, args in plan:
        try:
            result = await registry.invoke(
                tool_id=tool_id,
                workspace_id=workspace_id,
                caller_member_id=caller_member_id,   # 강제 주입
                input=args,
                db=db,
            )
            results.append(result)
            trace.append({"tool": tool_id, "outcome": "ok"})
        except (PermissionDenied, TierGated) as e:
            # 권한 누수 차단: 합성 입력에서 제거
            trace.append({"tool": tool_id, "outcome": "denied", "reason": str(e)})
            # 합성 단계 마스킹 시도 X — sub-tool 단계에서 차단

    # 3. 합성 — 거부된 sub-tool 결과는 LLM에 안 보임
    answer = await llm_factory.get_llm(mode=settings.agent_mode).synthesize(
        intent=intent,
        results=results,
    )

    # 4. audit_log
    await audit_log.record(
        workspace_id=workspace_id,
        actor_member_id=caller_member_id,
        action="a2ui.cross_domain_query",
        metadata={"intent": intent, "trace": trace},
    )

    return CrossDomainAnswer(answer=answer, trace=trace)
```

### Trace / Observability

모든 Tool 호출은 **OpenTelemetry span** ([`tech-stack.md`](./tech-stack.md) 위임, 작성 예정):

| span attribute | 값 |
| --- | --- |
| `workspace.id` | UUID |
| `workspace.tier` | free / team / business / enterprise |
| `actor.member_id` | UUID |
| `tool.id` | `pm.identify_blockers` 등 |
| `tool.cross_domain` | true / false |
| `permission.result` | granted / tier_gated / permission_denied |
| `service_fn.duration_ms` | 실행 시간 |
| `llm.mode` | mock / llm / ollama / vllm |
| `llm.tokens_used` | (Phase 2+ 비용 추적) |

합성 결과의 LLM 응답은 `audit_log.metadata.composed_answer_hash` 로 저장 (전문은 Tier별 보관 정책, [`pricing-strategy.md`](../01-market/pricing-strategy.md) Tier 게이팅과 정합).

---

## 권한 전파 (Permission Propagation)

> 이 절이 [`positioning.md`](../00-vision/positioning.md) 차별화 축 2 "도메인 횡단 AI 인터페이스" + 차별화 축 3 "노무사 외부 협업자 모델" 의 **권한 운명**을 결정한다.

### `caller_member_id` 강제 주입

- supervisor가 모든 Tool 호출에 `caller_member_id` 를 명시적으로 전달.
- service 함수 시그니처에서 keyword-only 필수 (위 "시그니처 규칙 #2" 참조).
- 누락 시 service 함수가 즉시 raise (방어 코드).
- **super user 모드 차단**: supervisor 자체에 "system 권한" 같은 우회 모드 금지. system이 호출해야 하는 경우 (예: 스케줄러) 도 명시적 system Member ID + RoleAssignment 부여 → AuditLog 기록.

### 도메인 횡단 권한 누수 차단 (가장 중요한 패턴)

[`domain-overview.md`](../02-product/domain-overview.md) 예시 1: **"지난 스프린트 블로커 멤버 + 그 멤버의 1:1 피드백"**

권한 모델:

- M1이 블로커 → caller (M5)는 M1의 **직속 매니저**인가?
- YES → `hr.summarize_one_on_ones(member_id=M1)` 정상 호출 → keywords 반환
- NO → `hr.summarize_one_on_ones` 가 403 raise → composer가 합성 입력에서 제외

```python
# server/src/app/hr/service.py
async def summarize_one_on_ones(
    *,
    workspace_id: UUID,
    caller_member_id: UUID,
    member_id: UUID,
    time_range: DateRange,
    db: AsyncSession,
) -> SummarizeOneOnOnesOutput:
    # 권한 체크: caller가 member_id의 매니저인가? 본인인가? HR Admin인가?
    target = await Member.get(workspace_id, member_id)
    if not (
        target.manager_member_id == caller_member_id
        or target.id == caller_member_id
        or has_role(caller_member_id, "hr_admin")
    ):
        # 권한 없음 → keywords / themes 도 안 반환 (메타데이터조차 누수 X)
        raise PermissionDenied(tool="hr.summarize_one_on_ones", target=member_id)

    one_on_ones = await OneOnOne.list(member_id=member_id, range=time_range)
    keywords = await llm_summarize_keywords(one_on_ones)  # 원문 노출 X
    return SummarizeOneOnOnesOutput(themes=keywords, action_items=[...])
```

**중요한 패턴 결정**:

- **마스킹은 LLM 합성 입력에서 제거** — 즉 sub-tool 호출이 실패하면 그 결과는 LLM에게 안 보낸다 → LLM이 안 보면 합성에 안 들어감.
- **합성 후 사후 필터는 신뢰 X** — LLM이 일부 유출 가능. 사후 정규식 마스킹은 보조 안전망이지 1차 방어가 아니다.
- 이게 [`domain-hr.md`](../02-product/domain-hr.md) "권한 누수 방지 원칙" 의 구현 표현.

### 외부 협업자 (노무사) 권한 전파

[`domain-hr.md`](../02-product/domain-hr.md) / [`domain-documents.md`](../02-product/domain-documents.md) 노무사 모델의 코드 결정:

- 노무사 `caller_member_id` 는 resource-scoped `RoleAssignment` 만 보유 (예: `resource_type='documents.review'`, `resource_id=D7`).
- 노무사가 도메인 횡단 Tool (`a2ui.cross_domain_query`) 호출 시 → composer가 plan 생성 → 각 sub-tool 호출 시 노무사 권한 검증:
  - `pm.search_issues` → 노무사는 PM 권한 0 → 즉시 raise → 합성 입력에서 제외
  - `documents.list_pending_review(reviewer_role="labor_advisor")` → 노무사 본인 큐만 반환
  - `comms.search_messages` → 노무사가 멤버인 지정 채널만 반환
- 다른 클라이언트사 노무사 가입 워크스페이스로 같은 caller 가 호출해도 `workspace_id` RLS로 격리.

### 권한 회로 차단 (Circuit Breaker)

`server/src/app/common/circuit_breaker.py` (기존 구조 확장):

- Tool 호출 중 권한 위반 발견 (sub-tool 1건이라도 `super_user_bypass` 발견) → 즉시 해당 Tool 전체 정지 + alarm.
- [`domain-overview.md`](../02-product/domain-overview.md) Watch List #6 발동 시 자동 패턴.
- 알람 → 보안 Admin DM (Comms) + Slack #alerts 채널 + PagerDuty (Phase 3+).
- 회로 닫힘 조건: 사후 audit 통과 + 보안 Admin 명시 승인.

### 합성 결과 권한 누수 회귀 테스트 (CI 강제)

cross_domain=true 인 모든 Tool은 `tests/permission_leakage/` 디렉토리에 회귀 테스트 의무:

```python
# tests/permission_leakage/test_cross_domain_one_on_one.py
async def test_non_manager_cannot_see_one_on_one_keywords_via_a2ui():
    # Given: M5는 M3의 매니저가 아니다
    # When: M5가 a2ui.cross_domain_query("M3의 1:1") 호출
    answer = await registry.invoke(
        tool_id="a2ui.cross_domain_query",
        workspace_id=ws.id,
        caller_member_id=M5.id,
        input={"intent": "M3의 최근 1:1 피드백"},
        db=db,
    )
    # Then: keywords 가 응답에 없어야 함
    assert "bandwidth" not in answer.composed_answer
    assert "design review delay" not in answer.composed_answer
    # 그리고 trace에 "denied" 가 기록되어야 함
    assert any(t["outcome"] == "denied" for t in answer.trace)
```

회귀 테스트 1건이라도 실패 시 **즉시 배포 차단**. Phase 2 출시 전 cross_domain Tool 전체에 대해 테스트 의무.

---

## 도메인 횡단 합성 정확도

### Phase 2 종료 조건 (외부 PoC 5/3 통과)

[`phases.md`](../03-roadmap/phases.md) Phase 2 종료 조건의 코드 결정 표현:

- **"정확도"의 정의**: 합성 결과가 도메인 데이터의 사실과 일치하는가 (hallucination 부재) + 사용자가 유용하다고 평가하는가 (정성).
- **측정 방법** ([`metrics.md`](../03-roadmap/metrics.md) 위임, 작성 예정):
  - 합성 결과 → 사실 검증 (annotator 수동 또는 결정론적 sub-tool 비교).
  - PoC 5개사 × 시나리오 N개 (사별 5-10개) → 평균 정확도 임계치 검증.
  - 사용자 인터뷰 (8주 PoC 기간 매주 회수).

### 도메인별 임계치 (참고)

도메인 문서 4개에서 가져온 값들을 한 표로 통합:

| 지표 | Phase 2 임계치 | Phase 3 임계치 | 출처 |
| --- | --- | --- | --- |
| **Decision 추출 정밀도** (Comms) | 70%+ | 80%+ | [`domain-comms.md`](../02-product/domain-comms.md) |
| **Decision 추출 재현율** (Comms) | 50-60% (보수적) | 65%+ | [`domain-comms.md`](../02-product/domain-comms.md) |
| **Decision 추출 오탐률** (Comms) | < 20% | < 15% | [`domain-comms.md`](../02-product/domain-comms.md) |
| **회의 요약 사용자 평가** | 4/5+ ("원본 누락 없음") | 동일 | [`domain-comms.md`](../02-product/domain-comms.md) |
| **합성 응답 hallucination** | < 5% (사실 자동 검증) | < 3% | 본 문서 (가설) |
| **권한 누수 0건** | 절대 임계치 | 절대 임계치 | [`domain-overview.md`](../02-product/domain-overview.md) Watch List #6 |
| **합성 응답 시간 p95** | < 8초 | < 5초 | 본 문서 (가설) |

### 정확도 측정 인프라

- `eval_dataset` 테이블 (sandbox 환경 PoC 5개사 사례 모음, 익명화).
- 각 cross_domain Tool 마다 케이스 10-30개 누적.
- 회귀 테스트: 매 배포에서 eval_dataset 정확도 측정 → 임계치 위반 시 배포 차단.
- 신규 시나리오 추가는 백엔드 + AI 엔지니어 합의.

### "이게 실패하면"

- **Phase 2 PoC 5/3 미통과** → [`product-vision.md`](../00-vision/product-vision.md) Watch List #1 발동 → A2UI 출시 6개월 연기, 데이터 모델 통합 깊이 재점검, 비전 v2 작성.
- **권한 누수 1건이라도** → [`domain-overview.md`](../02-product/domain-overview.md) Watch List #6 → circuit breaker로 Tool 정지 + 사후 audit + 모든 cross_domain Tool 회귀 테스트 재실행.

---

## Agent Mode (mock/llm/ollama/vllm) 스위치 전략

### 4 모드의 역할

| 모드 | 용도 | 환경 | 비용 / 지연 |
| --- | --- | --- | --- |
| `mock` | 결정론적 stub, 테스트, CI 게이트, 데모 데이터 | dev, CI | 0원 / < 10ms |
| `llm` | OpenAI gpt-4o-mini (기본) | prod, alpha, Phase 1-3 표준 | 시트당 월 < 2,000원 (Team) / < 4,000원 (Business) |
| `ollama` | 로컬 Ollama 서버 | enterprise on-prem (Phase 4+) | 0원 (하드웨어 분리) / 1-3초 |
| `vllm` | OpenAI 호환 vLLM 엔드포인트 | enterprise on-prem high-throughput (Phase 4+) | 자체 호스팅 비용 / < 500ms |

### 추상화 계층 (`llm_factory.py`)

```python
# server/src/app/core/llm_factory.py
from enum import Enum
from typing import Protocol

class AgentMode(str, Enum):
    MOCK = "mock"
    LLM = "llm"
    OLLAMA = "ollama"
    VLLM = "vllm"

class BaseLLM(Protocol):
    async def plan(self, *, intent: str, available_tools: list[dict]) -> list[tuple[str, dict]]: ...
    async def synthesize(self, *, intent: str, results: list[dict]) -> str: ...
    async def classify(self, *, text: str, labels: list[str]) -> dict[str, float]: ...

def get_llm(*, mode: AgentMode, model: str | None = None) -> BaseLLM:
    if mode == AgentMode.MOCK:
        return MockLLM()
    if mode == AgentMode.LLM:
        return OpenAILLM(model=model or "gpt-4o-mini")
    if mode == AgentMode.OLLAMA:
        return OllamaLLM(base_url=settings.ollama_url, model=model)
    if mode == AgentMode.VLLM:
        return VLLMLLM(base_url=settings.vllm_url, model=model)
    raise ValueError(mode)
```

### 모드 전환 = `.env` 한 줄

```bash
# dev / CI
CONFLOW_AGENT_MODE=mock

# prod
CONFLOW_AGENT_MODE=llm
OPENAI_API_KEY=sk-...

# enterprise on-prem (Phase 4+)
CONFLOW_AGENT_MODE=vllm
VLLM_URL=https://vllm.internal/v1
```

**일관성 보장**:

- 같은 supervisor / 같은 Tool Registry / 같은 권한 전파 / 같은 audit_log.
- 모드 전환은 호출 인터페이스를 바꾸지 않는다 — 결과 품질만 다름.
- Phase 4 Enterprise 자체 호스팅 옵션은 `vllm` 또는 `ollama` 로 분기.

### 모드별 비용 / 지연 SLO

비용/지연 SLO 상세는 [`tech-stack.md`](./tech-stack.md) 위임. 본 문서는 결정 규칙만:

- mock 모드: CI 결정론적 (같은 입력 → 같은 출력). 외부 API 호출 금지.
- llm 모드: gpt-4o-mini 기본. 다른 OpenAI 모델은 `model=` 명시.
- ollama / vllm: Phase 4 Enterprise 출시 전 PoC 검증 의무 (한국어 품질 + 지연).

### 안티패턴

| 안티패턴 | 결과 | Watch List |
| --- | --- | --- |
| service 함수에 LLM provider 직접 import (예: `from openai import ...`) | llm_factory 우회 — 모드 전환 깨짐 | 본 문서 Watch List #5 |
| mock 모드에서 외부 API 호출 | CI 결정론 깨짐 — fixture로 격리 의무 | 본 문서 Watch List #5 |
| llm 모드에서 mock fallback | 일관성 깨짐 — 실패 시 명시적 raise | 본 문서 Watch List #5 |
| 같은 호출에 모드 다른 두 호출 (예: plan은 llm / synthesize는 mock) | 디버깅 지옥 | 코드 리뷰 차단 |
| Phase 4 전에 ollama/vllm 모드 prod 사용 | 한국어 품질 미검증 | Phase 4 출시 전 PoC 의무 |

---

## Sandbox 격리 (`server/src/app/sandbox/`)

CLAUDE.md "Runtime security for AI agent execution (syscall blocking, path validation)" 의 결정 표현.

### 역할

- AI 에이전트가 **Tool 호출 외 코드 실행** 시 (Phase 3+ Tool calling 확장 시) 격리 실행.
- syscall 차단 / path validation / network egress 제어.
- **A2UI Tool 호출 자체는 sandbox 불필요** — service 함수는 신뢰 코드 (CI 검증, 정적 분석 통과).

### Phase 진화

| Phase | 범위 | 결정 |
| --- | --- | --- |
| Phase 1-2 | `file_analysis` 워커에만 sandbox 적용 (사용자 업로드 파일 분석 — 신뢰 X) | 현재 가동 |
| Phase 3+ | Tool 확장 (예: SQL 실행 도구, 외부 API 호출 Tool) 도입 시 sandbox 강화 | 시점 결정 |
| Phase 4+ | 사용자 정의 Tool 허용 검토 → sandbox 풀 (사용자 코드 격리) | 보류 |

### Sandbox 안 들어가는 것

- service 함수 (신뢰 코드, CI 통과)
- supervisor / composer 노드 (코드)
- LLM 호출 자체 (`llm_factory`)

### Sandbox 들어가는 것

- 사용자 업로드 파일 분석 (Phase 1-2 file_analysis 워커)
- (Phase 3+) 동적 SQL 실행 Tool
- (Phase 4+) 사용자 정의 Tool 실행 (허용 시)

상세 syscall whitelist / network egress 정책은 [`security-compliance.md`](./security-compliance.md) 위임 (작성 예정).

---

## Phase별 출시 범위

[`phases.md`](../03-roadmap/phases.md) 의 A2UI 관련 OKR을 본 문서 관점으로 재정렬.

### Phase 0-1 (2026 Q3 ~ 2027 Q2)

- **A2UI 도메인 횡단은 출시 X**. 기본 워커만 가동 (meeting_summary / blocker_triage / retro_insights / user_query / file_analysis — 모두 mock 또는 단일 도메인 LLM).
- **Tool Registry 골격 합의** (`tool_registry.yaml` v1 스키마 박기).
- **헤드리스 service 함수 시그니처 규칙 5개 강제** (PR 리뷰 + CI ruff 룰).
- **Schema-first CI 검증 가동**.

### Phase 2 (2027 Q3 - 2028 Q2) — A2UI 첫 출시

[`phases.md`](../03-roadmap/phases.md) Phase 2 종료 조건과 정합:

- **A2UI Tool 6-8개 출시** (PM Tool 일부 + Comms Tool 일부 + `a2ui.cross_domain_query` composer).
- **도메인 횡단: PM ↔ Comms** ([`product-vision.md`](../00-vision/product-vision.md) Phase 2 빌드 목표).
- **HR Tool 알파** (`hr.get_member_context`, `hr.list_onboarding`, `hr.summarize_one_on_ones`) — 단, 외부 PoC는 PM↔Comms 중심.
- **외부 PoC 5개사 검증** (8주 PoC × 5사) — Phase 2 종료 조건.
- **권한 전파 회귀 테스트 인프라** 가동.
- **eval_dataset 테이블** + 회귀 잡 (매 배포).

### Phase 3 (2028 Q3 - 2029 Q2) — 3도메인 횡단

- **HR 포함** (1:1 키워드 마스킹 권한 전파 정식).
- **노무사 외부 협업자 권한 전파** ([`domain-hr.md`](../02-product/domain-hr.md) / [`domain-documents.md`](../02-product/domain-documents.md) 모델).
- **`hr.check_labor_compliance`** Tool 출시 — 법령 규칙 엔진, 자문 X.
- **Tool Registry DB 마이그레이션 검토** (사용자 정의 Tool 시점, 보류).
- **A2UI Tool 약 25개 누적**.

### Phase 4 (2029 Q3+) — 4도메인 횡단 + 자체 호스팅

- **Documents 포함** (KISA 서명 / ezTax 컨텍스트).
- **on-prem `ollama` / `vllm` 모드 정식** (Enterprise 자체 호스팅).
- **`documents.file_eztax`**, **`documents.request_signature` (KISA mode)** Enterprise 한정.
- **A2UI 4도메인 풀 횡단** ([`product-vision.md`](../00-vision/product-vision.md) North Star 시나리오).

---

## Watch List (A2UI 차별화 깨짐 신호)

[`domain-overview.md`](../02-product/domain-overview.md) Watch List 8개 중 A2UI 관련 + 본 문서 추가:

| # | 신호 | 액션 |
| --- | --- | --- |
| 1 | Tier 게이팅이 service 함수에 흩어짐 (PR 검출) | 즉시 Tool Registry로 이전 + 정적 분석 룰 추가. [`domain-overview.md`](../02-product/domain-overview.md) Watch List #2 직결. |
| 2 | 권한 우회 (super user 모드 / `caller_member_id=system` 우회) | 회로 차단(circuit breaker)로 Tool 정지 + 사후 audit + 보안 Admin 알람. [`domain-overview.md`](../02-product/domain-overview.md) Watch List #6 직결. |
| 3 | service 함수가 React 컴포넌트 import | 즉시 리팩토링 + ruff 룰 강화. [`domain-overview.md`](../02-product/domain-overview.md) Watch List #5 직결. |
| 4 | LLM 합성 결과의 권한 누수 발견 (회귀 테스트 또는 사후 audit) | sub-tool 단계 권한 강화 + 합성 입력 차단 패턴 재점검 + 사후 audit. |
| 5 | mock 모드에서 외부 API 호출 (CI 결정론 깨짐) | fixture로 격리 + llm_factory 우회 코드 제거. 본 문서 안티패턴 표. |
| 6 | hallucination > 5% (eval_dataset 회귀) | eval_dataset 케이스 추가 + 모델 조정 (gpt-4o-mini → gpt-4o 검토) + Phase 진입 게이트 재검토. |
| 7 | 외부 PoC 5/3 미통과 (Phase 2 종료 시점) | [`product-vision.md`](../00-vision/product-vision.md) Watch List #1 발동 → A2UI 출시 6개월 연기 + 비전 v2. |
| 8 | service_fn 호출에서 `workspace_id` 누락 | 다중 테넌트 격리 위협. 핫픽스 + RLS 정책 강화 + 정적 분석 룰. [`domain-overview.md`](../02-product/domain-overview.md) Watch List #4 직결. |
| 9 | Tool Registry YAML 외 코드에서 Tier 게이팅 검출 | 단일 게이팅 원칙 깨짐. PR revert + 회수. |
| 10 | Agent Mode 전환 시 응답 형식 / Schema 차이 | llm_factory 추상화 누수. mode별 BaseLLM 구현 정렬. |

---

## 의도적 보류 (책임 이전)

다음 결정들은 이 문서에서 **하지 않는다**. Tool Registry / 권한 전파 / Agent Mode 3개를 잠그는 데 필요한 만큼만 정의했다.

| 결정 | 어디로 미루는가 |
| --- | --- |
| LangGraph 워커별 상세 프롬프트 / 모델 선택 | `server/src/app/agent/` 모듈 README + ADR |
| LLM 비용 예측 / Tier별 한도 정밀 시뮬레이션 | [`pricing-strategy.md`](../01-market/pricing-strategy.md) + [`metrics.md`](../03-roadmap/metrics.md) (작성 예정) |
| 벡터 검색 (pgvector) 인덱스 / 임베딩 모델 설계 | [`data-model.md`](./data-model.md) (작성 예정) |
| Sandbox syscall whitelist 상세 / network egress 정책 | [`security-compliance.md`](./security-compliance.md) (작성 예정) |
| Tool Registry 구현 언어 / 저장소 결정 (YAML vs DB) Phase 3 마이그레이션 | 후속 ADR (Phase 2 종료 시점) |
| OpenTelemetry 백엔드 (Jaeger / Tempo / Datadog) 선택 | [`tech-stack.md`](./tech-stack.md) (작성 예정) |
| eval_dataset 케이스 큐레이션 정책 / annotator 운영 | [`metrics.md`](../03-roadmap/metrics.md) (작성 예정) |
| LLM 응답 보존 정책 (Tier별 audit_log 보관) | [`security-compliance.md`](./security-compliance.md) (작성 예정) |
| RLHF / 사용자 피드백 루프 인프라 (Phase 3+) | 후속 ADR (Phase 3 진입 시점) |
| supervisor 노드 추가 시 워크플로우 (planning 모듈) | `server/src/app/agent/` 내부 README |

---

## 관련 문서

- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 축 2 (도메인 횡단 AI), 본 문서의 약속 출처
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — 불변 원칙 3 (A2UI 우선 / 헤드리스), Watch List #1 (A2UI PoC 5/3 미통과), Phase 2-4 빌드 목표
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — 원칙 5 (A2UI Tier 차등 / 도메인 횡단 Business+), Tier별 AI 한도
- [`../02-product/domain-overview.md`](../02-product/domain-overview.md) — A2UI Tool 카탈로그 v1 16개, 도메인 횡단 쿼리 데이터 흐름 3개, Watch List #2·#6
- [`../02-product/domain-pm.md`](../02-product/domain-pm.md) — PM Tool 10개, 시나리오 1 (스프린트 회고 자동 생성)
- [`../02-product/domain-comms.md`](../02-product/domain-comms.md) — Comms Tool 9개, Decision 추출 정밀도 임계치
- [`../02-product/domain-hr.md`](../02-product/domain-hr.md) — HR Tool 9개, 프라이버시 4계층, 노무사 권한 모델
- [`../02-product/domain-documents.md`](../02-product/domain-documents.md) — Documents Tool 8개, 노무사 작업면, 보고서 자동 생성
- [`../03-roadmap/phases.md`](../03-roadmap/phases.md) — Phase 2 A2UI 첫 출시 OKR, 외부 PoC 5/3 통과
- `./data-model.md` — ERD, RLS, pgvector 인덱스 (작성 예정)
- `./tech-stack.md` — OpenTelemetry, Event Bus, WebRTC SFU (작성 예정)
- `./security-compliance.md` — Sandbox syscall 정책, SCIM, SOC2, 권한 모델 구현 (작성 예정)
- `../03-roadmap/metrics.md` — 합성 정확도 / 권한 누수 / 응답 시간 SLO (작성 예정)

---

## 문서 변경 정책

이 문서는 **5개 트리거** 시 갱신한다.

1. **[`domain-overview.md`](../02-product/domain-overview.md) A2UI Tool 카탈로그가 바뀔 때** — overview를 먼저 갱신 후 이 문서 동기 (Tool 카탈로그 표).
2. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음.
3. **Phase 종료 시점** — 다음 Phase의 A2UI 출시 범위 확정과 동시에 갱신.
4. **외부 PoC 5개사 검증 결과 회수 시 (Phase 2 종료 시점)** — 정확도 임계치 / Tier 게이팅 / Tool Registry 스키마 재검토.
5. **Agent Mode 추상화 변경 시 (예: 신규 LLM provider 추가)** — `llm_factory` 인터페이스 갱신과 동시에.

문서 책임자: backend-architect + AI 엔지니어 + 보안. 갱신 시 변경 이력을 본 파일 하단에 추가.

---

## 변경 이력

| 날짜 | 버전 | 변경 | 작성자 |
| --- | --- | --- | --- |
| 2026-06-24 | draft v1 | 최초 작성 — Tool Registry 패턴, 권한 전파 호출 규약, Agent Mode 4종 추상화, Phase 2-4 출시 범위 봉인. domain-overview.md A2UI Tool 카탈로그 16개 + 도메인 문서 4개 추가 Tool 통합 (총 38개). | AI Architect + Backend Architect |
