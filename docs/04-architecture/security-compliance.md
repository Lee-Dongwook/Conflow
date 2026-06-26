---
title: 보안 + 컴플라이언스 전략 (SOC2 Type II / K-ISMS / KISA / 노무사 협업)
최종 업데이트: 2026-06-24
상태: draft v1
독자: 보안, 백엔드, HR/노무, 영업, CTO, CISO
---

# 보안 + 컴플라이언스 전략

> 이 문서는 [`positioning.md`](../00-vision/positioning.md) **차별화 축 3 (KR-first 컴플라이언스)** 약속의 **인증·통제 결정 문서**다. SOC2 Type II (Phase 3) → K-ISMS (Phase 4) → KISA 전자서명 (Phase 4)의 인증 일정과 통제 항목, [`domain-hr.md`](../02-product/domain-hr.md) 프라이버시 4계층의 시스템 통제, [`domain-documents.md`](../02-product/domain-documents.md) 보존 정책 매트릭스 12종 + 노무사 작업면의 보안 약속, [`domain-overview.md`](../02-product/domain-overview.md) 단일 권한 모델 / AuditLog / 외부 협업자 모델의 구현 결정을 **하나의 컴플라이언스 통제 표** 위에 봉합한다.

> 이 문서는 [`domain-overview.md`](../02-product/domain-overview.md) "Open Decisions" 중 **권한 모델 구현 / SCIM / SOC2 / K-ISMS / KISA / 외부 협업자 / 데이터 보존 / 한국 리전 / 침해 대응** 9개 결정을 봉인한다. 한국 시장 미드마켓 영업의 1차 자료.

> **draft v1 가설 주의** — SOC2 감사 가동 (Phase 3 진입 시 2028 Q3) 후 v2 갱신. KISA 자체구축 vs 모두싸인 OEM 결정 (2029 Q1-Q2) 시 별도 갱신. 4대 보험 EDI 정확도 가설 (99%+)은 Phase 3 검토 트레일 데이터 후 v2 보정.

---

## 이 문서로 내릴 결정

1. **인증 로드맵 봉인**: SOC2 Type II (2028 Q3 감사 시작 → 2029 Q2 완료) / K-ISMS (2029 Q3 감사 시작 → 2030 Q1 완료) / KISA 전자서명 (자체구축 vs 모두싸인 OEM, 2029 Q3 빌드 시작 → 2030 Q1 정식) / ISO 27001 / GDPR의 분기 일정 + 미달 시 액션. [`phases.md`](../03-roadmap/phases.md) 분기 OKR과 정확히 정합.
2. **단일 권한 모델의 시스템 구현**: PostgreSQL RLS + service 함수 caller_member_id 강제 + A2UI Tool Registry 게이팅의 3중 강제. resource-scoped RoleAssignment로 4도메인 가시성 매트릭스 강제. 도메인별 권한 테이블 영구 금지.
3. **HR 프라이버시 4계층의 시스템 통제**: 컬럼별 `privacy_layer` 메타데이터 + service 함수 권한·계층 매핑 + A2UI sub-tool 권한 상속 — 매니저 권한 없는 호출자는 1:1 노트 *키워드*조차 못 받음. Admin도 1:1 노트 못 봄 (감사 모드 제외).
4. **노무사 외부 협업자 보안 모델**: `members.status='external'` + resource-scoped `role_assignments` + 5초 이내 권한 회수 + 모든 액션 AuditLog `external_collaborator=true`. 한 노무사 = 여러 클라이언트 워크스페이스 동시 가입 (한 사람 = 한 워크스페이스 1회 원칙은 **워크스페이스 단위**).
5. **AuditLog 통합 감사 + 보존 정책 매트릭스 12종**: 단일 `audit_logs` 테이블 (도메인별 audit_* 금지). Tier별 보관 (Team 90일 / Business 1년 / Enterprise 무제한). [`domain-documents.md`](../02-product/domain-documents.md) 보존 매트릭스 12종을 시스템 자동 잡으로 강제. 만료 잡 연속 3회 실패 = 컴플라이언스 위반 직전 신호.
6. **사고 대응 + 한국 PIPA / GDPR 통지 절차**: SEV-1 (cross-tenant leak) / SEV-2 (외부 협업자 권한 누수) / SEV-3 (가용성) / SEV-4 (기능 결함) 4단계 + 한국 PIPA 72시간 KISA 신고 + GDPR Phase 4 일본/동남아 알파에 부분 적용.

---

## 보안 원칙

1. **Defense in depth (5계층)**: 네트워크 (WAF / VPC) → 인증 (Supabase / SSO / SAML / SCIM) → 인가 (RoleAssignment + RLS) → 데이터 (TDE / KMS) → 감사 (AuditLog) 5계층. 한 계층 무너져도 차단 가능해야 함.
2. **Least privilege (최소 권한 + 자동 만료)**: 모든 `RoleAssignment`는 `expires_at` TIMESTAMPTZ (기본 1년). 만료 90일 전 알람. 외부 협업자는 강제 만료 정책 + 1-click 즉시 회수 (5초 이내).
3. **Zero trust 도메인 횡단**: A2UI Tool 호출의 권한 전파 ([`a2ui-strategy.md`](./a2ui-strategy.md) 위임). 각 sub-tool 호출 단계마다 권한 재확인 — 합성 단계에서가 아니라. 메타데이터(키워드 / 요약 / 카운트)조차 누수 안 됨.
4. **개인정보 최소 수집 + 한국 PIPA 정렬**: HR 프라이버시 4계층의 시스템 강제. 의료 정보 (병가 진단서)는 별도 카테고리 + 즉시 delete. 정보주체 삭제 요청 90일 이내 처리.
5. **인증은 시장 진입 게이트**: SOC2 (미드마켓 RFP 통과) / K-ISMS (한국 미드마켓 공공/금융 옵션 + 영업 자료) / KISA (법적 효력 + 노무사 협업 완성). 인증 일정 = 영업 일정.
6. **노무사 외부 협업자는 별도 신뢰 영역**: 워크스페이스 가입 없이 resource-scoped 권한만. 한 노무사 = 여러 클라이언트사 동시 가입 가능. 본인 영역 외 데이터 1건이라도 노출 = 차별화 축 3 무력화 신호 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #8).

---

## 인증 로드맵 (Phase 3-4)

[`phases.md`](../03-roadmap/phases.md) 분기 OKR과 정확히 맞춤. 일정이 흔들리면 phases.md를 먼저 갱신 후 이 문서 동기.

