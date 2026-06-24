---
title: Conflow 문서 맵
최종 업데이트: 2026-06-24
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
| `01-market/`       | gtm-strategy.md                                                    | TODO     |
| `02-product/`      | domain-overview / domain-pm / domain-comms / domain-hr / documents | TODO     |
| `03-roadmap/`      | moscow.md / phases.md / metrics.md                                 | TODO     |
| `04-architecture/` | tech-stack / data-model / a2ui-strategy / security-compliance      | TODO     |

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

---

## 다음 작성 순서 (제안)

1. ~~`00-vision/product-vision.md`~~ — 완료 (draft v1)
2. ~~`01-market/jtbd.md`~~ — 완료 (draft v1)
3. ~~`01-market/pricing-strategy.md`~~ — 완료 (draft v1)
4. `02-product/domain-overview.md` — 4개 도메인 통합 그림, 데이터/이벤트 흐름. **다음 차례**
5. 이후 도메인별 상세 (`domain-pm`, `domain-comms`, `domain-hr`, `domain-documents`).
6. `03-roadmap/` — MoSCoW와 Phase 0→4.
7. `04-architecture/` — 기술 스택 결정, 데이터 모델, 컴플라이언스.

---

## 문서 규칙

- **언어**: 한국어
- **메타데이터**: 모든 문서 상단에 `title`, `최종 업데이트`, `상태`, `독자` 프론트매터
- **목적 명시**: 각 문서 첫 섹션은 "이 문서로 내릴 결정"
- **백과사전 금지**: 일반론 나열보다 **의사결정에 직접 도움되는 판단**을 담는다
