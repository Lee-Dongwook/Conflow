---
title: Documents 도메인 상세 (Documents & Compliance)
최종 업데이트: 2026-06-24
상태: draft v1
독자: PM, 백엔드, 보안, 법무, 노무 자문, 디자인
---

# Documents 도메인 (Documents & Compliance)

> 이 문서는 [`domain-overview.md`](./domain-overview.md)의 Documents 계약표를 시작점으로, [`jtbd.md`](../01-market/jtbd.md) COO-4 / COO-5 / Switch Trigger #3 / Compliance(IT-5)와 [`positioning.md`](../00-vision/positioning.md) **차별화 축 3 (KR-first Compliance)** 의 마지막 마일을 Documents 도메인의 **결정 카탈로그**로 풀어낸다.
> [`product-vision.md`](../00-vision/product-vision.md) **Phase 2 기본 워크플로우 → Phase 3 노무사 검토 트레일 → Phase 4 KISA 전자서명 + 국세청 ezTax 완성**으로 단계 출시한다. 한국 법정 문서·전자서명·세무 신고를 글로벌 SaaS UX로 묶어 Enterprise ACV 1억원+의 근거를 만드는 것이 목표.
> 데이터 모델 ERD, RLS, KISA 자체구축 vs 모두싸인 OEM 같은 구현 결정은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md), [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md).
> **이 문서에서 추가하는 모든 책임은 [`domain-overview.md`](./domain-overview.md) Documents 계약표를 시작점으로 한다 — 계약을 벗어나는 책임이 필요하면 overview를 먼저 갱신해야 한다.**

---

## 이 문서로 내릴 결정

1. **Phase 2 기본 워크플로우 범위**: `DocumentTemplate` / `DocumentInstance` / `ReviewWorkflow` / `ReviewStep` / `DocumentVersion` + 5개 카테고리(노무 / 세무 / 사내 발급 / 외부 제출 / 보고서) + HR 입퇴사 이벤트 구독 자동 인스턴스화. **전자서명·ezTax는 Phase 4까지 빌드 안 한다 (PDF + 워크플로우 트레일만)**.
2. **Phase 3 노무사 검토 트레일 범위**: `SignatureRequest` / `Signer` (Phase 3는 단순 클릭 동의 / 도장 이미지 한정 — KISA 인증 X), `RetentionPolicy` 엔진, 노무사 외부 협업자 실제 작업면(검토→코멘트→승인→반려), HR LaborDocument 인터페이스 정식, 보존 정책 자동 만료/익명화.
3. **Phase 4 KISA + ezTax 완성**: `KisaSignature` 모듈 (자체구축 vs 모두싸인 OEM은 Phase 3 종료 시점 결정), `EzTaxFiling` (원천세 / 연말정산 / 사업소득), `PayrollRun` 발급 측 골격 (계산은 HR `PayrollRecord` 임포트 위임). **Enterprise Tier 한정 — ACV 1억원+ 가격 근거**.
4. **노무사 외부 협업자가 실제로 일하는 도메인**: HR이 권한을 발급하고 인사 데이터를 제공하면, **Documents가 실제 작업면**(문서 검토 → 코멘트 → 승인 → 서명 발행) — [`domain-hr.md`](./domain-hr.md) 노무사 절과 강하게 연결, HR과 중복 책임은 금지. Documents 측면의 인터페이스 4개(검토 큐 / 코멘트 / 승인-반려 / 감사 트레일)만 정의.
5. **법정 보존 정책 매트릭스의 자동화**: 근로기준법 제42조 노동관계 서류 3년, 임금명세 5년, 세법 5년, 의료 정보(병가 진단서) 별도. `RetentionPolicy` 엔티티 + 자동 만료/익명화 잡 (Celery + APScheduler). 보존 기간 미준수 = 차별화 깨짐 신호.
6. **A2UI Tool 카탈로그 (Documents 한정)**: 8개. `documents.generate_from_template` / `documents.list_pending_review` / `documents.request_signature` (Phase 4) / `documents.generate_report` (PM·HR 횡단, COO-5 직접 표현) 등. **호출자 권한 상속 — 노무사는 자기 담당 외 문서 1건도 못 봄, A2UI 합성에서도 동일**.
7. **영구 안 하는 것**: Notion식 일반 협업 문서 / 위키 / 페이지, 파일 드라이브, 협업 화이트보드, PM·HR 보고서의 데이터 소스(템플릿만 제공), 자체 OCR/번역 SaaS, 외부 마켓플레이스(템플릿 마켓은 Phase 4+ 별도 검토).

---

## 도메인 책임

### Documents가 책임지는 것

- **정형 문서 템플릿 (`DocumentTemplate`)**: 근로계약서 / 재직증명서 / 임금명세서 / 권고사직 합의서 / 4대 보험 신고서 / 원천징수영수증 / 스프린트 보고서 등 정형 문서의 템플릿. 변수 치환 + 버전 관리.
- **문서 발급 워크플로우 (`DocumentInstance` + `ReviewWorkflow`)**: 제출 → 검토 → 승인 → 발급의 4단 라이프사이클. 다단 검토자 (HR Admin → 노무사 → 본인 서명) 라우팅.
- **전자서명 (Phase 4 KISA + Phase 3 simple)**: 단일 / 다중 서명자 (순차 vs 병렬). Phase 3는 클릭 동의 / 도장 이미지 한정, Phase 4는 KISA 인증 (자체구축 vs 모두싸인 OEM).
- **국세청 ezTax 연동 (Phase 4 Enterprise)**: 원천세 신고, 연말정산, 사업소득 신고서 자동 생성·전송. Enterprise 한정.
- **법정 보존 정책 (`RetentionPolicy`)**: 근로기준법 / 세법 / 개인정보보호법의 보존 기간 자동 적용 + 만료 시 익명화 / 삭제 잡.
- **노무사 외부 협업자 작업면**: HR이 발급한 외부 협업자 권한이 실제로 사용되는 곳. 문서 검토 / 코멘트 / 승인 / 반려 액션.
- **PM/HR 보고서 자동 생성 (COO-5)**: 스프린트 보고서 PDF, 인사 통계 보고서, 투자사 월간 보고서 — **템플릿만 Documents 소유, 데이터는 다른 도메인이 API 호출로 제공**.
- **감사 트레일**: 모든 문서 mutation은 Shared `AuditLog` 발생. 노무사 액션은 `external_collaborator=true` 마킹.

### Documents가 안 책임지는 것 (경계)

- **일반 협업 문서 / 위키 / 페이지**: **영구 안 함**. Notion 정면 충돌 회피 ([`product-vision.md`](../00-vision/product-vision.md) Anti-Vision "5번째 도메인 확장 금지"). 자유 형식 노트는 Comms (Slack Canvas 수준)가, 위키는 Notion 임포터를 통해 PM Project Description으로 변환 ([`domain-pm.md`](./domain-pm.md)).
- **파일 드라이브 (일반 스토리지)**: 영구 안 함. Comms 첨부, PM 첨부는 각 도메인의 attachment 모델로 — Documents는 **정형 발급 문서 한정**.
- **보고서의 데이터 소스**: COO-5 ("투자사 월간 보고서") 템플릿은 Documents가 소유하되, 데이터는 PM (스프린트 통계), HR (인원 변동) API 호출로 가져오기만. PM·HR 데이터를 Documents에 복제 저장 안 함.
- **자체 OCR / 번역 / 문서 인식**: Phase 4+ 보류. 외부 시스템 (예: Google Document AI) 위임 또는 Phase 4 자체 vLLM 옵션.
- **외부 챗봇 / 슬랙봇 통합**: Comms 영역.
- **계약서 협상 협업 (DocuSign CLM 영역)**: Phase 4+ 보류. Phase 1-4는 발급·서명·보존까지만.
- **블록체인 / 분산원장 서명**: 영구 안 함 (한국 법령 효력 KISA가 표준).
- **HR `PayrollRecord` 계산 자체**: HR 도메인의 비-책임이자 Documents도 비-책임. 외부 ADP/Flex/노무사 시스템 위임. Documents는 임금명세서 **발급**만.

### 경계 모호한 케이스 — 결정

| 케이스                           | 결정                                                                                | 근거                                                                                                                                                                  |
| -------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 미팅 의사록 / 회의록 PDF 발급    | **Comms 소유** (Huddle 트랜스크립트 + 요약). Documents는 안 함.                     | 회의록은 정형 발급 문서가 아니다. Decision 추출 ([`domain-comms.md`](./domain-comms.md)) → PM 이슈 변환 흐름이 이미 작업의 정본. PDF 다운로드는 Comms의 export 기능.  |
| 스프린트 보고서 PDF              | **Documents 소유 (템플릿만)**, PM이 데이터 제공.                                    | COO-5의 직접 표현. PM의 `pm.get_sprint_summary` Tool 호출 → 템플릿 렌더링 → PDF. PM이 PDF 생성 책임 갖는 순간 PM이 렌더링 엔진 의존.                                  |
| 근로계약서                       | **Documents 소유**. HR이 데이터 제공 (`hr.member.onboarded` 이벤트 구독).           | 법적 효력 있는 문서 발급은 Documents. HR `LaborDocument`는 **메타 핸들**, 실제 인스턴스는 Documents `DocumentInstance`. [`domain-hr.md`](./domain-hr.md) 결정과 정합. |
| 1:1 노트 PDF export              | **HR 소유** (export 기능). Documents 안 거침.                                       | 1:1 노트는 발급 문서가 아니라 인사 기록. 보존 정책도 HR이 정의. Documents 카테고리에 안 들어감.                                                                       |
| 직장 내 괴롭힘 신고서            | **Documents 소유** (LaborDocument의 특수 카테고리). HR이 트리거.                    | 법정 효력 + 외부 제출 가능성 + 노무사 검토 필요. 보존 정책 별도. [`domain-hr.md`](./domain-hr.md) 결정과 정합.                                                        |
| 휴가 진단서 (병가)               | **Documents 소유** (메타+파일), HR이 LeaveRequest에서 링크.                         | 의료 정보 — Documents의 별도 컴플라이언스 보관 정책 적용. HR은 링크만. [`domain-hr.md`](./domain-hr.md) 결정과 정합.                                                  |
| 사내 공지문 / 사규               | **Documents 소유 (사내 발급 카테고리)** 단 사내 게시는 Comms 채널 자동 게시 트리거. | 사규는 정형 문서 (제정/개정 워크플로우 + 보존). Comms는 알림 채널.                                                                                                    |
| 외부 컨설팅 계약서 (NDA, MSA 등) | **Documents 소유 (외부 제출 카테고리)**.                                            | 다중 서명자 + 외부 협업자 모델 사용. Phase 4 KISA 시점에 풀 기능.                                                                                                     |
| 영수증 / 경비 처리 첨부          | **안 함 (Phase 4+ 보류)**.                                                          | 5번째 도메인 (Expense Management) 영역. 외부 SaaS (스피이큐, ezAdmin) 위임. Anti-Vision.                                                                              |
| 사원증 / 명함 발급               | **안 함 (Phase 4+ 보류)**.                                                          | 인쇄·실물 발급 영역. ICP-3 대기업 진입 시 별도 검토 ([`domain-hr.md`](./domain-hr.md) Open Decisions와 정합).                                                         |
| PM 보고서에 Comms 결정 요약 포함 | **Documents가 렌더링 시 PM + Comms 양쪽 Tool 호출**. 결과 데이터를 캐싱 안 함.      | 도메인 횡단 합성은 A2UI 영역. Documents는 템플릿 + 렌더링 책임만.                                                                                                     |

---

## 핵심 엔티티

전체 ERD와 인덱스 / RLS는 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 책임·핵심 필드·상태·권한·이벤트.

### `DocumentTemplate` — 정형 문서의 청사진, Documents 도메인의 핵심 aggregate

