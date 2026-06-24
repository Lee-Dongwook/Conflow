---
title: Comms 도메인 상세 (Communication)
최종 업데이트: 2026-06-24
상태: draft v1
독자: PM, 백엔드, 프론트엔드, 디자인, 보안
---

# Comms 도메인 (Communication)

> 이 문서는 [`domain-overview.md`](./domain-overview.md)의 Comms 계약표를 시작점으로, [`jtbd.md`](../01-market/jtbd.md) USR-2/USR-3/USR-5/COO-2와 [`positioning.md`](../00-vision/positioning.md) 차별화 축 1·2를 Comms 도메인의 **결정 카탈로그**로 풀어낸다.
> [`product-vision.md`](../00-vision/product-vision.md) Phase 1의 **PM과 함께 출시되는 기본 도메인**이며, [`competitive-landscape.md`](../00-vision/competitive-landscape.md)에서 **Slack 대안**으로 평가받는 영역이다.
> 데이터 모델 ERD, RLS, WebRTC 인프라 같은 구현 결정은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md), [`04-architecture/tech-stack.md`](../04-architecture/tech-stack.md).

---

## 이 문서로 내릴 결정

1. **Phase 1 P0 범위**: Channel(public/private/dm) / Message(텍스트·파일) / Thread / Mention / 검색(풀텍스트) / Reaction / 알림 / 외부 협업자 채널 모델. **Huddle / Decision 추출 / Slack 임포터는 Phase 2**.
2. **Comms 도메인 엔티티 경계**: Channel / Message / Thread / Reaction / Notification + Phase 2의 Huddle / Decision. "메시징"은 Slack 수준 UX, "결정 추출"은 Conflow 고유 차별화.
3. **`comms.decision.detected` 구현 방식**: 메시지 스트림에서 LLM 분류기 + 휴리스틱으로 액션 아이템 검출 → 작성자/멘션자 1클릭 컨펌 → PM Issue 변환. **자동 변환은 금지** — 컨펌 워크플로우가 차별화 축 2의 신뢰 근거.
4. **외부 협업자(노무사) Comms 노출 방식**: 지정 1-2개 채널만 가시, 다른 채널 검색 0 노출, DM은 워크스페이스 내부 멤버와만. Slack Connect의 약한 권한 모델 대비 강점이자 [`jtbd.md`](../01-market/jtbd.md) Trigger 2·3 약속의 직접 표현.
5. **안 빌드하는 것**: 이메일 보관/통합(영구 보류 가능성), 외부 챗봇 통합(Phase 3+), 자체 캘린더(영구), 화상 회의 풀스택(Phase 4+), CRM/마케팅 자동화 메시지(Anti-Vision).

---

## 도메인 책임

### Comms가 책임지는 것

- **Channel**: public / private / dm / external 4종. 워크스페이스 단위 격리.
- **Message**: 텍스트 / 파일 / 리치 (마크다운 + 멘션 + 링크 프리뷰).
- **Thread**: 메시지 그룹화. Slack 모델 동등.
- **Mention**: `@member`, `@channel`, `@here`. 알림 라우팅의 진입점.
- **Search**: 풀텍스트(Phase 1) + 시맨틱(Phase 2 pgvector). 권한 필터 강제.
- **Huddle (Phase 2)**: 음성 + 화면공유 세션. 녹음·트랜스크립트·요약 옵션.
- **Notification**: 멘션 / DM / 스레드 응답 알림. 4도메인 통합 알림 채널 (다른 도메인이 Comms에 발행).
- **Reaction**: 이모지 반응.
- **Decision (Phase 2 — 차별화 핵심)**: 메시지에서 LLM이 추출한 "결정 / 액션 아이템". PM Issue로 변환 가능.

### Comms가 안 책임지는 것 (경계)

- **이슈 트래킹**: PM 도메인 소유. Comms는 `comms.decision.detected` 발행으로 PM에 후보를 넘긴다.
- **1:1 노트의 _프라이빗 인사 컨텍스트_**: HR 도메인 소유. DM이 비공식 대화라면, 1:1은 HR의 공식 기록이다 — 다른 모델.
- **문서 발급**: Documents 도메인 소유. 채널에 파일 첨부는 Comms이지만, 근로계약서 발급 워크플로우는 Documents.
- **이메일**: **3rd-party 통합만 (Phase 3+), 보관 안 함**. Slack/Teams와 정면 충돌하는 영역만 한다 ([`domain-overview.md`](./domain-overview.md) Comms 비-책임).
- **외부 챗봇 통합**: Phase 3+. Slack 생태계의 수만 개 통합과 정면 대결 안 함.
- **무제한 영구 보관**: Tier별 보관 기간 강제 ([`pricing-strategy.md`](../01-market/pricing-strategy.md): Free 검색 90일 / Team 무제한 검색 / Business 1년 감사 / Enterprise 무제한).

### 경계 모호한 케이스 — 결정

| 케이스                                      | 결정                            | 근거                                                                                                                                                              |
| ------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Slack의 Canvas / Lists 같은 lightweight doc | **Comms 소유**                  | Documents는 정형/법적 문서만 (근로계약서, 재직증명서). 채널 안의 자유 형식 노트는 Comms 안에서 닫는다.                                                            |
| Notion 식 페이지 / 위키                     | **Comms도 Documents도 아님**    | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision "5번째 도메인 확장 금지". Notion 임포터는 PM Issue 또는 Project Description으로 변환 (PM 소유). |
| 보이스 / 음성 메시지                        | **Comms (Huddle 하위)**         | Huddle 인프라의 1:1 비동기 변형으로 본다. Phase 2.                                                                                                                |
| 화상 회의 (Zoom 수준)                       | **안 함 (Phase 4+ 보류)**       | Huddle은 1클릭 음성+화면공유까지. 풀 화상 회의는 Zoom/Meet에 위임.                                                                                                |
| 이슈 코멘트                                 | **PM 소유 (Comment 별도 모델)** | [`domain-pm.md`](./domain-pm.md) 결정. 이슈 컨텍스트 안 코멘트는 검색·필터·알림 라우팅이 이슈 도메인과 강결합.                                                    |
| 회의록 / 액션 아이템 추출                   | **Comms 발행, PM 변환**         | Huddle 종료 시 요약 → Decision 후보 발행 → 사용자 컨펌 → PM Issue 생성.                                                                                           |

---

## 핵심 엔티티

전체 ERD와 인덱스 / RLS는 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 책임·핵심 필드·상태·권한·이벤트.

### `Channel` — 대화 그룹, Comms의 핵심 aggregate

- **책임 한 줄**: 메시지가 흐르는 그릇. 가시성·권한의 단위.
- **핵심 필드**: `id`, `workspace_id`, `name`, `type` (public / private / dm / external), `topic?`, `created_by_member_id`, `is_archived`, `created_at`
- **상태 머신**: `active → archived`. archived는 읽기만 가능 (Phase 2 정식 도입).
- **권한 모델 진입점**:
  - `public`: 워크스페이스 Member 자동 가입 가능. Guest 명시 초대만.
  - `private`: 명시적 초대만. 검색 결과 비노출 (멤버 외).
  - `dm`: 1:1 또는 그룹 DM (최대 9명). 양 당사자만, Admin도 못 봄.
  - `external`: 외부 협업자(노무사 등) 전용 채널. 지정 외부 시트 + 내부 멤버 일부.
- **이벤트 발행**: `comms.channel.created`, `comms.channel.archived`, `comms.member.joined_channel`, `comms.member.left_channel`

