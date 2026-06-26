---
title: MoSCoW 우선순위 매트릭스
최종 업데이트: 2026-06-24
상태: draft v1
독자: PM, 백엔드, 영업, 경영진
---

# MoSCoW 우선순위 매트릭스

이 문서는 [`jtbd.md`](../01-market/jtbd.md)의 **P0/P1/P2/P3 우선순위**와 [`product-vision.md`](../00-vision/product-vision.md)의 **Phase 0→4 빌드 목표**를 **MoSCoW 프레임(Must / Should / Could / Won't)** 으로 재매핑한 정책 문서다. 도메인 문서 4개의 "Phase별 출시 (P0/P1/P2/P3)" 표가 1차 입력이다.

> 이 문서는 **무엇을 언제 만드는가**가 아니라 **무엇이 출시 필수이고 무엇은 명시적으로 안 하는가**를 박는다. 분기 단위 일정은 [`phases.md`](./phases.md), 측정 정의는 [`metrics.md`](./metrics.md).

---

## 이 문서로 내릴 결정

1. **Phase 1 출시(2027 H1) 비건(non-negotiable) 기능 목록을 박는다** — Must에 들어가지 못한 것은 Phase 1 출시 게이트에서 빠진다.
2. **차별화 4축이 깨지지 않는 최소 Should 집합을 정의한다** — Should가 빠지면 [`positioning.md`](../00-vision/positioning.md)의 차별화 4축 중 하나가 약해진다. 영업이 가져온 경쟁사 매칭 요구는 Should 표 기준으로 응답.
3. **Could과 Won't의 경계를 박는다** — "자원 있으면 좋은 것"(Could, Phase 3-4)과 "영구 안 함"(Won't, 5번째 도메인 등) 사이를 영업·디자인·외부 PoC가 흔들지 못하게 박는다.
4. **재분류 규칙을 정한다** — 어떤 신호(Watch List, JTBD 인터뷰 결과, 매출 데이터)가 Must를 Should로 / Should를 Could로 격하시키는가. 즉흥적 재분류 금지.
5. **도메인별 MoSCoW 분포의 균형을 점검한다** — PM·Comms는 Must 비중이 높고, HR·Documents는 Should 이후가 높다. 이 비대칭이 의도된 것임을 명시.

---

## MoSCoW 정의 (Conflow 식)

표준 MoSCoW를 Conflow의 Phase 모델과 정렬한다.

| 카테고리       | Conflow 식 정의                                                                                                            | Phase 매핑                                  | JTBD P 매핑    |
| -------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | -------------- |
| **Must (M)**   | 출시 비건. 빠지면 Phase 1 정식 출시 불가. 빠지면 차별화 축 1·2의 알파(도메인 통합도 + 도메인 횡단 AI 진입점)가 성립 안 함. | Phase 0-1 P0                                | jtbd.md **P0** |
| **Should (S)** | 빠지면 차별화 4축 중 하나가 약해짐. Phase 2-3 진입 시 점진 도입. Business+ Tier 게이팅 근거.                               | Phase 2 P0 + Phase 2 P1 핵심 + Phase 3 핵심 | jtbd.md **P1** |
| **Could (C)**  | 자원 있으면 좋은 것. ICP-3 (200-2000명 미드마켓) 진입과 Enterprise ACV 1억원+ 정당화 항목. 미달 시 Phase 4+ 보류.          | Phase 3 P1·P2 + Phase 4 P2                  | jtbd.md **P2** |
| **Won't (W)**  | 명시적 안 함. 5번째 도메인 / 비-ICP의 Job / 안티-비전 항목. **영구 안 함**과 **Phase 4+ 보류** 두 종류로 구분.             | 안티-비전 + 비-ICP                          | jtbd.md **P3** |

**핵심 원칙 3가지**

1. **Must는 Phase 1 출시 게이트의 합격선**. 한 개라도 빠지면 Phase 1 출시 안 함.
2. **Should는 Tier 게이팅의 근거**. Should는 Business+ Tier 한정 기능이 다수.
3. **Won't는 영업이 가져와도 거절**. 차별화 4축의 뿌리(단일 데이터 모델 + 4도메인 깊이)를 지킨다.

> Must vs Should의 결정적 차이: **"Phase 1 정식 출시를 못 할 정도인가"** — Yes면 Must, No면 Should.
> Should vs Could의 결정적 차이: **"미드마켓 ACV 1억원+ 정당화에 필수인가"** — Yes면 Should, No면 Could.

---

## Must (M) — 출시 필수 비건

Phase 1 출시(2027 H1)에 빠지면 안 되는 기능. **JTBD P0 + 인프라 P0 + 4도메인 알파 진입점 + 차별화 축 1·4의 뿌리**.

### Must — PM 도메인 (Phase 1 P0)

도메인 문서 [`domain-pm.md`](../02-product/domain-pm.md) Phase 1 P0 표 14개에서 발췌.

