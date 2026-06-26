---
title: Conflow 문서 맵
최종 업데이트: 2026-06-26
상태: draft v1 (작성 진행 중)
---

# Conflow 문서

> Conflow는 SMB(10-200명)에서 시작해 미드마켓(200-2000명)으로 확장하는
> **올인원 엔터프라이즈 협업 플랫폼**이다.
> PM(Jira) + Comms(Slack/Huddle) + HR + 문서발급을 한 데이터 모델 위에 통합한다.

이 문서들은 **2026-06-24 엔터프라이즈 피벗** 결정 이후 처음부터 다시 작성되고 있다.
피벗 이전 문서는 [`_archive/2026-06-24-pre-enterprise-pivot/`](./_archive/2026-06-24-pre-enterprise-pivot/) 에 보존.

---

## 작성 상태

| 폴더               | 문서                                                               | 상태     |
| ------------------ | ------------------------------------------------------------------ | -------- |
| `00-vision/`       | [positioning.md](./00-vision/positioning.md)                       | draft v1 |
| `00-vision/`       | [competitive-landscape.md](./00-vision/competitive-landscape.md)   | draft v1 |
| `00-vision/`       | [product-vision.md](./00-vision/product-vision.md)                 | draft v1 |
| `01-market/`       | [icp.md](./01-market/icp.md)                                       | draft v1 |
| `01-market/`       | [jtbd.md](./01-market/jtbd.md)                                     | draft v1 |
| `01-market/`       | [pricing-strategy.md](./01-market/pricing-strategy.md)             | draft v1 |
| `01-market/`       | [gtm-strategy.md](./01-market/gtm-strategy.md)                     | draft v1 |
| `02-product/`      | [domain-overview.md](./02-product/domain-overview.md)              | draft v1 |
| `02-product/`      | [domain-pm.md](./02-product/domain-pm.md)                          | draft v1 |
| `02-product/`      | [domain-comms.md](./02-product/domain-comms.md)                    | draft v1 |
| `02-product/`      | [domain-hr.md](./02-product/domain-hr.md)                          | draft v1 |
| `02-product/`      | [domain-documents.md](./02-product/domain-documents.md)            | draft v1 |
| `03-roadmap/`      | [moscow.md](./03-roadmap/moscow.md)                                | draft v1 |
| `03-roadmap/`      | [phases.md](./03-roadmap/phases.md)                                | draft v1 |
| `03-roadmap/`      | [metrics.md](./03-roadmap/metrics.md)                              | draft v1 |
| `04-architecture/` | [tech-stack.md](./04-architecture/tech-stack.md)                   | draft v1 |
| `04-architecture/` | [data-model.md](./04-architecture/data-model.md)                   | draft v1 |
| `04-architecture/` | [a2ui-strategy.md](./04-architecture/a2ui-strategy.md)             | draft v1 |
| `04-architecture/` | [security-compliance.md](./04-architecture/security-compliance.md) | draft v1 |

---

## 어떤 문서를 언제 보는가

**제품/시장의 큰 그림이 궁금할 때**
→ [`00-vision/positioning.md`](./00-vision/positioning.md) — 한 문장 포지셔닝, 차별화
→ [`00-vision/competitive-landscape.md`](./00-vision/competitive-landscape.md) — Jira/Linear/Slack/Monday/Workday 대비 우리 자리

**누구에게 무엇을 팔지 결정할 때**
→ [`01-market/icp.md`](./01-market/icp.md) — ICP-1(beachhead) → ICP-2 → ICP-3 단계별 정의, 자격 기준, 비-ICP 목록

**5년 뒤 모습과 Phase 0→4 순서가 궁금할 때**
→ [`00-vision/product-vision.md`](./00-vision/product-vision.md) — North Star, Phase별 빌드/안빌드/종료 조건, 불변 원칙, Watch List

**고객이 우리 제품을 "왜" 고용하는지 / 무엇을 빌드 우선순위로 둘지**
→ [`01-market/jtbd.md`](./01-market/jtbd.md) — Big Job 2개, Functional Jobs P0-P3 우선순위, 도메인 매핑표, Switch Trigger