| 인증 / 표준 | 분기 시작 | 분기 완료 | 시장 효과 | 비용 가설 (v1) | metrics.md 위임 |
| --- | --- | --- | --- | --- | --- |
| **SOC2 Type II** | 2028 Q3 (감사 시작) | 2029 Q2 (완료) | 미드마켓 RFP 통과 / Phase 3 종료 조건 ([`phases.md`](../03-roadmap/phases.md)) | 감사 비용 1.5-2.5억원 (1년 감사 사이클) + 통제 자동화 엔지니어링 0.5인년 | 통제 증거 수집률 / 분기 audit 완료율 |
| **K-ISMS 인증** | 2029 Q3 (감사 시작) | 2030 Q1 (완료) | 한국 미드마켓 공공·금융·통신 입찰 가능성 + 영업 자료 차별화 축 3 핵심 | 감사 비용 1.5-2.5억원 + 한국어 통제 문서화 0.3인년 | K-ISMS 통제 매핑률 |
| **KISA 전자서명** | 2029 Q3 (빌드 시작) | 2030 Q1 (정식) | 법적 효력 + 노무사 협업 완성 + Enterprise ACV 1억원+ 근거 | 자체구축 12-18개월 / 8-15억원 vs OEM 4-6개월 / 월 라이센스 + 어댑터 인프라 | KISA 검증 실패율 < 1% |
| **ISO 27001** | 보류 (Phase 5 검토) | - | 글로벌 진출 시 검토 ([`product-vision.md`](../00-vision/product-vision.md) 영미권 보류와 정합) | - | - |
| **GDPR** | Phase 4 (일본 / 동남아 알파 부분 적용) | - | 글로벌 시장 시그널만 — 한국 본부 시장에선 한국 PIPA 우선 | DPO 0.2인년 (Phase 4) | - |

### 인증 일정의 영업 의미

- **2028 Q3 — SOC2 감사 시작**: Phase 3 진입과 동시에 미드마켓 RFP 응찰 시 "감사 가동 중" 시그널.
- **2029 Q2 — SOC2 완료**: Phase 3 종료 조건의 하나 ([`phases.md`](../03-roadmap/phases.md)). 미달 시 Phase 3 종료 1-2분기 지연.
- **2030 Q1 — K-ISMS + KISA 정식**: Phase 4 한국 노무·세무 완성과 동시에 영업 자료 차별화 축 3 4축 모두 "O" 충족.

### 인증 지연 위험 (분기 핫리스트 매핑)

- SOC2 12개월 감사 사이클 초과 → Phase 3 종료 지연 ([`phases.md`](../03-roadmap/phases.md) Phase 3 핫리스트).
- KISA 자체구축 12개월 초과 → [`product-vision.md`](../00-vision/product-vision.md) Watch List #5 발동 → 모두싸인 OEM 폴백 가동.
- K-ISMS 한국어 문서화 지연 → Phase 4 종료 1-2분기 지연.

---

## 인증 (Authentication) + 권한 (Authorization)

### Phase 1-2 — Supabase Auth + 이메일 / Google / MS SSO

- Supabase Auth가 user → `Member` 매핑.
- `members.user_id` ↔ Supabase user (1:1).
- MFA 옵션 (이메일 OTP / TOTP) — Admin은 강제, Member는 권장.
- SSO (Google / Microsoft) 무료 제공 ([`pricing-strategy.md`](../01-market/pricing-strategy.md) Free Tier 의도) — IT 블로커 우회.

### Phase 3 — SSO / SAML 정식 + SCIM

- **SAML 2.0**: Okta / Azure AD / Google Workspace 우선. SP-initiated + IdP-initiated 양방향.
- **SCIM 2.0**: IdP 그룹 변경 → Webhook → `scim_mappings` 테이블 → `RoleAssignment` 자동 갱신.
- `scim_mappings` 데이터 모델 (필드: `id`, `workspace_id`, `idp_group_id`, `role_id`, `resource_type?`, `resource_id?`, `precedence`, `last_synced_at`) — 상세는 [`data-model.md`](./data-model.md) 위임.
- **매핑 충돌 시 정책**: deny by default + Admin 알람 + 수동 해결 요구. 자동 권한 상승 금지.
- Webhook 실패 시: 5분 재시도 × 3회 → 실패 시 IdP 측 권한 동결 + 알람.

### Phase 4 — 자체 호스팅 SSO 옵션 (Enterprise 한정)

- on-prem LDAP 통합 (대기업 한정).
- 한국 리전 자체 호스팅 시 SSO도 한국 리전.

### 인증 진입점 통일

- 모든 API는 `caller_member_id` 강제 주입 (미들웨어).
- A2UI Tool 호출 시 LangGraph supervisor가 caller 전파 ([`a2ui-strategy.md`](./a2ui-strategy.md) 위임).
- 인증 실패율 / SSO 실패율은 metrics.md SLO로 위임.

---

## 단일 권한 모델 구현

[`domain-overview.md`](../02-product/domain-overview.md) Role / RoleAssignment 정의를 시스템 통제로 봉인.

### Role / RoleAssignment 시스템 구현

- **Role 종류 (5종)**: Owner / Admin / Member / Guest / External.
- **Resource-scoped role_assignments**: 도메인별 권한 테이블 금지. `RoleAssignment(member_id, role_id, resource_type?, resource_id?, expires_at?)`로만 표현.
- **권한 진입점**: 모든 service 함수 시작점에서 `check_permission(caller_member_id, action, resource_type, resource_id)` 호출. 우회 시 정적 분석 룰 차단.
- **상세 ERD / RLS SQL**: [`data-model.md`](./data-model.md) 위임.

### 4도메인 가시성 매트릭스 (시스템 강제 방법)

[`domain-overview.md`](../02-product/domain-overview.md) "Role 정의" 표를 시스템 통제로 매핑.

| Role | 범위 | PM | Comms | HR | Documents | 시스템 강제 방법 |
| --- | --- | --- | --- | --- | --- | --- |
| **Owner** | Workspace | full | full | full | full | RLS + service caller_member_id 권한 통과 |
| **Admin** | Workspace | full | full | full (1:1 노트 제외) | full | RLS + 1:1 노트는 `privacy_layer=4` + 감사 모드 제외 차단 |
| **Member** | Workspace | full read, own write | own channels + DMs | own profile, own 1:1 | own documents | RLS + service 함수 `subject_member_id` 매칭 |
| **Guest** | Resource | invited only | invited only | none | invited only | resource-scoped RoleAssignment + RLS |
| **External (노무사)** | Resource | none | assigned channel(s) | assigned member docs | assigned documents | resource-scoped + AuditLog `external_collaborator=true` |

**3중 시스템 강제**:

1. **PostgreSQL RLS**: 모든 도메인 테이블에 `rls_workspace_isolation` 정책. 세션 변수 `app.workspace_id` 강제. 우회는 super role만 + AuditLog 강제.
2. **service 함수**: 시작점에서 caller_member_id + 권한 체크. 권한 통과 없으면 403 + AuditLog.
3. **A2UI Tool Registry**: `tool_registry.yaml`에 Tool마다 `permission_required` 필드. LangGraph supervisor가 호출 전 검증 ([`a2ui-strategy.md`](./a2ui-strategy.md) 위임).

### 권한 누수 탐지 (3중 회로 차단)