| 기능                        | JTBD         | 근거                                                               |
| --------------------------- | ------------ | ------------------------------------------------------------------ |
| Issue CRUD + 상태 전이      | USR-1, COO-1 | PM 도메인 핵심 aggregate. 없으면 도메인 자체 성립 안 함.           |
| Sprint 생성·시작·종료       | COO-1        | "월요일 9시" Big Job #1의 데이터 단위.                             |
| Project (이슈 그룹화)       | USR-1, COO-1 | Linear Project 동등. 50명+ 회사 보드 규율의 최소 단위.             |
| Backlog (정렬 큐)           | USR-1        | Linear 벤치마크.                                                   |
| Board (칸반 + 리스트 뷰)    | USR-1, COO-1 | UX 차별화 1번. 타임라인 뷰는 Should로.                             |
| Label                       | USR-1        | 분류·필터의 기본. 워크스페이스별 custom status를 안 만드는 우회로. |
| Comment + 멘션              | USR-2, USR-3 | 이슈 컨텍스트의 대화. Comms 멘션 라우팅과 통합.                    |
| 키보드 단축키 + Cmd+K 검색  | USR-1, EMO-5 | 불변 원칙 5 (Linear UX 벤치마크). EMO-5 신뢰의 직접 표현.          |
| 실시간 보드 + Optimistic UI | USR-1        | Linear 동등 — 다른 사용자 이동이 즉시 보임.                        |
| **Jira 이슈 임포터**        | Trigger 1, 6 | Atlassian 공략. Habit 해제 무기. 정확도 90% 미만이면 차별화 깨짐.  |
| **Linear 이슈 임포터**      | Trigger 1    | PLG 전환층.                                                        |
| REST API + Webhook 기본     | IT-2         | 통합 / IT 검토 통과.                                               |

### Must — Comms 도메인 (Phase 1 P0)

[`domain-comms.md`](../02-product/domain-comms.md) Phase 1 P0 표 12개에서 발췌.

| 기능                                        | JTBD             | 근거                                                   |
| ------------------------------------------- | ---------------- | ------------------------------------------------------ |
| Channel (public / private / dm)             | USR-3, COO-1     | Comms 핵심 aggregate.                                  |
| Message + Thread + Mention + Reaction       | USR-3            | Slack 동등 UX 최소 기준.                               |
| 검색 (한글 풀텍스트 + 권한 필터)            | USR-3, EMO-5     | Cmd+K 통합 검색의 절반.                                |
| 알림 (멘션 / DM / 스레드 응답)              | USR-3            | 4도메인 통합 알림 채널. "Slack/Jira 양쪽 무시" 방어.   |
| **외부 협업자 채널 모델** (`type=external`) | COO-4, Trigger 2 | Slack Connect 약한 권한 모델 대비 차별화 축 3 알파.    |
| 실시간 전달 (WebSocket)                     | USR-3            | Slack 동등 UX. 기존 `server/src/app/websockets/` 확장. |
| 파일 업로드 / 첨부                          | USR-3            | Phase 1은 자체 스토리지.                               |
| 알림 설정 (채널별 / 키워드)                 | USR-3            | 알림 폭주 방어. EMO-1 (압도되지 않음) 직접 입력.       |

### Must — 공통 인프라 (Phase 1 P0)

[`jtbd.md`](../01-market/jtbd.md) "공통 인프라 (04-architecture가 받아갈 입력)" 표에서 발췌.

| 기능                                            | JTBD                | 근거                                                                         |
| ----------------------------------------------- | ------------------- | ---------------------------------------------------------------------------- |
| **단일 데이터 모델 v1**                         | Big Job #2          | 불변 원칙 1. Phase 0 종료 조건. Phase 1-4 내내 안 깨짐.                      |
| **단일 권한 모델 (Workspace = 단일 테넌트)**    | IT-3, Big Job #2    | 불변 원칙 2. 퇴사 시 4도메인 한 클릭 회수의 기반.                            |
| **SSO (Google / Microsoft)**                    | IT-1                | IT 블로커 우회. **Free Tier 무료 제공** (가격 의도).                         |
| 보안 백서 / 데이터 처리 위치 / 암호화 정책      | IT-2                | 보안 검토 1주일 → 1일. 영업 자료 Must.                                       |
| **단일 청구 (통합 청구서)**                     | COO-6               | CEO-3 ROI 30초 승인의 직접 표현. 도메인별 분리 청구는 영구 금지.             |
| Free / Team / Business 3-Tier 결제 + PLG 온보딩 | (Phase 1 종료 조건) | [`pricing-strategy.md`](../01-market/pricing-strategy.md) Phase 1 출시 조건. |
| 헤드리스 비즈니스 로직 (CLAUDE.md 규칙)         | (불변 원칙 3)       | A2UI 진입 가능성 보장. UI에 비즈니스 로직 박으면 Phase 2 무력화.             |
| 감사로그 기초 (Shared AuditLog)                 | IT-2, IT-4 알파     | SOC2 Type II Phase 3 준비. Phase 1부터 누락 없음.                            |

### Must — Documents/HR 도메인의 Phase 1 "스키마만"

