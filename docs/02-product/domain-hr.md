---
title: HR 도메인 상세 (People Operations)
최종 업데이트: 2026-06-24
상태: draft v1
독자: PM, 백엔드, 보안, 법무, 디자인
---

# HR 도메인 (People Operations)

> 이 문서는 [`domain-overview.md`](./domain-overview.md)의 HR 계약표를 시작점으로, [`jtbd.md`](../01-market/jtbd.md) COO-3/COO-4/USR-7/CEO-4와 [`positioning.md`](../00-vision/positioning.md) **차별화 축 3 (KR-first Compliance)** 를 HR 도메인의 **결정 카탈로그**로 풀어낸다.
> [`product-vision.md`](../00-vision/product-vision.md) **Phase 2 알파 → Phase 3 정식 → Phase 4 한국 노무·세무 완성**으로 단계 출시한다. Workday 수준 인사 깊이와 Flex 수준 한국 노무 정확도를 글로벌 SaaS UX로 통합하는 것이 목표.
> 데이터 모델 ERD, RLS, KISA 전자서명 자체구축 vs 모두싸인 OEM 같은 구현 결정은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md), [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md).

---

## 이 문서로 내릴 결정

1. **Phase 2 알파 범위**: `EmployeeProfile` / `OrgUnit` / `OnboardingWorkflow` / `OffboardingWorkflow` / `OneOnOne` / `LeaveRequest` 기초 + 권한·프라이버시 4계층. **4대 보험 연동은 Phase 3까지 빌드 안 한다**.
2. **Phase 3 정식 범위**: 4대 보험 가입/탈퇴 워크플로우 + 노무사 검토 트레일, 근로기준법 핵심 워크플로우 8개, **노무사 외부 협업자 모델** (차별화 축 3의 핵심), `EvaluationCycle`, `Attendance`(시프티 흡수), SCIM, SOC2 Type II.
3. **Phase 4 한국 노무·세무 완성**: KISA 전자서명(Documents 경유), 국세청 ezTax 연동, `PayrollRecord` 골격(자체 계산 금지 — 외부 시스템 연동만), 평가 사이클 풀, K-ISMS. ACV 1억원+ Enterprise 가격의 근거.
4. **HR 데이터의 권한·프라이버시 원칙**: 4계층 분류 (Public / Manager-visible / HR-only / Self-only). 도메인 횡단 A2UI 호출 시 호출자 권한 상속 — 매니저 권한 없는 호출자는 1:1 노트 *요약*조차 못 받는다. 1:1 노트는 Admin도 못 본다 (감사 모드 제외).
5. **노무사 외부 협업자 모델**: 워크스페이스 가입 없이 특정 리소스만 접근. 한 노무사가 여러 클라이언트사에 동시 외부 협업자로 가입 가능. 시트 무료. 모든 조회·수정 AuditLog 기록. 1-click 권한 회수. **이게 [`jtbd.md`](../01-market/jtbd.md) Switch Trigger #3 ("노무 이슈가 카톡으로 새는 순간") 해결의 직접 표현**.
6. **영구 안 하는 것**: 자체 급여 계산 엔진, 채용 ATS, LMS, CRM식 영업 평가.

---

## 도메인 책임

### HR이 책임지는 것

- **Employee Profile**: `Member`의 인사 측면 메타데이터 정본 — 입사일, 직급, 소속, 정규/계약/외주 구분, 4대 보험 가입 여부, 연차 잔여. HR이 1차 소유, 다른 도메인은 `EntityLink`로 참조.
- **OrgUnit (조직도)**: 팀 / 부서의 계층 구조. 매니저 연결. PM의 Project와는 별도 (Project = 작업 묶음, OrgUnit = 조직 단위).
- **Onboarding / Offboarding 워크플로우**: 입퇴사 절차 인스턴스. 체크리스트 + 자동 액션 (4도메인 계정 발급, 장비, 문서 서명 트리거).
- **1:1 미팅 기록 (OneOnOne)**: 매니저-멤버의 공식 1:1 노트. *프라이빗 컨텍스트*의 정본. DM (Comms)과는 다른 모델.
- **휴가·근태**: `LeaveRequest` (연차/병가/경조사/보상휴가), `Attendance` (Phase 3 시프티 흡수).
- **인사평가 (EvaluationCycle)**: Phase 3+. 360 / 매니저 / 셀프 평가 사이클.
- **4대 보험 데이터 (InsuranceEnrollment)**: Phase 3. 국민/건강/고용/산재 가입 정보, 노무사 검토 트레일.
- **근로기준법 워크플로우**: Phase 3+. 연차 발생/소멸, 주 52시간 모니터링, 권고사직 절차 등. _법률 자문은 안 함_ — 워크플로우 가이드만.
- **노무사 외부 협업자 모델**: Phase 3. 한 노무사가 여러 클라이언트사 동시 접근.
- **급여 골격 (PayrollRecord)**: Phase 4. **계산은 외부 ADP/노무사 시스템 위임**, 메타·임포트·익스포트만.

### HR이 안 책임지는 것 (경계)

- **급여 계산 자체**: 영구 안 함. ADP / 노무사 시스템 / Flex 등 외부 연동만. 자체 계산은 4대 보험 요율 / 세법 변경 추적 부담이 SaaS 경제성 파괴.
- **법적 효력 있는 문서 발급**: 근로계약서·재직증명서·해고통지서 등 발급은 Documents 도메인. HR은 **데이터 제공자**.
- **개인 성과의 PM 이슈 자동 평가**: 안 함. A2UI가 합성할 수 있게 데이터를 노출만 하고, **자동 평가 로직은 도메인에 박지 않는다** (윤리·법적 리스크).
- **외부 채용 ATS**: Phase 4+ 검토. 영구 보류 가능성. 지원자 도메인은 별도 시스템과 양립.
- **학습관리 (LMS)**: 영구 안 함. 5번째 도메인 확장 금지 ([`product-vision.md`](../00-vision/product-vision.md) Anti-Vision).
- **CRM식 영업 평가 (할당량 / 커미션)**: 영구 안 함. 영업 조직 전용 도구 위임.
- **이메일 / 외부 메신저 통합**: HR 알림은 Comms 채널 또는 DM 경유. HR 자체 이메일 발송 안 함.

### 경계 모호한 케이스 — 결정

| 케이스                                          | 결정                                                                                             | 근거                                                                                                                                            |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1:1 노트                                        | **HR 소유** (`OneOnOne` 모델). 단 1:1 일정 알림은 Comms 연동.                                    | 1:1은 공식 인사 기록 — DM (비공식 대화)과 권한 행렬·보존 정책·검색 노출 모두 다름. Admin도 못 봄 (감사 모드 제외).                              |
| 스프린트 회고에서 나온 멤버 피드백              | **PM의 회고 노트에 머무름. HR로 자동 복사 안 됨.**                                               | 프라이버시. A2UI가 요청 시 사용자(매니저 권한)가 명시적으로 1:1 노트로 옮기는 액션만. 자동 복사는 신뢰 붕괴.                                    |
| 직급 / 타이틀                                   | **HR 1차 소유**. PM·Comms는 `EntityLink` 또는 `Member.display_name` 참조만.                      | `EmployeeProfile.title`이 정본. PM이 자체 `pm_role` 같은 컬럼을 두면 단일 데이터 모델 깨짐 ([`domain-overview.md`](./domain-overview.md) 원칙). |
| 입사자의 PM Project / Comms 채널 자동 추가      | **HR이 트리거, PM / Comms가 실행**. `hr.member.onboarded` 이벤트 구독.                           | HR이 PM 내부를 알지 않는다. 어떤 Project·Channel에 추가할지는 OnboardingWorkflow 템플릿이 명시.                                                 |
| 직장 내 괴롭힘 신고                             | **HR 소유 (LaborDocument의 특수 카테고리). 별도 채널·라우팅**.                                   | 일반 1:1 노트와 분리 — 매니저 라인 우회 가능해야 함 (근로기준법 제76조의2). 법무 라우팅 옵션.                                                   |
| 노무사가 보는 채널 메시지                       | **Comms 소유** (외부 협업자 채널 모델, [`domain-comms.md`](./domain-comms.md) 참조).             | HR은 노무사의 *문서 검토 권한*만 소유. 노무사가 일반 채팅에 참여하는 건 Comms 영역.                                                             |
| 휴가 신청에 첨부된 진단서                       | **HR이 메타 (LeaveRequest.attachments[]), 실제 파일은 정형 문서로 Documents 위임** (Phase 3+).   | 진단서는 민감 의료 정보 — Documents의 컴플라이언스 보관 정책 적용. HR은 링크만.                                                                 |
| 매니저가 부하 직원의 PM 이슈 상세를 평가에 인용 | **사용자 1클릭으로 EntityLink 생성. 자동 인용 금지.**                                            | A2UI는 후보 제안까지. 자동 평가 로직 금지 원칙 유지.                                                                                            |
| 외부 발급 근로계약서                            | Documents가 발급, HR이 데이터 소스 제공 + `EmployeeProfile.contract_signed_at` 갱신 트리거 구독. | `documents.contract.signed` 이벤트 구독.                                                                                                        |

---

## 핵심 엔티티

전체 ERD와 인덱스 / RLS는 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 책임·핵심 필드·상태·권한·이벤트.

### `EmployeeProfile` — `Member`의 HR 확장, HR 도메인의 핵심 aggregate

- **책임 한 줄**: Member의 인사 측면 메타데이터 정본. 입사일·직급·소속·고용 형태의 단일 출처.
- **핵심 필드**: `id`, `workspace_id`, `member_id` (FK Shared Core), `employee_no`, `title`, `org_unit_id`, `employment_type` (regular / contract / outsourced / intern), `hired_at`, `manager_member_id?`, `birth_date`, `phone`, `tenure_status` (candidate / pre_hire / active / on_leave / pre_offboarding / offboarded / archived_legal), `leave_balance_days?`, `insurance_consent_at?`
- **상태 머신**: 아래 라이프사이클 절 참조.
- **권한 모델 진입점**:
  - Public 계층: `title`, `org_unit_id`, `email` (Member 측), `hired_at` (대략) — 워크스페이스 전체 노출.
  - HR-only 계층: `birth_date`, `phone`, `employment_type`, `leave_balance_days` 등 — HR Admin + 본인.
  - Self-only 계층: 본인 평가 피드백 원문 (관련 엔티티에서).