- **pytest contract test**: 워크스페이스 2개를 fixture로 만들고 cross-tenant read 시도 → 모두 차단되는지 검증. CI 필수.
- **A2UI Tool 호출 회로 차단**: 권한 우회 발견 시 즉시 Tool 정지 + 사후 audit ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #6).
- **분기 권한 audit**: 모든 RoleAssignment의 `last_used` + 만료 알람 + Admin 분기 검토 (SOC2 통제 항목).

### 권한 진입점 정적 분석 룰

- service 함수 시그니처에 `caller_member_id` 누락 검출 (ruff plugin).
- SQLAlchemy query에 `.filter(Model.workspace_id == ...)` 누락 검출 (`WorkspaceScopedSession` mixin).
- A2UI Tool 등록 시 `permission_required` 필드 누락 검출.

---

## 데이터 격리 (Multi-tenancy)

[`domain-overview.md`](../02-product/domain-overview.md) "데이터 격리" 절의 시스템 구현. 워크스페이스 = 단일 테넌트 = 불변 원칙 2.

### PostgreSQL RLS 정책

- **모든 도메인 테이블**: `rls_workspace_isolation` 정책 — 세션 변수 `app.workspace_id` 강제.
- **상세 SQL**: [`data-model.md`](./data-model.md) 위임.
- **우회 금지**: super role + AuditLog 강제 (DBA 직접 접근은 별도 정책).
- **세션 변수 누락 탐지**: pytest fixture로 두 워크스페이스 데이터 cross-tenant read 시도 → 모두 차단.

### EntityLink 횡단 참조의 권한 통과

- `EntityLink`는 source / target 양쪽 권한 모두 확인 후 노출.
- **편도 가시성 보장**: source에 권한 있어도 target에 권한 없으면 link 자체 비가시.

### 자체 호스팅 옵션 (Phase 4 Enterprise)

- **한국 리전 자체 호스팅**: 별도 클러스터 + 단일 데이터 모델 유지. PDF 보존 / KISA 서명 / ezTax 통신 모두 한국 리전 보장.
- **인프라 결정**: NCP / KT Cloud / 자체 IDC 비교 — Phase 4 출시 전 별도 결정 ([`tech-stack.md`](./tech-stack.md) 위임).
- **망분리 / 폐쇄망 옵션**: 공공 / 금융 시그널만 (Phase 5+ 검토 — ICP는 IT 미드마켓이 1순위).

---

## HR 프라이버시 4계층 (시스템 통제)

[`domain-hr.md`](../02-product/domain-hr.md) 프라이버시 4계층의 시스템 통제. **HR은 가장 민감한 도메인 — 데이터 노출 1건이 신뢰 붕괴**.

### 4계층 정의

[`domain-hr.md`](../02-product/domain-hr.md)에서 받음.

| 계층 | 노출 범위 | 예시 |
| --- | --- | --- |
| **Public** | 워크스페이스 전체 (Guest 제외) | `title`, `org_unit`, `email`, `hired_at` (월 단위 대략) |
| **Manager-visible** | 본인 + 직속 매니저 + HR Admin | 본인 직속 부하의 1:1 노트 (매니저 본인 작성), `leave_balance_days`, 평가 진행 상태 |
| **HR-only** | HR Admin + Workspace Owner (1:1 노트 제외) + 본인 일부 | 급여, 4대 보험, 권고사직 문서, 1:1 노트 (타인 작성), `birth_date`, `phone` |
| **Self-only** | 본인만 | 평가 피드백 원문 (캘리브레이션 전), 본인 의료 관련, 본인 1:1 노트의 본인 코멘트 |

### 시스템 통제