Phase 1 출시 시점에 HR / Documents는 **UI 없음**. 하지만 데이터 모델 v1에 **`Member`, `EmployeeProfile` 골격 스키마**는 포함되어야 Phase 2 알파 진입이 가능. [`product-vision.md`](../00-vision/product-vision.md) Phase 0 결정.

| 기능                                               | 근거                                                         |
| -------------------------------------------------- | ------------------------------------------------------------ |
| `Member` / `EmployeeProfile` 스키마 골격 (UI 없음) | 불변 원칙 1·2. Phase 2 알파 활성화가 "스위치"로 가능해야 함. |
| `Workspace` / `Tenant` / `Role` 권한 골격          | 단일 권한 모델의 기반.                                       |
| 이벤트 버스 (transactional outbox) 기초            | 도메인 간 이벤트 우선 원칙. PM ↔ Comms 결합도 방어.          |

**Must 합산 (Phase 1 출시 비건)**: PM 12개 + Comms 8개 + 공통 인프라 8개 + 스키마 골격 3개 = **약 31개 기능 / 4개 카테고리**.

---

## Should (S) — 빠지면 차별화가 약해지는 것

Phase 2 (2027 H2 – 2028 H1) 진입 시 출시. Phase 3의 핵심 차별화 항목도 포함. **차별화 4축의 강화 항목 + Business Tier 게이팅의 근거**.

### Should — PM 도메인 (Phase 2 P1)

| 기능                                   | JTBD         | 차별화 축             | 근거                                                                              |
| -------------------------------------- | ------------ | --------------------- | --------------------------------------------------------------------------------- |
| **A2UI 도메인 횡단 Tool (PM ↔ Comms)** | COO-2, USR-4 | 축 2 (도메인 횡단 AI) | Phase 2 외부 데모. Business+ Tier 게이트. Watch List #1.                          |
| Milestone (마감 단위)                  | CEO-1        | 축 1                  | 분기 OKR 회고 입력.                                                               |
| Roadmap 뷰 (타임라인)                  | CEO-2        | 축 1                  | Project × Milestone × Sprint 시각화.                                              |
| Notion 페이지 임포터                   | Trigger 1    | 축 4 (마이그레이션 0) | [`competitive-landscape.md`](../00-vision/competitive-landscape.md) Phase 2 약속. |
| Release Note 자동 생성                 | COO-5        | 축 2                  | Sprint 종료 → AI 합성.                                                            |
| 자동화 룰 기초                         | USR-1        | (UX 깊이)             | "라벨 X → 담당자 할당" 수준.                                                      |
| 회고(Retro) 흐름 정식                  | CEO-2        | 축 2                  | Sprint 종료 후 회고. Comms 데이터 인용.                                           |
| 모바일 풀 기능 (iOS/Android)           | USR-6        | (UX 깊이)             | Phase 1은 읽기 전용.                                                              |

### Should — Comms 도메인 (Phase 2 P1)

| 기능                         | JTBD                | 차별화 축 | 근거                                             |
| ---------------------------- | ------------------- | --------- | ------------------------------------------------ |
| **Huddle (음성 + 화면공유)** | USR-5               | 축 1      | Slack Huddle 동등. WebRTC + 외주 SFU.            |
| Huddle 녹음 / 트랜스크립트   | USR-4               | 축 2      | 회의록 자동화의 데이터 소스.                     |
| **Slack 임포터**             | Trigger 1, USR-3    | 축 4      | Habit 해제 무기. 정확도 85%+ 임계치.             |
| **Decision 추출 (A2UI)**     | COO-2, USR-2, USR-4 | 축 2      | **차별화 축 2 정식 데모**. PM ↔ Comms 횡단 핵심. |
| 메시지 → 이슈 변환 (1클릭)   | USR-2, Trigger 5    | 축 1      | Decision 컨펌 워크플로우 출구.                   |
| 채널 요약 (A2UI)             | COO-2, USR-4        | 축 2      | "지난주 이 채널의 결정·블로커 한 줄".            |
| 시맨틱 검색 (pgvector)       | USR-3               | (UX 깊이) | Phase 1 풀텍스트 위에 추가.                      |

### Should — HR 도메인 (Phase 2 알파 P0 + Phase 3 정식 P1)

[`domain-hr.md`](../02-product/domain-hr.md) Phase 2 알파 표 9개 + Phase 3 핵심.