- **이벤트 발행**: `hr.member.onboarded` (active 전이 시), `hr.member.offboarded` (offboarded 전이 시), `hr.profile.updated` (Phase 3)

### `OrgUnit` — 조직도 노드

- **책임 한 줄**: 팀 / 부서 / 본부의 계층 단위. 매니저 연결.
- **핵심 필드**: `id`, `workspace_id`, `name`, `parent_org_unit_id?`, `manager_member_id?`, `kind` (department / team / squad), `cost_center_code?` (Phase 4)
- **상태 머신**: 없음 (단순 CRUD). 단 archived 플래그로 소프트 보존.
- **권한 모델 진입점**: 읽기 = 워크스페이스 Member 전체. 쓰기 = HR Admin + Workspace Owner.
- **이벤트 발행**: `hr.org_unit.changed` (재편 시 — PM·Comms가 채널·Project 매핑 갱신 후보)

### `OnboardingWorkflow` — 입사 절차 인스턴스

- **책임 한 줄**: 한 신입의 입사 체크리스트 + 자동 액션 실행 트래킹. JTBD COO-3의 직접 표현.
- **핵심 필드**: `id`, `workspace_id`, `target_member_id`, `template_id`, `phase` (pending / in_progress / completed / cancelled), `started_at?`, `completed_at?`, `progress_pct`, `assigned_buddy_member_id?`
- **상태 머신**: `pending → in_progress → completed` (또는 `cancelled`).
- **권한 모델 진입점**: 본인 + 직속 매니저 + HR Admin이 진행 상태 조회. 외부 협업자 노출 불가.
- **이벤트 발행**: `hr.onboarding.started`, `hr.onboarding.step_completed`, `hr.member.onboarded` (모든 P0 step 완료 시)

### `OnboardingStep` — 워크플로우 안 개별 액션

- **책임 한 줄**: 체크리스트 1행. PM Project 부여 / Comms 채널 추가 / 장비 신청 / 계약서 서명 등.
- **핵심 필드**: `id`, `workflow_id`, `kind` (account_provision / channel_join / equipment / document_sign / training / kpi_setup), `target_domain?` (pm / comms / documents), `target_payload` (JSONB), `status` (pending / in_progress / done / skipped), `due_date?`, `responsible_member_id?`
- **상태 머신**: `pending → in_progress → done` (또는 `skipped`).
- **권한 모델 진입점**: Workflow 권한과 동일.
- **이벤트 발행**: `hr.onboarding.step_completed` (대상 도메인 이벤트 발행은 해당 도메인이 자체 책임)

### `OffboardingWorkflow` — 퇴사 절차 인스턴스

- **책임 한 줄**: 퇴사·해고·권고사직 절차 트래킹. **민감 사유 시 노무사 검토 자동 큐잉**.
- **핵심 필드**: `id`, `workspace_id`, `target_member_id`, `reason_code` (resignation / agreed_termination / dismissal / contract_end / retirement), `requires_labor_review`, `effective_date`, `phase` (draft / pending_review / in_progress / completed), `final_payment_status?`, `data_retention_policy`
- **상태 머신**: `draft → pending_review (노무사 검토 필요 시) → in_progress → completed`.
- **권한 모델 진입점**: HR Admin + Workspace Owner + 본인 (제한 정보). 노무사는 `reason_code=agreed_termination/dismissal`인 경우 검토 단계 진입.
- **이벤트 발행**: `hr.offboarding.started`, `hr.member.offboarded` (effective_date 도달 시)

### `OneOnOne` — 1:1 미팅 기록 (HR-only)

- **책임 한 줄**: 매니저-멤버 1:1 노트. *프라이빗 컨텍스트*의 정본. **Admin도 못 봄 (감사 모드 제외)**.
- **핵심 필드**: `id`, `workspace_id`, `manager_member_id`, `report_member_id`, `scheduled_at`, `held_at?`, `notes_md` (마크다운), `action_items[]` (Member·due_date 포함), `mood?` (Phase 3 셀프 평가), `visibility` (manager_and_report / report_only_after_session)
- **상태 머신**: `scheduled → held → archived` (수정 잠금은 held 후 7일, Phase 3 옵션).
- **권한 모델 진입점**:
  - 읽기: manager + report 양쪽만. **Admin / Owner도 못 봄** (감사 모드 진입 시에만 AuditLog 영구 기록 조건).
  - 수정: 작성자(매니저) 기본, `visibility=manager_and_report`면 report도 코멘트 추가 가능.
- **이벤트 발행**: `hr.one_on_one.recorded` (A2UI 한정 — 페이로드는 _키워드 / 테마만_, 원문 X)

### `LeaveRequest` — 휴가 신청

- **책임 한 줄**: 연차 / 병가 / 경조사 / 보상휴가 / 공가 신청·승인 단위.
- **핵심 필드**: `id`, `workspace_id`, `requester_member_id`, `leave_type` (annual / sick / family / compensatory / public / parental / maternity), `start_date`, `end_date`, `half_day?`, `reason_md?`, `attachments[]` (진단서 등 Documents 링크), `status` (draft / submitted / approved / rejected / consumed / cancelled), `approver_member_id?`
- **상태 머신**: 아래 라이프사이클 절 참조.
- **권한 모델 진입점**: 본인 + 직속 매니저(승인자) + HR Admin. 부서 동료는 일정 위에 "휴가 중" 표시만 (사유 비공개).
- **이벤트 발행**: `hr.leave.submitted`, `hr.leave.approved`, `hr.leave.rejected`, `hr.leave.consumed` (소진 후)

### `Attendance` — 근태 (Phase 3, 시프티 흡수 영역)

- **책임 한 줄**: 출퇴근 / 야근 / 시간외 누적. 주 52시간 모니터링의 데이터 소스.
- **핵심 필드**: `id`, `workspace_id`, `member_id`, `work_date`, `check_in_at?`, `check_out_at?`, `overtime_minutes`, `policy_id` (근무 정책 참조), `anomaly_flag?` (지각·결근·미체크아웃)
- **상태 머신**: 없음 (날짜별 1행, 사후 보정 시 AuditLog 기록).
- **권한 모델 진입점**: 본인 + 직속 매니저 + HR Admin. 동료는 안 봄.
- **이벤트 발행**: `hr.attendance.anomaly_detected` (지각 누적 등), `hr.labor_compliance.alert` (주 52시간 임박)

### `EvaluationCycle` (Phase 3+) — 평가 주기

- **책임 한 줄**: 360 / 매니저 평가 / 셀프 평가의 주기 컨테이너. Workday 수준 깊이 목표 (단 자동 평가 로직 금지).
- **핵심 필드**: `id`, `workspace_id`, `name` (예: "2027 H1"), `period_start`, `period_end`, `phase` (scheduled / self_review / manager_review / calibration / closed), `participants[]` (Member 또는 OrgUnit), `template_id`
- **상태 머신**: 아래 라이프사이클 절 참조.
- **권한 모델 진입점**: 셀프 단계는 본인만 / 매니저 단계는 매니저 + 본인 (피드백은 본인은 캘리브레이션 후) / Calibration은 HR + 임원.
- **이벤트 발행**: `hr.evaluation.cycle_started`, `hr.evaluation.phase_transitioned`, `hr.evaluation.cycle_closed`

### `InsuranceEnrollment` (Phase 3) — 4대 보험 가입

- **책임 한 줄**: 국민연금 / 건강보험 / 고용보험 / 산재보험 가입·탈퇴·보수월액 변경 기록 + 노무사 검토 트레일.
- **핵심 필드**: `id`, `workspace_id`, `employee_profile_id`, `insurance_type` (national_pension / health / employment / industrial_accident), `event_kind` (enroll / unenroll / monthly_salary_change), `effective_date`, `monthly_compensation`, `status` (draft / pending_review / submitted_to_authority / acknowledged), `labor_advisor_review_id?` (LaborDocument 참조), `external_submission_id?` (EDI 번호)
- **상태 머신**: `draft → pending_review → submitted_to_authority → acknowledged`.
- **권한 모델 진입점**: HR Admin + 본인 (자기 가입 내역) + 노무사 (외부 협업자, 검토 단계).
- **이벤트 발행**: `hr.insurance.enrollment_submitted`, `hr.insurance.acknowledged`

### `LaborDocument` (Phase 3+) — 노무 문서 메타 (정형 문서의 HR 측 핸들)

- **책임 한 줄**: 근로계약서 / 사직서 / 권고사직 합의서 / 직장 내 괴롭힘 신고 등의 **메타**. 실제 발급·서명·보존은 Documents.
- **핵심 필드**: `id`, `workspace_id`, `employee_profile_id`, `kind` (employment_contract / resignation / agreed_termination / dismissal_notice / harassment_report / wage_statement), `document_instance_id` (Documents 참조), `labor_advisor_review_state?` (none / requested / in_review / approved / objected), `confidential_level` (hr_only / advisor_visible)
- **상태 머신**: Documents의 `DocumentInstance` 상태와 정렬.
- **권한 모델 진입점**: HR Admin + 본인 + 매니저 (kind에 따라) + 노무사 (외부 협업자).
- **이벤트 발행**: `hr.labor_document.review_requested`, `hr.labor_document.review_completed` (구독: `documents.contract.signed`)

### `PayrollRecord` (Phase 4) — 급여 명세 메타 (외부 계산 결과 임포트)