- **컬럼별 메타데이터**: `employee_profiles.privacy_layer = 1|2|3|4` (또는 컬럼별 분류 테이블) — [`data-model.md`](./data-model.md) 위임.
- **service 함수**: caller 권한 + 컬럼 privacy_layer 매핑 → 비가시 컬럼 마스킹.
- **A2UI Tool 권한 전파**: sub-tool 호출 단계에서 권한 적용 ([`a2ui-strategy.md`](./a2ui-strategy.md) 위임).
- **응답 스키마 정적 분석 룰**: HR-only 컬럼이 Manager-visible API 응답에 노출 안 되는지 룰 ([`domain-hr.md`](../02-product/domain-hr.md) Watch List #8).

### 1:1 노트 특수 보호

- **권한**: 매니저 + 본인 외 가시성 0. **Admin / Owner도 못 봄** (감사 모드 제외).
- **감사 모드 (Phase 3+)**: 양 당사자 동의 + Workspace Owner 동의 + AuditLog 영구 기록 조건. 인사노무 분쟁 시 한정.
- **A2UI 노출**: 키워드 / 테마만 (`hr.one_on_one.recorded` 이벤트 페이로드). **원문은 절대 이벤트에 포함 안 됨**.
- **다른 도메인 구독 금지**: `hr.one_on_one.recorded`는 A2UI 한정 구독.

### 의료 정보 (병가 진단서)

- Documents의 별도 컴플라이언스 보관 정책 적용 (1년 보존 → 즉시 delete).
- HR은 링크만 (`leave_requests.attachments[]`).
- 본인 + HR Admin 한정 가시.

---

## 외부 협업자 (노무사) 보안 모델

[`domain-overview.md`](../02-product/domain-overview.md) 외부 협업자 모델 + [`domain-hr.md`](../02-product/domain-hr.md) 노무사 모델 + [`domain-documents.md`](../02-product/domain-documents.md) 노무사 작업면을 시스템 통제로 봉인.

### 별도 신뢰 영역 (시스템 구현)

- `members.status='external'` + resource-scoped `role_assignments`.
- 노무사 자기 워크스페이스 (노무법인) + 클라이언트 워크스페이스(들)에 동시 존재 — 한 사람 = 한 워크스페이스 1회 원칙은 **워크스페이스 단위**.
- 각 워크스페이스마다 별도 `members.id`. `users.id` (Supabase)만 공유.
- 워크스페이스 간 데이터 격리: RLS + `external_collaborator=true` 마킹 + `RoleAssignment.resource_type='documents.review'` 같은 형태.

### 노무사 작업면 (Documents) 접근

[`domain-documents.md`](../02-product/domain-documents.md) "노무사 작업면 인터페이스" 절.

- **검토 큐 → 코멘트 → 승인 → 발급 트레일** — Documents의 4단 라이프사이클.
- **카테고리 가시성**: labor 카테고리만. 다른 카테고리 0 노출.
- **인스턴스 단위 권한**: HR이 발급한 RoleAssignment로 지정된 인스턴스만.
- **본문 수정**: 코멘트만 가능. 본문 직접 수정 X.
- **다운로드**: PDF 다운로드 가능 (워터마크 + AuditLog).
- **모든 액션 AuditLog**: `metadata.external_collaborator=true` + `actor_org_kind=labor_advisor` 마킹.
- **Tier별 보관**: 회사 측 Workspace Tier에 따라 — Enterprise 무제한.

### 권한 회수 / 만료

- `role_assignments.expires_at` TIMESTAMPTZ — 기본 1년.
- **만료 90일 전 알람**: HR Admin DM.
- **즉시 회수 (5초 이내)**: HR Admin 1-click → 실시간 RoleAssignment 삭제 + WebSocket 연결 종료 + 다음 API 호출 401.
- **회수 후 90일 read-only 보존** → hard delete (GDPR + 한국 개인정보보호법).
- **회수 audit**: 회수자 + 회수 사유 + 회수 시각 영구 기록.

### Watch List (외부 협업자 보안 신호)

[`domain-overview.md`](../02-product/domain-overview.md) Watch List #8 + [`domain-hr.md`](../02-product/domain-hr.md) Watch List #2 + [`domain-documents.md`](../02-product/domain-documents.md) Watch List #1 매핑.

| 신호 | 액션 |
| --- | --- |
| 노무사가 본인 영역 외 데이터 접근 1건이라도 발생 | **즉시 회로 차단** + 사후 audit + 외부 협업자 모드 회귀 테스트 추가 + 차별화 축 3 약속 점검 |
| 다른 클라이언트사 데이터 1건 노출 | 데이터 격리 깨짐 = SEV-1. 즉시 인스턴스 freeze + KISA 신고 검토 |
| 노무사 검토 SLA 초과율 > 20% (Phase 3) | 외부 카톡 / 이메일 우회 신호 — Switch Trigger #3 약속 위협 |
| 권한 회수 후 외부 협업자가 데이터 접근 시도 | RoleAssignment 삭제 실패 또는 WebSocket 종료 실패 — 인프라 결함 즉시 핫픽스 |

---

## AuditLog 통합 감사 (SOC2 Type II 1차 자료)

[`domain-overview.md`](../02-product/domain-overview.md) AuditLog 약속의 시스템 구현.

### 데이터 모델

- **단일 `audit_logs` 테이블**: 도메인별 `audit_*` 영구 금지 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #7).
- **핵심 필드**: `id`, `workspace_id`, `actor_member_id`, `domain`, `action`, `resource_type`, `resource_id`, `metadata` (JSONB), `occurred_at`, `trace_id`.
- **상세 ERD / 파티션 / 인덱스**: [`data-model.md`](./data-model.md) 위임.

### 발생 규칙

- **모든 mutation은 AuditLog 발생**: service 함수 끝점에서 자동.
- **외부 협업자 액션**: `metadata.external_collaborator=true` + `actor_org_kind` 마킹.
- **노무사 GET / POST도 기록**: 일반 사용자는 mutation만, 노무사는 조회까지 — 회사 측 Admin 활동 대시보드.
- **A2UI Tool 호출 audit**: caller + Tool 이름 + 입력 해시 + 응답 해시 + permission_check 통과 여부.

### Tier별 보관 기간

| Tier | AuditLog 보관 | 메시지 보관 | 1:1 노트 | 근로계약서 (법정) | 4대 보험 신고서 (법정) | 평가 데이터 |
| --- | --- | --- | --- | --- | --- | --- |
| Free | 30일 | 90일 | 1년 | 영구 (법정) | - | - |
| Team | 90일 | 1년 | 3년 | 영구 | - | - |
| Business | 1년 | 3년 | 무제한 | 영구 | 5년 (법정) | 3-5년 |
| Enterprise | **무제한** (설정 가능) | 무제한 (설정) | 무제한 | 영구 | 5년 (법정) | 무제한 |

- Tier별 보존 정책 근거: [`pricing-strategy.md`](../01-market/pricing-strategy.md) Tier 게이팅 + [`domain-documents.md`](../02-product/domain-documents.md) 보존 매트릭스 12종.
- 무제한 보관 (Enterprise): **월 단위 파티션** (`audit_logs_yyyymm`) — [`data-model.md`](./data-model.md) 위임.
- 법정 보존 데이터는 Tier 무관 — 근로기준법 / 세법 / 개인정보보호법이 1차.

### SOC2 Type II 자료 요구

- **Access log**: 인증 결과 (Supabase Auth) + 인가 결과 (RoleAssignment 통과 / 차단).
- **Change log**: 모든 mutation의 actor + 이전 state + 새 state.
- **Admin action log**: super role 사용 (RLS 우회) + DBA 직접 접근.
- **Incident response log**: 회로 차단 / 권한 회수 / 사고 대응 액션.

### audit_logs 무결성

- **write-only**: UPDATE / DELETE 정책 + RLS로 차단. 보존 만료 잡만 hard delete 가능.
- **hash chain (Phase 3+)**: 검토 — 인접 audit_log의 hash chain으로 tampering 방어. Phase 3 SOC2 감사 요구사항 점검 후 결정.
- **외부 SIEM 연계 (Phase 3+)**: Splunk 또는 Datadog Security로 sink. 미드마켓 RFP 요구 시 가동.

---

## SOC2 Type II 인증 (Phase 3)

### 5 Trust Service Criteria

- **Security**: 접근 통제 / 네트워크 보안 / 변경 관리 / 사고 대응.
- **Availability**: 가용성 SLO (Phase 3 99.9%+) — metrics.md 위임.
- **Processing Integrity**: 데이터 처리 정확성 / 검증.
- **Confidentiality**: 데이터 분류 / 암호화 / 접근 제한.
- **Privacy**: 개인정보 수집 / 사용 / 공유 / 보존 / 폐기.

### 12개월 감사 사이클

- **2028 Q3 감사 시작** ([`phases.md`](../03-roadmap/phases.md) Phase 3 Q3 OKR).
- 매달 통제 증거 수집 — 통제 자동화 엔지니어링 0.5인년.
- 분기별 외부 감사인 인터뷰 + 증거 점검.
- **2029 Q2 보고서 발행** (Phase 3 종료 조건).

### 통제 항목 (대표 15-20개)

| # | 통제 | 구현 | 증거 |
| --- | --- | --- | --- |
| 1 | 변경 관리 | PR 리뷰 + 머지 룰 + 환경별 배포 | GitHub log + 머지 정책 |
| 2 | 접근 권한 분기 검토 | quarterly RoleAssignment audit (자동 스크립트) | audit script output + Admin 검토 서명 |
| 3 | MFA 강제 (Admin) | Supabase MFA 강제 정책 | Supabase log |
| 4 | 백업 + 복원 테스트 (분기 1회) | PostgreSQL pg_dump + 분기 복원 훈련 | 복원 결과 보고서 |
| 5 | 데이터 암호화 (전송) | TLS 1.3 | 인증서 + 설정 |
| 6 | 데이터 암호화 (저장) | PostgreSQL TDE + S3 SSE-KMS | KMS 키 정책 |
| 7 | 침해 대응 절차 | runbook + 분기 훈련 | 훈련 로그 |
| 8 | 직원 보안 교육 | 연 2회 + 신입 입사 시 | 교육 로그 |
| 9 | 자산 인벤토리 | 모든 서비스 / 데이터베이스 / 키 등록 | 인벤토리 docs |
| 10 | 취약점 관리 | 의존성 스캔 (Dependabot / Snyk) + 분기 pentest | 스캔 결과 + 패치 로그 |
| 11 | 모니터링 + 알람 | APM (Datadog / NewRelic) + 알람 룰 | 알람 이벤트 로그 |
| 12 | 네트워크 분리 | VPC + Security Group | 인프라 설정 docs |
| 13 | 비밀 관리 | KMS / Vault (Phase 4) | 키 회전 로그 |
| 14 | 데이터 분류 | privacy_layer 메타데이터 + 보존 정책 | 분류 docs + RetentionPolicy |
| 15 | 벤더 관리 | 서드파티 (Supabase / OpenAI / S3) 보안 검토 | 벤더 SOC2 보고서 |
| 16 | 데이터 보존 + 삭제 | RetentionPolicy 잡 + 만료 audit | 만료 잡 로그 |
| 17 | 권한 회수 (퇴사 / 외부 협업자) | offboarding 자동 액션 + 회수 audit | 회수 로그 |
| 18 | 사고 보고 + 사후 분석 | runbook + post-mortem 템플릿 | 사고 보고서 |

### 감사 지연 위험 ([`phases.md`](../03-roadmap/phases.md) Phase 3 핫리스트)

- **12개월 초과 시**: Phase 3 종료 지연 → Phase 4 (KISA + ezTax) 진입 1-2분기 지연.
- **분기 증거 수집 누락 발견**: 백필 + 통제 강화 + 분기 감사인 재인터뷰.
- **외부 감사인 거절 의견**: 비전 v2 작성 + 통제 항목 재설계.

---

## K-ISMS 인증 (Phase 4)

### 한국 시장 의미

- **공공 / 금융 / 통신 입찰**: Phase 5+ 시그널만 (ICP는 IT 미드마켓 1순위).
- **미드마켓 (200-2000명)**: 일부에서 RFP 요건. 영업 자료 차별화 축 3 핵심.
- **글로벌 진출**: ISO 27001 동급 신호 — 일본 / 동남아 알파 시 정합.

### SOC2 vs K-ISMS 통제 매핑

| K-ISMS 통제 분야 | SOC2 동등 통제 | 추가 작업 |
| --- | --- | --- |
| 정보보호 정책 수립 / 운영 | (SOC2 통제 1, 8, 9 정합) | 한국어 문서화 + 정책 검토 회의록 |
| 위험 관리 (자산 식별 + 위험 평가) | (통제 9, 10 정합) | 한국 시장 위협 모델 + 분기 평가 |
| 접근 통제 | RoleAssignment + RLS (통제 2, 3) | (동일 — 매핑만) |
| 암호화 통제 | TDE + KMS + TLS (통제 5, 6) | **KISA 인증 암호 모듈 사용** (선택, Phase 5+) |
| 침해 사고 대응 | runbook + 분기 훈련 (통제 7, 18) | 한국어 절차 + **KISA 신고 양식** (PIPA 72시간) |
| 외부자 보안 | 외부 협업자 모델 (통제 15, 17) | 노무사 / 세무사 위탁 계약 한국어 양식 |
| 데이터 보호 (개인정보) | privacy_layer + RetentionPolicy (통제 14, 16) | **한국 PIPA 매핑 + 정보주체 권리 양식** |

### 인증 사이클

- **2029 Q3 감사 시작** ([`phases.md`](../03-roadmap/phases.md) Phase 4 Q3 OKR).
- **2030 Q1 완료** ([`phases.md`](../03-roadmap/phases.md) Phase 4 Q1 OKR).
- **매 3년 재인증** + 매년 사후 심사.
- 한국 인증기관: KISA (한국인터넷진흥원) 위탁 심사기관.

### 비용 가설

- 감사 비용 1.5-2.5억원 (1년 감사 사이클).
- 한국어 통제 문서화 0.3인년 + 한국 시장 위협 모델 0.1인년.
- SOC2와 통제 90% 정합 — 추가 부담은 한국어 문서화 + 한국 PIPA 매핑.

---

## KISA 전자서명 (Phase 4)

[`domain-documents.md`](../02-product/domain-documents.md) "KISA 전자서명" 절의 보안 측 결정.

### 법적 효력 (전자서명법)

- **KISA 인증 서명만 법적 효력**: 위·변조 부인 불가 + 법정 증거 채택.
- **노무사 협업 워크플로우의 마지막 단계**: 검토 → 코멘트 → 승인 → **KISA 서명** → 발급.
- Phase 3 simple 서명 (클릭 동의 + 도장 이미지) → Phase 4 KISA 정식.

### 자체 구축 vs 모두싸인 OEM (2029 Q1-Q2 결정)

[`product-vision.md`](../00-vision/product-vision.md) Watch List #5 + [`phases.md`](../03-roadmap/phases.md) "Phase 간 마이그레이션 결정 시점" 표.

| 항목 | 자체 구축 | 모두싸인 OEM 어댑터 |
| --- | --- | --- |
| 빌드 기간 | 12-18개월 | 4-6개월 |
| 비용 (가설 v1) | 8억-15억원 (1회) | 월 라이센스 + 어댑터 인프라 (사용량 기반) |
| 인증 부담 | **자체 KISA 인증 (KISA 공인인증기관 양립 또는 인정전자서명)** | 모두싸인의 인증 사용 |
| 차별화 메시지 | "Conflow 안에서 끝남" (외부 서명 노출 X) | "외부 서명 사용" 노출 |
| 폴백 | OEM 폴백 가능 | (이미 OEM) |
| 사후 인증서 재검증 | 자체 잡 (1년 / 5년) | 모두싸인 위임 |

### 결정 시점

- **2029 Q1-Q2** ([`phases.md`](../03-roadmap/phases.md)) — Phase 3 종료 시점에 비교 보고서 완성.
- **결정 기준**:
  1. 자체 구축 인력 확보 가능 여부 (백엔드 시니어 2명 12개월 풀타임).
  2. 모두싸인 어댑터 단가 vs 자체 인프라 단가 비교 (1년 후 break-even).
  3. KISA 인증 사업자 자격 취득 부담 — 영구 안 함 결정 ([`domain-documents.md`](../02-product/domain-documents.md) "안 한다" 결정과 정합).
- **폴백 정책**: 자체 구축 12개월 초과 시 → 즉시 모두싸인 OEM 폴백 ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5).