### `Message` — 대화의 단위, **결정의 발생 지점**

- **책임 한 줄**: 사용자 1발화. 결정의 발생 지점 → PM Issue 승격 후보.
- **핵심 필드**: `id`, `workspace_id`, `channel_id`, `thread_id?`, `author_member_id`, `body` (마크다운), `attachments[]` (파일 메타), `mentions[]` (Member ID 배열), `decision_flag` (Phase 2 — null/candidate/confirmed/dismissed), `created_at`, `edited_at?`, `deleted_at?` (soft delete)
- **상태 머신**: `posted → edited → deleted` (soft delete, 보존 정책 Tier별).
- **권한 모델 진입점**:
  - 읽기: 해당 Channel 읽기 권한과 동일.
  - 수정: 작성자 본인만 (24시간 이내 — Slack 표준), Admin은 못 함 (DM 프라이버시).
  - 삭제: 작성자 본인 + Workspace Admin (단 DM은 Admin도 못 함).
- **이벤트 발행**: `comms.message.posted`, `comms.message.edited`, `comms.message.deleted`, `comms.mention.created` (mentions가 비어있지 않을 때)

### `Thread` — 메시지 그룹화

- **책임 한 줄**: 같은 토픽의 연쇄 답글. 채널 노이즈 분리.
- **핵심 필드**: `id`, `workspace_id`, `channel_id`, `root_message_id`, `reply_count`, `last_reply_at`, `participant_member_ids[]`
- **상태 머신**: 없음 (root 메시지가 삭제되면 thread도 삭제).
- **권한 모델 진입점**: Channel과 동일.
- **이벤트 발행**: `comms.thread.replied` (reply_count 증가 시)

### `Reaction` — 이모지 반응

- **책임 한 줄**: 메시지에 대한 가벼운 응답.
- **핵심 필드**: `id`, `workspace_id`, `message_id`, `member_id`, `emoji_code`, `created_at`
- **권한 모델 진입점**: Message 읽기 권한과 동일.
- **이벤트 발행**: 없음 (Phase 1 기준 — 알림 발생 안 함). Phase 2에 자동화 룰용 `comms.reaction.added` 검토.

### `Huddle` (Phase 2) — 음성 / 화면공유 세션

- **책임 한 줄**: 채널·DM 안의 1클릭 음성 회의.
- **핵심 필드**: `id`, `workspace_id`, `channel_id`, `started_by_member_id`, `phase` (scheduled / active / ended / archived), `participants[]`, `started_at`, `ended_at?`, `recording_uri?`, `transcript_uri?`, `summary?` (텍스트)
- **상태 머신**: `scheduled → active → ended → archived`. archived는 녹음·요약만 남음.
- **권한 모델 진입점**: Channel 멤버. 녹음 시작은 참가자 1인 이상 동의 (Phase 2 정책).
- **이벤트 발행**: `comms.huddle.started`, `comms.huddle.ended` (summary·action_items 포함)

### `Decision` (Phase 2 — 차별화 핵심)

- **책임 한 줄**: 메시지에서 LLM이 추출한 "결정 / 액션 아이템" 후보. PM Issue로 변환 가능.
- **핵심 필드**: `id`, `workspace_id`, `source_message_id` (또는 `source_huddle_id`), `decision_text`, `participants[]` (Member ID), `confidence` (0.0-1.0), `state` (detected / confirmed / converted_to_issue / dismissed), `confirmed_by_member_id?`, `converted_issue_id?`, `created_at`
- **상태 머신**: `detected → confirmed (작성자/멘션자가 1클릭) → converted_to_issue / dismissed`.
- **권한 모델 진입점**: Source Message 읽기 권한 동일. 컨펌은 작성자 또는 멘션된 사람만.
- **이벤트 발행**: `comms.decision.detected`, `comms.decision.confirmed`, `comms.decision.dismissed`

### `Notification` — 4도메인 통합 알림 채널

- **책임 한 줄**: 멘션 / DM / 스레드 응답 / 다른 도메인 이벤트의 단일 라우팅 큐.
- **핵심 필드**: `id`, `workspace_id`, `recipient_member_id`, `source_type` (comms.mention / pm.comment.mentioned / hr.onboarding_due / ...), `source_id`, `payload` (JSONB), `read_at?`, `dismissed_at?`, `created_at`
- **상태 머신**: `unread → read → dismissed`.
- **권한 모델 진입점**: recipient 본인만.
- **이벤트 발행**: 없음 (Notification은 다른 이벤트의 소비자 출력).

### `SearchIndex` (개념적)

- **책임 한 줄**: 메시지 + Huddle 트랜스크립트의 통합 검색 인덱스. PostgreSQL FTS(Phase 1) + pgvector(Phase 2).
- **핵심 필드** (논리적): `entity_type`, `entity_id`, `workspace_id`, `channel_id?`, `tsvector_kor`, `tsvector_eng`, `embedding (vector, Phase 2)`, `accessible_member_ids[]` (캐시된 권한)
- **권한 모델 진입점**: 쿼리 시점에 caller의 채널 가시성 강제 필터.
- 상세 인덱스 전략은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md).

> **명시적으로 안 만드는 엔티티** (Phase 1-2): `Email`, `Calendar`, `Bot`, `Webhook` (외부 시스템 → Comms 단방향만 Phase 2). 모두 Phase 3+ 또는 영구 보류.

---

## 상태 머신 / 라이프사이클

### Message 라이프사이클

```
   [posted] ──(author edit, 24h)──> [edited]
       │                                │
       │                                v
       └──────(author or admin)──> [deleted (soft)]
                                        │
                                        └─> 보존 정책 (Tier별) 후 hard delete
```

전이 → 이벤트:

- `posted`: `comms.message.posted` + (mentions ≠ ∅이면) `comms.mention.created`
- `edited`: `comms.message.edited`
- `deleted`: `comms.message.deleted`

규칙:

- DM 메시지의 `deleted`는 Admin도 못 실행 (프라이버시).
- 24시간 후 수정 차단 (Slack 동등 정책, Watch List 회귀 방지).
- soft delete 후 보존 기간: Free 30일 / Team 90일 / Business 1년 / Enterprise 정책 협상.

### Huddle 라이프사이클 (Phase 2)

```
   [scheduled (optional)] ──> [active] ──(end)──> [ended] ──> [archived]
                                                     │
                                                     └─> comms.huddle.ended
                                                         (summary, action_items, recording_uri)
```

규칙:

- `ended` 시점에 자동 요약 + 액션 아이템 추출 (LLM). Decision 후보 발행.
- 녹음·트랜스크립트는 참가자 1인 이상 동의 시작 시점부터 (개인정보 정책).
- `archived` 후 트랜스크립트만 검색 인덱스에 남음 (Tier 보존 정책 적용).

### Decision 라이프사이클 (Phase 2 — 차별화 핵심)

```
   [detected] ──(작성자/멘션자 컨펌)──> [confirmed] ──(변환)──> [converted_to_issue]
       │                                    │
       │                                    └──> [dismissed]
       │
       └──(72시간 무응답)──> [auto_dismissed]
```

규칙:

- **자동 변환 금지** — 컨펌이 반드시 사용자 1클릭. 자동 변환은 알림 폭주 + 신뢰 붕괴.
- 72시간 무응답 시 자동 dismiss → 알림 회수 (소음 방지).
- `converted_to_issue` 전이는 `EntityLink(source=comms.message, target=pm.issue, link_kind='derived_from')` 생성과 트랜잭션 단위.