- **책임 한 줄**: 한 종류의 문서를 발급하기 위한 청사진 (변수 + 본문 + 검토 단계 + 보존 정책). Documents 도메인의 1차 소유.
- **핵심 필드**: `id`, `workspace_id`, `name`, `category` (labor / tax / internal_issuance / external_submission / report), `subtype` (employment_contract / wage_statement / harassment_report / sprint_report / ...), `body_md` (마크다운 + Jinja 변수), `variables[]` (각 변수 type / source_domain / required), `default_review_workflow_id?`, `default_retention_policy_id`, `requires_signature` (boolean), `version` (semver), `published_at?`, `created_by_member_id`
- **상태 머신**: `draft → published → deprecated`. published는 새 인스턴스 생성 가능, deprecated는 기존 인스턴스만 발급 진행.
- **권한 모델 진입점**: 생성/수정 = HR Admin + Workspace Owner. 일부 카테고리(예: 노무 템플릿)는 **노무사 검토 의무** (Phase 3+). 조회 = 카테고리별 분기.
- **이벤트 발행**: `documents.template.published`, `documents.template.deprecated`

### `DocumentInstance` — 발급된 문서의 1건

- **책임 한 줄**: 한 사람·한 사건에 대해 실제로 발급된 문서 1건. 라이프사이클의 핵심.
- **핵심 필드**: `id`, `workspace_id`, `template_id`, `template_version`, `subject_member_id?` (대상자 — 근로계약서면 본인), `requester_member_id`, `variables_snapshot` (JSONB, 발급 시점 데이터 동결), `rendered_pdf_uri?`, `state` (draft / pending_review / approved / signed / issued / void / archived), `review_workflow_id?`, `signature_request_id?`, `retention_policy_id`, `retention_expires_at?`, `issued_at?`, `void_reason?`
- **상태 머신**: 아래 라이프사이클 절 참조.
- **권한 모델 진입점**:
  - 읽기: `subject_member_id` 본인 + `requester_member_id` + HR Admin + 카테고리별 (예: labor → 노무사 외부 협업자 지정 시).
  - 수정: state별 분기. `pending_review`에서는 검토자만, `signed` 이후 본문 수정 불가 (void 후 재발행만).
- **이벤트 발행**: `documents.instance.created`, `documents.instance.review_requested`, `documents.review.completed`, `documents.contract.signed` (Phase 4), `documents.instance.issued`, `documents.instance.voided`

### `DocumentVersion` — 인스턴스의 본문 버전 이력

- **책임 한 줄**: `DocumentInstance` 본문이 검토 단계에서 수정될 때마다의 스냅샷. 감사 추적의 단위.
- **핵심 필드**: `id`, `instance_id`, `version_no`, `body_snapshot` (또는 PDF URI), `rendered_at`, `rendered_by_member_id`, `change_summary?`
- **상태 머신**: 없음 (append-only). 한 번 만들어진 버전은 수정·삭제 불가.
- **권한 모델 진입점**: Instance 읽기 권한 동일.
- **이벤트 발행**: 없음 (Instance 이벤트로 충분).

### `ReviewWorkflow` — 검토 단계 정의 (인스턴스 단위)

- **책임 한 줄**: 한 인스턴스가 거쳐야 할 검토 단계의 순서·담당자 정의. 템플릿이 기본을 정하고, 인스턴스 시점에 복사·커스텀 가능.
- **핵심 필드**: `id`, `workspace_id`, `instance_id`, `steps[]` (각 step: `order`, `reviewer_role` (hr_admin / labor_advisor / legal / subject_self / signer), `reviewer_member_id?`, `requires_approval` (boolean), `parallel_group?`), `current_step_index`, `state` (pending / in_progress / approved / rejected)
- **상태 머신**: `pending → in_progress → approved` (또는 `rejected`).
- **권한 모델 진입점**: Step의 reviewer만 해당 step에서 행동 가능. Workspace Admin은 관찰 가능.
- **이벤트 발행**: `documents.review.step_started`, `documents.review.step_completed`, `documents.review.completed`, `documents.review.rejected`

### `ReviewStep` — 검토 단계 1행 (워크플로우 안)

- **책임 한 줄**: 한 검토자의 한 액션 (승인 / 반려 / 코멘트 추가).
- **핵심 필드**: `id`, `workflow_id`, `order`, `reviewer_role`, `reviewer_member_id`, `requires_approval`, `state` (pending / in_progress / approved / rejected / skipped), `acted_at?`, `comment_md?`, `parallel_group?`
- **상태 머신**: `pending → in_progress → approved` (또는 `rejected`, `skipped`).
- **권한 모델 진입점**: reviewer 본인 + Workspace Admin (관찰).
- **이벤트 발행**: Workflow 이벤트로 라우팅 (자체 발행 없음).

### `ReviewComment` — 검토자 코멘트 (인라인)

- **책임 한 줄**: 검토 단계에서 노무사·HR Admin이 남기는 인라인 코멘트. 본문 위치 anchor 옵션.
- **핵심 필드**: `id`, `workflow_id`, `step_id`, `author_member_id`, `body_md`, `anchor?` (body 안의 위치), `parent_comment_id?` (스레드), `resolved_at?`
- **상태 머신**: `open → resolved` (작성자 또는 다음 step reviewer가 resolve).
- **권한 모델 진입점**: Workflow 권한 동일.
- **이벤트 발행**: `documents.review.comment_added` (A2UI 한정)

### `SignatureRequest` — 서명 요청 (Phase 3 simple / Phase 4 KISA)

- **책임 한 줄**: 한 인스턴스에 대한 다중 서명자의 서명 요청 단위. 순차 / 병렬 정책 보유.
- **핵심 필드**: `id`, `workspace_id`, `instance_id`, `mode` (sequential / parallel), `signers[]` (Signer 참조), `state` (draft / sent / in_progress / completed / cancelled / expired), `sent_at?`, `completed_at?`, `expires_at?`, `provider` (internal_simple_phase3 / kisa_self_phase4 / modusign_oem_phase4)
- **상태 머신**: `draft → sent → in_progress → completed` (또는 `cancelled`, `expired`).
- **권한 모델 진입점**: Instance 권한 + 각 Signer는 자기 서명 단계만.
- **이벤트 발행**: `documents.signature.requested`, `documents.signature.completed`, `documents.contract.signed` (Phase 4 KISA 완료 시)

### `Signer` — 서명자 1인

- **책임 한 줄**: 서명 요청의 한 서명자. 한 인스턴스에 여러 명 가능.
- **핵심 필드**: `id`, `signature_request_id`, `signer_member_id?` (내부 멤버) 또는 `signer_external_email?` (외부, Phase 4), `role` (employee / employer / witness / labor_advisor / counterparty), `order` (sequential 모드에서), `state` (waiting / notified / viewed / signed / declined), `signed_at?`, `signature_artifact_uri?` (Phase 3는 클릭 동의 로그 / 도장 이미지, Phase 4는 KISA 인증서 + 타임스탬프), `ip_address?`, `device_info?`
- **상태 머신**: `waiting → notified → viewed → signed` (또는 `declined`).
- **권한 모델 진입점**: signer 본인만 자기 행동. Instance 권한자는 진행 상태만 조회.
- **이벤트 발행**: `documents.signer.notified`, `documents.signer.signed`, `documents.signer.declined`

### `KisaSignature` (Phase 4) — KISA 인증 서명 메타

- **책임 한 줄**: Phase 4 KISA 인증 전자서명의 인증서·타임스탬프·검증 메타. **자체구축 vs 모두싸인 OEM 어댑터 패턴**.
- **핵심 필드**: `id`, `signer_id`, `certificate_serial`, `issuer_dn`, `subject_dn`, `signing_algorithm`, `signed_hash`, `timestamp_token` (RFC 3161), `validation_state` (valid / revoked / expired / unverifiable), `provider_response_blob` (JSONB), `verified_at?`
- **상태 머신**: `pending → valid → revoked` (또는 `expired`).
- **권한 모델 진입점**: Instance 권한 + 보안 Admin (재검증).
- **이벤트 발행**: `documents.kisa.signed`, `documents.kisa.verification_failed` (사후 재검증 실패 시 — 차별화 깨짐 신호)

### `RetentionPolicy` — 법정 보존 정책 정의

- **책임 한 줄**: 카테고리·서브타입별 보존 기간 + 만료 시 동작 (delete / anonymize / archive_legal_only) 정의. 자동 잡의 입력.
- **핵심 필드**: `id`, `workspace_id`, `name` (예: "근로계약서 3년"), `category`, `subtype?`, `retention_years`, `retention_basis` (creation / issuance / employment_end / fiscal_year_end), `on_expiry` (delete / anonymize / archive_legal_only), `legal_basis_ref` (근로기준법 제42조 등)
- **상태 머신**: 없음 (단순 CRUD, 단 변경 시 기존 인스턴스의 retention_expires_at 재계산 잡 트리거).
- **권한 모델 진입점**: Workspace Owner + 보안 Admin만 수정. 조회 = HR Admin + 노무사.
- **이벤트 발행**: `documents.retention.policy_updated`, `documents.retention.expired` (만료 잡이 트리거할 때)

### `EzTaxFiling` (Phase 4 Enterprise) — 국세청 ezTax 신고 메타

- **책임 한 줄**: 원천세 / 연말정산 / 사업소득 신고서의 ezTax 제출 메타. Enterprise 한정.
- **핵심 필드**: `id`, `workspace_id`, `filing_kind` (withholding_monthly / year_end_settlement / business_income), `period` (YYYY-MM 또는 YYYY), `subject_employee_profile_ids[]`, `document_instance_ids[]`, `state` (draft / prepared / submitted_to_eztax / acknowledged / rejected / void), `eztax_submission_id?`, `acknowledged_at?`, `error_blob?`
- **상태 머신**: `draft → prepared → submitted_to_eztax → acknowledged` (또는 `rejected`).
- **권한 모델 진입점**: HR Admin + 세무 담당 (외부 협업자) + Workspace Owner.
- **이벤트 발행**: `documents.eztax.submitted`, `documents.eztax.acknowledged`, `documents.eztax.rejected`

### `PayrollRun` (Phase 4) — 월별 임금명세서 발급 묶음

- **책임 한 줄**: 한 달의 전 임직원 임금명세서 발급 배치. **계산은 HR `PayrollRecord` 임포트에서 위임, Documents는 발급·배포·서명·보존만**.
- **핵심 필드**: `id`, `workspace_id`, `period` (YYYY-MM), `source_payroll_record_ids[]`, `document_instance_ids[]`, `state` (draft / generated / delivered / sealed), `delivered_at?`, `total_count`, `error_count`
- **상태 머신**: `draft → generated → delivered → sealed`.
- **권한 모델 진입점**: HR Admin + Workspace Owner.
- **이벤트 발행**: `documents.payroll.processed`, `documents.payroll.delivered`

### `Report` (Phase 2 — COO-5 직접 표현) — 자동 생성 보고서 인스턴스

- **책임 한 줄**: `DocumentTemplate.category=report` 인스턴스의 특화. 데이터 소스는 PM·HR·Comms Tool 호출. 정기 스케줄링 옵션.
- **핵심 필드**: `id`, `instance_id`, `report_kind` (sprint_report / investor_monthly / hr_quarterly / labor_compliance), `period_start`, `period_end`, `data_source_trace[]` (어떤 Tool이 어떤 입력으로 호출되어 어떤 결과를 줬는지 감사용), `regenerable` (boolean — 데이터 변경 시 재생성 가능 여부)
- **상태 머신**: `DocumentInstance`와 정렬.
- **권한 모델 진입점**: Instance 권한 + 보고서 카테고리별 (예: investor_monthly = CEO + COO 한정).
- **이벤트 발행**: `documents.report.generated`

> **명시적으로 안 만드는 엔티티** (Phase 1-4): `WikiPage` / `Whiteboard` / `Drive` (5번째 도메인 영역, 영구 안 함), `ExpenseReceipt` (Phase 4+ 또는 영구 보류), `OcrJob` (외부 위임), `ContractNegotiationThread` (DocuSign CLM 영역, Phase 4+).

---

## 상태 머신 / 라이프사이클

### DocumentInstance 라이프사이클 (핵심)