| 기능                                                               | JTBD                     | 차별화 축           | 근거                                                                         |
| ------------------------------------------------------------------ | ------------------------ | ------------------- | ---------------------------------------------------------------------------- |
| EmployeeProfile + OrgUnit + 라이프사이클 (Phase 2)                 | COO-3, USR-7             | 축 1                | HR 알파 진입. Member 1차 소유의 실체.                                        |
| **OnboardingWorkflow + 4도메인 자동 액션** (Phase 2)               | COO-3, Trigger #4        | 축 1                | "신입 4명 반나절" Switch Trigger의 직접 표현. **차별화 축 1의 핵심 데모**.   |
| **OffboardingWorkflow + 도메인 access 회수** (Phase 2)             | IT-3                     | 축 1                | 보안 약속. 4도메인 한 클릭 회수.                                             |
| OneOnOne 노트 (HR-only 권한)                                       | USR-7                    | (UX 깊이)           | 매니저-멤버 공식 기록. DM과 분리.                                            |
| LeaveRequest 기초 (Phase 2)                                        | (COO 운영)               | 축 1                | Flex 수준 정확도는 Phase 3.                                                  |
| **권한·프라이버시 4계층** (Public / Manager / HR / Self) (Phase 2) | IT-4, EMO-6              | 축 1                | 차별화 깨짐 방어. 데이터 노출 1건이 신뢰 붕괴.                               |
| **InsuranceEnrollment (4대 보험)** (Phase 3)                       | COO-4, CEO-4             | **축 3 (KR-first)** | 차별화 축 3 핵심. Flex 1위 영역 정면.                                        |
| **노무사 외부 협업자 모델 + 검토 트레일** (Phase 3)                | COO-4, Trigger #3, EMO-6 | **축 3**            | Switch Trigger #3 ("노무 카톡 유출") 해결. **차별화 축 3의 단일 최대 무기**. |
| 근로기준법 핵심 워크플로우 8개 (Phase 3)                           | COO-4, CEO-4             | 축 3                | 법령 매핑. 워크플로우만 — 법률 자문화 금지.                                  |
| Flex 임포터 (Phase 3)                                              | Trigger #1               | 축 4                | Flex 흡수. 정확도 90% 목표.                                                  |
| SCIM (Phase 3)                                                     | IT-2, IT-4               | 축 1                | 미드마켓 진입 필수.                                                          |
| EvaluationCycle (Phase 3)                                          | CEO-4, USR-7             | 축 1                | Workday 수준 시작점.                                                         |

### Should — Documents 도메인 (Phase 2 P0 + Phase 3 P1)

[`domain-documents.md`](../02-product/domain-documents.md) Phase 2 알파 + Phase 3 정식.

| 기능                                                              | JTBD              | 차별화 축 | 근거                                                          |
| ----------------------------------------------------------------- | ----------------- | --------- | ------------------------------------------------------------- |
| DocumentTemplate + DocumentInstance + ReviewWorkflow (Phase 2)    | COO-4             | 축 1      | Documents 핵심 aggregate.                                     |
| `hr.member.onboarded` 구독 → 근로계약서 자동 인스턴스 (Phase 2)   | COO-3             | 축 1      | HR ↔ Documents 이벤트 정합.                                   |
| RetentionPolicy + 만료 잡 (Phase 2)                               | (compliance)      | 축 3      | 근로기준법 제42조 / 5년 매트릭스. 미준수 = 컴플라이언스 위반. |
| PDF 렌더링 (한글 폰트)                                            | COO-4             | (UX 깊이) | 발급 문서 기본 출력.                                          |
| **노무사 외부 협업자 작업면** (검토 큐 → 코멘트 → 승인) (Phase 3) | COO-4, Trigger #3 | **축 3**  | HR 노무사 모델의 실제 작업면. 차별화 축 3 완성의 절반.        |
| **SignatureRequest (simple — Phase 3)**                           | COO-4             | 축 3      | KISA 없이 클릭 동의 + 도장 이미지. Phase 4 KISA의 사전 단계.  |
| LaborDocument 인터페이스 정식 (HR ↔ Documents) (Phase 3)          | COO-4             | 축 1      | HR 메타 ↔ Documents 실체 동기화 계약.                         |
| `documents.generate_report` Tool (스프린트 보고서)                | COO-5             | 축 2      | COO-5 ("투자사 월간 6시간 → 30분") 직접 표현.                 |

### Should — 공통 인프라 (Phase 3)

| 기능                                           | JTBD         | 차별화 축 | 근거                                                           |
| ---------------------------------------------- | ------------ | --------- | -------------------------------------------------------------- |
| **SOC2 Type II 인증**                          | IT-4         | 축 1      | 미드마켓 진입 필수. Phase 3 종료 조건.                         |
| **SSO/SAML 정식** + 권한 그룹 v2 (RBAC 세분화) | IT-4, COO-7  | 축 1      | 미드마켓 진입.                                                 |
| 외부 협업자 권한 모델 (노무사·세무사·컨설턴트) | COO-4        | **축 3**  | Phase 3 정식. 권한 모델 v2의 핵심.                             |
| A2UI 3도메인 횡단 (PM ↔ Comms ↔ HR)            | CEO-2, CEO-4 | **축 2**  | HR 정식 후 가능. "스프린트 기여도 + 1:1 피드백 + 평가 정합성". |
| 영업 조직 (SDR + AE) 가동                      | (GTM)        | (분배)    | PLG : SLG = 50:50. Enterprise 견적 시작.                       |

**Should 합산**: PM 8개 + Comms 7개 + HR 12개 + Documents 8개 + 공통 5개 = **약 40개 기능**.

---

## Could (C) — 자원 있으면 좋은 것