---

## Phase별 출시 (P0/P1/P2/P3)

> 모든 기능은 [`jtbd.md`](../01-market/jtbd.md) Job ID에 매핑. ID 없는 기능은 빌드 안 한다.

### Phase 1 (P0) — Beachhead 정식 출시 (2027 H1)

| 기능                                    | Phase | JTBD ID          | 우선순위 | 근거                                                          |
| --------------------------------------- | ----- | ---------------- | -------- | ------------------------------------------------------------- |
| Channel (public / private / dm)         | 1     | USR-3, COO-1     | P0       | Comms 도메인의 핵심 aggregate. 없으면 도메인 자체 성립 안 함. |
| Message (텍스트 + 파일 + 마크다운)      | 1     | USR-3            | P0       | 메시지 모델은 모든 후속 기능의 기반.                          |
| Thread (스레드 답글)                    | 1     | USR-3            | P0       | Slack 동등. 채널 노이즈 분리 필수.                            |
| Mention (@member / @channel / @here)    | 1     | USR-3            | P0       | 알림 라우팅의 진입점.                                         |
| Reaction (이모지)                       | 1     | USR-3            | P0       | Slack 동등 UX 최소 기준.                                      |
| 검색 (풀텍스트)                         | 1     | USR-3, EMO-5     | P0       | Cmd+K 통합 검색의 절반. 한글 FTS + 권한 필터.                 |
| 알림 (멘션 / DM / 스레드 응답)          | 1     | USR-3            | P0       | 4도메인 통합 알림 채널.                                       |
| 외부 협업자 채널 모델 (`type=external`) | 1     | COO-4, Trigger 2 | P0       | Slack Connect 약한 권한 모델 대비 차별화.                     |
| 실시간 전달 (WebSocket)                 | 1     | USR-3            | P0       | Slack 동등 UX. 기존 `server/src/app/websockets/` 확장.        |
| 파일 업로드 / 첨부                      | 1     | USR-3            | P0       | Phase 1은 자체 스토리지.                                      |
| 멤버 검색 / 채널 검색                   | 1     | USR-3            | P0       | Cmd+K 통합 검색의 일부.                                       |
| 알림 설정 (채널별 / 키워드)             | 1     | USR-3            | P0       | "Slack/Jira 양쪽 모두 무시되는 알림" 방어.                    |

### Phase 2 (P1) — 통합 (2027 H2 – 2028 H1)

| 기능                         | Phase | JTBD ID             | 우선순위 | 근거                                                                                               |
| ---------------------------- | ----- | ------------------- | -------- | -------------------------------------------------------------------------------------------------- |
| **Huddle (음성 + 화면공유)** | 2     | USR-5               | P1       | Slack Huddle 동등. WebRTC + 외주 SFU.                                                              |
| Huddle 녹음 / 트랜스크립트   | 2     | USR-4               | P1       | 회의록 자동화의 데이터 소스.                                                                       |
| **Slack 임포터**             | 2     | Trigger 1, USR-3    | P1       | Habit 해제 무기. [`competitive-landscape.md`](../00-vision/competitive-landscape.md) Phase 2 약속. |
| **Decision 추출 (A2UI)**     | 2     | COO-2, USR-2, USR-4 | P1       | **차별화 축 2의 정식 데모**. PM ↔ Comms 횡단의 핵심.                                               |
| 메시지 → 이슈 변환 (1클릭)   | 2     | USR-2, Trigger 5    | P1       | Decision 컨펌 워크플로우의 출구.                                                                   |
| 채널 요약 (A2UI)             | 2     | COO-2, USR-4        | P1       | "지난주 이 채널의 결정·블로커 한 줄" — 도메인 횡단 데모.                                           |
| Huddle 종료 자동 요약        | 2     | USR-4               | P1       | 회의록 손 정리 제거 (USR-4 직접 표현).                                                             |
| 시맨틱 검색 (pgvector)       | 2     | USR-3               | P1       | Phase 1 풀텍스트 위에 추가. "키워드 없이 의미로" 검색.                                             |
| 메시지 핀 / 북마크           | 2     | USR-3               | P1       | Slack 동등. Phase 1 보류 가능.                                                                     |
| 모바일 풀 기능               | 2     | USR-6               | P1       | Phase 1은 읽기 전용.                                                                               |

### Phase 3 (P2) — 미드마켓 진입 (2028 H2 – 2029 H1)

| 기능                               | Phase | JTBD ID     | 우선순위 | 근거                                                    |
| ---------------------------------- | ----- | ----------- | -------- | ------------------------------------------------------- |
| **Slack Connect 호환**             | 3     | Trigger 2   | P2       | 외부 워크스페이스와의 채널 공유. 미드마켓 진입 시 필요. |
| 미드마켓 RBAC (채널별 세분화 권한) | 3     | IT-4, COO-7 | P2       | SOC2 Type II와 함께.                                    |
| DLP 기초 (메시지 필터 / 차단어)    | 3     | IT-4        | P2       | 미드마켓 컴플라이언스.                                  |
| 채널 아카이브 정책 (자동 / 수동)   | 3     | (운영)      | P2       | 채널 수 폭증 대응.                                      |
| 감사 로그 확장 (Comms 전 동작)     | 3     | IT-4        | P2       | SOC2 Type II 인증 자료.                                 |
| Huddle 자체 SFU 검토               | 3     | (비용)      | P2       | Phase 2 외주 비용·지연 데이터로 결정.                   |
| 카카오워크 임포터 (조건부)         | 3     | (시장)      | P2       | 한국 점유율 조사 후 결정.                               |

### Phase 4+ (P3) — 보류 또는 영구 안 함

| 기능                              | 결정                      | 근거                                                                          |
| --------------------------------- | ------------------------- | ----------------------------------------------------------------------------- |
| 외부 챗봇 통합 (Slack App 동급)   | Phase 3+ 검토             | Slack 생태계 정면 충돌 회피. A2UI가 자체 챗봇 대체.                           |
| 화상 회의 풀 스택 (Zoom 수준)     | Phase 4+                  | Huddle은 1클릭 음성+화면공유까지만. Zoom/Meet 위임.                           |
| 자체 캘린더                       | **영구 안 함**            | 4도메인 외부. Google Calendar / Outlook 통합만 (Phase 3+).                    |
| 이메일 보관 / 통합                | **영구 보류 가능성 명시** | Phase 4+ 검토. Slack/Teams가 풀지 않은 이유 = SaaS 경제성 부재.               |
| CRM / 마케팅 자동화 메시지 트리거 | **Anti-Vision**           | [`product-vision.md`](../00-vision/product-vision.md) 5번째 도메인 확장 금지. |

---

## API 표면 (개념 수준)

> 전체 OpenAPI 3.1 / AsyncAPI 스펙은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 엔드포인트 카탈로그.

### REST 엔드포인트