- **책임 한 줄**: 월별 급여 명세서 / 원천세 / 4대 보험 공제 기록. **계산은 외부 시스템 (ADP / Flex / 노무사 시스템)**, Conflow는 메타·임포트·익스포트만.
- **핵심 필드**: `id`, `workspace_id`, `employee_profile_id`, `period` (YYYY-MM), `gross_amount`, `net_amount`, `withholding_tax`, `insurance_deductions` (JSONB: 4대 보험별), `source` (manual / adp_import / flex_import / labor_advisor_system), `document_instance_id?` (임금명세서 발급), `state` (draft / approved / paid / void)
- **상태 머신**: `draft → approved → paid` (또는 `void` 재발행 시).
- **권한 모델 진입점**: HR Admin + 본인 + 노무사 (위임 시).
- **이벤트 발행**: `hr.payroll.imported`, `hr.payroll.approved`, `hr.payroll.paid` (구독: `documents.payroll.processed`)

### `KpiNote` (선택, Phase 3) — 일상 피드백

- **책임 한 줄**: 평가 사이클 외 일상 칭찬 / 코칭 메모. 매니저-멤버 양쪽 가시.
- **핵심 필드**: `id`, `workspace_id`, `subject_member_id`, `author_member_id`, `kind` (praise / coaching / concern), `body_md`, `visibility` (subject_and_author / hr_admin_too), `created_at`
- **권한 모델 진입점**: 작성자 + 대상자. `hr_admin_too` 명시 시 HR Admin.
- **이벤트 발행**: `hr.kpi_note.added` (A2UI 한정, 매니저 권한 호출자만)

> **명시적으로 안 만드는 엔티티**: `JobApplication` / `Candidate` (ATS 영역, Phase 4+ 또는 영구 보류), `LearningCourse` (LMS 영역, 영구 안 함), `SalesQuota` / `Commission` (CRM 영역, 영구 안 함), `PayrollCalculation` (자체 계산 엔진, 영구 안 함).

---

## 상태 머신 / 라이프사이클

### EmployeeProfile 라이프사이클

```
   [candidate] ──> [pre_hire] ──> [active] ──┬──> [on_leave] ──> [active]
                                              │
                                              ├──> [pre_offboarding] ──> [offboarded]
                                              │                            │
                                              │                            v
                                              │                       [archived_legal]
                                              │                       (법정 보존: 통상 3년)
                                              │
                                              └──> [active] (정상 재직)

   전이 → 이벤트:
     pre_hire → active            : hr.member.onboarded
     pre_offboarding → offboarded : hr.member.offboarded
     offboarded → archived_legal  : 법정 보존 기간 만료 시 익명화/삭제 (GDPR + 한국 개인정보보호법)
```

규칙:

- **`active` 전이는 모든 OnboardingWorkflow P0 step 완료가 조건**. 미완료 step이 있으면 active 진입 금지.
- **`offboarded → archived_legal` 전이는 법정 보존 기간 (근로기준법 제42조 노동관계 서류 3년, 임금명세 5년 등) 별로 다름** — Phase 4 정밀 매핑.
- 전이는 모두 `AuditLog`에 기록 (actor + reason).

### OnboardingWorkflow 라이프사이클

```
   [pending] ──(첫 step 시작)──> [in_progress] ──(모든 P0 step done)──> [completed]
                                       │
                                       └──> [cancelled] (퇴사 결정 시)
```

규칙:

- `in_progress` 진입 시 4도메인 자동 액션 이벤트 발행 (PM Project 멤버 추가, Comms 채널 자동 추가 등).
- `completed` 시점에 `hr.member.onboarded` 발행 → 다른 도메인이 후속 처리.
- step 단위 실패는 워크플로우 전체를 막지 않는다 (Phase 2 — 사용자 수동 보정 가능).

### LeaveRequest 라이프사이클

```
   [draft] ──> [submitted] ──┬──> [approved] ──(휴가 사용 후)──> [consumed]
                              │
                              └──> [rejected]

   approved → cancelled : 사용 전 본인 취소 가능 (사유 기록)
```

규칙:

- `approved` 전이 → `hr.leave.approved` 발행 → Comms에 일정 표시 (사유 비공개, "휴가 중"만).
- `consumed` 전이는 휴가 마지막 날 자동 진입 → `EmployeeProfile.leave_balance_days` 차감.
- 진단서 첨부 (병가)는 Documents의 컴플라이언스 보관 정책 적용.

### EvaluationCycle 라이프사이클 (Phase 3+)

```
   [scheduled] ──> [self_review] ──> [manager_review] ──> [calibration] ──> [closed]
                                                                ^
                                                                │
                                          (HR + 임원만 진입, 본인 피드백 잠금)
```

규칙:

- 각 phase 전이는 HR Admin 명시 액션. 자동 전이 금지 (감사 부담).
- `calibration` 동안 본인은 자기 피드백 원문을 볼 수 없음 (Self-only는 closed 후).
- `closed` 후 7일 수정 가능 (오타 보정만), 이후 잠금.

### OffboardingWorkflow 라이프사이클

```
   [draft] ──(노무사 검토 필요 시)──> [pending_review] ──> [in_progress] ──> [completed]
       │                                                          │
       └────(단순 자진 퇴사)─────────────────────────────────────>┘

   완료 시 → hr.member.offboarded → 4도메인 access 회수 (Comms 채널, PM 권한, Documents 권한)
```

규칙:

- `reason_code in (agreed_termination, dismissal)` 시 `pending_review` 의무 — 노무사 검토 단계 자동 큐잉.
- `completed` 전이 → `hr.member.offboarded` 동기 발행 → Comms는 채널 access **실시간 회수** ([`jtbd.md`](../01-market/jtbd.md) IT-3 "퇴사 시 한 클릭 회수").
- 데이터 보존: `data_retention_policy`에 따라 즉시 삭제 (개인 DM) / 90일 read-only (업무 메시지) / 3년 보존 (근로계약·임금 자료) 분기.

---

## Phase별 출시 (P0/P1/P2/P3)

> 모든 기능은 [`jtbd.md`](../01-market/jtbd.md) Job ID에 매핑. ID 없는 기능은 빌드 안 한다.

### Phase 2 알파 (P0) — HR 알파 (2027 H2 – 2028 H1)

| 기능                                                 | Phase | JTBD ID           | 우선순위 | 근거                                                                             |
| ---------------------------------------------------- | ----- | ----------------- | -------- | -------------------------------------------------------------------------------- |
| EmployeeProfile CRUD + 라이프사이클                  | 2     | COO-3, USR-7      | P0       | HR 도메인의 핵심 aggregate. Member 1차 소유의 실체.                              |
| OrgUnit (조직도 트리)                                | 2     | COO-3, CEO-4      | P0       | 부서·매니저 매핑의 기반. 평가 / 1:1 / 권한 행렬의 입력.                          |
| OnboardingWorkflow 템플릿 + 인스턴스                 | 2     | COO-3, Trigger #4 | P0       | "신입 4명 동시 입사로 반나절" Switch Trigger #4의 직접 표현.                     |
| Onboarding 4도메인 자동 액션 (PM/Comms 권한)         | 2     | COO-3             | P0       | 차별화 축 1 (도메인 통합). HR 단독으로 입사가 끝나지 않는다 — 4도메인이 한 번에. |
| OffboardingWorkflow + 도메인 access 회수             | 2     | IT-3              | P0       | 보안 약속. `hr.member.offboarded` → Comms / PM 동기 access 회수.                 |
| OneOnOne 노트 (HR-only 권한)                         | 2     | USR-7             | P0       | 매니저-멤버 공식 기록. DM과 분리.                                                |
| LeaveRequest 기초 (연차 / 병가 / 경조사)             | 2     | (COO 운영)        | P0       | Flex 수준 정확도는 Phase 3. Phase 2는 기본 워크플로우만.                         |
| 권한·프라이버시 4계층 (Public / Manager / HR / Self) | 2     | IT-4, EMO-6       | P0       | 차별화 깨짐 방어. 데이터 노출 1건이 신뢰 붕괴.                                   |
| HR 영역 감사 로그 (Shared AuditLog)                  | 2     | IT-4              | P0       | SOC2 Type II 준비.                                                               |
| 입사자 환영 (Comms 자동 메시지 트리거)               | 2     | USR-3             | P0       | `hr.member.onboarded` → Comms 구독, 입사자 채널 자동 추가.                       |

### Phase 3 정식 (P1) — 한국 노무 핵심 + 노무사 협업 (2028 H2 – 2029 H1)

| 기능                                                       | Phase | JTBD ID                  | 우선순위 | 근거                                                                                                         |
| ---------------------------------------------------------- | ----- | ------------------------ | -------- | ------------------------------------------------------------------------------------------------------------ |
| **InsuranceEnrollment (4대 보험 가입/탈퇴) 워크플로우**    | 3     | COO-4, CEO-4             | P1       | 차별화 축 3 (KR-first Compliance)의 핵심. Flex 1위 영역 정면.                                                |
| **노무사 외부 협업자 모델 + 검토 트레일**                  | 3     | COO-4, Trigger #3, EMO-6 | P1       | Switch Trigger #3 ("노무 이슈가 카톡으로 새는 순간") 해결. 한 노무사가 여러 클라이언트사 동시 가입.          |
| **근로기준법 핵심 워크플로우 (연차, 주 52시간, 권고사직)** | 3     | COO-4, CEO-4             | P1       | 법령 매핑 (제55조 / 제50-53조 / 제23조). 워크플로우만 — 법률 자문화 금지.                                    |
| 임금명세서 발급 (제48조 2021 개정)                         | 3     | COO-4                    | P1       | Documents 위임. HR이 LaborDocument 메타 + 트리거.                                                            |
| 직장 내 괴롭힘 신고 채널 (제76조의2)                       | 3     | EMO-6                    | P1       | 별도 라우팅 (매니저 라인 우회). HR ↔ 법무 옵션.                                                              |
| EvaluationCycle (360 + 매니저 + 셀프)                      | 3     | CEO-4, USR-7             | P1       | Workday 수준 깊이의 시작점. 자동 평가 로직 금지.                                                             |
| Attendance (시프티 흡수)                                   | 3     | COO-3                    | P1       | 근태를 HR 하위로 통합. 시프티 임포터 제공.                                                                   |
| Flex 임포터 (인사 DB + 4대 보험 기록)                      | 3     | Trigger #1               | P1       | Flex 정면 대결 회피 — **흡수**. [`competitive-landscape.md`](../00-vision/competitive-landscape.md) Phase 3. |
| SCIM (SSO 그룹 ↔ Role + EmployeeProfile 동기)              | 3     | IT-2, IT-4               | P1       | 미드마켓 진입 필수. Workday 자회사 양립.                                                                     |
| 출산/육아휴직 워크플로우 (남녀고용평등법)                  | 3     | (운영)                   | P1       | 한국 노무 정확도. 법령 매핑.                                                                                 |
| 퇴직금 정산 워크플로우 (제34조)                            | 3     | COO-4                    | P1       | Offboarding 하위. 계산은 외부, 트래킹만.                                                                     |
| KpiNote (일상 피드백)                                      | 3     | USR-7                    | P1       | EvaluationCycle 보완. 비공식 코칭 기록.                                                                      |