Phase 3 P2 후반 + Phase 4 P2. **ICP-3 (200-2000명 미드마켓) 진입과 Enterprise ACV 1억원+ 정당화 항목**. 자원 미달 시 다음 Phase로 보류.

### Could — PM 도메인 (Phase 3 P2)

| 기능                                 | JTBD         | 근거                                          |
| ------------------------------------ | ------------ | --------------------------------------------- |
| 미드마켓 RBAC (Project별 세분화)     | IT-4, COO-7  | SCIM·SOC2와 함께.                             |
| OKR / 목표 추적                      | CEO-2        | 미드마켓 요구. Phase 1-2 의도적 보류.         |
| 의존성 그래프 (Dependency)           | USR-1        | Phase 1은 EntityLink로 우회.                  |
| Time tracking                        | (미드마켓)   | 광고대행·외주 미드마켓이 요구. ICP-1은 안 씀. |
| 자동화 룰 풀 기능 (Workflow Builder) | USR-1        | If-this-then-that 풀 빌더.                    |
| Sprint 회고 AI 분석 (3도메인 횡단)   | CEO-2, CEO-4 | HR 정식 출시 후 가능.                         |

### Could — Comms 도메인 (Phase 3 P2)

| 기능                            | JTBD        | 근거                                                     |
| ------------------------------- | ----------- | -------------------------------------------------------- |
| Slack Connect 호환              | Trigger 2   | 외부 워크스페이스 채널 공유.                             |
| 미드마켓 RBAC (채널별 세분화)   | IT-4, COO-7 | SOC2 Type II와 함께.                                     |
| DLP 기초 (메시지 필터 / 차단어) | IT-4        | 미드마켓 컴플라이언스.                                   |
| Huddle 자체 SFU 검토            | (비용)      | Phase 2 외주 비용·지연 데이터로 결정.                    |
| 카카오워크 임포터 (조건부)      | (시장)      | 한국 점유율 조사 후 결정. 보류 — 다음 라운드에서 정밀화. |

### Could — HR/Documents 도메인 (Phase 4 P2)

| 기능                                                 | JTBD  | 근거                                                         |
| ---------------------------------------------------- | ----- | ------------------------------------------------------------ |
| **KISA 전자서명** (자체구축 vs 모두싸인 OEM)         | COO-4 | 차별화 축 3 완성. Phase 3 종료 시점 결정. Watch List #5.     |
| **국세청 ezTax 연동** (원천세 / 연말정산 / 사업소득) | COO-4 | **차별화 축 3 완성. Enterprise ACV 1억원+ 가격 근거**.       |
| PayrollRun (외부 시스템 임포트만, 자체 계산 금지)    | COO-4 | ADP / 노무사 시스템 / Flex 임포트.                           |
| K-ISMS 인증                                          | IT-4  | 미드마켓 + 한국 공공/대기업 진입. Phase 4 종료 조건.         |
| 4대 보험 EDI 자동 신고                               | COO-4 | Phase 3 수동 + 노무사 검토 → Phase 4 EDI. 99% 정확도 임계치. |
| **한국 리전 자체 호스팅 옵션** (Enterprise)          | IT-4  | 데이터 주권. KISA + 한국 리전 결합.                          |
| 평가 사이클 풀 (보상 / 베네핏 연동)                  | CEO-4 | Workday 수준 깊이 완성.                                      |
| 다중 외부 서명자 (counterparty, witness)             | COO-4 | NDA/MSA 외부 회사 서명자.                                    |

### Could — 글로벌 알파 (Phase 4)

| 기능                               | 근거                               |
| ---------------------------------- | ---------------------------------- |
| 일본 / 동남아 한국계 법인 알파     | 5-10개사 대상. **영미권은 Won't**. |
| 다국어 UI (영문 준비, 영업은 한국) | 보류 — 다음 라운드에서 정밀화.     |

**Could 합산**: PM 6개 + Comms 5개 + HR/Documents 8개 + 글로벌 2개 = **약 21개 기능**.

---

## Won't (W) — 명시적으로 안 함

영업이 가져와도 거절. 디자인이 제안해도 스코프 아웃. **영구 안 함**과 **Phase 4+ 보류** 두 종류로 구분.

### Won't — 영구 안 함 (불변 안티-비전)

[`product-vision.md`](../00-vision/product-vision.md) "안 하는 것 (Anti-Vision)" + 도메인 문서 영구 안 함 항목 통합.