### 키 관리

- **Phase 4 — KMS** (AWS KMS 또는 Vault) — 인증서 / 서명 키 / ezTax 사업자 키.
- **HSM (자체 구축 시)** — Phase 4 결정 시점에 KISA 요구사항 확인 후 검토.
- 키 회전: 분기 1회 + 사후 audit (SOC2 통제 13).

### Watch List

- 자체구축 12개월 초과 → [`product-vision.md`](../00-vision/product-vision.md) Watch List #5 발동.
- KISA 인증서 사후 검증 실패율 > 1% ([`domain-documents.md`](../02-product/domain-documents.md) Watch List #3) → 즉시 발급사 점검 + 모두싸인 OEM 백업 검토.
- 자체 구축 + 모두싸인 OEM 모두 실패 → 제3 옵션 (한국전자인증 등 다른 사업자) 긴급 검토 + Phase 4 출시 연기 ([`domain-hr.md`](../02-product/domain-hr.md) Watch List #4).

---

## ezTax 연동 (Phase 4)

[`domain-documents.md`](../02-product/domain-documents.md) "국세청 ezTax 연동" 절의 보안 측 결정.

### 국세청 연동의 보안 요구

- **사업자 인증서 (보안 카드 또는 공인인증서)**: 워크스페이스별 별도 vault.
- **전송 암호화**: TLS + ezTax 시스템 요구 추가 암호 (KISA 인증 암호 모듈 옵션).
- **신고 결과 audit**: 장기 보관 (5년 — 세법 / 국세기본법).

### 외부 키 관리

- **사업자 키는 Workspace 별도 vault (KMS)**: 키 자체는 Conflow가 보관하되 워크스페이스 격리.
- **노무사 외부 협업자가 사용자 사업자 키 사용 시**: **위임 트레일 audit** — 회사 측 동의 + 노무사 활동 audit.
- 키 분실 / 노출 신호 → 즉시 폐기 + 재발급 + 사후 audit.

### 단계별 출시 ([`domain-documents.md`](../02-product/domain-documents.md) Phase 4 정합)

- **Phase 1 (2029 Q3-Q4)**: 원천세 신고 (월 1회).
- **Phase 2 (2030 Q1)**: 연말정산 (연 1회 1-2월) + 사업소득 신고서 (분기 / 연).

### 정확도 임계치

- **ezTax 제출 정확도 < 99%** → [`domain-documents.md`](../02-product/domain-documents.md) Watch List #2 발동 → 즉시 제출 중단 + 노무사 / 세무사 수동 모드로 격하 + ACV 1억원+ 근거 무너짐.
- 측정: 사후 KISA 신고 결과 vs Conflow 제출 결과 비교 (메트릭스 위임).

### ezTax API 변경 추적

- 국세청 시스템 변경 시 24시간 안 어댑터 패치 의무.
- 운영 프로세스: 분기 1회 ezTax 시스템 변경 사항 점검 + 어댑터 회귀 테스트.

---

## 데이터 보존 + 삭제 정책 (Data Lifecycle)

[`domain-documents.md`](../02-product/domain-documents.md) 보존 정책 매트릭스 12종을 시스템 강제로 봉인.

### Tier별 보존 ([`pricing-strategy.md`](../01-market/pricing-strategy.md) 정합)

| 데이터 종류 | Free | Team | Business | Enterprise |
| --- | --- | --- | --- | --- |
| 메시지 | 90일 | 1년 | 3년 | 무제한 (또는 설정) |
| AuditLog | 30일 | 90일 | 1년 | 무제한 |
| 1:1 노트 | 1년 | 3년 | 무제한 | 무제한 |
| 근로계약서 | 영구 (법정) | 영구 | 영구 | 영구 |
| 4대 보험 신고서 | - | - | 5년 (법정) | 5년 (법정) |
| 평가 데이터 | - | 3년 | 5년 | 무제한 |

### 보존 정책 매트릭스 (12종 — [`domain-documents.md`](../02-product/domain-documents.md))

| # | 문서 카테고리·서브타입 | 법령 / 근거 | 보존 기간 | 보존 기준점 | 만료 시 동작 | Phase |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 근로계약서 / 사직서 | 근로기준법 제42조 | 3년 | 근로관계 종료일 | anonymize → 5년 후 delete | 2 |
| 2 | 임금명세서 | 근로기준법 제48조 (2021 개정) | 5년 | 발급일 | delete | 2 |
| 3 | 권고사직 합의서 / 해고예고통지서 | 근로기준법 제23조 / 제27조 / 노위 분쟁용 | 3년+ | 근로관계 종료일 | archive_legal_only (분쟁 시 unlock) | 3 |
| 4 | 4대 보험 신고서 (가입 / 탈퇴 / 변경) | 국민건강보험법 등 | 5년 | 신고일 | delete | 3 |
| 5 | 원천징수영수증 | 국세기본법 / 소득세법 | 5년 | 회계연도 종료일 | delete | 3 |
| 6 | 연말정산 자료 | 소득세법 | 5년 | 회계연도 종료일 | delete | 4 |
| 7 | 직장 내 괴롭힘 신고서 | 근로기준법 제76조의2 | 3년+ | 사건 종결일 | archive_legal_only | 3 |
| 8 | 휴가 진단서 (병가, 의료 정보) | 개인정보보호법 (민감정보) | 1년 | 휴가 종료일 | delete (즉시) | 3 |
| 9 | 재직증명서 | (발급 사실만 AuditLog) | 1년 | 발급일 | delete | 2 |
| 10 | NDA / MSA (외부 컨설팅) | 민법 / 계약법 | 10년 | 계약 종료일 | archive_legal_only | 3 |
| 11 | 사규 / 사내 공지문 | (사내 정책) | 영구 | 폐지일까지 | (안 함) | 2 |
| 12 | 스프린트 보고서 / 투자사 월간 보고서 | (운영) | 7년 | 발행일 | delete | 2 |

### 시스템 강제

- 각 `RetentionPolicy` 인스턴스는 `legal_basis_ref` 필드에 법령 ID 기록 — 감사 시 즉시 확인.
- **`anonymize`**: PII (이름, 주민번호, 주소, 전화) 마스킹 + PDF 재렌더. 본문 구조는 보존 (통계 / 감사용).
- **`archive_legal_only`**: 조회 차단. 법령 요청 시 Workspace Owner + 법무 2인 승인 후 unlock + 추가 AuditLog.

### 만료 잡 (retention_policies 테이블 + 매일 02:00 KST 잡)

- **잡 정의**: `find DocumentInstance where retention_expires_at <= now() AND state IN [issued, archived]` → 각 인스턴스에 `on_expiry` 적용.
- **잡 실패 시 알람**: 보안 Admin DM.
- **연속 3회 실패**: [`domain-documents.md`](../02-product/domain-documents.md) Watch List #4 발동 — 컴플라이언스 위반 직전.
- soft delete → hard delete 단계 (단, 법정 보존 기간은 immutable).

### 정보주체 요청 (Right to be forgotten)

- **한국 PIPA + GDPR (Phase 4)**: 정보주체 삭제 / 열람 / 정정 요청 → Admin 검토 → 만료 잡 강제 실행 → audit.
- **응답 시간**: 한국 PIPA 30일 이내 (Phase 4 GDPR 일본/동남아 알파 시 30일 정합).
- **법정 보존 기간 내**: 거부 가능 (근거 명시).
- **자기 대상 모든 문서 export**: 본인 요청 시 30일 이내 ZIP + JSON 메타.

### 법령 매핑 갱신 책임자

- 법령 개정 시 24시간 내 RetentionPolicy 갱신.
- 책임자: 노무 자문 + 법무 자문 + 백엔드 아키텍트.
- 갱신 시 본 문서 + [`domain-documents.md`](../02-product/domain-documents.md) 보존 매트릭스 동시 갱신.

---

## 사고 대응 (Incident Response)

### Severity 분류

| Severity | 정의 | 대응 시간 | 통지 대상 |
| --- | --- | --- | --- |
| **SEV-1** | 데이터 격리 깨짐 (cross-tenant leak), 외부 협업자가 다른 클라이언트사 데이터 1건 노출 | < 15분 격리, < 1시간 통지 | CEO + CTO + CISO + 영향받은 워크스페이스 Owner + KISA (PIPA 72시간) |
| **SEV-2** | 권한 누수 (외부 협업자 영역 외 접근), HR 1:1 노트 누수, KISA 인증서 사후 검증 실패 1% 초과 | < 1시간 격리, < 4시간 통지 | CTO + CISO + 영향받은 Workspace Admin + 노무사 (관련 시) |
| **SEV-3** | 가용성 (서비스 다운, 99.9% SLO 위반), AuditLog 무결성 의심 | < 30분 회복 시작, < 2시간 통지 | 엔지니어링 리더 + 영향받은 워크스페이스 Owner |
| **SEV-4** | 기능 결함 (개별 사용자 워크플로우 막힘, 권한 회수 지연) | 다음 분기 회의 | 제품 리더 + 사용자 |

### 사고 대응 6단계

1. **탐지**: 모니터링 (Datadog / Sentry) + 알람 + 사용자 신고 + 분기 audit script.
2. **격리**: 회로 차단 (A2UI Tool 정지) + 권한 회수 (RoleAssignment 즉시 삭제) + 트래픽 차단 (WAF rule).
3. **분석**: AuditLog + `trace_id` 추적 + 사후 audit 스크립트.
4. **통지**: 사용자 (Workspace Owner DM) + 법무 + KISA (한국 PIPA 72시간) + DPO (GDPR Phase 4).
5. **복구**: 데이터 복원 (백업 + 분기 훈련 결과) + 통제 강화 + 핫픽스.
6. **사후 분석 + 통제 보강**: post-mortem 템플릿 + Watch List 업데이트 + 회귀 테스트 추가.

### 분기 침해 시뮬레이션 (SOC2 통제 7)

- **시뮬레이션 종류** (분기 1회 로테이션): cross-tenant 데이터 격리 / 외부 협업자 권한 회수 / KISA 인증서 폐기 시나리오 / 만료 잡 실패 / SOC2 통제 자료 누락.
- **복원 테스트**: 분기 1회 백업 복원 훈련 — 보관 → 복원 → 검증 → 운영 복귀 시간 측정 (RTO / RPO).
- **결과**: 분기 보안 리뷰 회의 + 통제 강화 액션.

---

## 침해 대응 통지 (한국 PIPA + GDPR)

### 한국 PIPA (개인정보보호법)

- **개인정보 유출 발견 시 72시간 내 KISA 신고 + 정보주체 통지** (1,000명 이상 영향).
- **1,000명 미만**: 정보주체 통지 의무 (시간 명시 안 되지만 지체 없이 — 24시간 권장).
- **신고 양식**: KISA 표준 양식. runbook에 한국어 양식 + 절차 봉인.
- **통지 내용**: 유출된 정보 항목 / 유출 시점 / 원인 / 영향 / 대응 / 정보주체 권리 행사 방법.

### GDPR (Phase 4 일본 / 동남아 알파에 부분 적용)

- **72시간 + DPO + 데이터 보호 영향 평가 (DPIA)**: Phase 4 일본 / 동남아 한국계 법인 알파 시점에 가동.
- **한국 본부 시장에선 부분 적용**: 한국 PIPA 우선 + GDPR은 영업 시그널만.
- **DPO 지정**: Phase 4 일본 알파 진입 시 0.2인년 — 외부 자문 가능.

### 통지 자동화 (Phase 3+)

- 사고 대응 runbook에 한국어 통지 양식 + KISA 신고 절차 봉인.
- SEV-1 / SEV-2 발생 시 자동 통지 후보 (KISA / 정보주체 / DPO) — 단, 실제 통지는 CISO 검토 후 발송.

---

## 사고 사전 신호 (Watch List 통합)

[`domain-overview.md`](../02-product/domain-overview.md) Watch List 8개 + 다른 도메인 Watch List + 보안 추가 신호.

| # | 신호 | 점검 주기 | 액션 |
| --- | --- | --- | --- |
| 1 | workspace_id 누락 머지 (PR) | 매 PR (정적 분석) | 머지 차단 + 핫픽스 + RLS 강화 |
| 2 | A2UI 권한 우회 (super user 모드 발견) | A2UI 호출 audit (일간) | **회로 차단** + 사후 audit ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #6) |
| 3 | SOC2 통제 증거 누락 | 월간 SOC2 점검 | 백필 + 통제 자동화 강화 |
| 4 | 노무사 영역 외 데이터 접근 1건이라도 | A2UI + AuditLog (일간) | **즉시 회로 차단** + 권한 모델 재설계 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #8) |
| 5 | KISA 자체구축 12개월 초과 | 분기 (Phase 4 초) | 모두싸인 OEM 폴백 가동 ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5) |
| 6 | 외부 침해 신고 (사용자) | 상시 | 인시던트 발동 — SEV 분류 후 대응 |
| 7 | 보존 만료 잡 연속 3회 실패 | 매일 잡 모니터링 | 컴플라이언스 위반 직전 — 보안 Admin DM + 수동 점검 ([`domain-documents.md`](../02-product/domain-documents.md) Watch List #4) |
| 8 | KISA 인증서 사후 검증 실패율 > 1% | 분기 (Phase 4+) | KISA 발급사 점검 + 모두싸인 OEM 백업 검토 ([`domain-documents.md`](../02-product/domain-documents.md) Watch List #3) |
| 9 | ezTax 제출 정확도 < 99% (Phase 4) | 분기 (Phase 4+) | 제출 중단 + 노무사 / 세무사 수동 모드 ([`domain-documents.md`](../02-product/domain-documents.md) Watch List #2) |
| 10 | HR-only 데이터가 Manager-visible API 응답에 노출 | 응답 스키마 정적 분석 (매 PR) | 핫픽스 + 룰 강화 ([`domain-hr.md`](../02-product/domain-hr.md) Watch List #8) |
| 11 | 1:1 노트 키워드가 매니저 외 호출자에게 노출 (A2UI) | A2UI sub-tool 권한 회귀 테스트 (매 PR) | 즉시 회로 차단 + sub-tool 권한 체크 강화 ([`domain-hr.md`](../02-product/domain-hr.md) Watch List #3) |
| 12 | 도메인별 `audit_*` 테이블 신설 (PR) | 매 PR (정적 분석) | 머지 차단 — 통합 AuditLog 약속 깨짐, SOC2 위협 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #7) |
| 13 | 권한 회수 후 외부 협업자 데이터 접근 시도 | 회수 audit (일간) | RoleAssignment 삭제 / WebSocket 종료 인프라 결함 → 즉시 핫픽스 |
| 14 | SCIM Webhook 실패율 > 1% | 일간 모니터링 | IdP 측 권한 동결 + 수동 해결 + 매핑 점검 |

---

## 의도적 보류 (책임 이전)

이 문서가 **다루지 않는** 것 — 다른 문서로 위임.

| 결정 | 위임 대상 |
| --- | --- |
| 보안 인프라 상세 (WAF / VPC / KMS / Vault 결정) | [`tech-stack.md`](./tech-stack.md) |
| 데이터 모델 SQL / RLS 정책 SQL / 파티션 SQL / audit_logs ERD | [`data-model.md`](./data-model.md) |
| LangGraph supervisor → Tool 권한 전파 구현 | [`a2ui-strategy.md`](./a2ui-strategy.md) |
| Tool Registry permission_required 필드 구현 | [`a2ui-strategy.md`](./a2ui-strategy.md) |
| 노무사 작업면 UX / 인터페이스 상세 | [`domain-documents.md`](../02-product/domain-documents.md) |
| HR 프라이버시 4계층 데이터 사양 / 컬럼별 분류 | [`domain-hr.md`](../02-product/domain-hr.md), [`data-model.md`](./data-model.md) |
| 분기 OKR (SOC2 / K-ISMS / KISA 일정) | [`phases.md`](../03-roadmap/phases.md) |
| 보안 KR 측정 정의 (AuditLog 무결성 / KISA 검증 실패율 / SLO) | [`metrics.md`](../03-roadmap/metrics.md) (TODO) |
| 가용성 SLO (99.9% / 99.95%) | [`metrics.md`](../03-roadmap/metrics.md) (TODO) + [`tech-stack.md`](./tech-stack.md) |
| KISA 사업자 선정 / 모두싸인 OEM 계약 조건 | 별도 RFP (Phase 3 종료 시점) |
| 한국 리전 자체 호스팅 인프라 (NCP / KT Cloud / 자체 IDC) | [`tech-stack.md`](./tech-stack.md) (Phase 4 출시 전 결정) |
| ezTax API 변경 추적 운영 프로세스 | 운영 매뉴얼 (Phase 4 출시 전) |
| 외부 SIEM (Splunk / Datadog Security) 선정 | [`tech-stack.md`](./tech-stack.md) (Phase 3+) |
| 직원 보안 교육 콘텐츠 | 운영 매뉴얼 (Phase 3 출시 전) |
| 백업 / 복원 RTO·RPO 정의 | [`metrics.md`](../03-roadmap/metrics.md) (TODO) + [`tech-stack.md`](./tech-stack.md) |

---

## 관련 문서

- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 축 3 (KR-first 컴플라이언스) 약속의 직접 근거
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — Phase 3-4 인증 일정, 불변 원칙 1·2 (단일 데이터 모델 + 단일 권한 모델), Watch List #5 (KISA)
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — Tier별 보관 기간, Enterprise 자체 호스팅 / 한국 리전 옵션 가격 근거
- [`../02-product/domain-overview.md`](../02-product/domain-overview.md) — 단일 권한 모델 / AuditLog / 외부 협업자 모델 / Watch List 8개의 시스템 통제 매핑
- [`../02-product/domain-hr.md`](../02-product/domain-hr.md) — HR 프라이버시 4계층, 노무사 외부 협업자 모델, 근로기준법 워크플로우 8개의 보안 통제
- [`../02-product/domain-documents.md`](../02-product/domain-documents.md) — KISA 전자서명 / ezTax / 보존 정책 매트릭스 12종 / 노무사 작업면 인터페이스
- [`../03-roadmap/phases.md`](../03-roadmap/phases.md) — SOC2 Type II / K-ISMS / KISA 분기 OKR, Phase 간 마이그레이션 결정 시점 (KISA 자체구축 vs OEM)
- [`../03-roadmap/moscow.md`](../03-roadmap/moscow.md) — Phase 1 Must (보안 백서 / 감사로그 기초 / SSO) + Phase 3-4 Should (SOC2 / K-ISMS / KISA)
- [`./data-model.md`](./data-model.md) — `audit_logs` / `role_assignments` / `scim_mappings` / `retention_policies` ERD, RLS SQL (작성 예정)
- [`./a2ui-strategy.md`](./a2ui-strategy.md) — LangGraph supervisor 권한 전파, Tool Registry permission_required (작성 예정)
- [`./tech-stack.md`](./tech-stack.md) — KMS / Vault / WAF / VPC / 한국 리전 인프라 결정 (작성 예정)
- [`../03-roadmap/metrics.md`](../03-roadmap/metrics.md) — 보안 SLO (AuditLog 무결성 / KISA 검증 실패율 / 외부 협업자 회수 시간) (작성 예정)

---

## 변경 정책

이 문서는 **5개 트리거** 시 갱신한다.

1. **SOC2 / K-ISMS / KISA 인증 일정 변경**: [`phases.md`](../03-roadmap/phases.md)의 분기 OKR이 바뀔 때 — phases.md를 먼저 갱신 후 이 문서 동기.
2. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음. 외부 협업자 권한 누수 / KISA 검증 실패 / 보존 만료 잡 실패 등.
3. **한국 법령 개정 시** — 개인정보보호법 / 근로기준법 / 세법 / 전자서명법. 보존 정책 매트릭스 + 통지 절차 즉시 갱신.
4. **인증 감사 결과 (분기)** — SOC2 분기 인터뷰 결과 / K-ISMS 사후 심사 / KISA 인증서 사후 검증 — 통제 항목 보강.
5. **사고 대응 사후 분석** — SEV-1 / SEV-2 발생 시 통제 항목 + Watch List + runbook 갱신.

**금지 사항**

- 통제 항목을 영업 압력으로 약화 — 거절. SOC2 / K-ISMS 인증 위협.
- 도메인별 `audit_*` 테이블 신설 — 영구 금지 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #7).
- 권한 체크를 service 함수 안에 흩어진 if문으로 구현 — 영구 금지. RoleAssignment 진입점 통합 ([`domain-overview.md`](../02-product/domain-overview.md) Watch List #2).
- 노무사 외부 협업자 권한을 워크스페이스 게스트 권한으로 격하 — 영구 금지. resource-scoped 유지.

**책임자**: CISO + Backend Architect (1차) + 노무 자문 + 법무 자문 (한국 법령 개정 시) + 제품 리더 (인증 일정 검토). 갱신 시 변경 이력을 본 파일 하단에 추가.

---

## 변경 이력

| 날짜 | 버전 | 변경 요약 | 작성자 |
| --- | --- | --- | --- |
| 2026-06-24 | draft v1 | 최초 작성. domain-overview.md Open Decisions 9개 봉인 (권한 모델 구현 / SCIM / SOC2 / K-ISMS / KISA / 외부 협업자 / 데이터 보존 / 한국 리전 / 침해 대응). domain-hr.md 프라이버시 4계층 + domain-documents.md 보존 매트릭스 12종 + 노무사 작업면 시스템 통제 매핑. phases.md 분기 OKR과 인증 일정 정합. | CISO + Backend Architect |