### Phase 4 (P2) — 한국 노무·세무 완성 (2029 H2+)

| 기능                                      | Phase | JTBD ID | 우선순위 | 근거                                                                                             |
| ----------------------------------------- | ----- | ------- | -------- | ------------------------------------------------------------------------------------------------ |
| **KISA 전자서명 (Documents 경유)**        | 4     | COO-4   | P2       | 차별화 축 3 완성. 자체구축 vs 모두싸인 OEM 결정은 Phase 3 종료 시점.                             |
| **국세청 ezTax 연동 (원천세 / 연말정산)** | 4     | COO-4   | P2       | 차별화 축 3 완성. Enterprise 가격 인상 근거 (ACV 1억원+).                                        |
| PayrollRecord 골격 (외부 시스템 임포트만) | 4     | COO-4   | P2       | 자체 계산 금지. ADP / 노무사 시스템 / Flex 임포트.                                               |
| 평가 사이클 풀 기능 (보상 / 베네핏 연동)  | 4     | CEO-4   | P2       | Workday 수준 깊이 완성.                                                                          |
| **K-ISMS 인증 자료**                      | 4     | IT-4    | P2       | 미드마켓 + 한국 공공/대기업 진입 필수.                                                           |
| 4대 보험 EDI 자동 신고 (국민건강보험)     | 4     | COO-4   | P2       | Phase 3 수동 + 노무사 검토 → Phase 4 EDI 자동화. 정확도 99% 임계치 (Watch List).                 |
| 한국 리전 자체 호스팅 옵션 (Enterprise)   | 4     | IT-4    | P2       | 데이터 주권 요구 미드마켓. [`pricing-strategy.md`](../01-market/pricing-strategy.md) Enterprise. |

### Phase 4+ / 영구 안 함 (P3)

| 기능                              | 결정                         | 근거                                                                                        |
| --------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------- |
| 채용 ATS (지원자 추적)            | Phase 4+ 또는 영구 보류      | 별도 시스템 양립. ATS 깊이는 Greenhouse / Lever 위임.                                       |
| LMS (학습관리)                    | **영구 안 함**               | 5번째 도메인 확장 금지 ([`product-vision.md`](../00-vision/product-vision.md) Anti-Vision). |
| CRM식 영업 평가 (할당량 / 커미션) | **영구 안 함**               | Anti-Vision. 영업 도구는 Salesforce / HubSpot 위임.                                         |
| 자체 급여 계산 엔진               | **영구 안 함**               | 외부 ADP / Flex / 노무사 시스템 위임. 자체 계산은 SaaS 경제성 파괴.                         |
| 글로벌 노무 (미국 / EU)           | Phase 4+ 보류                | KR-first 1순위 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 4).         |
| 일본 노무                         | Phase 4+ 글로벌 알파 시 검토 | [`product-vision.md`](../00-vision/product-vision.md) 일본 알파 시점에 한정 검토.           |

---

## API 표면 (개념 수준)

> 전체 OpenAPI 3.1 스펙은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 엔드포인트 카탈로그.

### REST 엔드포인트

| 메서드 | 경로                                                      | 권한                    | Phase |
| ------ | --------------------------------------------------------- | ----------------------- | ----- |
| GET    | `/workspaces/{ws}/employees`                              | Member+ (Public 계층만) | 2     |
| GET    | `/employees/{id}`                                         | 계층별 분기 응답        | 2     |
| POST   | `/workspaces/{ws}/employees`                              | HR Admin                | 2     |
| PATCH  | `/employees/{id}`                                         | HR Admin + 본인 일부    | 2     |
| GET    | `/workspaces/{ws}/org-units`                              | Member+                 | 2     |
| POST   | `/workspaces/{ws}/org-units`                              | HR Admin                | 2     |
| POST   | `/workspaces/{ws}/onboardings`                            | HR Admin                | 2     |
| GET    | `/onboardings/{id}`                                       | 본인 + 매니저 + HR      | 2     |
| PATCH  | `/onboardings/{id}/steps/{sid}`                           | 책임자 + HR             | 2     |
| POST   | `/workspaces/{ws}/offboardings`                           | HR Admin                | 2     |
| PATCH  | `/offboardings/{id}`                                      | HR Admin (+ 노무사)     | 2     |
| POST   | `/employees/{id}/one-on-ones`                             | 매니저 또는 본인        | 2     |
| GET    | `/employees/{id}/one-on-ones`                             | 매니저 + 본인만         | 2     |
| POST   | `/leave-requests`                                         | Member+ (본인)          | 2     |
| POST   | `/leave-requests/{id}/approve`                            | 직속 매니저 + HR        | 2     |
| POST   | `/leave-requests/{id}/reject`                             | 직속 매니저 + HR        | 2     |
| GET    | `/employees/{id}/insurance-enrollments`                   | HR + 본인 + 노무사      | 3     |
| POST   | `/employees/{id}/insurance-enrollments`                   | HR Admin                | 3     |
| POST   | `/insurance-enrollments/{id}/request-review`              | HR Admin                | 3     |
| POST   | `/insurance-enrollments/{id}/submit-to-authority`         | HR + 노무사 (검토 후)   | 3     |
| GET    | `/workspaces/{ws}/labor-documents`                        | HR + 본인 + 노무사      | 3     |
| POST   | `/labor-documents/{id}/review`                            | 노무사                  | 3     |
| GET    | `/workspaces/{ws}/evaluation-cycles`                      | 참여자 + HR             | 3     |
| POST   | `/evaluation-cycles/{id}/transition`                      | HR Admin                | 3     |
| GET    | `/employees/{id}/attendance?from=...&to=...`              | 본인 + 매니저 + HR      | 3     |
| POST   | `/workspaces/{ws}/importers/flex`                         | HR Admin                | 3     |
| POST   | `/workspaces/{ws}/importers/shifty`                       | HR Admin                | 3     |
| GET    | `/employees/{id}/payroll-records?period=YYYY-MM`          | HR + 본인               | 4     |
| POST   | `/workspaces/{ws}/importers/payroll`                      | HR Admin                | 4     |
| POST   | `/workspaces/{ws}/integrations/eztax/year-end-settlement` | HR Admin + Enterprise   | 4     |

### WebSocket / SSE 이벤트 (선택적)

| 이벤트                        | 채널                          | 페이로드                            | Phase |
| ----------------------------- | ----------------------------- | ----------------------------------- | ----- |
| `onboarding.step_completed`   | `ws:{ws}/onboarding/{id}`     | `step_id`, `status`, `progress_pct` | 2     |
| `leave.approved`              | `ws:{ws}/member/{mid}`        | `leave_request_id`, `approver_id`   | 2     |
| `labor_document.review_state` | `ws:{ws}/labor-document/{id}` | `state`, `actor_id`                 | 3     |

규칙:

- 모든 mutation은 `AuditLog` 발생. HR Admin / 노무사 액션은 `metadata.role` 명시.
- 노무사가 호출한 모든 GET / POST는 `AuditLog`에 `external_collaborator=true` 마킹.

---

## A2UI Tool 카탈로그 (HR 전용)

> [`domain-overview.md`](./domain-overview.md) A2UI Tool 카탈로그 v1의 HR Tool 4개를 시작점으로 확장 (9개). 모든 Tool은 헤드리스 service 함수 + Pydantic Input/Output Schema. **호출자 권한 상속 — 매니저 권한 없는 호출자는 1:1 노트 요약조차 못 받음**.

| Tool                            | Input Schema 핵심 필드                                                                | Output Schema 핵심 필드                                                       | Tier            | Phase | JTBD ID      |
| ------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------- | ----- | ------------ |
| `hr.get_member_context`         | `member_id`, `scope` (public / manager / hr_admin)                                    | `profile`, `org_unit?`, `manager?`, `leave_balance?`, `recent_1on1_keywords?` | Business+       | 2     | COO-3, USR-7 |
| `hr.list_onboarding`            | `workspace_id`, `status?`, `start_date_range?`                                        | `onboardings[]` with `progress_pct`, `pending_steps[]`                        | Business+       | 2     | COO-3        |
| `hr.summarize_one_on_ones`      | `member_id`, `time_range`                                                             | `themes[]`, `action_items[]` (원문 X, _권한 통과 시에만 호출 성공_)           | Business+       | 2     | USR-7, CEO-4 |
| `hr.draft_offboarding`          | `member_id`, `reason_code`, `effective_date`, `notes?`                                | `workflow` (draft 상태), `requires_labor_review`                              | Business+ Admin | 2     | IT-3, COO-4  |
| `hr.check_labor_compliance`     | `workspace_id`, `workflow_type` (overtime / annual_leave / dismissal / ...), `params` | `ok`, `warnings[]`, `required_steps[]` (법령 매핑 — 자문 아님)                | Business+       | 3     | COO-4        |
| `hr.list_evaluation_progress`   | `cycle_id`                                                                            | `total`, `completed_by_phase[]`, `pending_reviewers[]`                        | Business+       | 3     | CEO-4        |
| `hr.draft_one_on_one_agenda`    | `manager_member_id`, `report_member_id`                                               | `agenda_md` (지난 1:1 action items + 최근 블로커 — _둘 다 권한 통과 시_)      | Business+       | 3     | USR-7        |
| `hr.list_pending_labor_reviews` | `reviewer_role` (labor_advisor / hr_admin), `member_id?`                              | `labor_documents[]`, `insurance_enrollments[]`                                | Business+       | 3     | COO-4        |
| `hr.get_org_chart`              | `workspace_id`, `root_org_unit_id?`                                                   | `org_tree` (계층 구조 + manager 매핑)                                         | Team+           | 2     | COO-3        |