| Won't 항목                                                          | 근거                                                                                            |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **5번째 도메인 (CRM / BI / LMS / Expense / Marketing Auto)**        | 불변 원칙. 4도메인 깊이 우선. Salesforce / Metabase / Greenhouse / 스피이큐 / HubSpot 영역.     |
| **자체 급여 계산 엔진 (PayrollCalculation)**                        | HR `PayrollRecord`는 외부 임포트만. ADP / 노무사 시스템 위임.                                   |
| **카테고리 창조 ("통합 워크스페이스 OS" 같은 신조어)**              | Coda/Airtable/Tana 함정.                                                                        |
| **온프레미스 / 프라이빗 클라우드 배포**                             | 단일 데이터 모델 운영 비용 폭증. 미드마켓이 요구해도 거절. (한국 리전 자체 호스팅 옵션과 다름.) |
| **Notion식 일반 협업 문서 / 위키 / 페이지 / 드라이브 / 화이트보드** | Documents는 **정형 문서**만. 일반 협업 페이지는 영구 안 함.                                     |
| **자체 캘린더**                                                     | 4도메인 외부. Google Calendar / Outlook 통합만 (Phase 3+).                                      |
| **이메일 보관 / 통합 (풀 스택)**                                    | Slack/Teams가 안 푼 이유 = SaaS 경제성 부재. Phase 4+ 보류로도 두지만 영구 보류 가능성 명시.    |
| **워크스페이스별 커스텀 status / 워크플로우 빌더 (Jira 동급)**      | "단순함" 약속. Label로 우회 + 자동화 룰 (Phase 3)로 80% 커버.                                   |
| **자체 OCR / 번역 SaaS**                                            | 외부 (Google Document AI) 위임.                                                                 |
| **공공기관 / 금융 (망분리 시장)**                                   | [`icp.md`](../01-market/icp.md) 비-ICP. 망분리 / 조달 18개월.                                   |
| **2030 이전 영미권 직접 진출 / 영어 UI 완성도**                     | 불변 원칙 4 (한국 노무·세무 1순위). 2031+ 검토.                                                 |
| **비IT 산업 (제조·유통·식음료) 진입**                               | Phase 4까지 안 함. IT 워크플로우 깊이가 우리의 우위.                                            |

### Won't — Phase 4+ 보류 (재검토 여지)

영구는 아니지만 Phase 4까지 안 함. Phase 4 종료 시점에 재검토.

| Won't 항목                                 | 재검토 조건                                                       |
| ------------------------------------------ | ----------------------------------------------------------------- |
| 채용 ATS (지원자 추적 / Candidate)         | Greenhouse / Lever 양립. ICP-3 ATS 요구 비율 > 50% 시 재검토.     |
| LMS (학습 / 교육 / 자격증 트래킹)          | 별도 시장. Phase 4+ 보류.                                         |
| 영수증 / 경비 처리 (Expense)               | 5번째 도메인 (스피이큐, ezAdmin) 영역.                            |
| 사원증 / 명함 / 실물 발급                  | 인쇄·실물 영역. ICP-3 대기업 진입 시 검토.                        |
| 계약서 협상 협업 (DocuSign CLM)            | 발급·서명·보존이 Phase 4까지 우선.                                |
| 외부 마켓플레이스 / 플러그인               | Atlassian 마켓플레이스 함정 회피. 4도메인 깊이 완성 전 분산 금지. |
| 외부 챗봇 통합 (Slack App 동급)            | A2UI가 자체 챗봇 대체. Phase 4+ 검토.                             |
| 화상 회의 풀 스택 (Zoom 수준)              | Huddle은 1클릭 음성+화면공유까지. Zoom/Meet 위임.                 |
| 글로벌 노무 (미국 / EU)                    | 한국 미드마켓 ACV 1억원+ 도달 후 재검토.                          |
| 일본 노무                                  | Phase 4 글로벌 알파 시 한정 검토.                                 |
| 글로벌 전자서명 (eIDAS / ESIGN)            | 일본 알파 시 일본만 검토.                                         |
| 한국 공공·금융 망분리 (K-ISMS 망분리 옵션) | IT-5 (P3). Phase 4까지 보류. 그 후 비-ICP.                        |

---

## 도메인별 MoSCoW 분포

한눈에 균형 점검. **PM·Comms는 Must 비중 높음, HR·Documents는 Should 이후 비중 높음** — 이 비대칭이 의도된 것 (Phase 1 Beachhead는 PM+Comms 우선).

| 도메인          | Must             | Should | Could | Won't (영구)                                        | Won't (보류)                                |
| --------------- | ---------------- | ------ | ----- | --------------------------------------------------- | ------------------------------------------- |
| **PM**          | 12               | 8      | 6     | 3 (custom status, 마켓플레이스, 워크플로우 빌더)    | 2 (포트폴리오 뷰, ATS 통합)                 |
| **Comms**       | 8                | 7      | 5     | 4 (캘린더, 이메일 통합, 화상 풀스택, CRM 메시지)    | 2 (외부 챗봇, 카카오워크 임포터)            |
| **HR**          | 1 (스키마)       | 12     | 4     | 3 (PayrollCalc, LMS, 자체 ATS)                      | 4 (글로벌 노무, 일본 노무, ATS, 사원증)     |
| **Documents**   | 0 (Phase 1 없음) | 8      | 4     | 5 (위키, 드라이브, 화이트보드, 자체 OCR, 일반 협업) | 4 (Expense, CLM, 마켓플레이스, 글로벌 서명) |
| **공통 인프라** | 10               | 5      | 2     | 3 (온프레미스, 카테고리 창조, 망분리 자체)          | 1 (공공/금융 망분리)                        |