```
   [draft] ──(reviewer 지정)──> [pending_review] ──(모든 step approved)──> [approved]
       │                              │                                         │
       │                              └──> [rejected] ──> [draft] (재작성)     │
       │                                                                        │
       │                                                                        v
       │                                                            (서명 필요?)
       │                                                                        │
       │                                                       ┌───── YES ─────┴──── NO ─────┐
       │                                                       v                               v
       │                                                  [signed] ──> [issued]          [issued]
       │                                                                   │
       │                                                                   v
       │                                                             [archived] (보존 만료 시)
       │                                                                   │
       │                                                                   v
       │                                            (RetentionPolicy.on_expiry) → delete / anonymize
       │
       └──> [void] (취소·재발행 트리거, AuditLog 영구)
```

규칙:

- **`signed` 이후 본문 수정 불가** — `void` 후 새 `DocumentInstance` 발급만. 법적 효력 보호.
- **`pending_review`에서 reject** 시 모든 step state는 보존 (감사). 새 draft 인스턴스 생성 (이전 인스턴스는 `void`).
- **`issued` 진입 = Subject Member에게 알림 (Comms DM)** + AuditLog 발생.
- **`archived` 전이는 `retention_expires_at` 도달 시 자동 잡** (Celery + APScheduler). `RetentionPolicy.on_expiry`에 따라 후속.
- **전이는 모두 `AuditLog` 기록** (actor + 사유 + 이전 state).

### ReviewWorkflow 라이프사이클

```
   [pending] ──(첫 step in_progress)──> [in_progress] ──(모든 step approved)──> [approved]
                                            │
                                            └──> [rejected] (어떤 step reject 시)
```

규칙:

- **Sequential 모드**: order 순서대로. 이전 step approved 후 다음 step in_progress.
- **Parallel 모드 (`parallel_group` 같은 step)**: 동시 진행. 모두 approved일 때만 그룹 통과.
- **Reject 발생 시 즉시 workflow rejected** — 후속 step은 skipped 마킹. AuditLog 영구.
- 단일 reviewer가 정해진 SLA (예: 7일) 안에 행동하지 않으면 escalation 알림 → HR Admin DM. SLA 초과는 Watch List 신호.

### SignatureRequest 라이프사이클 (Phase 3 simple / Phase 4 KISA)

```
   [draft] ──(sent)──> [sent] ──(첫 signer notified)──> [in_progress]
                                                              │
                                                              ├──> [completed] (모든 signer signed)
                                                              ├──> [cancelled] (요청자가 취소)
                                                              └──> [expired] (expires_at 도달, 미완료)

   Sequential: signer order 순서대로 notified → viewed → signed → 다음 signer
   Parallel:    모든 signer 동시 notified, 모두 signed 시 completed
```

규칙:

- **Phase 3 simple**: 서명 = 클릭 동의 + IP/디바이스 로그 + 도장 이미지 옵션. 법적 효력 자체 보장 X — 노무사 검토 트레일이 보조 증거.
- **Phase 4 KISA**: KisaSignature 발생. RFC 3161 타임스탬프. 인증서 검증 잡 + 사후 재검증 (1년·5년 시점).
- **`expired` 전이**: 만료 잡 (Celery). Signer 1인 이상 미완료 시 인스턴스 `void` 후보 (요청자 알림).
- **`completed` → `documents.contract.signed` 발행** → HR이 `EmployeeProfile.contract_signed_at` 갱신.

### Report 라이프사이클 (COO-5 자동 보고서)

```
   [draft] ──(데이터 수집)──> [generating] ──(모든 Tool 호출 성공)──> [generated]
                                   │                                          │
                                   └──> [failed] (한 Tool 실패)               v
                                                                       (검토 워크플로우 있으면 pending_review)
                                                                              │
                                                                              v
                                                                          [issued]
```

규칙:

- **데이터 소스 추적 (`data_source_trace[]`) 필수** — 감사·재현 위해 어떤 Tool 호출이 어떤 시점에 어떤 결과를 줬는지 기록.
- **PM/HR 데이터 변경 시 재생성 가능** (`regenerable=true`)만. `regenerable=false`는 시점 동결 (예: 분기 마감 보고서).
- 정기 스케줄링은 별도 `ReportSchedule` 엔티티 (Phase 3) — Phase 2는 수동 트리거만.

### RetentionPolicy 만료 잡

```
   매일 02:00 KST:
     find DocumentInstance where retention_expires_at <= now() AND state IN [issued, archived]
       for each:
         policy = RetentionPolicy.get(instance.retention_policy_id)
         switch policy.on_expiry:
           delete            → DocumentInstance.delete (hard delete, AuditLog 영구 기록)
           anonymize         → variables_snapshot의 PII 마스킹 + rendered_pdf 익명화 재렌더
           archive_legal_only → state → archived_legal_only (조회 차단, 법령 요청 시만 unlock)
       record AuditLog (actor=system, retention_basis=policy.legal_basis_ref)
```

규칙:

- 잡 실패 시 알람 → 보안 Admin DM. **연속 3회 실패는 차별화 깨짐 신호 (Watch List #5)**.
- `archive_legal_only` 진입 후 법령 요청 (예: 노동위원회 조회) 시 Workspace Owner + 법무 2인 승인 후 unlock.

---

## Phase별 출시 (P0/P1/P2/P3)

> 모든 기능은 [`jtbd.md`](../01-market/jtbd.md) Job ID에 매핑. ID 없는 기능은 빌드 안 한다.

### Phase 2 기본 워크플로우 (P0) — Documents 알파 (2027 H2 – 2028 H1)

| 기능                                                                   | Phase | JTBD ID      | 우선순위 | 근거                                                                                                      |
| ---------------------------------------------------------------------- | ----- | ------------ | -------- | --------------------------------------------------------------------------------------------------------- |
| DocumentTemplate CRUD + 변수 + 버전 (5개 카테고리)                     | 2     | COO-4        | P0       | Documents 도메인의 핵심 aggregate. 5개 카테고리 (노무 / 세무 / 사내 / 외부 / 보고서) 골격.                |
| DocumentInstance + 라이프사이클 (draft→pending_review→approved→issued) | 2     | COO-4        | P0       | 발급 워크플로우의 4단 핵심. Phase 2는 서명 없이 issued 가능 (PDF + 워크플로우 트레일).                    |
| ReviewWorkflow + ReviewStep + ReviewComment                            | 2     | COO-4        | P0       | 다단 검토자 라우팅. Phase 2는 sequential만 (parallel는 Phase 3).                                          |
| `hr.member.onboarded` 구독 → 근로계약서 자동 인스턴스화                | 2     | COO-3        | P0       | "신입 4명 동시 입사 반나절" Switch Trigger #4의 Documents 측 표현. HR 이벤트 → Documents 자동.            |
| `hr.member.offboarded` 구독 → 퇴직 관련 문서 자동 생성                 | 2     | IT-3         | P0       | Offboarding 자동 액션의 Documents 측 책임 (사직서 / 경위서 / 4대 보험 탈퇴 신고 후보).                    |
| RetentionPolicy 기본 + 만료 잡 (delete / anonymize)                    | 2     | (compliance) | P0       | 근로기준법 제42조 / 임금명세 5년 / 세법 5년 매트릭스. 자동 잡은 Phase 2부터 — 미준수 = 컴플라이언스 위반. |
| PDF 렌더링 (template + 변수 → PDF)                                     | 2     | COO-4        | P0       | 발급 문서의 기본 출력. 한글 폰트 보장 + 인쇄 가능 품질.                                                   |
| 카테고리별 권한 매트릭스 (노무 / 세무 / 사내 / 외부 / 보고서)          | 2     | EMO-6, IT-4  | P0       | 노무사·세무사 외부 협업자가 각 카테고리에 어떻게 접근하는지 정의. Phase 3 외부 협업자 풀 작업면의 기반.   |
| Documents 감사 로그 (Shared AuditLog)                                  | 2     | IT-4         | P0       | SOC2 Type II 준비. 모든 mutation은 AuditLog 발생.                                                         |
| `documents.generate_from_template` Tool                                | 2     | COO-3        | P0       | A2UI 첫 노출. 입사 워크플로우의 자동 액션 트리거.                                                         |
| `documents.list_pending_review` Tool                                   | 2     | COO-4        | P0       | "내가 검토할 문서" 큐 — HR Admin이 첫 사용자, Phase 3에 노무사로 확장.                                    |
| `documents.generate_report` Tool (스프린트 보고서 PDF)                 | 2     | COO-5        | P0       | COO-5 ("투자사 월간 보고서 6시간 → 30분") 직접 표현. Phase 2는 스프린트 보고서 한 종류부터.               |

### Phase 3 정식 (P1) — 노무사 검토 트레일 + Simple 서명 (2028 H2 – 2029 H1)

| 기능                                                                 | Phase | JTBD ID                  | 우선순위 | 근거                                                                                                                        |
| -------------------------------------------------------------------- | ----- | ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| **SignatureRequest + Signer (simple — Phase 3 한정)**                | 3     | COO-4                    | P1       | KISA 인증 없이 클릭 동의 + 도장 이미지. 법적 효력 보조 (노무사 검토 + AuditLog 영구). Phase 4 KISA의 사전 단계.             |
| **노무사 외부 협업자 작업면 (검토 큐 → 코멘트 → 승인 / 반려)**       | 3     | COO-4, EMO-6, Trigger #3 | P1       | [`domain-hr.md`](./domain-hr.md) 노무사 모델의 실제 작업면. **Switch Trigger #3 ("노무 이슈 카톡 유출") 해결의 직접 표현**. |
| Parallel 검토 (`parallel_group`)                                     | 3     | COO-4                    | P1       | 다중 서명자 다중 검토 시 필수. 직장 내 괴롭힘 신고 = HR + 법무 병렬 검토 같은 케이스.                                       |
| LaborDocument 인터페이스 정식 (HR ↔ Documents)                       | 3     | COO-4                    | P1       | HR `LaborDocument`는 메타, Documents `DocumentInstance`가 실체. 동기화 계약 정식.                                           |
| `hr.insurance.enrollment_submitted` 구독 → 4대 보험 신고서 자동 생성 | 3     | COO-4                    | P1       | HR Phase 3의 4대 보험 워크플로우와 정합. Documents가 PDF + 노무사 검토 트레일 발급.                                         |
| 직장 내 괴롭힘 신고서 (별도 카테고리, HR + 법무 병렬 검토)           | 3     | EMO-6                    | P1       | [`domain-hr.md`](./domain-hr.md)와 정합. 매니저 라인 우회 라우팅.                                                           |
| Report 정기 스케줄링 (`ReportSchedule`)                              | 3     | COO-5, CEO-1             | P1       | 분기 보고서 / 월간 보고서 자동. COO-5 풀 표현.                                                                              |
| HR 분기 보고서 (`report_kind=hr_quarterly`)                          | 3     | CEO-1                    | P1       | CEO-1 ("이사회 KPI 한 페이지") HR 측 입력. HR Tool 호출 + 템플릿 렌더링.                                                    |
| 보존 정책 매트릭스 정식 (법령 ID 매핑)                               | 3     | (compliance)             | P1       | 근로기준법·세법·개인정보보호법 매핑 표 정식. 보존 기간 오류 = 컴플라이언스 위반.                                            |
| 외부 컨설팅 NDA/MSA 발급 워크플로우                                  | 3     | COO-4                    | P1       | 외부 협업자 모델의 두 번째 사례 (노무사 외 외부 컨설턴트).                                                                  |
| `documents.request_signature` Tool (simple)                          | 3     | COO-4                    | P1       | A2UI 노출. Phase 4 KISA 모드는 후속.                                                                                        |
| Comms 채널 자동 게시 (사규 / 사내 공지 발급 시)                      | 3     | (운영)                   | P1       | `documents.instance.issued` 이벤트 → Comms `#announcements` 자동 게시.                                                      |

### Phase 4 (P2) — KISA 전자서명 + ezTax 완성 (2029 H2+)

| 기능                                                | Phase | JTBD ID      | 우선순위 | 근거                                                                                                                                           |
| --------------------------------------------------- | ----- | ------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **KisaSignature (자체구축 vs 모두싸인 OEM)**        | 4     | COO-4        | P2       | 차별화 축 3 완성. **자체구축 vs 모두싸인 OEM은 Phase 3 종료 시점 결정** ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5). |
| **국세청 ezTax 연동 (`EzTaxFiling`)** — 원천세      | 4     | COO-4        | P2       | Enterprise 한정. ACV 1억원+ 가격 근거.                                                                                                         |
| 국세청 ezTax 연말정산                               | 4     | COO-4        | P2       | 연 1회 폭증 워크플로우. 사전 검증 + 노무사·세무사 검토 트레일.                                                                                 |
| 국세청 ezTax 사업소득 신고                          | 4     | COO-4        | P2       | 외주 디자이너·노무사·외부 컨설턴트 사업소득 신고. Enterprise 한정.                                                                             |
| **PayrollRun (Documents 측 발급 배치)**             | 4     | COO-4        | P2       | HR `PayrollRecord` 임포트 → 임금명세서 일괄 발급. **계산은 외부 위임 ([`domain-hr.md`](./domain-hr.md) 결정과 정합)**.                         |
| 사후 인증서 재검증 잡 (1년·5년)                     | 4     | (compliance) | P2       | KISA 인증서 폐기·갱신 추적. 실패 시 Watch List 신호.                                                                                           |
| K-ISMS 인증 자료 구조 (감사 트레일 + 보존 매트릭스) | 4     | IT-4         | P2       | 미드마켓 한국 공공/대기업 진입 필수. Documents 영역의 ISMS 요구사항.                                                                           |
| 한국 리전 자체 호스팅 옵션 (Enterprise)             | 4     | IT-4         | P2       | 데이터 주권. KISA 인증 + 한국 리전 결합 ([`pricing-strategy.md`](../01-market/pricing-strategy.md) Enterprise).                                |
| `documents.request_signature` (KISA mode) Tool      | 4     | COO-4        | P2       | Phase 3 simple → Phase 4 KISA. 동일 Tool, provider 분기.                                                                                       |
| `documents.file_eztax` Tool                         | 4     | COO-4        | P2       | A2UI 노출. Enterprise + HR Admin 한정.                                                                                                         |
| 다중 외부 서명자 (counterparty, witness 포함)       | 4     | COO-4        | P2       | NDA/MSA의 외부 회사 서명자. KISA 인증 또는 외부 이메일+OTP 방식.                                                                               |