### 도메인 횡단 Tool 진입점 — 가장 중요

[`domain-overview.md`](./domain-overview.md) A2UI 도메인 횡단 쿼리 절과 정렬. **HR Tool은 도메인 횡단 호출에서 호출자 권한을 상속한다.**

**시나리오 1**: "지난 스프린트 블로커 + 그 멤버의 1:1 피드백" ([`positioning.md`](../00-vision/positioning.md) 차별화 축 2 정식 데모, [`domain-pm.md`](./domain-pm.md) 시나리오 1과 정렬)

```
사용자(매니저 M5): "M3가 또 블로커네. 우리 1:1에서 뭐 얘기했지?"

Agent: a2ui.cross_domain_query(intent="M3's blockers + recent 1:1 themes", caller=M5)
  └→ pm.identify_blockers(workspace_id, since=last_sprint_start, assignee_id=M3)
       returns: [{issue_id: I7, blocked_hours: 72, reason: "design review delay"}]
  └→ hr.summarize_one_on_ones(member_id=M3, time_range=last_30_days)
       Permission check: caller=M5가 M3의 매니저인가?
         YES → returns: themes=["bandwidth", "design review delay"], action_items=[...]
         NO  → returns: 403 (Tool 실패, 합성 단계에 도달 안 함)
  └→ 합성: "M3가 72시간째 블로커. 최근 1:1에서 'design review delay' 키워드 일치. 권장 액션: 디자인 리뷰 일정 별도 잡기."
```

**중요**: 매니저 권한 없는 호출자는 `hr.summarize_one_on_ones` 단계에서 차단. 합성 단계에서가 아니라 **sub-tool 호출 단계에서** 권한이 적용 — 메타데이터(키워드, 요약)조차 누수 안 됨.

**시나리오 2**: "신입 5명 온보딩 진행률 + 1:1 일정 잡힘 여부" (COO 권한, [`domain-overview.md`](./domain-overview.md) 예시 2)

```
사용자(COO): "이번달 입사자들 어떻게 되고 있어?"

Agent: a2ui.cross_domain_query(intent="this month's onboarding + 1:1 status", caller=COO)
  └→ hr.list_onboarding(workspace_id, status="in_progress", start_date_range=this_month)
       returns: [{onboarding_id: O1, member_id: M3, progress_pct: 60, pending_steps: ["equipment", "manager_intro"]}, ...]
  └→ for each member_id:
       hr.summarize_one_on_ones(member_id, time_range=next_14_days)
         returns: scheduled=true/false (메타데이터만)
       hr.get_member_context(member_id, scope="manager")
         returns: manager_id, org_unit
  └→ 합성 표: 입사자 / 진행률 / 누락 step / 1:1 일정 / 매니저
```