**얼마에 팔지 / 어떤 가격 실수를 피할지**
→ [`01-market/pricing-strategy.md`](./01-market/pricing-strategy.md) — Free/Team/Business/Enterprise 4-Tier, 경쟁사 대비 가격, AI 가격 모델, 안티패턴

**4도메인 경계 / 공유 엔티티 / 이벤트·A2UI Tool 카탈로그가 궁금할 때**
→ [`02-product/domain-overview.md`](./02-product/domain-overview.md) — 도메인 경계, 공유 엔티티 5개, 이벤트 13개, A2UI Tool 16개, 도메인 문서 4개 계약표

**PM 도메인 상세 (이슈/스프린트/보드/임포터/PM A2UI Tool)**
→ [`02-product/domain-pm.md`](./02-product/domain-pm.md) — 핵심 엔티티 7개, Phase 1 P0 14개, A2UI Tool 10개, Jira/Linear/Notion 임포터 우선순위

**Comms 도메인 상세 (채널/메시지/Huddle/Decision 추출/Slack 임포터)**
→ [`02-product/domain-comms.md`](./02-product/domain-comms.md) — 엔티티 8개, Phase 1 P0 12개, A2UI Tool 9개, Decision 추출 정밀도 목표, 외부 협업자 권한 모델

**HR 도메인 상세 (인사·노무·노무사 협업·프라이버시)**
→ [`02-product/domain-hr.md`](./02-product/domain-hr.md) — 엔티티 13개, Phase 2/3/4 단계 출시, A2UI Tool 9개, 노무사 외부 협업자 모델, 프라이버시 4계층, 근로기준법 8 워크플로우

**Documents 도메인 상세 (정형 문서·전자서명·ezTax·노무사 작업면·보존 정책)**
→ [`02-product/domain-documents.md`](./02-product/domain-documents.md) — 엔티티 13개, Phase 2/3/4 단계 출시, A2UI Tool 8개, 노무사 작업면 인터페이스, 보존 정책 매트릭스 12종, KISA/ezTax Phase 4 결정

**무엇이 출시 비건이고 무엇은 명시적으로 안 하는가 / 영업의 끼워넣기를 거절할 근거가 필요할 때**
→ [`03-roadmap/moscow.md`](./03-roadmap/moscow.md) — Must (Phase 1 출시 비건) / Should (차별화 4축 강화) / Could (ICP-3 + ACV 1억원+) / Won't (영구 안 함 + Phase 4+ 보류). JTBD P0-P3 + 도메인 Phase별 표를 MoSCoW로 재매핑

**Phase 0→4 분기 OKR / 일정 / 진입·종료 조건이 궁금할 때**
→ [`03-roadmap/phases.md`](./03-roadmap/phases.md) — 2026 Q3 ~ 2030 Q4 14개 분기 × Objective/KR/의존성/위험 매트릭스, Phase 종료 조건 매트릭스, Phase 간 마이그레이션 결정 시점 (Event Bus / KISA / PLG-SLG), 분기별 리스크 핫리스트

---

## 다음 작성 순서 (제안)

1. ~~`00-vision/product-vision.md`~~ — 완료 (draft v1)
2. ~~`01-market/jtbd.md`~~ — 완료 (draft v1)
3. ~~`01-market/pricing-strategy.md`~~ — 완료 (draft v1)
4. ~~`02-product/domain-overview.md`~~ — 완료 (draft v1)
5. 도메인별 상세 — ~~`domain-pm`~~(완료) / ~~`domain-comms`~~(완료) / ~~`domain-hr`~~(완료) / ~~`domain-documents`~~(완료)
6. `03-roadmap/` — ~~`moscow.md`~~(완료) / ~~`phases.md`~~(완료, 분기 OKR) / `metrics.md` (성공 지표 측정 정의).
7. `04-architecture/` — 기술 스택 결정, 데이터 모델, 컴플라이언스.

---

## 문서 규칙

- **언어**: 한국어
- **메타데이터**: 모든 문서 상단에 `title`, `최종 업데이트`, `상태`, `독자` 프론트매터
- **목적 명시**: 각 문서 첫 섹션은 "이 문서로 내릴 결정"
- **백과사전 금지**: 일반론 나열보다 **의사결정에 직접 도움되는 판단**을 담는다