| 메서드 | 경로                                                        | 권한           | Phase |
| ------ | ----------------------------------------------------------- | -------------- | ----- |
| GET    | `/workspaces/{ws}/channels`                                 | Member+        | 1     |
| POST   | `/workspaces/{ws}/channels`                                 | Member+        | 1     |
| GET    | `/channels/{cid}`                                           | Channel Read   | 1     |
| PATCH  | `/channels/{cid}`                                           | Channel Admin  | 1     |
| POST   | `/channels/{cid}/archive`                                   | Channel Admin  | 1     |
| POST   | `/channels/{cid}/members`                                   | Channel Admin  | 1     |
| DELETE | `/channels/{cid}/members/{mid}`                             | Channel Admin  | 1     |
| GET    | `/channels/{cid}/messages?cursor=...`                       | Channel Read   | 1     |
| POST   | `/channels/{cid}/messages`                                  | Channel Write  | 1     |
| PATCH  | `/messages/{mid}`                                           | 작성자 (24h)   | 1     |
| DELETE | `/messages/{mid}`                                           | 작성자 + Admin | 1     |
| POST   | `/messages/{mid}/reactions`                                 | Channel Read   | 1     |
| GET    | `/messages/{mid}/thread`                                    | Channel Read   | 1     |
| POST   | `/messages/{mid}/thread`                                    | Channel Write  | 1     |
| GET    | `/workspaces/{ws}/dms`                                      | Member+        | 1     |
| POST   | `/workspaces/{ws}/dms`                                      | Member+        | 1     |
| GET    | `/workspaces/{ws}/search?q=...&type=message,channel,member` | Member+        | 1     |
| GET    | `/workspaces/{ws}/notifications`                            | recipient만    | 1     |
| POST   | `/notifications/{nid}/read`                                 | recipient만    | 1     |
| POST   | `/channels/{cid}/huddles`                                   | Channel Member | 2     |
| POST   | `/huddles/{hid}/end`                                        | 참가자         | 2     |
| POST   | `/messages/{mid}/decisions/confirm`                         | 작성자/멘션자  | 2     |
| POST   | `/decisions/{did}/convert_to_issue`                         | 컨펌자         | 2     |
| POST   | `/workspaces/{ws}/importers/slack`                          | Admin          | 2     |

### WebSocket / SSE 이벤트 (실시간 — Phase 1 P0)

| 이벤트                      | 채널                    | 페이로드                                         | Phase |
| --------------------------- | ----------------------- | ------------------------------------------------ | ----- |
| `typing`                    | `ws:{ws}/channel/{cid}` | `member_id`, `started_at`                        | 1     |
| `message.posted`            | `ws:{ws}/channel/{cid}` | `message_id`, `author_id`, `body_preview`        | 1     |
| `message.edited`            | `ws:{ws}/channel/{cid}` | `message_id`, `edited_at`                        | 1     |
| `message.deleted`           | `ws:{ws}/channel/{cid}` | `message_id`                                     | 1     |
| `reaction.added`            | `ws:{ws}/channel/{cid}` | `message_id`, `member_id`, `emoji`               | 1     |
| `presence`                  | `ws:{ws}/global`        | `member_id`, `status` (online/away/offline)      | 1     |
| `huddle.signal`             | `ws:{ws}/huddle/{hid}`  | WebRTC SDP / ICE 교환                            | 2     |
| `huddle.participant_joined` | `ws:{ws}/channel/{cid}` | `huddle_id`, `member_id`                         | 2     |
| `decision.detected`         | `ws:{ws}/member/{mid}`  | `decision_id`, `source_message_id`, `confidence` | 2     |

규칙:

- 모든 WebSocket 메시지에 `trace_id` 포함 (OpenTelemetry 전파).
- 클라이언트 재연결 시 `since=cursor` 지원 — 누락 이벤트 따라잡기.
- Huddle 시그널링은 기존 `server/src/app/websockets/` 모듈 확장 ([CLAUDE.md](../../CLAUDE.md)).

---

## A2UI Tool 카탈로그 (Comms 전용)

> [`domain-overview.md`](./domain-overview.md) A2UI Tool 카탈로그 v1의 Comms Tool 4개를 시작점으로 확장 (9개). 모든 Tool은 헤드리스 service 함수 + Pydantic Input/Output Schema.

| Tool                         | Input Schema 핵심 필드                                                      | Output Schema 핵심 필드                                         | Tier                            | Phase | JTBD ID      |
| ---------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------- | ----- | ------------ |
| `comms.search_messages`      | `workspace_id`, `query`, `channel_ids?`, `time_range?`, `pagination`        | `messages[]`, `total`, `facets`                                 | Free+                           | 1     | USR-3        |
| `comms.post_message`         | `channel_id`, `text`, `mentions[]?`, `thread_id?`, `attachments[]?`         | `message_id`, `event`                                           | Team+                           | 1     | USR-3        |
| `comms.summarize_channel`    | `channel_id`, `time_range`, `style?` (decisions / blockers / digest)        | `summary`, `key_decisions[]`, `action_items[]`                  | Team+ (Business+ for 횡단)      | 2     | COO-2, USR-4 |
| `comms.detect_decisions`     | `workspace_id`, `message_window` (channel_id + time_range 또는 message_ids) | `decisions[]` (with confidence, participants)                   | **Business+**                   | 2     | COO-2, USR-2 |
| `comms.confirm_decision`     | `decision_id`, `confirmed_by_member_id`                                     | `decision`, `event`                                             | Team+                           | 2     | USR-2        |
| `comms.message_to_issue`     | `message_id`, `assignee_id?`, `project_id?`                                 | `issue_id`, `link_id`, `event`                                  | Team+                           | 2     | USR-2        |
| `comms.summarize_huddle`     | `huddle_id`                                                                 | `summary`, `action_items[]`, `participants[]`                   | Team+ (Business+ for 횡단 변환) | 2     | USR-4, USR-5 |
| `comms.list_unread_mentions` | `member_id`, `since?`                                                       | `mentions[]` with `message_id`, `channel_id`, `context_snippet` | Free+                           | 1     | USR-3        |
| `comms.create_channel`       | `workspace_id`, `name`, `type`, `initial_member_ids[]?`, `topic?`           | `channel_id`, `event`                                           | Team+                           | 1     | COO-3        |

### 도메인 횡단 시나리오 — 데이터 흐름 2개

**시나리오 1**: "Slack에서 결정된 것 중 Jira 티켓에 안 옮겨진 것" ([`jtbd.md`](../01-market/jtbd.md) USR-2, [`domain-overview.md`](./domain-overview.md) 예시 3)

```
사용자: "지난주 우리 채널에서 결정된 것 중 이슈로 안 만든 거 있나?"

Agent: a2ui.cross_domain_query(intent="comms decisions not converted to issues")
  └→ comms.detect_decisions(workspace_id, message_window=last_7_days)
       returns: [{message_id: ms1, decision_text: "M3가 onboarding flow 재설계", confidence: 0.87}, ...]
  └→ for each decision:
       check EntityLink(source=comms.message:ms1, link_kind='derived_from', target=pm.issue)
         empty → "미전환" 분류
  └→ pm.search_issues(query=decision_text, time_range=last_7_days) — fuzzy 매칭으로 cross check
  └→ 합성: 미전환 결정 리스트 + "이슈로 만들기" 액션 제안 (각각 comms.message_to_issue 호출 준비)
  Permission check: caller가 각 채널의 멤버인가? 아니면 해당 decision 마스킹.
```

**시나리오 2**: "지난 스프린트 회고 채널 토론 요약 → 회고 노트" ([`jtbd.md`](../01-market/jtbd.md) COO-5, [`domain-pm.md`](./domain-pm.md) 시나리오 1과 정렬)