**시나리오 3**: "퇴사자 M7 인수인계 자동 초안" (Switch Trigger #3과 정렬)

```
사용자(매니저): "M7 퇴사 결정됨. 인수인계 초안 만들어줘."

Agent:
  └→ hr.draft_offboarding(member_id=M7, reason_code="resignation", effective_date=...)
       returns: workflow (draft), requires_labor_review=false (단순 자진 퇴사)
  └→ pm.search_issues(assignee_id=M7, status_in=["in_progress", "blocked"])
       returns: M7가 담당 중인 이슈 12건
  └→ comms.search_messages(channel_ids=M7가 활성 채널, time_range=last_30_days, author_id=M7)
       returns: 최근 결정·블로커 메시지
  └→ 합성: 인수인계 체크리스트 (PM 이슈 재할당 후보 + Comms 채널 access 회수 일정 + Documents 퇴직 관련 문서 발급 큐)
  Permission check: caller는 M7의 직속 매니저인가? + Offboarding 권한 있는가?
```

### 권한 누수 방지 원칙 (가장 중요)

**A2UI가 도메인 횡단으로 HR 데이터 합성 시 호출자 권한 상속.**

- LangGraph supervisor가 `caller_member_id`를 강제 주입 → 각 sub-tool 호출 시 HR service가 `RoleAssignment` 체크.
- 매니저 권한 없는 호출자는 **1:1 노트 요약 / 휴가 사유 / 평가 진행률 / 4대 보험 가입 내역도 못 받음**.
- "Public 계층" 데이터 (직급, 소속 팀)는 워크스페이스 Member 전체 노출 — 단 외부 협업자(노무사)는 자기 담당 사원 외 정보 0 노출.
- 합성 단계에서가 아니라 **각 sub-tool 호출 단계에서** 권한 적용 — 메타데이터조차 누수 안 됨.

### Tool Registry 게이팅

- 모든 HR Tool은 기본 **Business+ Tier 게이트** ([`pricing-strategy.md`](../01-market/pricing-strategy.md) HR 도메인 Business 이상 노출).
- `hr.draft_offboarding`은 **HR Admin 권한 추가 필요** (Tier + Role 동시).
- 게이트는 `tool_registry.yaml` 한 곳에서만 강제. service 함수 안에 박지 않음 ([`domain-overview.md`](./domain-overview.md) Watch List #2).

---

## 노무사 외부 협업자 모델 (차별화 핵심)

[`positioning.md`](../00-vision/positioning.md) 차별화 축 3, [`jtbd.md`](../01-market/jtbd.md) Switch Trigger #3, [`competitive-landscape.md`](../00-vision/competitive-landscape.md) 노무사 사무소 + 엑셀의 Conflow 측 표현. **이게 깨지면 차별화 무력화**.

### 워크플로우

```
1. Workspace Owner / HR Admin이 노무사 외부 협업자 시트 발급
   ([`pricing-strategy.md`](../01-market/pricing-strategy.md): 노무사 외부 시트 무료, Business+ 워크스페이스만 발급 가능).
2. 노무사 이메일 입력 → 초대 링크. 노무사는 이미 다른 클라이언트사 워크스페이스에 외부 협업자로 있을 수 있음 (한 노무사 = 여러 클라이언트사).
3. 노무사가 가입 후 지정 리소스에만 접근:
   - 특정 EmployeeProfile 그룹의 LaborDocument
   - 특정 InsuranceEnrollment (검토 대기 중인 것)
   - Comms는 지정 채널만 (외부 협업자 채널 모델, [`domain-comms.md`](./domain-comms.md))
   - PM / 다른 HR 데이터 0 노출
4. 노무사 워크플로우:
   - LaborDocument 검토 요청 (HR Admin이 큐잉) → 노무사 의견 코멘트 → 승인 / 반려
   - 승인 시 액션 자동 트리거 (예: 4대 보험 EDI 신고, Documents 발급 큐)
5. 감사 로그: 노무사의 모든 조회·수정이 AuditLog에 `external_collaborator=true`로 기록.
   회사 측 Admin이 노무사 활동 대시보드에서 가시.
6. 권한 회수: HR Admin 1-click → 즉시 access 차단 (실시간 RoleAssignment 삭제 + WebSocket 연결 종료).
   회수 후 90일 read-only 보존 → hard delete (GDPR + 개인정보보호법).
```

### 핵심 약속

| 측면                    | 약속                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 시트 가격               | **무료** (단, 단독 워크스페이스로는 사용 불가 — 클라이언트사에 종속).                                                                            |
| 멀티 클라이언트         | 한 노무사가 여러 회사 워크스페이스에 동시 외부 협업자 가입 가능. 각 워크스페이스마다 별도 `Member.id` (한 사람 = 한 워크스페이스 1회 원칙 유지). |
| 데이터 격리             | 다른 클라이언트사 데이터 0 노출. `workspace_id` RLS로 강제.                                                                                      |
| 회수 응답 시간          | < 5초 (실시간 access 차단). WebSocket 연결 즉시 종료 + 다음 API 호출 401.                                                                        |
| 감사 추적               | 노무사의 모든 조회 / 수정 / 다운로드가 AuditLog (회사 Admin 가시).                                                                               |
| 노무사 ↔ 노무사 DM      | **금지** ([`domain-comms.md`](./domain-comms.md) 외부 ↔ 외부 DM 정책).                                                                           |
| 노무사 검토 의무 케이스 | `OffboardingWorkflow.reason_code in (agreed_termination, dismissal)`, `InsuranceEnrollment.event_kind` 변경 시 자동 큐잉.                        |

### Slack Connect / 일반 게스트 모델 대비 차별점

| 측면            | 일반 SaaS 외부 협업자                | Conflow 노무사 외부 협업자                               |
| --------------- | ------------------------------------ | -------------------------------------------------------- |
| 권한 단위       | 워크스페이스 게스트 권한 (광범위)    | 리소스 단위 (특정 EmployeeProfile 그룹 + 채널)           |
| 검토 워크플로우 | 별도 도구로 (이메일 / 카톡)          | Conflow 안에서 검토 → 승인 → 액션 자동                   |
| 감사 추적       | 부분적 (Slack Audit Premium 등 별도) | 기본 AuditLog 포함                                       |
| 권한 회수       | 게스트 비활성화 (며칠 걸림)          | 1-click + 5초 이내 access 차단                           |
| 멀티 클라이언트 | 별도 계정으로 각 회사                | 한 노무사 = 여러 워크스페이스 동시 (한 사람 = 한 ws 1회) |
| 가격            | 시트당 유료                          | **무료** (Business+ 워크스페이스가 부담)                 |

### "이게 깨지면" — Switch Trigger #3 미해결

- 노무사가 카톡으로 권고사직 문서를 받는 순간이 차별화 무력화 신호.
- 정량 기준: 노무사 access의 99% 이상이 Conflow 안에서 (외부 카톡/이메일 < 1%).
- 측정: PoC 기간 노무사 인터뷰 + AuditLog 활동률 vs 실제 검토 건수 비교.

---

## 한국 노무·세무 컴플라이언스 매핑

> 법령은 구체적으로 — _법률 자문은 아님, 워크플로우 결정만_. 실제 적용 시 노무사 검토 필수.

### 4대 보험 (Phase 3)

| 보험          | 가입 / 탈퇴 트리거                         | 워크플로우                                                                              | Tier      |
| ------------- | ------------------------------------------ | --------------------------------------------------------------------------------------- | --------- |
| 국민연금      | EmployeeProfile.tenure_status → active     | InsuranceEnrollment.draft → 노무사 검토 → 국민연금공단 신고 (Phase 3 수동, Phase 4 EDI) | Business+ |
| 건강보험      | active 진입 + 피부양자 등록 옵션           | 동일 + 피부양자 등록 별도 워크플로우                                                    | Business+ |
| 고용보험      | active 진입 (정규/계약/일용 분기)          | 동일. 고용센터 신고.                                                                    | Business+ |
| 산재보험      | active 진입 (자동, 사업장 단위)            | 사업장 단위 사후 보고. 개인 가입 신고 별도 없음.                                        | Business+ |
| 보수월액 변경 | EmployeeProfile.compensation 변경 이벤트   | InsuranceEnrollment.monthly_salary_change → 노무사 검토 → 신고                          | Business+ |
| 탈퇴 (퇴사)   | EmployeeProfile.tenure_status → offboarded | unenroll 자동 큐잉 → 노무사 검토 → 신고                                                 | Business+ |

### 근로기준법 핵심 워크플로우 8개 (Phase 3+)

| 법령                               | 워크플로우                                                                                                          | 노무사 검토 필수 | Phase               |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------------- |
| 제55조 휴일 / 연차 (제60조)        | 연차 발생 / 소멸 자동 계산 (입사일 + 근속). 1년 미만 월 1일 / 1년 이상 15일+. **`hr.check_labor_compliance` 노출**. | 선택             | 3                   |
| 제50-53조 근로시간 / 주 52시간     | Attendance 데이터로 주 단위 모니터링. 임박 시 `hr.labor_compliance.alert` 발행 → 매니저 + HR 알림.                  | 필수 (분쟁 시)   | 3                   |
| 제23조 권고사직 / 합의해지         | OffboardingWorkflow.reason_code=agreed_termination → pending_review 의무. 합의서 Documents 발급.                    | **필수**         | 3                   |
| 제27조 해고 절차 (30일 전 통지)    | OffboardingWorkflow.reason_code=dismissal → 30일 전 LaborDocument (해고예고통지서) 발급 트리거.                     | **필수**         | 3                   |
| 제48조 임금명세서 발급 (2021 개정) | PayrollRecord → 임금명세서 자동 발급 (Documents). 항목별 명시 (기본급 / 수당 / 공제) 의무.                          | 선택             | 3 (메타) / 4 (정식) |
| 제76조의2 직장 내 괴롭힘           | 별도 신고 채널 (LaborDocument.kind=harassment_report). HR ↔ 법무 라우팅 옵션. 매니저 라인 우회.                     | 케이스별         | 3                   |
| 남녀고용평등법 출산 / 육아휴직     | LeaveRequest.leave_type=maternity/parental → 별도 워크플로우 (정부 지원금 신청 연동 보류).                          | 선택             | 3                   |
| 제34조 퇴직금 정산                 | Offboarding 하위. 평균임금 산정은 외부 시스템 (자체 계산 금지). Conflow는 트래킹만.                                 | **필수**         | 3 (메타) / 4 (정밀) |

규칙:

- 각 워크플로우는 `hr.check_labor_compliance` Tool로 노출 — 사용자가 "이거 적법한지 체크" 호출 가능. **법령 규칙 엔진**만 — 자문 아님.
- 노무사 검토 필수 케이스는 자동 큐잉. 우회 시 AuditLog 경고.
- 법령 개정 시 워크플로우 갱신 의무 — `04-architecture/security-compliance.md`에 갱신 책임자 명시.

### 외부 시스템 컴플라이언스 (Phase 4)

| 시스템               | 용도                                  | 결정 시점                                             |
| -------------------- | ------------------------------------- | ----------------------------------------------------- |
| **KISA 전자서명**    | 근로계약서 / 합의서 등 법적 효력 서명 | Phase 3 종료 시점 (자체구축 vs 모두싸인 OEM)          |
| **국세청 ezTax**     | 원천세 / 연말정산 신고                | Phase 4 초                                            |
| **국민건강보험 EDI** | 4대 보험 자동 신고                    | Phase 3 수동 → Phase 4 EDI 자동화. 99% 정확도 임계치. |
| **K-ISMS**           | 정보보호 관리체계 인증                | Phase 4 (한국 공공/대기업 필수)                       |

---

## 프라이버시 / 권한 모델 (가장 민감한 절)

[`domain-overview.md`](./domain-overview.md) Role 5개의 HR 특화 적용. **HR은 가장 민감한 도메인 — 4계층 분류로 데이터 노출을 닫는다**.

### HR 데이터 4계층 분류

| 계층                | 노출 범위                                                | 예시                                                                               |
| ------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Public**          | 워크스페이스 전체 (Guest 제외)                           | `title`, `org_unit`, `email`, `hired_at` (월 단위 대략)                            |
| **Manager-visible** | 본인 + 직속 매니저 + HR Admin                            | 본인 직속 부하의 1:1 노트 (매니저 본인 작성), `leave_balance_days`, 평가 진행 상태 |
| **HR-only**         | HR Admin + Workspace Owner (1:1 노트는 제외) + 본인 일부 | 급여, 4대 보험, 권고사직 문서, 1:1 노트 (타인 작성), `birth_date`, `phone`         |
| **Self-only**       | 본인만                                                   | 평가 피드백 원문 (캘리브레이션 전), 본인 의료 관련, 본인 1:1 노트의 본인 코멘트    |

### Role × 4계층 접근 매트릭스

| 동작 / 데이터                                  | Owner      | Admin (HR) | Member (본인)       | Member (타인) | Guest | External (노무사)                 |
| ---------------------------------------------- | ---------- | ---------- | ------------------- | ------------- | ----- | --------------------------------- |
| `EmployeeProfile` Public 계층 조회             | O          | O          | O                   | O             | X     | 지정 EmployeeProfile만            |
| `EmployeeProfile` Manager 계층 조회            | O          | O          | O (본인)            | 직속 매니저만 | X     | X                                 |
| `EmployeeProfile` HR-only 계층 조회            | O          | O          | O (일부)            | X             | X     | 지정 EmployeeProfile + HR 위임 시 |
| `OneOnOne` 노트 (매니저-멤버 양쪽 본인)        | **X**      | **X**      | O (본인 참여 시)    | X             | X     | X                                 |
| `OneOnOne` 노트 (감사 모드)                    | O (조건부) | O (조건부) | O                   | X             | X     | X                                 |
| `LeaveRequest` 본인                            | O          | O          | O                   | X (사유)      | X     | X                                 |
| `LeaveRequest` 부서 동료 (사유 비공개)         | O          | O          | -                   | "휴가 중"만   | X     | X                                 |
| `EvaluationCycle` 본인 피드백 원문 (캘리브 전) | **X**      | **X**      | **X (closed 후만)** | X             | X     | X                                 |
| `InsuranceEnrollment`                          | O          | O          | O (본인)            | X             | X     | 지정 + 검토 단계                  |
| `LaborDocument`                                | O          | O          | O (본인 대상)       | X             | X     | 지정 + 검토 단계                  |
| `PayrollRecord`                                | O          | O          | O (본인)            | X             | X     | HR 위임 시 (Phase 4)              |

### DM과 1:1 노트의 차이 (가장 자주 혼동되는 부분)

| 측면                 | DM (Comms)                             | OneOnOne (HR)                                                       |
| -------------------- | -------------------------------------- | ------------------------------------------------------------------- |
| 모델                 | `Message` (type=dm)                    | `OneOnOne`                                                          |
| 권한                 | 양 당사자만, **Admin도 못 봄**         | 매니저 + 멤버 양쪽, **Admin도 못 봄** (감사 모드 제외)              |
| 검색 노출            | DM 검색 (본인만)                       | 1:1 검색 (양 당사자만)                                              |
| 보존 정책            | Tier별 (Free 30일 ~ Enterprise 무제한) | 법정 보존 (재직 + 3년 등). 퇴사 후 익명화 옵션.                     |
| AuditLog             | 메시지 자체는 안 기록 (메타만)         | 모든 작성·수정 기록 (메타 + actor)                                  |
| A2UI 노출            | `comms.search_messages` (본인만)       | `hr.summarize_one_on_ones` (양 당사자만, _키워드 / 테마만_, 원문 X) |
| 감사 모드 (Phase 3+) | 양 당사자 동의 + AuditLog 영구 기록    | 양 당사자 동의 + Workspace Owner + AuditLog 영구 기록               |

### GDPR / 개인정보보호법 매핑

| 요구사항                | Conflow 대응                                                                                                           |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 정보주체 삭제 요청      | `EmployeeProfile.tenure_status` → 익명화 (법정 보존 기간 만족 시 hard delete, 그 전까지 식별자만 마스킹)               |
| 보존 기간               | 근로기준법 제42조 노동관계 서류 3년, 임금명세 5년. `data_retention_policy`에 기록.                                     |
| 노무사 access 동의 모델 | 외부 협업자 시트 발급 시 회사 측 동의 + 노무사 활동은 AuditLog 가시. 사원 개별 동의는 InsuranceEnrollment 단위로 받음. |
| 1:1 노트의 익명화       | 퇴사 후 3년 보존 → 익명화. 본문은 매니저 / 본인 식별자 마스킹.                                                         |
| 의료 정보 (병가 진단서) | Documents의 별도 컴플라이언스 보관 정책 적용. HR은 링크만 보유.                                                        |

### "이게 깨지는 신호" — 방어

| 신호                                                            | 방어                                                                                                                                           |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| A2UI 도메인 횡단 응답에 매니저 외 사용자의 1:1 노트 키워드 포함 | **즉시 회로 차단** ([`domain-overview.md`](./domain-overview.md) Watch List #6). `hr.summarize_one_on_ones` 의 sub-tool 권한 체크 회귀 테스트. |
| HR-only 데이터가 Manager-visible API 응답에 노출                | 핫픽스 + RLS 점검 + 응답 스키마 정적 분석 룰 추가.                                                                                             |
| 노무사가 자기 담당 외 EmployeeProfile 조회 가능                 | Switch Trigger #3 약속 깨짐. 외부 협업자 모드 회귀 테스트 추가 + 사후 audit. Watch List 신호.                                                  |
| 1:1 노트가 Admin 인터페이스에서 보임 (감사 모드 외)             | 프라이버시 핵심 약속 무너짐. 즉시 핫픽스. 데이터 격리 점검.                                                                                    |
| 평가 캘리브레이션 중 본인이 자기 피드백 봄                      | 평가 프로세스 신뢰 붕괴. 즉시 phase 권한 잠금 강화.                                                                                            |

---

## 이벤트 발행 / 구독

### HR이 발행하는 이벤트

| 이벤트                               | Phase | 페이로드 핵심 필드                                                              | 구독 도메인                           |
| ------------------------------------ | ----- | ------------------------------------------------------------------------------- | ------------------------------------- |
| `hr.member.onboarded`                | 2     | `member_id`, `start_date`, `team_ids[]`, `manager_id`                           | PM, Comms, Documents, A2UI            |
| `hr.member.offboarded`               | 2     | `member_id`, `end_date`, `data_retention_policy`                                | PM, Comms, Documents, Auth, A2UI      |
| `hr.profile.updated`                 | 3     | `member_id`, `delta` (변경 필드만)                                              | A2UI, AuditLog                        |
| `hr.org_unit.changed`                | 2     | `org_unit_id`, `kind` (created/renamed/moved/archived), `parent_id?`            | PM (Project 매핑), Comms (채널 매핑)  |
| `hr.onboarding.started`              | 2     | `workflow_id`, `target_member_id`, `template_id`                                | Comms (입사 알림), A2UI               |
| `hr.onboarding.step_completed`       | 2     | `workflow_id`, `step_id`, `kind`, `target_domain?`                              | A2UI                                  |
| `hr.offboarding.started`             | 2     | `workflow_id`, `target_member_id`, `reason_code`, `requires_labor_review`       | Documents (관련 문서 큐), A2UI        |
| `hr.one_on_one.recorded`             | 2     | `one_on_one_id`, `manager_id`, `member_id`, `keywords[]` (요약만, 원문 X)       | **A2UI 한정** (다른 도메인 구독 금지) |
| `hr.leave.submitted`                 | 2     | `leave_request_id`, `requester_id`, `leave_type`, `dates`                       | Comms (매니저 알림), A2UI             |
| `hr.leave.approved`                  | 2     | `leave_request_id`, `approver_id`                                               | Comms (일정 표시 — 사유 비공개), A2UI |
| `hr.leave.rejected`                  | 2     | `leave_request_id`, `approver_id`, `reason?`                                    | Comms (요청자 DM 알림), A2UI          |
| `hr.evaluation.cycle_started`        | 3     | `cycle_id`, `period`, `evaluator_assignments[]`                                 | Comms (참여자 알림), A2UI             |
| `hr.evaluation.phase_transitioned`   | 3     | `cycle_id`, `from_phase`, `to_phase`                                            | A2UI                                  |
| `hr.evaluation.cycle_closed`         | 3     | `cycle_id`, `completion_rate`                                                   | A2UI                                  |
| `hr.insurance.enrollment_submitted`  | 3     | `enrollment_id`, `member_id`, `insurance_type`, `event_kind`                    | Documents (관련 LaborDocument), A2UI  |
| `hr.insurance.acknowledged`          | 3     | `enrollment_id`, `external_submission_id`                                       | A2UI                                  |
| `hr.labor_document.review_requested` | 3     | `labor_document_id`, `reviewer_role` (labor_advisor)                            | Comms (외부 협업자 채널 알림), A2UI   |
| `hr.labor_compliance.alert`          | 3     | `member_id`, `rule` (overtime_52h_imminent / annual_leave_expiring), `severity` | Comms (매니저 + HR DM), A2UI          |
| `hr.attendance.anomaly_detected`     | 3     | `member_id`, `work_date`, `anomaly_kind`                                        | Comms (매니저 DM), A2UI               |
| `hr.payroll.imported`                | 4     | `period`, `member_count`, `source`                                              | Documents (임금명세서 발급), A2UI     |
| `hr.payroll.approved`                | 4     | `period`, `approver_id`                                                         | A2UI, AuditLog                        |

### HR이 구독하는 이벤트

| 이벤트                        | 발행 도메인 | HR의 반응                                                                                           | Phase |
| ----------------------------- | ----------- | --------------------------------------------------------------------------------------------------- | ----- |
| `pm.sprint.ended`             | PM          | **선택**: 멤버 통계를 평가 자료로 노출 가능 (Tool 호출 시). 자동 평가 X. EvaluationCycle 입력 후보. | 3     |
| `comms.message.posted`        | Comms       | **직장 내 괴롭힘 신고 채널만 감지** (LaborDocument 생성 후보). 일반 메시지는 안 봄.                 | 3     |
| `documents.contract.signed`   | Documents   | `EmployeeProfile.contract_signed_at` 갱신 + OnboardingStep (document_sign) 완료 트리거.             | 4     |
| `documents.payroll.processed` | Documents   | `PayrollRecord.state` → paid 전이.                                                                  | 4     |
| `documents.review.completed`  | Documents   | `LaborDocument.labor_advisor_review_state` 동기.                                                    | 3     |

규칙:

- **`hr.one_on_one.recorded` 페이로드는 _키워드 / 테마만_**. 원문은 절대 이벤트 페이로드에 포함 안 됨. A2UI 외 도메인은 구독 금지.
- **`hr.member.offboarded` → 다른 도메인 access 회수는 동기 (실시간)** — IT-3 보안 약속.
- 이벤트 핸들러는 모두 idempotent ([`domain-overview.md`](./domain-overview.md) 규칙).

---

## 외부 시스템 연동 전략

### Phase 3 (정식)

| 시스템               | 용도                                | 접근 방식                                                                                                                               | 한계 / 결정 시점                           |
| -------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| **Flex 임포터**      | 인사 DB + 4대 보험 기록 흡수        | Flex Export API + 매핑 마법사. Phase 3 권장.                                                                                            | 정확도 90% 목표. < 85% 시 Watch List 신호. |
| **시프티 임포터**    | 근태 데이터 흡수                    | 시프티 Export. Attendance 모델로 매핑.                                                                                                  | 시프티 API 한계 후 결정.                   |
| **국민건강보험 EDI** | 4대 보험 신고                       | Phase 3는 **수동 + 노무사 검토 트레일**. Phase 4 EDI 자동화.                                                                            | 99% 정확도 임계치.                         |
| **SSO / SCIM**       | IdP ↔ Member + EmployeeProfile 동기 | SAML 2.0 / OIDC. SCIM 2.0 (`/Users` 엔드포인트). [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md). | Okta / Azure AD / Google Workspace 우선.   |

### Phase 4

| 시스템               | 용도                               | 결정                                                                                                                         |
| -------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **KISA 전자서명**    | 근로계약서 / 합의서 법적 효력 서명 | **자체구축 vs 모두싸인 OEM** — Phase 3 종료 시점 결정 ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5). |
| **국세청 ezTax**     | 원천세 / 연말정산                  | Enterprise Tier 한정. ACV 1억원+ 근거.                                                                                       |
| **국민건강보험 EDI** | 4대 보험 자동 신고                 | 99% 정확도 임계치. 미달 시 Phase 3 노무사 검토 모드로 격하.                                                                  |
| **외부 급여 시스템** | ADP / Flex / 노무사 시스템         | **자체 계산 안 함**. 임포트·익스포트 어댑터만.                                                                               |

### "안 한다" 결정

- **자체 급여 계산 엔진** — 4대 보험 요율 / 세법 변경 추적 부담이 SaaS 경제성 파괴. ADP / Flex / 노무사 시스템에 위임.
- **글로벌 노무 (미국 / EU)** — KR-first 1순위. Phase 4+ 일본 알파 시 일본만 검토.
- **자체 캘린더 / 자체 이메일** — Comms와 동일 ([`domain-comms.md`](./domain-comms.md)). 외부 통합만.

---

## 차별화 깨짐 신호 (Watch List)

| #   | 신호                                                                           | 그러면 무엇을 한다                                                                                                                                                      |
| --- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **4대 보험 신고 정확도 < 99%** (Phase 3-4)                                     | 한국 노무 신뢰 붕괴. Flex 대비 차별화 무력화. 즉시 노무사 검토 모드 강화 + EDI 자동화 격하 검토. [`product-vision.md`](../00-vision/product-vision.md) Watch List 직결. |
| 2   | **노무사 외부 협업자 권한 누수** (다른 클라이언트사 데이터 1건이라도 노출)     | Switch Trigger #3 미해결 → 차별화 무력화. **즉시 회로 차단** + 사후 audit. 외부 협업자 모드 회귀 테스트 추가.                                                           |
| 3   | **1:1 노트가 도메인 횡단 AI에서 권한 누수** (매니저 외 호출자에게 키워드 노출) | 사용자 신뢰 즉시 붕괴. 핫픽스 + `hr.summarize_one_on_ones` sub-tool 권한 체크 강화. [`domain-overview.md`](./domain-overview.md) Watch List #6 직결.                    |
| 4   | **Phase 4 KISA 자체구축 + 모두싸인 OEM 모두 실패**                             | 차별화 축 3 약속 미완 ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5). 제3 옵션 (다른 전자서명 사업자) 긴급 검토 + Phase 4 출시 연기.             |
| 5   | **HR 데이터 보존 기간이 법정과 충돌** (예: 임금명세 5년 미만 삭제)             | 컴플라이언스 위반. 즉시 `data_retention_policy` 점검 + 법정 보존 기간 자동 계산 룰 강화.                                                                                |
| 6   | Flex 임포터 정확도 < 85% (인사 DB + 4대 보험 기록)                             | Phase 3 마이그레이션 동기 좌초. [`competitive-landscape.md`](../00-vision/competitive-landscape.md) Phase 3 정면 대결 회피 전략 실패. 매핑 규칙 보강.                   |
| 7   | OnboardingWorkflow가 4도메인 자동 액션 실패율 > 10% (Phase 2)                  | "신입 4명 동시 입사로 반나절" Switch Trigger #4 약속 깨짐. step 단위 idempotency 점검 + 재시도 정책 강화.                                                               |
| 8   | HR-only 데이터가 Manager-visible API 응답에 노출                               | 권한 누수. 핫픽스 + 응답 스키마 정적 분석 룰 추가. [`domain-overview.md`](./domain-overview.md) Watch List #4 직결.                                                     |
| 9   | 자동 평가 로직이 service 함수에 박힘 (PM 데이터로 평가 점수 계산 등)           | 윤리·법적 리스크. 즉시 제거. A2UI 합성에서만 후보 제안 허용, 자동 계산 금지 원칙 회복.                                                                                  |
| 10  | HR service 함수가 React 컴포넌트 import                                        | 헤드리스 원칙 깨짐. A2UI Tool 등록 불가능. 즉시 리팩토링.                                                                                                               |
| 11  | HR이 PM 또는 Comms 테이블 직접 JOIN                                            | 도메인 경계 침식. `EntityLink` + 이벤트로 강제 리팩토링.                                                                                                                |
| 12  | "한국형 협업 툴" 메시지가 마케팅에 등장                                        | 안티-포지셔닝 위반 ([`positioning.md`](../00-vision/positioning.md)). 글로벌 SaaS UX 약속 깨짐 신호. 즉시 메시지 정정.                                                  |

---

## 의도적 보류 (Open Decisions)

명시적으로 **안 한다** 또는 **누가 묻기 전에 확정한** 결정들.

| 결정                                                          | 시점                                                                                         | 근거                                                                                        |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 채용 ATS (Applicant Tracking System)                          | Phase 4+ 또는 **영구 보류 가능성**                                                           | Greenhouse / Lever 양립. 지원자 도메인은 별도 시스템.                                       |
| LMS (학습관리)                                                | **영구 안 함**                                                                               | 5번째 도메인 확장 금지 ([`product-vision.md`](../00-vision/product-vision.md) Anti-Vision). |
| CRM식 영업 평가 (할당량 / 커미션)                             | **영구 안 함**                                                                               | Anti-Vision. Salesforce / HubSpot 위임.                                                     |
| 자체 급여 계산 엔진                                           | **영구 안 함**                                                                               | 4대 보험 요율 / 세법 변경 추적 부담. ADP / Flex / 노무사 위임.                              |
| 글로벌 노무 (미국 / EU / 동남아)                              | Phase 4+ 보류                                                                                | KR-first 1순위 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 4).         |
| 일본 노무                                                     | Phase 4+ 글로벌 알파 시 검토                                                                 | 일본 알파 시점에 한정 검토.                                                                 |
| Phase 2에서 4대 보험 연동                                     | Phase 3로 미룸                                                                               | Phase 2 알파는 인사 DB·입퇴사·1:1까지. 한국 노무는 Phase 3 정식.                            |
| Phase 2에서 평가 사이클                                       | Phase 3로 미룸                                                                               | 깊이가 부족한 평가는 신뢰 붕괴.                                                             |
| 모바일 풀 기능                                                | Phase 3                                                                                      | Phase 2는 읽기 + 휴가 신청까지.                                                             |
| DM 감사 모드 (Admin 조회)                                     | Phase 3+ 정책 ([`domain-comms.md`](./domain-comms.md))                                       | 인사노무 분쟁 시 양 당사자 동의 + AuditLog 영구 기록.                                       |
| 1:1 노트 감사 모드                                            | Phase 3+ 정책                                                                                | 양 당사자 동의 + Workspace Owner 동의 + AuditLog 영구 기록.                                 |
| KISA 자체구축 vs 모두싸인 OEM                                 | Phase 3 종료 시점 결정                                                                       | 자체구축 가능성·비용·KISA 인증 일정으로 분기.                                               |
| 카카오워크 임포터                                             | Phase 3 검토 (Comms 위임)                                                                    | HR 영역 데이터는 카카오워크에 없음. Comms 임포터 결정에 종속.                               |
| 사원증 / 출입통제 시스템 연동                                 | Phase 4+ 보류                                                                                | 한국 대기업 요구. ICP-3 진입 시 검토.                                                       |
| 베네핏 마켓플레이스 (커피·식대 등)                            | Phase 4+ 보류                                                                                | 별도 사업 영역. 4도메인 외부.                                                               |
| `EmployeeProfile` ERD / RLS / 인덱스 / 샤딩 SQL               | [`04-architecture/data-model.md`](../04-architecture/data-model.md)로 위임                   |                                                                                             |
| LangGraph supervisor → HR Tool 권한 전파 패턴                 | [`04-architecture/a2ui-strategy.md`](../04-architecture/a2ui-strategy.md)로 위임             |                                                                                             |
| 4대 보험 EDI 실제 구현 (정부 시스템 API)                      | [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md)로 위임 |                                                                                             |
| KISA 전자서명 사업자 선정 / OEM 계약 조건                     | Phase 3 종료 시점 별도 RFP                                                                   |                                                                                             |
| HR 도메인 LangGraph 에이전트 정의 (`onboarding_assistant` 등) | Phase 2 알파 출시 전 별도 결정                                                               | CLAUDE.md 기존 LangGraph 구조 확장.                                                         |