**관찰**

- **HR/Documents Must = 거의 0**. 의도된 것 — Phase 1은 PM+Comms만으로 출시. 단, **스키마 골격은 Must** (Phase 2 알파 활성화 보장).
- **HR Should = 12개**로 가장 높음. 차별화 축 3 (KR-first)의 무게중심이 HR에 쏠림.
- **공통 인프라 Must = 10개**로 두 번째로 높음. 불변 원칙 1-3 (단일 데이터 모델 + 단일 권한 모델 + 헤드리스)이 인프라에 박힘.
- **Won't (영구) 합산 = 18개**. 의도적 깊이 — 영업/디자인이 흔들기 어려운 두께.

---

## MoSCoW vs Phase 정렬 매트릭스

각 Phase에서 어떤 MoSCoW 카테고리가 출시 단위인가.

| Phase                                            | Must                                                      | Should                                                 | Could                                   | Won't                    |
| ------------------------------------------------ | --------------------------------------------------------- | ------------------------------------------------------ | --------------------------------------- | ------------------------ |
| **Phase 0** (2026 H2)                            | 데이터 모델 v1 / 단일 권한 모델 / 알파 워크스페이스       | -                                                      | -                                       | (스코프 절제 강화)       |
| **Phase 1** (2027 H1) — Beachhead                | PM 12 + Comms 8 + 공통 8 + 스키마 골격 = **약 31개 전체** | -                                                      | -                                       | -                        |
| **Phase 2** (2027 H2–2028 H1) — 통합             | (Phase 1 Must 유지)                                       | **PM 8 + Comms 7 + HR 알파 9 + Documents 4 = 약 28개** | -                                       | -                        |
| **Phase 3** (2028 H2–2029 H1) — 미드마켓         | (유지)                                                    | **HR 정식 12 + Documents 노무사 + 공통 5 = 약 17개**   | PM 6 + Comms 5 = 약 11개                | -                        |
| **Phase 4** (2029 H2–2030) — 한국 노무·세무 완성 | (유지)                                                    | (유지)                                                 | **HR/Documents 8 + 글로벌 2 = 약 10개** | (Won't 보류 항목 재검토) |

**핵심 관찰**

1. **Phase 1은 Must만**. 영업이 Should/Could를 끼우자고 하면 거절 — Phase 1 종료 조건 (유료 워크스페이스 100개, NPS 30+) 위협.
2. **Phase 2 A2UI 도메인 횡단 + HR 알파**가 Should의 가장 큰 덩어리. 차별화 축 2와 축 1의 강화.
3. **Phase 3 Should = HR 정식 + 노무사 외부 협업자**. 차별화 축 3의 본격 진입.
4. **Phase 4 Could = KISA + ezTax**. ACV 1억원+ 정당화. 자원 미달 시 Phase 5로 보류 가능 — Watch List #5 신호.

---

## 재분류 규칙 — 어떤 신호가 카테고리를 바꾸는가

즉흥적 재분류 금지. 다음 신호 발견 시에만 분기 검토.

### Must → Should 격하 (출시 후 불가, Phase 1 전 발견 시만)

| 트리거 신호                                                     | 대응                                           |
| --------------------------------------------------------------- | ---------------------------------------------- |
| Phase 0 인터뷰 5/5 중 4명이 해당 기능을 자발적으로 언급 안 함   | Must 후보를 Should로 격하 검토. JTBD P 재평가. |
| Phase 0 알파 워크스페이스 3개가 해당 기능을 0회 사용 (4주 누적) | Must 정의 재검토. Phase 1 진입 보류 사유.      |
| 차별화 축 1·4 직접 연관 없음 + 경쟁사 동등 기능 부재            | Should로 격하 가능.                            |

### Should → Could 격하

| 트리거 신호                                                                                   | 대응                                                      |
| --------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [`product-vision.md`](../00-vision/product-vision.md) Watch List #1: A2UI PoC 5건 중 3건 실패 | A2UI 횡단 Should 일부 → Could로 격하 + 출시 6개월 연기.   |
| ICP-1 자생 확장률 18개월 누적 30% 미만 (Watch List #2)                                        | HR/Documents Should 일부 → Could로 격하. ICP 분리 재검토. |
| Phase 2 종료 시점에 ICP-1 워크스페이스의 해당 기능 사용률 < 20%                               | Should → Could 격하 검토.                                 |
| Slack 임포터 정확도 85% 미만                                                                  | Should 유지하되 Phase 3로 출시 연기.                      |

### Could → Won't 격하

| 트리거 신호                                                                 | 대응                                                                     |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Phase 3 종료 시점 미드마켓 워크스페이스 < 10개 (Watch List #3)              | Phase 4 KR-first 투자 보류 (KISA/ezTax → Won't 보류로 격하).             |
| KISA 전자서명 자체구축 12개월 이상 지연 + 모두싸인 OEM 거부 (Watch List #5) | Phase 4 축소 → "한국 노무 우위 유지" 모드. KISA Could → Won't 보류.      |
| 경쟁사가 A2UI 동급의 한국어 도메인 횡단 AI 출시 (Watch List #4)             | A2UI 4도메인 횡단 Could 일부 → Won't 보류 + 차별화 축 3·4 무게중심 이동. |

### Won't → Could 승격 (예외 케이스)

영구 안 함은 승격 금지. Phase 4+ 보류만 다음 조건에서 승격 검토.

| 트리거 신호                                             | 대응                                                       |
| ------------------------------------------------------- | ---------------------------------------------------------- |
| ICP-3 ATS 요구 비율 > 50% (영업 견적 6개월 누적)        | 채용 ATS → Could 승격 검토 (Greenhouse 양립 vs 자체 빌드). |
| 비IT 자연 발생 워크스페이스 > 전체 30% & 잔존율 IT 수준 | 비IT 산업 → 산업별 템플릿 Could 승격.                      |
| 한국 미드마켓 ACV 성장률 < 20% 2분기 연속               | 글로벌 알파 시점 6-12개월 앞당김 → 일본 노무 Could 승격.   |

---

## 의도적 보류 / 책임 이전

이 문서가 **다루지 않는** 것 — 다른 문서로 위임.

- **분기 단위 일정 / 마일스톤 / OKR** → [`phases.md`](./phases.md) (TODO).
- **각 기능의 성공 지표 정의 (NPS, 채택률, 정확도 임계치)** → [`metrics.md`](./metrics.md) (TODO).
- **각 Tier에서 어떤 Must/Should가 게이팅되는가 (Free/Team/Business/Enterprise)** → [`pricing-strategy.md`](../01-market/pricing-strategy.md).
- **각 기능의 데이터 모델 / 권한 / 이벤트 스펙** → 도메인 문서 4개 + [`04-architecture/`](../04-architecture/) (TODO).
- **AI / A2UI 도메인 횡단의 합성 정확도 임계치** → [`04-architecture/a2ui-strategy.md`](../04-architecture/) (TODO).

---

## 관련 문서

- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — Phase 0→4 빌드/안빌드/종료 조건, 불변 원칙, Watch List
- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 4축 (Must/Should의 근거)
- [`../00-vision/competitive-landscape.md`](../00-vision/competitive-landscape.md) — 임포터 우선순위 (Must 임포터의 근거)
- [`../01-market/jtbd.md`](../01-market/jtbd.md) — Functional Jobs P0-P3 (MoSCoW의 1차 입력)
- [`../01-market/icp.md`](../01-market/icp.md) — ICP-1/2/3 정의 (Phase별 Must/Should 정렬)
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — Tier 게이팅 (Should의 가격 근거)
- [`../02-product/domain-overview.md`](../02-product/domain-overview.md) — 공유 엔티티, Watch List (Must 강제 항목 후보)
- [`../02-product/domain-pm.md`](../02-product/domain-pm.md) — PM Phase별 P0/P1/P2/P3
- [`../02-product/domain-comms.md`](../02-product/domain-comms.md) — Comms Phase별 P0/P1/P2/P3
- [`../02-product/domain-hr.md`](../02-product/domain-hr.md) — HR Phase 2/3/4 단계 출시
- [`../02-product/domain-documents.md`](../02-product/domain-documents.md) — Documents Phase 2/3/4 단계 출시
- `./phases.md` — Phase 0-4 분기별 OKR (작성 예정)
- `./metrics.md` — Phase별 성공 지표 측정 정의 (작성 예정)

---

## 변경 정책

이 문서는 **3개 트리거** 시 갱신한다.

1. **분기 GTM 리뷰**: 위 "재분류 규칙" 섹션의 신호 점검. 신호 미발견 시 분기 갱신 생략 가능.
2. **Phase 종료**: 각 Phase 종료 시점에 다음 Phase의 Must / Should / Could 재정의. Won't 보류 항목 재검토.
3. **Watch List 신호 발견**: [`product-vision.md`](../00-vision/product-vision.md) Watch List 6개 + [`domain-overview.md`](../02-product/domain-overview.md) Watch List 신호 1개 이상 발견 시 분기 기다리지 않음.

**금지 사항**

- 영업 압력만으로 Must / Should 끼워넣기 — 거절 (영업 자료의 "기능 비교" 요청은 Should 표 + 거절 이유로 응답).
- Won't (영구) 승격 — 금지. Phase 4+ 보류만 위 승격 트리거에서 검토.
- 한 분기에 2회 이상 갱신 — Watch List 신호 외에는 금지 (정책 안정성 보장).

**책임자**: Product Lead (1차) + Backend Architect (도메인 경계·인프라 Must 검증). 갱신 시 변경 이력을 본 파일 하단에 추가.

---

## 변경 이력

| 날짜       | 버전     | 변경 요약                                                       | 작성자       |
| ---------- | -------- | --------------------------------------------------------------- | ------------ |
| 2026-06-24 | draft v1 | 최초 작성. JTBD P0-P3 + 도메인 문서 Phase별 표 → MoSCoW 재매핑. | Product Lead |