```
사용자가 회고 채널에서 "/ai 회고 초안" 입력.

Agent:
  └→ pm.get_sprint_summary(sprint_id=current)
       returns: velocity=23, blockers=[{issue_id: I7, blocked_hours: 72, assignee_id: M3}]
  └→ comms.summarize_channel(channel_id=sprint_channel, time_range=sprint_period, style="decisions+blockers")
       returns: key_decisions[], unresolved_threads[]
  └→ comms.detect_decisions(workspace_id, message_window=sprint_period, channel_id=sprint_channel)
       returns: decisions[] (미전환 후보 포함)
  └→ 합성: 회고 마크다운 초안 (PM 스프린트 통계 + Comms 결정·블로커 요약)
  └→ pm.create_retro_note(sprint_id, body) — Phase 2 PM Tool
```

### Tool Registry 게이팅 — Tier 강제

[`domain-overview.md`](./domain-overview.md) 절차 따름:

- `comms.search_messages` / `comms.post_message` 등 단일 도메인 Tool: Free 또는 Team+.
- `comms.detect_decisions` / `comms.summarize_channel` (도메인 횡단 합성으로 들어가는 경우): **Business+ Tier 게이트**.
- 게이트는 `tool_registry.yaml` 한 곳에서만 강제. service 함수 안에 박지 않음 ([`domain-overview.md`](./domain-overview.md) Watch List #2).

---

## Decision 추출 (차별화 핵심)

이 절이 **[`positioning.md`](../00-vision/positioning.md) 차별화 축 2**의 Comms 측 운명을 결정한다. PM ↔ Comms 횡단의 핵심 데모.

### 작동 방식

1. **검출**: 메시지 스트림 (또는 Huddle 트랜스크립트)에서 LLM 분류기 + 휴리스틱이 액션 아이템 후보 검출.
   - LLM 1차 분류 (gpt-4o-mini): "이 메시지는 결정/액션 아이템인가?"
   - 휴리스틱 보강: 동사 패턴 ("하기로 했어요", "~할게요", "TODO:"), 멘션 + 미래시제 결합.
2. **알림**: 검출된 Decision은 `comms.decision.detected` 발행. 작성자 + 멘션된 사람에게 Notification 인박스 표시.
3. **컨펌**: 작성자 또는 멘션자가 **1클릭 "맞아요" / "아니에요"**.
4. **변환**: "맞아요"면 `comms.message_to_issue` 진입 → PM Issue 생성 + EntityLink + `comms.decision.confirmed` 발행.

### 정확도 가설 (Phase 2 출시 시점)

| 지표                             | 목표                 | 측정                                                |
| -------------------------------- | -------------------- | --------------------------------------------------- |
| **Precision (정밀도)**           | > 80%                | 검출된 Decision 중 사용자가 "맞아요"로 컨펌한 비율  |
| **Recall (재현율)**              | 보수적 (50-60% 허용) | 실제 결정 중 검출된 비율. 외부 PoC 5개사 정성 평가. |
| **오탐률 (False Positive Rate)** | < 20%                | 농담 / 일상 대화가 Decision으로 검출되는 비율       |
| **72시간 컨펌율**                | > 40%                | 검출된 Decision이 72시간 내 사용자 응답 받는 비율   |

**재현율보다 정밀도 우선**: 검출 안 한 결정은 사용자가 수동 마킹으로 보완 가능. 오탐은 신뢰 붕괴 직결 — Watch List #2와 직결.

### 오탐 방지 메커니즘

- **농담 / 일상 대화 제외**: LLM 분류기에 채널 type (#random, #social) 컨텍스트 주입. DM은 1차 비활성화 (Phase 2 정책).
- **반복 패턴 감쇄**: 같은 사용자가 같은 시간대에 비슷한 발화 반복 시 confidence 감점.
- **사용자 피드백 루프**: dismissed가 누적된 패턴은 LLM 프롬프트 examples로 환류 (Phase 3 RLHF 검토).

### Tier 게이팅

- **Free / Team**: Decision 추출 자체 **불가**. 수동 마킹만 (`message → 이슈 변환` Tool은 사용 가능).
- **Business**: Decision 추출 풀 (시트당 무제한, 워크스페이스 cap 적용).
- **Enterprise**: 자체 호스팅 LLM 옵션 (vLLM, 한국 리전).

### "이게 실패하면"

- **차별화 축 2 무력화** → [`product-vision.md`](../00-vision/product-vision.md) Watch List 신호 1 (Phase 2 종료 시점 외부 PoC 5건 중 3건 실패)과 직결.
- 그러면 무엇을 한다: A2UI 출시 6개월 연기, Comms 데이터 모델 통합 깊이 재점검. Decision 추출을 수동 마킹 + AI 추천 모드로 격하 검토.

---

## Huddle 전략 (Phase 2)

### 인프라 결정

- **WebRTC 기반 음성 / 화면공유** — 기존 `server/src/app/websockets/` 시그널링 모듈 확장 ([CLAUDE.md](../../CLAUDE.md) Huddle/DM signaling).
- **SFU(Selective Forwarding Unit) 결정**:
  - **Phase 2: 외주 (Daily.co 또는 LiveKit Cloud)** — 가설 v1. 비용·지연 데이터 6개월 수집 후 Phase 3에서 자체 검토.
  - 자체 SFU 검토 트리거: 사용자당 월 Huddle 사용 시간 > 60분 또는 외주 비용이 매출의 5% 초과.
- **녹음 / 트랜스크립트**: 참가자 동의 시작 시점부터. Whisper 또는 vLLM 자체 호스팅 (Enterprise 한국 리전).

### 차별화

- **Huddle 종료 = Decision 추출 트리거** — `comms.huddle.ended` 시 자동 요약 + 액션 아이템 → Decision 후보 발행.
- Slack Huddle은 "그냥 음성"이지만, Conflow Huddle은 **회의 종료 즉시 PM Issue 후보로 변환 가능**한 회의다.
- 이게 차별화 축 2의 두 번째 데모 (USR-4 "회의록 손 정리 안 한다"의 직접 표현).

### 한계

- Phase 2 출시 시점: 동시 참가자 최대 10명 (Slack Huddle 동등).
- Phase 4+까지 풀 화상 회의 (Zoom 동급) 안 함.
- 트랜스크립트 한국어 정확도가 차별화 깨짐 신호 (Watch List).

---

## 임포터 전략

ICP-1·2가 Switch 결정의 마지막 30초에 묻는 질문: **"내 Slack 채널 5년치 검색 히스토리·핀 메시지·스레드를 잃지 않고 옮길 수 있나?"** ([`jtbd.md`](../01-market/jtbd.md) Trigger 1·6).

### Slack 임포터 (Phase 2 필수)

**접근**: Slack Export API (workspace admin 권한 필요). 미드마켓은 Slack Enterprise Grid Discovery API 옵션 (Phase 3).

**매핑 표**:

| Slack 개념                 | Conflow 개념                               | 변환 규칙                                                     |
| -------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| Workspace                  | Workspace                                  | 1:1 매핑 (대상 Conflow Workspace 선택).                       |
| Channel (public / private) | Channel (public / private)                 | 1:1. 채널명 충돌 시 suffix `_imported`.                       |
| Multi-party DM             | DM (그룹 DM, 최대 9명)                     | 1:1. 10명+는 자동 channel 변환 옵션.                          |
| Member                     | Member                                     | **이메일 기반 자동 매핑**. 매칭 안 되면 "Unmatched Users" 큐. |
| Message                    | Message                                    | 1:1. 마크다운 변환 (Slack mrkdwn → Conflow markdown).         |
| Thread                     | Thread                                     | 1:1.                                                          |
| Reaction                   | Reaction                                   | 이모지 코드 매핑 (Slack `:thumbsup:` ↔ Conflow).              |
| File attachment            | Attachment                                 | Phase 2: URL 보존 + 자체 스토리지 비동기 복사.                |
| Pinned message             | Pinned (Phase 2 P1 기능)                   | 1:1.                                                          |
| Bookmark                   | (Phase 3 검토)                             | 채널 북마크는 Phase 1 미지원 — 보류.                          |
| Canvas / Lists             | **1차 텍스트 추출만, 의미 변환 불가 명시** | Conflow에 동등 모델 없음. 채널 안 메시지로 변환.              |
| Workflow Builder           | **무시**                                   | Conflow Phase 3 자동화 룰로 재정의.                           |
| Slack Connect 채널         | (Phase 3)                                  | Phase 2 임포터에서는 무시.                                    |
| Bot / App                  | **무시**                                   | A2UI로 대체. 외부 App은 Phase 3+.                             |

**한계와 우회**:

- 100,000+ 메시지 워크스페이스는 **dry-run 모드** 필수 + 채널 선별 임포트 옵션.
- 권한 매핑: Slack의 channel privacy → Conflow channel type 자동 + Admin 확인.
- 부분 실패 시 재개 가능 (idempotent job, message external_id 추적).

**기대 정확도**: 85%+ (Phase 2 출시 기준). 85% 미만 시 차별화 깨짐 신호 (Watch List).

### Slack Connect 호환 (Phase 3)

- 외부 Slack 워크스페이스 → Conflow 채널 양방향 (Phase 3 검토).
- Slack Connect의 게스트 권한 모델보다 강한 외부 협업자 모델 (자기 채널 외 검색 0)으로 차별화.

### 카카오워크 임포터 (보류 — 데이터)

- 한국 점유율 위협 ([`competitive-landscape.md`](../00-vision/competitive-landscape.md) 신규 진입 위협 3).
- Phase 3 검토. 카카오워크 Export API 한계 + 메시지 모델 차이로 정확도 < 70% 예상 — 시장 데이터 후 결정.

### 임포트 한계 명시 (사용자 UX)

- Slack의 Canvas / Lists / Workflow Builder는 **1차 텍스트만 가져옴**. 의미 변환 불가 사용자에게 명시 표시.
- 임포트 보고서: 채널 X개 / 메시지 Y개 / 변환 실패 Z건 (사유 포함).

---

## 검색 (Phase 1 차별점)

### 인프라

- **Phase 1**: PostgreSQL FTS (`tsvector` 한글 + 영어 분리 인덱스). pg_trgm 보조.
- **Phase 2**: pgvector 추가. 시맨틱 검색 ("키워드 없이 의미로").
- **통합 검색 (Cmd+K)**: Comms 메시지 + PM 이슈 + HR 멤버 검색 통합. [`domain-overview.md`](./domain-overview.md) `EntityLink` 활용으로 관련 항목 탐색.

### 권한 필터 (Phase 1 필수)

- **사용자가 볼 수 없는 채널/DM은 검색 결과에서 제외** — 권한 누수 0건이 차별화 신뢰.
- 구현: 검색 쿼리에 `channel_id IN (caller가 멤버인 channel_ids)` 강제 필터. PostgreSQL RLS와 정합.
- private 채널 / DM 데이터는 인덱스 자체에 권한 메타 캐싱 (검색 속도 + 권한 정합 동시 달성).

### 검색 속도 SLO

| 지표                 | 목표    | 근거                                                        |
| -------------------- | ------- | ----------------------------------------------------------- |
| **p95 응답 시간**    | < 300ms | Linear Cmd+K 동등 ([`jtbd.md`](../01-market/jtbd.md) EMO-5) |
| **p99 응답 시간**    | < 500ms | UX 차별점 임계치 (Watch List)                               |
| **권한 필터 정확도** | 100%    | 권한 누수 0건. 1건 발견 시 즉시 회로 차단.                  |

### 시맨틱 검색 (Phase 2)

- 메시지 임베딩 (text-embedding-3-small 또는 동등).
- 사용자 쿼리 → 임베딩 → pgvector ANN 검색 → 권한 필터 → 결과.
- 풀텍스트 + 시맨틱 하이브리드 (BM25 + cosine).

---

## 권한 모델 적용

[`domain-overview.md`](./domain-overview.md)의 Role 5개가 Comms에서 어떻게 작동하는가.

### 권한 매트릭스

| 동작                           | Owner           | Admin           | Member              | Guest          | External (노무사)                   |
| ------------------------------ | --------------- | --------------- | ------------------- | -------------- | ----------------------------------- |
| public 채널 자동 가시 / 가입   | O               | O               | O                   | X (초대만)     | X                                   |
| private 채널 가시 / 가입       | O               | O               | 초대 시             | 초대 시        | 지정 채널만                         |
| DM 생성 (워크스페이스 내부)    | O               | O               | O                   | 초대 범위만    | **워크스페이스 내부 멤버와만**      |
| DM 가시 (본인 외)              | **X**           | **X**           | X                   | X              | X                                   |
| 채널 메시지 작성               | O               | O               | O                   | 초대 채널만    | 지정 채널만                         |
| 채널 생성 (public)             | O               | O               | O                   | X              | X                                   |
| 채널 생성 (private)            | O               | O               | O                   | X              | X                                   |
| 채널 삭제 / 아카이브           | O               | O               | 작성자 + Admin      | X              | X                                   |
| 검색 범위 (자신이 멤버인 채널) | 전체            | 전체            | 멤버 채널만         | 초대 채널만    | **지정 채널만**                     |
| Huddle 시작 (Phase 2)          | O               | O               | O                   | 초대 채널만    | 지정 채널만                         |
| Decision 컨펌 (Phase 2)        | 작성자 + 멘션자 | 작성자 + 멘션자 | 작성자 + 멘션자     | 동일           | 동일                                |
| A2UI Comms Tool 호출           | O               | O               | Tier 게이트 통과 시 | 초대 범위 안만 | **지정 채널만, Decision 추출 불가** |

**중요 결정**:

- **DM은 항상 양 당사자만 (Admin도 못 봄)** — 프라이버시 약속. Phase 3+에서 감사 모드(인사노무 분쟁 시 Workspace Owner + 양 당사자 동의 + AuditLog 영구 기록 조건) 검토.
- **External(노무사)은 검색 범위가 지정 채널로 한정** — 다른 채널 메시지 1건도 0 노출. [`positioning.md`](../00-vision/positioning.md) 차별화 (Slack Connect 약한 권한 모델 대비).
- **외부 협업자 DM은 워크스페이스 내부 멤버와만** — 외부 ↔ 외부 DM 금지 (정보 누수 방어).

### 권한 누수 케이스와 방어

| 누수 케이스                                                   | 방어                                                                            |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 검색에서 private 채널 메시지 1건 노출                         | 검색 인덱스에 `accessible_member_ids[]` 캐시 + RLS. 매 쿼리마다 contract test.  |
| Decision 추출이 caller가 못 보는 채널 데이터 사용             | A2UI Tool 진입 시 caller_member_id 강제 주입. 각 sub-step에서 채널 가시성 체크. |
| 외부 협업자가 다른 외부 협업자 메시지 검색                    | 외부 협업자 `accessible_channel_ids[]`를 명시적 화이트리스트로만 관리.          |
| Slack 임포트 후 권한 매핑 누락으로 private 채널이 public이 됨 | 임포터 dry-run 시 권한 매핑 검토 강제 + Admin 승인 후 본 임포트.                |

각 케이스 1건 발생 시 → [`domain-overview.md`](./domain-overview.md) Watch List #4·#8과 직결. circuit breaker로 Tool 정지 + 사후 audit.

---

## 이벤트 발행 / 구독

### Comms가 발행하는 이벤트

| 이벤트                        | Phase | 페이로드 핵심 필드                                                           | 구독 도메인                     |
| ----------------------------- | ----- | ---------------------------------------------------------------------------- | ------------------------------- |
| `comms.message.posted`        | 1     | `message_id`, `channel_id`, `author_id`, `mentions[]`, `thread_id?`          | A2UI, PM (스레드 링크 시)       |
| `comms.message.edited`        | 1     | `message_id`, `edited_at`                                                    | A2UI                            |
| `comms.message.deleted`       | 1     | `message_id`, `deleted_at`                                                   | A2UI, AuditLog                  |
| `comms.thread.replied`        | 1     | `thread_id`, `message_id`, `author_id`                                       | A2UI                            |
| `comms.mention.created`       | 1     | `message_id`, `mentioned_member_ids[]`                                       | Notification (Comms 내부), A2UI |
| `comms.channel.created`       | 1     | `channel_id`, `type`, `created_by`                                           | A2UI, AuditLog                  |
| `comms.channel.archived`      | 3     | `channel_id`, `archived_by`, `policy`                                        | AuditLog                        |
| `comms.member.joined_channel` | 1     | `channel_id`, `member_id`, `invited_by?`                                     | A2UI, AuditLog                  |
| `comms.member.left_channel`   | 1     | `channel_id`, `member_id`                                                    | A2UI                            |
| `comms.huddle.started`        | 2     | `huddle_id`, `channel_id`, `started_by`                                      | A2UI                            |
| `comms.huddle.ended`          | 2     | `huddle_id`, `participants[]`, `duration_sec`, `recording_uri?`, `summary?`  | A2UI, PM (action_items 후보)    |
| `comms.decision.detected`     | 2     | `decision_id`, `message_id`, `decision_text`, `participants[]`, `confidence` | PM (이슈 후보), A2UI            |
| `comms.decision.confirmed`    | 2     | `decision_id`, `confirmed_by_member_id`, `converted_issue_id?`               | PM, A2UI, AuditLog              |

### Comms가 구독하는 이벤트

| 이벤트                       | 발행 도메인 | Comms의 반응                                                     | Phase |
| ---------------------------- | ----------- | ---------------------------------------------------------------- | ----- |
| `pm.issue.created`           | PM          | 해당 Project 매핑 채널에 알림 메시지 게시 (선택, 사용자 설정)    | 1     |
| `pm.issue.blocked`           | PM          | 담당자에게 DM 알림 + Project 채널 알림                           | 1     |
| `pm.issue.resolved`          | PM          | Project 채널 알림 (선택)                                         | 1     |
| `pm.sprint.ended`            | PM          | 회고 채널 자동 메시지 + 회고 트리거 알림                         | 1     |
| `hr.member.onboarded`        | HR          | 입사자 환영 메시지 + 기본 채널 자동 추가 (#general, #onboarding) | 2     |
| `hr.member.offboarded`       | HR          | 해당 멤버의 채널 access 회수 + DM 보존 정책 적용                 | 2     |
| `documents.review.completed` | Documents   | 요청자에게 DM 알림                                               | 2     |

규칙:

- **`pm.*` → Comms 알림은 기본 ON이지만 채널별 끄기 가능** — 알림 폭주 방어 ([`jtbd.md`](../01-market/jtbd.md) USR-3 "Slack/Jira 양쪽 모두 무시되는 알림").
- **`hr.member.offboarded` → 채널 access 회수는 동기 (실시간)** — 보안 약속 ([`jtbd.md`](../01-market/jtbd.md) IT-3 "퇴사 시 한 클릭 회수").
- 이벤트 핸들러는 모두 idempotent ([`domain-overview.md`](./domain-overview.md) 규칙).

---

## 외부 협업자 (노무사) UX

[`jtbd.md`](../01-market/jtbd.md) Trigger 2 / Trigger 3 / EMO-6 / COO-4의 Comms 측 표현. [`positioning.md`](../00-vision/positioning.md) 차별화 (Slack Connect 약한 권한 대비 강점).

### 외부 협업자가 Comms에서 보는 것

- **지정된 1-2개 채널만 가시**. 사이드바에 다른 채널 0 표시.
- **검색 결과: 지정 채널 안 메시지만**. 다른 채널은 검색어가 맞아도 0건 (제목조차 노출 안 함).
- **DM: 워크스페이스 내부 멤버와만**. 외부 ↔ 외부 DM 금지.
- **UI 라벨링**: 사이드바 / 채널 헤더에 "외부 협업자" 명시. 내부 멤버도 외부가 있는 채널에 진입 시 헤더에 "외부 협업자 N명 있음" 배지.

### 초대 / 회수 워크플로우

```
1. Workspace Admin 또는 HR Admin이 외부 협업자 시트 발급
   ([`pricing-strategy.md`](../01-market/pricing-strategy.md): 노무사 외부 시트 무료, Business+).
2. 외부 협업자 이메일 입력 → 초대 링크 발송.
3. 외부 협업자가 가입 후 지정 채널에 자동 추가 (RoleAssignment.resource_type='comms.channel').
4. 외부 협업자 활동은 모두 AuditLog에 기록 (workspace_id + actor + action).
5. 회수: HR Offboarding 또는 Admin이 시트 비활성화 → 모든 채널 access 즉시 회수
   (`hr.member.offboarded` 이벤트 구독).
```

### 외부 협업자 DM 정책

- **내부 멤버 → 외부 협업자 DM**: 허용. 외부가 먼저 시작 가능하나 내부 멤버가 차단 가능.
- **외부 ↔ 외부 DM**: **금지** (정보 누수 방어).
- **외부 협업자 메시지의 보존 기간**: 외부 협업자 시트 비활성화 후 90일 read-only → hard delete (Tier 정책 + GDPR 정렬).

### Slack Connect 대비 차별점

| 측면            | Slack Connect 게스트           | Conflow External                               |
| --------------- | ------------------------------ | ---------------------------------------------- |
| 권한 단위       | 채널 단위                      | 채널 + 검색 + DM 통합 단위                     |
| 다른 채널 노출  | 검색에서 채널명 일부 노출 가능 | **0 노출** (검색 / 사이드바 / 멤버 디렉토리)   |
| 외부 ↔ 외부 DM  | 가능                           | **금지**                                       |
| 회수 워크플로우 | Slack Admin이 채널별 회수      | Conflow Admin 1클릭 또는 HR Offboarding 트리거 |
| 감사 추적       | Slack Audit Log Premium 필요   | 기본 AuditLog에 포함                           |

---

## 차별화 깨짐 신호 (Watch List)

| #   | 신호                                                            | 그러면 무엇을 한다                                                                                                                                    |
| --- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 메시지 전송 → 도착 지연이 Linear/Slack 대비 50% 이상 느림 (p99) | 사용자 페르소나 이탈. 즉시 WebSocket 인프라 성능 스프린트. 불변 원칙 5 위협.                                                                          |
| 2   | Decision 추출 정밀도 < 60% (Phase 2 출시 기준)                  | 차별화 축 2 무력화. [`product-vision.md`](../00-vision/product-vision.md) Watch List #1과 직결. Decision 추출을 수동 마킹 + AI 추천 모드로 격하 검토. |
| 3   | Slack 임포터 정확도 < 85% (메시지·채널·스레드 보존)             | 마이그레이션 동기 좌초. Trigger 1 약속 깨짐. 즉시 매핑 규칙 보강 + 사용자 매핑 UX 강화.                                                               |
| 4   | 외부 협업자 권한 누수 (다른 채널 메시지 1건이라도 노출)         | **신뢰 붕괴 — 즉시 회로 차단**. [`jtbd.md`](../01-market/jtbd.md) Trigger 2·3 약속 깨짐. 외부 협업자 모드 회귀 테스트 추가 + 사후 audit.              |
| 5   | 검색 p95 > 500ms 지속 (1주일 연속)                              | UX 차별점 상실. EMO-5 약속 위협. 인덱스 / 쿼리 최적화 스프린트.                                                                                       |
| 6   | DM이 Admin에게 노출되는 케이스 발생 (감사 모드 외)              | 프라이버시 약속 무너짐. 즉시 핫픽스 + 데이터 격리 점검.                                                                                               |
| 7   | Huddle 한국어 트랜스크립트 정확도 < 80%                         | USR-4 약속 깨짐. Whisper 한국어 fine-tune 검토 또는 LLM 변경.                                                                                         |
| 8   | Comms service 함수가 React 컴포넌트 import                      | 헤드리스 원칙 깨짐. A2UI Tool 등록 불가능. 즉시 리팩토링.                                                                                             |
| 9   | Comms가 PM 테이블 또는 HR 테이블 직접 JOIN                      | 도메인 경계 침식. [`domain-overview.md`](./domain-overview.md) Watch List #1과 직결. `EntityLink` + 이벤트로 강제 리팩토링.                           |
| 10  | Decision detection이 농담/일상 대화에서 오탐 > 30%              | 신뢰 붕괴 직전. LLM 프롬프트 튜닝 + 채널 type 컨텍스트 강화.                                                                                          |

---

## 의도적 보류 (Open Decisions)

명시적으로 **안 한다** 또는 **누가 묻기 전에 확정한** 결정들.

| 결정                                                 | 시점                                                                             | 근거                                                                           |
| ---------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| 이메일 보관 / 통합 (Comms 안에서)                    | **Phase 4+ 또는 영구 보류**                                                      | Slack/Teams가 풀지 않은 이유 = SaaS 경제성 부재. Conflow도 안 한다.            |
| 외부 챗봇 통합 (Slack App 동급)                      | Phase 3+로 미룸                                                                  | Slack 생태계 정면 충돌 회피. A2UI가 자체 챗봇 대체.                            |
| 화상 회의 풀 스택 (Zoom 동급)                        | Phase 4+로 미룸                                                                  | Huddle은 1클릭 음성+화면공유까지. Zoom/Meet 위임.                              |
| 자체 캘린더                                          | **영구 안 함**                                                                   | 4도메인 외부. Google Calendar / Outlook 통합만 (Phase 3+).                     |
| CRM / 마케팅 자동화 메시지 트리거                    | **영구 안 함 (Anti-Vision)**                                                     | [`product-vision.md`](../00-vision/product-vision.md) 5번째 도메인 확장 금지.  |
| 무제한 메시지 영구 보관 (전 Tier)                    | Tier별 정책 유지                                                                 | [`pricing-strategy.md`](../01-market/pricing-strategy.md) Tier 게이팅.         |
| Huddle 자체 SFU 구축                                 | Phase 2 외주, Phase 3+ 검토                                                      | 비용·지연 데이터로 결정.                                                       |
| Slack Workflow Builder 동등 자동화                   | Phase 3 자동화 룰로 우회                                                         | Linear 벤치마크와 충돌.                                                        |
| 카카오워크 임포터                                    | Phase 3 검토                                                                     | 한국 시장 점유율 조사 후 결정.                                                 |
| DM 감사 모드 (Admin 조회)                            | Phase 3+ 정책                                                                    | 인사노무 분쟁 시 양 당사자 동의 + AuditLog 영구 기록 조건.                     |
| Phase 1 Huddle                                       | Phase 2로 미룸                                                                   | [`product-vision.md`](../00-vision/product-vision.md) Phase 1 Comms 기본 약속. |
| 모바일 풀 기능                                       | Phase 2                                                                          | Phase 1은 읽기 전용.                                                           |
| 메시지 / Huddle ERD / RLS / 인덱스 / 샤딩 SQL        | [`04-architecture/data-model.md`](../04-architecture/data-model.md)로 위임       |
| WebRTC SFU 인프라 선택 (Daily.co vs LiveKit vs 자체) | [`04-architecture/tech-stack.md`](../04-architecture/tech-stack.md)로 위임       |
| Decision 추출 LLM 프롬프트 / 분류기 구현             | [`04-architecture/a2ui-strategy.md`](../04-architecture/a2ui-strategy.md)로 위임 |

---

## 관련 문서

- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 축 1(도메인 통합도)·축 2(도메인 횡단 AI), Slack 공략 메시지
- [`../00-vision/competitive-landscape.md`](../00-vision/competitive-landscape.md) — Slack 임포터 Phase 2 / Slack Connect Phase 3 약속, 카카오워크 위협
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — Phase 1 Comms 기본, Phase 2 Huddle + A2UI, 불변 원칙 3(헤드리스)
- [`../01-market/jtbd.md`](../01-market/jtbd.md) — Big Job #1, USR-2/3/4/5, Switch Trigger 2·3 (이 문서의 시작점)
- [`../01-market/icp.md`](../01-market/icp.md) — ICP-1 사용자 페르소나 (Slack 속도 기준)
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — Free/Team/Business Tier 게이팅, 노무사 외부 시트 무료
- [`./domain-overview.md`](./domain-overview.md) — 4도메인 경계, 공유 엔티티, A2UI Tool 카탈로그 v1 (이 문서의 Comms 계약표가 시작점)
- [`./domain-pm.md`](./domain-pm.md) — PM ↔ Comms 횡단의 반대편 (메시지 → 이슈 변환, 회고 자동 생성)
- `./domain-hr.md` — HR 도메인 (입퇴사 시 채널 자동 추가/회수의 발행자, 작성 예정)
- `./domain-documents.md` — Documents 도메인 (작성 예정)
- `../04-architecture/data-model.md` — Channel / Message / Huddle ERD, RLS, 샤딩 (작성 예정)
- `../04-architecture/a2ui-strategy.md` — Decision 추출 LLM 구현, Tool Registry 등록 (작성 예정)
- `../04-architecture/tech-stack.md` — WebRTC SFU, WebSocket 인프라 (작성 예정)
- `../03-roadmap/phases.md` — Phase 1-2 Comms 분기 OKR (작성 예정)
- `../03-roadmap/metrics.md` — Decision 정밀도, 검색 속도, Slack 임포터 정확도 SLO (작성 예정)

---

## 문서 변경 정책

이 문서는 **4개 트리거** 시 갱신한다.

1. **[`domain-overview.md`](./domain-overview.md)의 Comms 계약표가 바뀔 때** — overview를 먼저 갱신 후 이 문서 동기.
2. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음.
3. **Phase 종료 시점** — 다음 Phase의 Comms 출시 범위 확정과 동시에 갱신.
4. **Decision 추출 정밀도 분기 보고** — < 60% 신호 시 모델 / 휴리스틱 / 프롬프트 갱신.

문서 책임자: backend-architect + product lead. 갱신 시 변경 이력을 본 파일 하단에 추가.