### Phase 4+ / 영구 안 함 (P3)

| 기능                                    | 결정                    | 근거                                                                                                                |
| --------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Notion식 일반 협업 문서 / 위키 / 페이지 | **영구 안 함**          | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision "5번째 도메인 확장 금지" + Notion 정면 충돌 회피. |
| 파일 드라이브 (일반 스토리지)           | **영구 안 함**          | Anti-Vision. Google Drive / Dropbox 위임.                                                                           |
| 협업 화이트보드 / 다이어그램            | **영구 안 함**          | Anti-Vision. Miro / FigJam 위임.                                                                                    |
| 영수증 / 경비 처리 (Expense Management) | Phase 4+ 또는 영구 보류 | 5번째 도메인 (스피이큐, ezAdmin) 영역.                                                                              |
| 사원증 / 명함 / 실물 발급               | Phase 4+ 보류           | 인쇄·실물 영역. ICP-3 대기업 진입 시 검토.                                                                          |
| 계약서 협상 협업 (DocuSign CLM 영역)    | Phase 4+ 보류           | 발급·서명·보존이 Phase 4까지 우선. 협상 영역은 별도 시장.                                                           |
| 자체 OCR / 번역 / 문서 인식             | Phase 4+ 보류           | 외부 (Google Document AI) 위임 또는 Phase 4 자체 vLLM 옵션.                                                         |
| 블록체인 / 분산원장 서명                | **영구 안 함**          | 한국 법령 효력 표준 KISA. 블록체인은 정합성 보조에 한정 (Phase 5+ 가능성).                                          |
| 글로벌 전자서명 (eIDAS / ESIGN Act)     | Phase 4+ 보류           | KR-first 1순위 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 4). 일본 알파 시 일본만 검토.       |
| 일반 마켓플레이스 / 템플릿 거래         | Phase 4+ 보류           | 외부 마켓플레이스 함정 회피 ([`domain-pm.md`](./domain-pm.md) 결정과 정합).                                         |

---

## API 표면 (개념 수준)

> 전체 OpenAPI 3.1 스펙은 보류 — [`04-architecture/data-model.md`](../04-architecture/data-model.md). 여기는 엔드포인트 카탈로그.

### REST 엔드포인트

| 메서드 | 경로                                          | 권한                                                   | Phase |
| ------ | --------------------------------------------- | ------------------------------------------------------ | ----- |
| GET    | `/workspaces/{ws}/document-templates`         | Member+ (카테고리별 분기)                              | 2     |
| POST   | `/workspaces/{ws}/document-templates`         | HR Admin + Workspace Owner                             | 2     |
| PATCH  | `/document-templates/{id}`                    | 작성자 + Workspace Owner                               | 2     |
| POST   | `/document-templates/{id}/publish`            | HR Admin + Workspace Owner                             | 2     |
| POST   | `/document-templates/{id}/deprecate`          | Workspace Owner                                        | 2     |
| GET    | `/workspaces/{ws}/document-instances`         | 카테고리별 권한 분기 응답                              | 2     |
| GET    | `/document-instances/{id}`                    | subject + requester + HR Admin + 외부 협업자 (지정 시) | 2     |
| POST   | `/workspaces/{ws}/document-instances`         | 카테고리별 (HR Admin 표준)                             | 2     |
| POST   | `/document-instances/{id}/submit-for-review`  | requester                                              | 2     |
| POST   | `/document-instances/{id}/render-pdf`         | 권한자 (캐시 가능)                                     | 2     |
| POST   | `/document-instances/{id}/void`               | HR Admin + 작성자 (사유 필수)                          | 2     |
| GET    | `/document-instances/{id}/versions`           | Instance 권한 동일                                     | 2     |
| GET    | `/document-instances/{id}/review-workflow`    | Instance 권한 + reviewer                               | 2     |
| POST   | `/review-workflows/{id}/steps/{sid}/approve`  | step.reviewer                                          | 2     |
| POST   | `/review-workflows/{id}/steps/{sid}/reject`   | step.reviewer (사유 필수)                              | 2     |
| POST   | `/review-workflows/{id}/comments`             | reviewer                                               | 2     |
| PATCH  | `/review-comments/{id}/resolve`               | 작성자 + 다음 step reviewer                            | 2     |
| GET    | `/workspaces/{ws}/retention-policies`         | HR Admin + 보안 Admin                                  | 2     |
| POST   | `/workspaces/{ws}/retention-policies`         | Workspace Owner                                        | 2     |
| POST   | `/document-instances/{id}/signature-requests` | requester (HR Admin)                                   | 3     |
| GET    | `/signature-requests/{id}`                    | requester + signers + Instance 권한자                  | 3     |
| POST   | `/signers/{id}/sign` (simple — Phase 3)       | signer 본인                                            | 3     |
| POST   | `/signers/{id}/decline`                       | signer 본인                                            | 3     |
| POST   | `/signers/{id}/sign-kisa` (Phase 4 — KISA)    | signer 본인                                            | 4     |
| POST   | `/signature-requests/{id}/cancel`             | requester                                              | 3     |
| GET    | `/workspaces/{ws}/eztax-filings`              | HR Admin + Enterprise                                  | 4     |
| POST   | `/workspaces/{ws}/eztax-filings`              | HR Admin + Enterprise                                  | 4     |
| POST   | `/eztax-filings/{id}/submit`                  | HR Admin (검토 후)                                     | 4     |
| GET    | `/workspaces/{ws}/payroll-runs`               | HR Admin                                               | 4     |
| POST   | `/workspaces/{ws}/payroll-runs`               | HR Admin                                               | 4     |
| POST   | `/payroll-runs/{id}/deliver`                  | HR Admin                                               | 4     |
| GET    | `/workspaces/{ws}/reports`                    | 카테고리별 권한 분기                                   | 2     |
| POST   | `/workspaces/{ws}/reports/generate`           | 카테고리별                                             | 2     |
| GET    | `/document-instances/{id}/audit-log`          | Workspace Admin                                        | 2     |

### WebSocket / SSE 이벤트 (선택적)

| 이벤트                           | 채널                             | 페이로드                                  | Phase |
| -------------------------------- | -------------------------------- | ----------------------------------------- | ----- |
| `instance.state_changed`         | `ws:{ws}/document-instance/{id}` | `from_state`, `to_state`, `actor_id`      | 2     |
| `review.step_state_changed`      | `ws:{ws}/document-instance/{id}` | `step_id`, `state`, `actor_id`            | 2     |
| `review.comment_added`           | `ws:{ws}/document-instance/{id}` | `comment_id`, `author_id`, `body_preview` | 2     |
| `signature.signer_signed`        | `ws:{ws}/signature-request/{id}` | `signer_id`, `signed_at`                  | 3     |
| `signature.completed`            | `ws:{ws}/signature-request/{id}` | `instance_id`, `completed_at`             | 3     |
| `eztax.submission_state_changed` | `ws:{ws}/eztax-filing/{id}`      | `state`, `error?`                         | 4     |

규칙:

- 모든 mutation은 `AuditLog` 발생. 노무사·세무사 액션은 `metadata.external_collaborator=true` + `actor_org_kind=labor_advisor/tax_advisor` 마킹.
- 노무사가 호출한 모든 GET / POST는 회사 측 Admin 활동 대시보드에 실시간 반영.

---

## A2UI Tool 카탈로그 (Documents 전용)

> [`domain-overview.md`](./domain-overview.md) A2UI Tool 카탈로그 v1의 Documents Tool 3개를 시작점으로 확장 (8개). 모든 Tool은 헤드리스 service 함수 + Pydantic Input/Output Schema. **호출자 권한 상속 — 노무사는 자기 담당 외 인스턴스 1건도 못 봄, A2UI 합성에서도 동일**.

| Tool                               | Input Schema 핵심 필드                                                             | Output Schema 핵심 필드                                         | Tier                                                   | Phase | JTBD ID      |
| ---------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------ | ----- | ------------ |
| `documents.list_pending_review`    | `reviewer_member_id?`, `reviewer_role?`, `category?`                               | `instances[]` with `pending_step`, `sla_deadline`               | Business+                                              | 2     | COO-4        |
| `documents.generate_from_template` | `template_id`, `subject_member_id?`, `variables`, `auto_submit_for_review?`        | `instance_id`, `state`                                          | Business+                                              | 2     | COO-3, COO-4 |
| `documents.summarize_instance`     | `instance_id`                                                                      | `summary_md`, `key_terms[]` (권한 통과 시에만)                  | Business+                                              | 2     | COO-4        |
| `documents.generate_report`        | `report_kind`, `period_start`, `period_end`, `delivery?` (preview / pdf / channel) | `report_id`, `instance_id`, `data_source_trace[]`               | Business+                                              | 2     | COO-5, CEO-1 |
| `documents.request_signature`      | `instance_id`, `signers[]`, `mode` (sequential/parallel), `provider?`              | `signature_request_id`, `state`, `notified_signer_ids[]`        | Business+ (Phase 3 simple) / Enterprise (Phase 4 KISA) | 3 / 4 | COO-4        |
| `documents.search_archive`         | `query`, `category?`, `subject_member_id?`, `date_range?`, `include_voided?`       | `instances[]` (메타데이터만, 본문 권한 통과 시)                 | Business+                                              | 2     | (운영)       |
| `documents.check_retention_due`    | `workspace_id`, `days_ahead?` (기본 30)                                            | `expiring_instances[]` with `policy`, `expires_at`, `on_expiry` | Business+                                              | 3     | (compliance) |
| `documents.file_eztax`             | `filing_kind`, `period`, `subject_employee_profile_ids?`                           | `filing_id`, `state`, `validation_errors[]`                     | **Enterprise**                                         | 4     | COO-4        |

### 도메인 횡단 Tool 진입점 — 가장 중요

[`domain-overview.md`](./domain-overview.md) A2UI 도메인 횡단 쿼리 절과 정렬. **Documents Tool은 도메인 횡단 호출에서 호출자 권한을 상속한다.**