---

## 관련 문서

- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 축 3 (KR-first Compliance), 안티-포지셔닝 (한국형 협업 툴 금지)
- [`../00-vision/competitive-landscape.md`](../00-vision/competitive-landscape.md) — Flex 흡수 + AI 차별화, Workday 자회사 양립, 노무사 사무소 + 엑셀의 외부 협업자화
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — Phase 2 알파 / Phase 3 정식 / Phase 4 노무·세무 완성, 불변 원칙 4 (KR-first 1순위), Watch List #5 (KISA)
- [`../01-market/jtbd.md`](../01-market/jtbd.md) — Big Job #1 ("회사 운영의 단일 화면"), Switch Trigger #3 (노무 이슈 카톡 유출), Switch Trigger #4 (신입 동시 입사), COO-3 / COO-4 / USR-7
- [`../01-market/icp.md`](../01-market/icp.md) — ICP-1 COO 페르소나 (HR 행정 시간 50% 감소), 차단자 IT/보안
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — HR 도메인 Business+ 게이팅, 노무사 외부 시트 무료, Enterprise ACV 1억원+
- [`./domain-overview.md`](./domain-overview.md) — 4도메인 경계, 공유 엔티티 5개, A2UI Tool 카탈로그 v1 (이 문서의 HR 계약표가 시작점)
- [`./domain-pm.md`](./domain-pm.md) — PM ↔ HR 횡단 ("스프린트 블로커 + 1:1 피드백" 시나리오), `pm.sprint.ended` 발행
- [`./domain-comms.md`](./domain-comms.md) — Comms ↔ HR 횡단 (입퇴사 시 채널 자동 추가/회수, 외부 협업자 채널 모델), 1:1 노트와 DM의 차이
- `./domain-documents.md` — 근로계약서 발급, KISA 전자서명, 임금명세서 (작성 예정)
- `../04-architecture/data-model.md` — EmployeeProfile / OneOnOne / InsuranceEnrollment ERD, RLS, 샤딩 (작성 예정)
- `../04-architecture/a2ui-strategy.md` — LangGraph supervisor 권한 전파, HR Tool Registry (작성 예정)
- `../04-architecture/security-compliance.md` — SCIM, SOC2 Type II, K-ISMS, 4대 보험 EDI (작성 예정)
- `../03-roadmap/phases.md` — Phase 2 알파 / Phase 3 정식 / Phase 4 분기 OKR (작성 예정)
- `../03-roadmap/metrics.md` — 4대 보험 신고 정확도 / 노무사 외부 협업자 활동률 / 1:1 권한 누수 0건 SLO (작성 예정)

---

## 문서 변경 정책

이 문서는 **5개 트리거** 시 갱신한다.

1. **[`domain-overview.md`](./domain-overview.md)의 HR 계약표가 바뀔 때** — overview를 먼저 갱신 후 이 문서 동기.
2. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음.
3. **Phase 종료 시점** — 다음 Phase의 HR 출시 범위 확정과 동시에 갱신.
4. **한국 법령 개정 시** — 4대 보험 요율 / 근로기준법 / 개인정보보호법 / 세법. 워크플로우 매핑 즉시 갱신.
5. **노무사 PoC 인터뷰 분기 보고** — 외부 협업자 활동률 또는 권한 누수 신호 시.

문서 책임자: backend-architect + HR product lead + 노무 자문. 갱신 시 변경 이력을 본 파일 하단에 추가.