**시나리오 1**: "이번 주 검토 대기 문서 + 노무사 SLA 임박 알림" (Switch Trigger #3와 정렬)

```
사용자 (COO): "노무사 검토 대기 중인 것 중 SLA 임박한 거 알려줘"

Agent: a2ui.cross_domain_query(intent="pending docs near SLA + advisor activity", caller=COO)
  └→ documents.list_pending_review(reviewer_role="labor_advisor", category="labor")
       returns: [{instance_id: D1, pending_step: "advisor_review", sla_deadline: "+18h"}]
  └→ hr.get_member_context(member_id=D1.subject_member_id, scope="manager")
       returns: profile, manager
  └→ AuditLog query: 노무사의 최근 활동 (24시간) 횟수 / 마지막 액션 시점
  └→ 합성: "노무사 박○○ — 18시간 내 검토 필요 문서 3건. 최근 6시간 활동 없음. 카톡 / 이메일 우회 발생 가능성 신호."
  Permission check: caller (COO)가 Documents 카테고리 labor 가시 권한 보유? Workspace Owner라면 가능.
```

**시나리오 2**: "신입 5명 입사일 + 근로계약서 발급 상태" (COO-3 직접 표현)

```
사용자 (HR Admin): "이번주 신입들 계약서 어디까지 갔어?"

Agent: a2ui.cross_domain_query(intent="onboarding contract status", caller=HR_Admin)
  └→ hr.list_onboarding(workspace_id, status="in_progress", start_date_range=this_week)
       returns: [{member_id: M3, progress_pct: 60}, ...]
  └→ for each member_id:
       documents.search_archive(subject_member_id=M3, category="labor", subtype="employment_contract")
         returns: [{instance_id: D7, state: "pending_review", pending_step: "advisor_review"}]
       documents.summarize_instance(instance_id=D7)
         Permission check: HR_Admin이 labor 카테고리 권한 보유? YES → 요약 반환
  └→ 합성 표: 입사자 / 계약서 상태 / 검토자 / SLA
```

**시나리오 3**: "지난 분기 스프린트 보고서 PDF 자동 생성" (COO-5 직접 표현)

```
사용자 (COO): "이사회용 1분기 운영 보고서 만들어줘"

Agent:
  └→ documents.generate_report(report_kind="investor_monthly", period_start=Q1_start, period_end=Q1_end, delivery="pdf")
       └→ (내부) pm.get_sprint_summary(sprint_ids=Q1_sprints)
            returns: velocity, blocker_count, member_stats
       └→ (내부) hr.list_onboarding(date_range=Q1) + hr.list_offboarding
            returns: 인원 변동
       └→ (내부) 템플릿 렌더링 (investor_monthly) → PDF
       └→ data_source_trace[] 기록 (감사·재현 위해)
       returns: {report_id, instance_id, pdf_url}
  └→ 합성: PDF 링크 + "데이터 소스 검증: PM 6건 / HR 4건 Tool 호출 — 모두 권한 통과"
  Permission check: COO가 investor_monthly 카테고리 권한 보유? YES (CEO + COO 한정).
```

**시나리오 4**: "보존 기간 임박 문서 일괄 점검" (Compliance)

```
사용자 (보안 Admin): "다음달 만료될 문서 미리 알려줘"

Agent:
  └→ documents.check_retention_due(workspace_id, days_ahead=30)
       returns: expiring_instances[] with policy, expires_at, on_expiry
  └→ 합성 표: 카테고리별 / on_expiry별 카운트 + "anonymize 처리 12건 / delete 5건 / archive_legal_only 3건"
  Permission check: 보안 Admin이 retention 조회 권한? YES.
```

### 권한 누수 방지 원칙 (가장 중요)

**A2UI가 도메인 횡단으로 Documents 데이터 합성 시 호출자 권한 상속.**

- LangGraph supervisor가 `caller_member_id`를 강제 주입 → 각 sub-tool 호출 시 Documents service가 카테고리·인스턴스 단위 권한 체크.
- **노무사 외부 협업자는 자기 담당 인스턴스만** 반환. `documents.search_archive` 호출 시 다른 클라이언트사 / 다른 사원의 문서 1건도 못 봄. AuditLog에 `external_collaborator=true` 기록.
- **세무사 외부 협업자**(Phase 4)도 동일 원칙 — ezTax 카테고리만 가시.
- 합성 단계에서가 아니라 **각 sub-tool 호출 단계에서** 권한 적용 — 메타데이터(요약, 카테고리 카운트)조차 누수 안 됨.

### Tool Registry 게이팅

- 모든 Documents Tool은 기본 **Business+ Tier 게이트** ([`pricing-strategy.md`](../01-market/pricing-strategy.md) HR/문서 도메인 Business 이상 노출).
- `documents.file_eztax` / `documents.request_signature` (Phase 4 KISA mode)는 **Enterprise 한정** — ACV 1억원+ 가격 근거.
- `documents.request_signature` (Phase 3 simple mode)는 **HR Admin 권한 추가 필요** (Tier + Role 동시).
- 게이트는 `tool_registry.yaml` 한 곳에서만 강제. service 함수 안에 박지 않음 ([`domain-overview.md`](./domain-overview.md) Watch List #2).

---

## 노무사 외부 협업자 작업면 (HR과의 인터페이스)

[`domain-hr.md`](./domain-hr.md) 노무사 외부 협업자 모델이 **권한·시트·감사 정책**을 정의한다면, Documents 도메인은 **노무사가 실제로 일하는 작업면**을 정의한다. 중복 책임 금지 — Documents 측면만 정의.

### 인터페이스 계약 (HR ↔ Documents)

| 역할        | HR이 정의                                                                              | Documents가 정의                                                                                                     |
| ----------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 권한 발급   | `RoleAssignment.resource_type='documents.review'` + 지정 EmployeeProfile/카테고리 범위 | 권한 체크 진입점 (모든 service 함수의 caller_member_id 검증)                                                         |
| 가입·회수   | 시트 발급 / 1-click 회수 / 멀티 클라이언트 모델                                        | 회수 시 5초 이내 WebSocket 연결 종료 + 다음 API 401                                                                  |
| 검토 큐잉   | LaborDocument.kind / InsuranceEnrollment.event_kind에 따라 자동 큐잉 트리거 이벤트     | `documents.list_pending_review` Tool로 큐 노출 + Comms 알림 라우팅                                                   |
| 검토 액션   | (없음 — HR은 트리거만)                                                                 | **승인 / 반려 / 코멘트 / 본문 수정 제안 / 보충 자료 요청** 4가지 액션                                                |
| 감사 트레일 | AuditLog의 `external_collaborator=true` 마킹 책임 정의                                 | 모든 액션을 실시간 기록 + 회사 Admin 활동 대시보드 ↻ Comms 외부 협업자 채널과 정합                                   |
| SLA / 알림  | (없음 — Documents가 관리)                                                              | step.requires_approval 시 SLA 7일 기본. 임박 시 reviewer DM (Comms 외부 협업자 채널) + 초과 시 HR Admin 에스컬레이션 |

### 노무사 작업 흐름 (Documents 측면)

```
1. HR Admin이 LaborDocument.kind=employment_contract / agreed_termination 등 트리거
   → `hr.labor_document.review_requested` 이벤트 발행
2. Documents가 이벤트 구독 → ReviewWorkflow + ReviewStep 자동 생성
   - reviewer_role = labor_advisor
   - reviewer_member_id = HR이 지정한 외부 협업자 Member ID
   - SLA 7일
3. 노무사가 받는 알림 (Comms 외부 협업자 채널 또는 이메일 DM):
   - "검토 요청: [회사명] 권고사직 합의서 / SLA 6일 23시간 남음"
4. 노무사가 Conflow 외부 협업자 모드로 로그인 → Documents 검토 큐 진입
   - `documents.list_pending_review(reviewer_role="labor_advisor")` 응답
5. 노무사 작업면 (Documents UI):
   - 본문 + 인라인 코멘트 + 변수 검증 + 법령 매핑 ([`domain-hr.md`](./domain-hr.md) check_labor_compliance Tool 노출)
   - 액션: [승인] / [반려 + 사유] / [코멘트 추가] / [보충 자료 요청 (HR Admin DM)]
6. 노무사 승인 → ReviewStep.state=approved → 다음 단계 (서명 또는 issued)
   - Phase 4 KISA: SignatureRequest 자동 발생, 노무사가 witness 역할로 KISA 서명 옵션
7. 모든 액션이 AuditLog에 external_collaborator=true 기록
   → 회사 Admin 활동 대시보드에 실시간 표시
```

### "이게 깨지면" — Switch Trigger #3 미해결

[`domain-hr.md`](./domain-hr.md) Watch List와 정합. Documents 측의 추가 신호:

- **노무사가 작업면에 들어와도 5분 이내 첫 액션 안 함** → UI 학습 곡선 5분 컷 약속 (EMO-6) 깨짐.
- **노무사 검토 SLA 초과율 > 20%** → 외부 카톡/이메일 우회 신호.
- **노무사 활동 99% 이상이 Conflow 안에서** ([`domain-hr.md`](./domain-hr.md) Switch Trigger #3 정량 기준) — 미달 시 차별화 무력화.

---

## 보고서 자동 생성 (PM/HR 데이터 횡단)

### 책임 분할

- **Documents 소유**: 보고서 템플릿 (`DocumentTemplate.category=report`), Report 인스턴스 + 라이프사이클, PDF 렌더링, 정기 스케줄링 (Phase 3 `ReportSchedule`).
- **다른 도메인 책임**: 데이터 — PM은 `pm.get_sprint_summary` / `pm.identify_blockers` 노출, HR은 `hr.list_onboarding` / `hr.summarize_one_on_ones` 노출, Comms는 `comms.summarize_channel` 노출.

### 보고서 카테고리 (Phase 2-3)

| `report_kind`      | 데이터 소스 (Tool 호출)                                                                       | 권한                   | Phase |
| ------------------ | --------------------------------------------------------------------------------------------- | ---------------------- | ----- |
| `sprint_report`    | `pm.get_sprint_summary` + `pm.identify_blockers` + `comms.summarize_channel` (선택)           | Member+ (Project 단위) | 2     |
| `investor_monthly` | `pm.get_sprint_summary` 분기 / `hr.list_onboarding` 분기 / `comms.extract_decisions`          | CEO + COO 한정         | 2     |
| `hr_quarterly`     | `hr.list_onboarding` / offboarding / `hr.list_evaluation_progress` / labor compliance summary | HR Admin               | 3     |
| `labor_compliance` | `hr.check_labor_compliance` (모든 워크플로우) + 노무사 외부 협업자 활동률                     | HR Admin + 노무사      | 3     |
| `eztax_year_end`   | `documents.file_eztax(year_end_settlement)` 사전 검증 + HR PayrollRecord                      | HR Admin + Enterprise  | 4     |

### 데이터 소스 추적 (감사·재현)

- `Report.data_source_trace[]`에 **호출된 Tool / 입력 인자 / 응답 해시 / 호출 시점** 기록.
- 재생성 가능 (`regenerable=true`) 보고서는 같은 시점 입력으로 동일 결과 재현 가능해야 함.
- 시점 동결 (`regenerable=false`) 보고서는 분기 마감 / 연말정산 같은 케이스. PDF + trace[] 영구 보존.

### "보고서를 위해 Documents가 데이터를 캐싱하지 않는다"

이게 [`domain-overview.md`](./domain-overview.md) 단일 데이터 모델 원칙의 Documents 측 표현. Documents가 PM 이슈 데이터를 자체 테이블에 저장하면 **데이터 정합성 + 권한 누수 + 5번째 도메인 확장 압력**이 한꺼번에 발생. 매 보고서 생성마다 권한 통과한 Tool 호출 → 합성 → PDF만.

---

## 한국 법정 컴플라이언스 매핑

> 법령은 구체적으로 — _법률 자문은 아님, 워크플로우 결정만_. 실제 적용 시 노무사·세무사·법무 검토 필수.

### 보존 정책 매트릭스 (Phase 2 기본 / Phase 3 정식)

| 문서 카테고리·서브타입               | 법령 / 근거                              | 보존 기간 | 보존 기준점     | 만료 시 동작                        | Phase |
| ------------------------------------ | ---------------------------------------- | --------- | --------------- | ----------------------------------- | ----- |
| 근로계약서 / 사직서                  | 근로기준법 제42조                        | 3년       | 근로관계 종료일 | anonymize → 5년 후 delete           | 2     |
| 임금명세서                           | 근로기준법 제48조 (2021 개정)            | 5년       | 발급일          | delete                              | 2     |
| 권고사직 합의서 / 해고예고통지서     | 근로기준법 제23조 / 제27조 / 노위 분쟁용 | 3년+      | 근로관계 종료일 | archive_legal_only (분쟁 시 unlock) | 3     |
| 4대 보험 신고서 (가입 / 탈퇴 / 변경) | 국민건강보험법 등                        | 5년       | 신고일          | delete                              | 3     |
| 원천징수영수증                       | 국세기본법 / 소득세법                    | 5년       | 회계연도 종료일 | delete                              | 3     |
| 연말정산 자료                        | 소득세법                                 | 5년       | 회계연도 종료일 | delete                              | 4     |
| 직장 내 괴롭힘 신고서                | 근로기준법 제76조의2                     | 3년+      | 사건 종결일     | archive_legal_only                  | 3     |
| 휴가 진단서 (병가)                   | 개인정보보호법 (민감정보)                | 1년       | 휴가 종료일     | delete (즉시)                       | 3     |
| 재직증명서                           | (발급 사실만 AuditLog)                   | 1년       | 발급일          | delete                              | 2     |
| NDA / MSA (외부 컨설팅)              | 민법 / 계약법                            | 10년      | 계약 종료일     | archive_legal_only                  | 3     |
| 사규 / 사내 공지문                   | (사내 정책)                              | 영구      | 폐지일까지      | (안 함)                             | 2     |
| 스프린트 보고서 / 투자사 월간 보고서 | (운영)                                   | 7년       | 발행일          | delete                              | 2     |

규칙:

- 각 `RetentionPolicy` 인스턴스는 `legal_basis_ref` 필드에 법령 ID (예: "근로기준법 제42조") 기록 — 감사 시 즉시 확인.
- 법령 개정 시 정책 갱신 의무 — `04-architecture/security-compliance.md`에 갱신 책임자 명시.
- **`anonymize` 동작**: PII (이름, 주민번호, 주소, 전화) 마스킹 + PDF 재렌더. 본문 구조는 보존 (통계·감사용).
- **`archive_legal_only` 동작**: 조회 차단, 법령 요청 시 Workspace Owner + 법무 2인 승인 후 unlock + 추가 AuditLog.

### KISA 전자서명 (Phase 4)

| 측면             | Phase 3 simple                                        | Phase 4 KISA                                                                                     |
| ---------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 인증 방식        | 클릭 동의 + IP / 디바이스 로그 + 도장 이미지          | KISA 인증서 (공인전자서명 또는 인정전자서명) + RFC 3161 타임스탬프                               |
| 법적 효력        | 일반 계약 효력 (전자문서법) + 노무사 검토 트레일 보조 | **공인전자서명 효력** — 위·변조 부인 불가, 법정 증거 채택                                        |
| 자체구축 vs 외주 | (해당 없음)                                           | **Phase 3 종료 시점 결정** ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5) |
| 사후 검증        | 단순 로그 보관                                        | 1년 / 5년 시점 인증서 재검증 잡 — 폐기·갱신 추적                                                 |
| 외부 서명자 지원 | 이메일 + OTP 한정                                     | 외부 KISA 인증서 보유 시 풀 지원 (NDA / MSA 풀 케이스)                                           |
| Tier             | Business+ HR Admin                                    | **Enterprise 한정** — ACV 1억원+ 근거                                                            |

### 국세청 ezTax 연동 (Phase 4 Enterprise)

| Filing Kind                    | 빈도           | 데이터 소스                                   | 노무사 / 세무사 검토 의무 | 정확도 임계치 |
| ------------------------------ | -------------- | --------------------------------------------- | ------------------------- | ------------- |
| 원천세 (withholding_monthly)   | 월 1회         | HR PayrollRecord                              | 권장                      | 99%+          |
| 연말정산 (year_end_settlement) | 연 1회 (1-2월) | HR PayrollRecord 누적 + 사원 자료 (사후 제출) | **필수**                  | 99.5%+        |
| 사업소득 (business_income)     | 분기 / 연      | 외부 컨설팅 NDA / MSA + 송금 기록             | **필수**                  | 99%+          |

- ezTax API 변경 추적 — Phase 4 운영 정책. 국세청 시스템 변경 시 24시간 안 어댑터 패치 의무.
- 정확도 < 99% 발견 시 차별화 깨짐 신호 (Watch List #2와 정렬).

### K-ISMS 인증 (Phase 4)

- Documents 영역의 K-ISMS 요구사항: 감사 트레일 / 보존 매트릭스 / 외부 협업자 접근 통제 / 인증서 관리 / 보안 사고 대응 절차.
- Documents가 통합 `AuditLog` + `RetentionPolicy` + 외부 협업자 모델로 4개 영역 충족.
- 한국 리전 자체 호스팅 옵션 (Enterprise) — KISA 인증서 보관 / ezTax 통신 / 임금명세서 PDF 모두 한국 리전 보장.

---

## 프라이버시 / 권한 모델

[`domain-overview.md`](./domain-overview.md) Role 5개의 Documents 특화 적용. **Documents는 법정 효력 문서 + 민감 개인정보를 다루는 도메인 — 카테고리·인스턴스 단위 권한이 핵심**.

### 카테고리별 권한 매트릭스

| 카테고리                              | Owner      | Admin (HR) | Member (subject) | Member (타인)   | Guest | External (노무사) | External (세무사 Phase 4) |
| ------------------------------------- | ---------- | ---------- | ---------------- | --------------- | ----- | ----------------- | ------------------------- |
| labor (근로계약 등)                   | O          | O          | O (본인 대상)    | X               | X     | 지정 인스턴스만   | X                         |
| tax (원천세 등)                       | O          | O          | O (본인 대상)    | X               | X     | X                 | 지정 인스턴스만 (Phase 4) |
| internal_issuance (사규 / 재직증명서) | O          | O          | O (본인 발급 시) | X (사규는 read) | X     | X                 | X                         |
| external_submission (NDA / MSA)       | O          | O          | O (본인 서명 시) | X               | X     | X                 | X                         |
| report (스프린트 / 투자사 / HR)       | 카테고리별 | 카테고리별 | X                | X               | X     | X                 | X                         |

### Role × 카테고리 추가 세부

- **investor_monthly 보고서**: CEO + COO 한정. Workspace Admin도 자동 X — 명시적 권한 부여 필요.
- **labor_compliance 보고서**: HR Admin + 노무사 (지정 시).
- **eztax_year_end 보고서**: HR Admin + 세무사 (Phase 4 지정 시) + Enterprise.
- **1:1 노트 export**: HR 책임 ([`domain-hr.md`](./domain-hr.md)) — Documents 안 거침.
- **직장 내 괴롭힘 신고서**: 신고자 본인 + HR Admin (지정자만, 매니저 라인 우회) + 법무 (지정 시). 일반 HR Admin은 자동 X.

### Subject Member의 권한 (자기 자신의 문서)

- **읽기**: 자기 대상 모든 문서 — 단 본문 가시 시점은 state에 따라:
  - `pending_review`: variables_snapshot 일부만 가시 (검토 단계 비공개 옵션)
  - `signed` / `issued`: 본문 풀 가시
- **수정**: signer인 경우 자기 서명 단계만. 본문 수정은 안 됨 (`void` 후 재발행).
- **삭제**: 본인 요청 → HR Admin 승인 워크플로우 (단 법정 보존 기간 내는 거부).

### 외부 협업자 권한 (노무사 / 세무사)

- **카테고리 가시성**: 노무사 = labor 카테고리만, 세무사 = tax 카테고리만. 다른 카테고리 0 노출.
- **인스턴스 단위 권한**: HR이 발급한 `RoleAssignment.resource_type='documents.review'`로 지정된 인스턴스만. 다른 인스턴스 검색·조회 0.
- **본문 수정**: 코멘트만 가능. 본문 직접 수정 X (수정 제안은 가능 — HR Admin이 적용).
- **다운로드**: PDF 다운로드 가능 (워터마크 + AuditLog). 회사 측 Admin이 다운로드 활동 가시.
- **회수**: HR Admin 1-click → 5초 이내 access 차단 ([`domain-hr.md`](./domain-hr.md) 보장).

### GDPR / 개인정보보호법 매핑 (Documents 측)

| 요구사항                | Conflow Documents 대응                                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 정보주체 삭제 요청      | DocumentInstance 단위 `anonymize` 잡 (법정 보존 기간 만족 시 hard delete). 사용자 요청 시 90일 이내 처리 의무.         |
| 보존 기간 자동 적용     | `RetentionPolicy` + 만료 잡. 법령 ID 매핑 필수.                                                                        |
| 노무사·세무사 동의 모델 | 외부 협업자 시트 발급 시 회사 측 동의 + 사원 개별 동의 (필요 시 InsuranceEnrollment 단위) + 노무사 활동 AuditLog 가시. |
| 의료 정보 (병가 진단서) | 별도 카테고리 + 1년 보존 + 즉시 delete + 본인 + HR Admin 한정 가시.                                                    |
| 외부 서명자 PII         | Phase 4 외부 서명자 이메일 / 전화는 별도 컬럼 + 서명 완료 후 90일 보존 → 해시화.                                       |
| 데이터 이동권           | 자기 대상 모든 문서를 ZIP + JSON 메타로 export (본인 요청 시 30일 이내).                                               |

### "이게 깨지는 신호" — 방어

| 신호                                                                                 | 방어                                                                                                                         |
| ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| 노무사가 자기 담당 외 카테고리 / 인스턴스 1건이라도 조회 가능                        | Switch Trigger #3 약속 깨짐. 즉시 회로 차단 + 외부 협업자 모드 회귀 테스트 추가 + 사후 audit.                                |
| 보존 만료 잡 연속 3회 실패                                                           | 컴플라이언스 위반 직전. 즉시 알람 → 보안 Admin DM + 수동 점검.                                                               |
| `signed` 이후 본문이 변경된 흔적 발견                                                | 법적 효력 직접 위협. 즉시 인스턴스 freeze + 사후 audit + Workspace Owner 알림.                                               |
| KISA 인증서 사후 검증 실패율 > 1%                                                    | 차별화 축 3 약속 위협. 즉시 KISA 인증서 발급사 점검 + Phase 4 모두싸인 OEM 백업 검토.                                        |
| 카테고리 권한 행렬이 service 함수 안에 흩어짐                                        | 단일 권한 모델 원칙 위반. 즉시 RoleAssignment 진입점으로 통합.                                                               |
| 보고서 자동 생성에서 권한 없는 데이터 노출 (예: 일반 Member의 investor_monthly 접근) | A2UI 권한 누수 — circuit breaker로 Tool 정지 + 사후 audit ([`domain-overview.md`](./domain-overview.md) Watch List #6 직결). |
| ezTax 제출 정확도 < 99%                                                              | Enterprise 약속 위협. 즉시 제출 중단 + 노무사·세무사 수동 모드로 격하.                                                       |

---

## 이벤트 발행 / 구독

### Documents가 발행하는 이벤트

| 이벤트                                | Phase | 페이로드 핵심 필드                                                             | 구독 도메인                                                    |
| ------------------------------------- | ----- | ------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| `documents.template.published`        | 2     | `template_id`, `category`, `subtype`, `version`                                | A2UI                                                           |
| `documents.template.deprecated`       | 2     | `template_id`, `reason?`                                                       | A2UI                                                           |
| `documents.instance.created`          | 2     | `instance_id`, `template_id`, `subject_member_id?`, `requester_member_id`      | A2UI, AuditLog                                                 |
| `documents.instance.review_requested` | 2     | `instance_id`, `workflow_id`, `reviewer_role`, `reviewer_member_id?`           | Comms (reviewer DM), HR, A2UI                                  |
| `documents.review.step_started`       | 2     | `instance_id`, `step_id`, `reviewer_role`, `sla_deadline`                      | Comms (reviewer DM 알림), A2UI                                 |
| `documents.review.step_completed`     | 2     | `instance_id`, `step_id`, `state` (approved/rejected), `actor_id`              | A2UI                                                           |
| `documents.review.completed`          | 2     | `instance_id`, `workflow_id`, `outcome` (approved/rejected), `total_steps`     | HR (LaborDocument 동기), A2UI                                  |
| `documents.review.rejected`           | 2     | `instance_id`, `step_id`, `reason`, `actor_id`                                 | HR, A2UI                                                       |
| `documents.review.comment_added`      | 2     | `instance_id`, `comment_id`, `author_id`                                       | **A2UI 한정**                                                  |
| `documents.instance.issued`           | 2     | `instance_id`, `category`, `subject_member_id?`, `issued_at`                   | Comms (subject DM 알림), HR (LaborDocument 동기), A2UI         |
| `documents.instance.voided`           | 2     | `instance_id`, `reason`, `actor_id`                                            | HR, A2UI, AuditLog                                             |
| `documents.signature.requested`       | 3     | `signature_request_id`, `instance_id`, `mode`, `signer_count`                  | Comms (signer DM), A2UI                                        |
| `documents.signer.notified`           | 3     | `signature_request_id`, `signer_id`, `notification_channel`                    | A2UI                                                           |
| `documents.signer.signed`             | 3     | `signature_request_id`, `signer_id`, `signed_at`                               | A2UI                                                           |
| `documents.signer.declined`           | 3     | `signature_request_id`, `signer_id`, `reason?`                                 | HR, Comms, A2UI                                                |
| `documents.signature.completed`       | 3     | `signature_request_id`, `instance_id`, `completed_at`                          | HR, A2UI                                                       |
| `documents.contract.signed`           | 4     | `document_id`, `signer_member_id`, `signed_at`, `document_type`                | HR (`EmployeeProfile.contract_signed_at` 갱신), AuditLog, A2UI |
| `documents.kisa.signed`               | 4     | `signature_request_id`, `signer_id`, `kisa_signature_id`, `certificate_serial` | A2UI, AuditLog                                                 |
| `documents.kisa.verification_failed`  | 4     | `kisa_signature_id`, `failure_reason`, `verified_at`                           | 보안 Admin DM, A2UI                                            |
| `documents.retention.policy_updated`  | 2     | `policy_id`, `delta`                                                           | A2UI, AuditLog                                                 |
| `documents.retention.expired`         | 2     | `instance_id`, `on_expiry`, `executed_action`                                  | A2UI, AuditLog                                                 |
| `documents.eztax.submitted`           | 4     | `filing_id`, `filing_kind`, `period`                                           | A2UI                                                           |
| `documents.eztax.acknowledged`        | 4     | `filing_id`, `eztax_submission_id`, `acknowledged_at`                          | HR, A2UI                                                       |
| `documents.eztax.rejected`            | 4     | `filing_id`, `error_blob`                                                      | HR, 보안 Admin DM, A2UI                                        |
| `documents.payroll.processed`         | 4     | `payroll_run_id`, `period`, `member_count`, `total_amount`                     | HR (`PayrollRecord.state` paid 전이), A2UI                     |
| `documents.payroll.delivered`         | 4     | `payroll_run_id`, `delivered_at`, `total_count`                                | Comms (subject DM 알림), A2UI                                  |
| `documents.report.generated`          | 2     | `report_id`, `instance_id`, `report_kind`, `data_source_trace_summary`         | A2UI                                                           |

### Documents가 구독하는 이벤트

| 이벤트                                  | 발행 도메인 | Documents의 반응                                                                             | Phase |
| --------------------------------------- | ----------- | -------------------------------------------------------------------------------------------- | ----- |
| `hr.member.onboarded`                   | HR          | 근로계약서 자동 인스턴스화 (`employment_contract` 템플릿 + 본인 변수). pending_review 상태.  | 2     |
| `hr.member.offboarded`                  | HR          | 퇴직 관련 문서 후보 큐잉 (사직서 / 경위서 / 4대 보험 탈퇴 신고서 / 임금정산 명세서).         | 2     |
| `hr.onboarding.step_completed`          | HR          | `kind=document_sign`인 step의 인스턴스 진행 상태 동기.                                       | 2     |
| `hr.offboarding.started`                | HR          | `requires_labor_review=true`면 관련 문서 (권고사직 합의서 등) 자동 인스턴스화 + 노무사 검토. | 2     |
| `hr.labor_document.review_requested`    | HR          | LaborDocument.kind에 따라 ReviewWorkflow 생성 + 노무사 reviewer 지정.                        | 3     |
| `hr.insurance.enrollment_submitted`     | HR          | 4대 보험 신고서 PDF 자동 생성 + 노무사 검토 워크플로우. Phase 4 EDI 자동화 대상.             | 3     |
| `hr.payroll.imported`                   | HR          | PayrollRun 생성 → 임금명세서 일괄 발급 (Phase 4).                                            | 4     |
| `pm.sprint.ended`                       | PM          | `sprint_report` 자동 보고서 생성 (옵션, ReportSchedule에 등록된 워크스페이스).               | 2     |
| `comms.decision.detected` (특수 케이스) | Comms       | 직장 내 괴롭힘 신고 채널 메시지 → `harassment_report` 인스턴스 후보 큐잉.                    | 3     |

규칙:

- **`documents.contract.signed`는 HR에 동기 전달** — `EmployeeProfile.contract_signed_at` + `OnboardingStep(document_sign)` 갱신이 입사 절차 완료의 조건.
- **`documents.retention.expired`는 AuditLog 영구** — 컴플라이언스 증거.
- **`documents.review.comment_added` 페이로드는 코멘트 본문 포함 X** — A2UI는 ID만 받고, 본문 가시는 권한 통과한 호출자만.
- 이벤트 핸들러는 모두 idempotent ([`domain-overview.md`](./domain-overview.md) 규칙).
- HR → Documents 단방향 ([`domain-overview.md`](./domain-overview.md) 의존 다이어그램). Documents가 HR을 직접 mutate 하지 않음.

---

## 외부 시스템 연동 전략

### Phase 2 (기본)

| 시스템                   | 용도                          | 접근 방식                                                                 | 한계 / 결정 시점                              |
| ------------------------ | ----------------------------- | ------------------------------------------------------------------------- | --------------------------------------------- |
| **PDF 렌더링 엔진**      | DocumentInstance → PDF        | WeasyPrint 또는 Playwright (HTML → PDF). 한글 폰트 (NotoSansKR) 보장.     | Phase 2 가설. 성능·품질 검증 후 Phase 3 결정. |
| **객체 스토리지**        | PDF 보존                      | S3 호환 (AWS S3 / 한국 리전은 NCP / KT Cloud). 서명된 URL 만료 시간 분리. | Enterprise 자체 호스팅 옵션 Phase 4.          |
| **Celery + APScheduler** | 보존 만료 잡 / 정기 보고서 잡 | CLAUDE.md 기존 구조 활용.                                                 | Phase 4에서 잡 규모 1만건+ 시 큐 분리.        |

### Phase 3 (정식)

| 시스템                        | 용도                                 | 접근 방식                                                              | 한계 / 결정 시점                  |
| ----------------------------- | ------------------------------------ | ---------------------------------------------------------------------- | --------------------------------- |
| **Simple 서명 (Phase 3)**     | 클릭 동의 + 도장 이미지              | 자체 구현. IP / 디바이스 로그. 도장 이미지 PNG/SVG 보관.               | Phase 4 KISA 전 사전 단계.        |
| **이메일 발송 (외부 서명자)** | SES / Mailgun / 한국 SaaS            | 외부 협업자 알림. Phase 4 외부 KISA 서명자 OTP.                        | 한국 시장 발송 안정성 검토.       |
| **노무사 검토 SLA 알림**      | Comms 외부 협업자 채널 + 이메일      | Comms 도메인 위임. Documents는 트리거만.                               |                                   |
| **법령 매핑 데이터**          | RetentionPolicy.legal_basis_ref 표시 | 정적 JSON / DB seed. 법령 개정 시 수동 갱신 (운영 프로세스 정의 필요). | 자동 추적 시스템은 Phase 4+ 검토. |

### Phase 4

| 시스템                                     | 용도                                       | 결정                                                                                                                         |
| ------------------------------------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **KISA 전자서명**                          | 공인전자서명 + RFC 3161 타임스탬프         | **자체구축 vs 모두싸인 OEM** — Phase 3 종료 시점 결정 ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5). |
| **모두싸인 / 도큐사인 OEM (대안)**         | KISA 자체구축 대안                         | API 어댑터 패턴. Provider 추상화 (`SignatureProvider` 인터페이스) — Phase 3 simple 단계에서 미리 추상화 구축.                |
| **국세청 ezTax API**                       | 원천세 / 연말정산 / 사업소득               | Enterprise 한정. ezTax API 변경 추적 운영 프로세스 정의 필수.                                                                |
| **외부 KISA CA**                           | 외부 서명자 인증서 검증                    | KISA 공인인증기관 (한국정보인증, 한국전자인증 등). 인증서 검증 + CRL/OCSP 응답 캐싱.                                         |
| **K-ISMS 인증 도구**                       | 감사 트레일 + 보존 매트릭스 자동 추출      | 인증 자료 자동 생성 잡 (분기 1회).                                                                                           |
| **한국 리전 자체 호스팅**                  | Enterprise 데이터 주권                     | NCP / KT Cloud / 자체 IDC. PDF 보존 / KISA 서명 / ezTax 통신 모두 한국 리전.                                                 |
| **외부 ADP / Flex / 노무사 시스템 임포트** | HR PayrollRecord 임포트 후 임금명세서 발급 | HR 도메인 위임 ([`domain-hr.md`](./domain-hr.md)). Documents는 발급만.                                                       |

### "안 한다" 결정

- **자체 OCR / 번역 / 문서 인식** — Phase 4+ 보류. 외부 (Google Document AI / Naver Clova OCR) 위임 또는 Phase 4 자체 vLLM 옵션.
- **글로벌 전자서명 (eIDAS / ESIGN Act)** — KR-first 1순위 ([`product-vision.md`](../00-vision/product-vision.md) 불변 원칙 4). 일본 알파 시 일본 PIPA·전자서명법만 검토.
- **블록체인 / 분산원장 서명** — 영구 안 함. 한국 법령 효력 표준 KISA 우선.
- **자체 KISA CA 구축** — 영구 안 함. KISA 인증 사업자 자격 취득 비용 + 규제 부담이 SaaS 경제성 파괴.
- **계약서 협상 협업 (DocuSign CLM 영역)** — Phase 4+ 보류. 발급·서명·보존이 우선.

---

## 차별화 깨짐 신호 (Watch List)

| #   | 신호                                                                                          | 그러면 무엇을 한다                                                                                                                                                      |
| --- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **노무사 외부 협업자 권한 누수** (다른 클라이언트사 / 다른 사원의 문서 1건이라도 노출)        | Switch Trigger #3 약속 깨짐. **즉시 회로 차단** + 사후 audit + 외부 협업자 모드 회귀 테스트 추가. [`domain-hr.md`](./domain-hr.md) Watch List #2와 직결.                |
| 2   | **ezTax 제출 정확도 < 99%** (Phase 4)                                                         | Enterprise 약속 위협. 즉시 제출 중단 + 노무사·세무사 수동 모드로 격하. ACV 1억원+ 근거 무너짐.                                                                          |
| 3   | **KISA 인증서 사후 검증 실패율 > 1%** (Phase 4)                                               | 차별화 축 3 약속 위협. KISA 인증서 발급사 점검 + Phase 4 모두싸인 OEM 백업 검토 + 사후 audit.                                                                           |
| 4   | **보존 만료 잡 연속 3회 실패**                                                                | 컴플라이언스 위반 직전. 즉시 알람 → 보안 Admin DM + 수동 점검 + 잡 재설계.                                                                                              |
| 5   | **보존 기간이 법정과 충돌** (예: 임금명세 5년 미만 삭제, 노동관계 서류 3년 미만 익명화)       | 컴플라이언스 위반. 즉시 RetentionPolicy 점검 + 법정 보존 기간 자동 계산 룰 강화. [`domain-hr.md`](./domain-hr.md) Watch List #5와 직결.                                 |
| 6   | **`signed` 이후 본문 변경 흔적 발견**                                                         | 법적 효력 직접 위협. 즉시 인스턴스 freeze + 사후 audit + Workspace Owner 알림 + DocumentVersion append-only 정책 점검.                                                  |
| 7   | **노무사 검토 SLA 초과율 > 20%** (Phase 3)                                                    | Switch Trigger #3 약속 위협 — 외부 카톡/이메일 우회 신호. 노무사 UX 점검 + SLA 임박 알림 강화 + 노무사 인터뷰.                                                          |
| 8   | **노무사가 작업면 첫 액션까지 > 5분** (Phase 3)                                               | EMO-6 약속 ("노무사 권한 학습 5분 컷") 깨짐. UI 단순화 + 권한 학습 도움말 강화.                                                                                         |
| 9   | **카테고리 권한 행렬이 service 함수 안에 흩어짐**                                             | 단일 권한 모델 원칙 위반. 즉시 RoleAssignment 진입점으로 통합. [`domain-overview.md`](./domain-overview.md) Watch List #2와 직결.                                       |
| 10  | **보고서가 PM/HR 데이터를 캐싱 저장**                                                         | 단일 데이터 모델 원칙 위반 — 데이터 정합성 + 권한 누수 + 5번째 도메인 압력. 즉시 캐시 제거 + Tool 호출 패턴으로 회복.                                                   |
| 11  | **Documents가 일반 협업 문서 / 위키 / 페이지 기능 추가 압력**                                 | [`product-vision.md`](../00-vision/product-vision.md) Anti-Vision "5번째 도메인 확장 금지" 위반 신호. 거절 + 영업에 Anti-Vision 재전달.                                 |
| 12  | **Documents service 함수가 React 컴포넌트 import**                                            | 헤드리스 원칙 깨짐. A2UI Tool 등록 불가능. 즉시 리팩토링.                                                                                                               |
| 13  | **Documents가 HR 또는 PM 테이블 직접 JOIN**                                                   | 도메인 경계 침식. `EntityLink` + Tool 호출로 강제 리팩토링.                                                                                                             |
| 14  | **A2UI 보고서 자동 생성에서 권한 없는 데이터 노출** (예: 일반 Member의 investor_monthly 접근) | A2UI 권한 누수 — circuit breaker로 Tool 정지 + 사후 audit. [`domain-overview.md`](./domain-overview.md) Watch List #6 직결.                                             |
| 15  | **KISA 자체구축 12개월+ 지연 + 모두싸인 OEM 거부**                                            | 차별화 축 3 약속 완성 실패 ([`product-vision.md`](../00-vision/product-vision.md) Watch List #5). 제3 옵션 (한국전자인증 등 다른 사업자) 긴급 검토 + Phase 4 출시 연기. |

---

## 의도적 보류 (Open Decisions)

명시적으로 **안 한다** 또는 **누가 묻기 전에 확정한** 결정들.

| 결정                                                               | 시점                                                                                                                        | 근거                                                                                    |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Notion식 일반 협업 문서 / 위키 / 페이지                            | **영구 안 함**                                                                                                              | Anti-Vision + Notion 정면 충돌 회피.                                                    |
| 파일 드라이브 (일반 스토리지)                                      | **영구 안 함**                                                                                                              | Google Drive / Dropbox 위임.                                                            |
| 협업 화이트보드 / 다이어그램                                       | **영구 안 함**                                                                                                              | Miro / FigJam 위임.                                                                     |
| 자체 OCR / 번역 / 문서 인식                                        | Phase 4+ 보류                                                                                                               | 외부 위임. Phase 4 자체 vLLM 옵션 검토.                                                 |
| 영수증 / 경비 처리 (Expense Management)                            | Phase 4+ 또는 영구 보류                                                                                                     | 5번째 도메인 영역.                                                                      |
| 사원증 / 명함 / 실물 발급                                          | Phase 4+ 보류                                                                                                               | 인쇄·실물. ICP-3 대기업 진입 시 검토.                                                   |
| 계약서 협상 협업 (DocuSign CLM)                                    | Phase 4+ 보류                                                                                                               | 발급·서명·보존이 우선.                                                                  |
| 블록체인 / 분산원장 서명                                           | **영구 안 함**                                                                                                              | KISA 표준. Phase 5+ 가능성만 열림.                                                      |
| 글로벌 전자서명 (eIDAS / ESIGN Act)                                | Phase 4+ 보류                                                                                                               | KR-first 1순위.                                                                         |
| 자체 KISA CA 구축                                                  | **영구 안 함**                                                                                                              | 규제 부담 SaaS 경제성 파괴.                                                             |
| 외부 마켓플레이스 / 템플릿 거래                                    | Phase 4+ 보류                                                                                                               | Atlassian 마켓플레이스 함정 회피.                                                       |
| Phase 2에서 전자서명                                               | Phase 3 simple → Phase 4 KISA로 미룸                                                                                        | Phase 2는 워크플로우 트레일 + PDF까지. 서명 없이 issued 가능 — 노무 검토 트레일이 보조. |
| Phase 3에서 KISA / ezTax                                           | Phase 4로 미룸                                                                                                              | KISA 자체구축 12-18개월 / ezTax 운영 부담 — Phase 3은 simple + 노무사 검토로 충분.      |
| KISA 자체구축 vs 모두싸인 OEM                                      | Phase 3 종료 시점 결정                                                                                                      | [`product-vision.md`](../00-vision/product-vision.md) Watch List #5.                    |
| PDF 렌더링 엔진 (WeasyPrint vs Playwright vs 외부 SaaS)            | Phase 2 PoC 결과 후                                                                                                         | 한글 폰트 / 성능 / 라이선스 검증 필요.                                                  |
| 객체 스토리지 (S3 vs NCP vs KT Cloud)                              | Phase 4 Enterprise 한국 리전 옵션 시 결정                                                                                   | Phase 2-3는 AWS S3 글로벌, Phase 4 한국 리전 분기.                                      |
| Documents 도메인 LangGraph 에이전트 정의 (`labor_doc_reviewer` 등) | Phase 2 알파 출시 전 별도 결정                                                                                              | CLAUDE.md 기존 LangGraph 구조 확장.                                                     |
| ReportSchedule 정기 잡 인프라 (Celery vs 별도)                     | Phase 3 출시 전 결정                                                                                                        | 잡 규모에 따른 인프라 분리.                                                             |
| `DocumentTemplate` ERD / RLS / 인덱스 / 샤딩 SQL                   | [`04-architecture/data-model.md`](../04-architecture/data-model.md)로 위임                                                  |                                                                                         |
| Provider 추상화 (`SignatureProvider`) 인터페이스 상세              | Phase 3 simple 단계에서 구축 — [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md)로 위임 |                                                                                         |
| KISA 사업자 선정 / OEM 계약 조건                                   | Phase 3 종료 시점 별도 RFP                                                                                                  |                                                                                         |
| ezTax API 변경 추적 운영 프로세스                                  | [`04-architecture/security-compliance.md`](../04-architecture/security-compliance.md)로 위임                                |                                                                                         |
| 한국 리전 자체 호스팅 (Enterprise) 인프라 결정                     | Phase 4 출시 전 별도 결정                                                                                                   | NCP / KT Cloud / 자체 IDC 비교.                                                         |
| LangGraph supervisor → Documents Tool 권한 전파 패턴               | [`04-architecture/a2ui-strategy.md`](../04-architecture/a2ui-strategy.md)로 위임                                            |                                                                                         |
| 법령 매핑 자동 추적 시스템                                         | Phase 4+ 검토                                                                                                               | Phase 2-3은 수동 운영 프로세스.                                                         |

---

## 관련 문서

- [`../00-vision/positioning.md`](../00-vision/positioning.md) — 차별화 축 3 (KR-first Compliance), 안티-포지셔닝 (한국형 협업 툴 금지)
- [`../00-vision/competitive-landscape.md`](../00-vision/competitive-landscape.md) — 모두싸인 / 도큐사인 / 노무사 사무소 + 엑셀의 Conflow 측 자리, Flex 흡수 전략
- [`../00-vision/product-vision.md`](../00-vision/product-vision.md) — Phase 2 기본 / Phase 3 simple+노무사 / Phase 4 KISA+ezTax, 불변 원칙 4 (KR-first 1순위), Watch List #5 (KISA)
- [`../01-market/jtbd.md`](../01-market/jtbd.md) — Big Job #1 ("회사 운영의 단일 화면"), Switch Trigger #3 (노무 이슈 카톡 유출), COO-4 (노무사 협업) / COO-5 (보고서 자동 요약) / Compliance (IT-5)
- [`../01-market/icp.md`](../01-market/icp.md) — ICP-3 미드마켓 페르소나 (Enterprise ACV 1억원+ 근거), 차단자 IT/보안
- [`../01-market/pricing-strategy.md`](../01-market/pricing-strategy.md) — Documents 도메인 Business+ 게이팅, 노무사·세무사 외부 시트 무료, Enterprise ACV 1억원+ / ezTax + KISA 한정
- [`./domain-overview.md`](./domain-overview.md) — 4도메인 경계, 공유 엔티티 5개, 이벤트 카탈로그 v1, A2UI Tool 카탈로그 v1 (이 문서의 Documents 계약표가 시작점)
- [`./domain-pm.md`](./domain-pm.md) — PM ↔ Documents 횡단 (스프린트 보고서 PDF 데이터 소스), Anti-Vision (보드 위 자체조립 vs 정형 문서)
- [`./domain-comms.md`](./domain-comms.md) — Comms ↔ Documents 횡단 (외부 협업자 채널 → 검토 알림 라우팅), Slack Canvas와 Documents의 경계 결정
- [`./domain-hr.md`](./domain-hr.md) — HR ↔ Documents 강결합 (근로계약서 / 4대 보험 / 임금명세서 / LaborDocument 인터페이스), 노무사 외부 협업자 모델의 권한 측면
- `../04-architecture/data-model.md` — DocumentTemplate / DocumentInstance / SignatureRequest / RetentionPolicy ERD, RLS, 샤딩 (작성 예정)
- `../04-architecture/a2ui-strategy.md` — LangGraph supervisor 권한 전파, Documents Tool Registry, 보고서 자동 생성 trace 패턴 (작성 예정)
- `../04-architecture/security-compliance.md` — KISA 전자서명 자체구축 vs OEM, ezTax 연동, K-ISMS, 보존 정책 자동 잡 (작성 예정)
- `../04-architecture/tech-stack.md` — PDF 렌더링 엔진 / 객체 스토리지 / Celery + APScheduler 결정 (작성 예정)
- `../03-roadmap/phases.md` — Phase 2 기본 / Phase 3 노무사+simple / Phase 4 KISA+ezTax 분기 OKR (작성 예정)
- `../03-roadmap/metrics.md` — ezTax 정확도 99% / KISA 검증 실패율 < 1% / 노무사 SLA 초과율 < 20% / 보존 만료 잡 성공률 SLO (작성 예정)

---

## 문서 변경 정책

이 문서는 **6개 트리거** 시 갱신한다.

1. **[`domain-overview.md`](./domain-overview.md)의 Documents 계약표가 바뀔 때** — overview를 먼저 갱신 후 이 문서 동기.
2. **Watch List 신호 1개 이상 발견 시** — 분기 기다리지 않음.
3. **Phase 종료 시점** — 다음 Phase의 Documents 출시 범위 확정과 동시에 갱신.
4. **한국 법령 개정 시** — 근로기준법 / 세법 / 개인정보보호법 / 전자서명법. 보존 정책 매트릭스 + 워크플로우 매핑 즉시 갱신.
5. **KISA / ezTax API 변경 시** — 외부 어댑터 갱신과 동시에 본 문서 정합 점검.
6. **노무사·세무사 PoC 인터뷰 분기 보고** — 외부 협업자 작업면 활동률 또는 SLA 초과율 신호 시.

문서 책임자: backend-architect + Documents product lead + 노무 자문 + 법무 자문 + 세무 자문. 갱신 시 변경 이력을 본 파일 하단에 추가.
