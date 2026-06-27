/**
 * Demo fixtures — mock datasets served when the workspace is the demo
 * sentinel. Shapes mirror `shared/types/api.ts` exactly so the same Zod
 * schemas and widgets render them with zero special-casing.
 *
 * Timestamps are hardcoded ISO strings (deterministic; no `Date.now()`).
 */

import { DEMO_WORKSPACE_UUID } from './constants'
import type {
  ChannelListFilter,
  ChannelListOutput,
  ChannelRead,
  DocumentInstanceListFilter,
  DocumentInstanceListOutput,
  DocumentInstanceOutput,
  EmployeeProfileListFilter,
  EmployeeProfileListOutput,
  EmployeeProfileOutput,
  IssueListFilter,
  IssueListOutput,
  IssueRead,
  MessageListFilter,
  MessageListOutput,
  MessageRead,
  ToolCatalogOutput,
} from 'app/shared/types/api'

const WS = DEMO_WORKSPACE_UUID

/** First element of a known-non-empty fixture (satisfies noUncheckedIndexedAccess). */
const firstOf = <T>(arr: readonly T[]): T => {
  const [first] = arr
  if (first === undefined) throw new Error('demo fixture is empty')
  return first
}

// Member sentinels (no member-name resolution in the app yet — widgets show
// the uuid, same as a real workspace).
const M = {
  jiwoo: 'demo-member-jiwoo',
  minseo: 'demo-member-minseo',
  hyun: 'demo-member-hyun',
  sora: 'demo-member-sora',
} as const

// ---------------------------------------------------------------------------
// PM Issues
// ---------------------------------------------------------------------------

const ISSUES: readonly IssueRead[] = [
  {
    uuid: 'demo-issue-1',
    workspace_uuid: WS,
    project_uuid: null,
    sprint_uuid: null,
    title: '랜딩 페이지 카피 확정',
    description: '히어로 문구 A/B 후보 3개 중 1개 확정.',
    status: 'in_progress',
    priority: 'high',
    reporter_member_uuid: M.minseo,
    assignee_member_uuid: M.jiwoo,
    due_date: '2026-07-02',
    blocked_since: null,
    blocked_reason: null,
    created_at: '2026-06-20T01:00:00Z',
    updated_at: '2026-06-26T08:30:00Z',
  },
  {
    uuid: 'demo-issue-2',
    workspace_uuid: WS,
    project_uuid: null,
    sprint_uuid: null,
    title: 'OAuth 로그인 리다이렉트 버그',
    description: '가입 직후 콜백 URL 불일치로 흰 화면.',
    status: 'blocked',
    priority: 'urgent',
    reporter_member_uuid: M.hyun,
    assignee_member_uuid: M.hyun,
    due_date: '2026-06-28',
    blocked_since: '2026-06-25T00:00:00Z',
    blocked_reason: 'Supabase 리다이렉트 URL 미설정 — 인프라 권한 대기',
    created_at: '2026-06-19T05:00:00Z',
    updated_at: '2026-06-25T02:00:00Z',
  },
  {
    uuid: 'demo-issue-3',
    workspace_uuid: WS,
    project_uuid: null,
    sprint_uuid: null,
    title: '온보딩 플로우 와이어프레임',
    description: null,
    status: 'todo',
    priority: 'medium',
    reporter_member_uuid: M.jiwoo,
    assignee_member_uuid: M.sora,
    due_date: '2026-07-05',
    blocked_since: null,
    blocked_reason: null,
    created_at: '2026-06-22T03:00:00Z',
    updated_at: '2026-06-24T09:00:00Z',
  },
  {
    uuid: 'demo-issue-4',
    workspace_uuid: WS,
    project_uuid: null,
    sprint_uuid: null,
    title: '주간 회고 노트 정리',
    description: 'KPT 형식으로 정리해 공유.',
    status: 'done',
    priority: 'low',
    reporter_member_uuid: M.sora,
    assignee_member_uuid: M.minseo,
    due_date: null,
    blocked_since: null,
    blocked_reason: null,
    created_at: '2026-06-18T07:00:00Z',
    updated_at: '2026-06-23T10:15:00Z',
  },
  {
    uuid: 'demo-issue-5',
    workspace_uuid: WS,
    project_uuid: null,
    sprint_uuid: null,
    title: 'API 스키마 Zod 검증 추가',
    description: '외부 응답 전수 Zod 파싱.',
    status: 'in_progress',
    priority: 'medium',
    reporter_member_uuid: M.minseo,
    assignee_member_uuid: M.hyun,
    due_date: '2026-07-01',
    blocked_since: null,
    blocked_reason: null,
    created_at: '2026-06-21T02:00:00Z',
    updated_at: '2026-06-26T01:45:00Z',
  },
  {
    uuid: 'demo-issue-6',
    workspace_uuid: WS,
    project_uuid: null,
    sprint_uuid: null,
    title: '백로그 그루밍',
    description: null,
    status: 'backlog',
    priority: 'low',
    reporter_member_uuid: M.jiwoo,
    assignee_member_uuid: null,
    due_date: null,
    blocked_since: null,
    blocked_reason: null,
    created_at: '2026-06-17T04:00:00Z',
    updated_at: '2026-06-17T04:00:00Z',
  },
]

export const demoIssueList = (filters: IssueListFilter = {}): IssueListOutput => {
  const filtered = ISSUES.filter((i) => {
    if (filters.status && i.status !== filters.status) return false
    if (filters.assignee_member_uuid && i.assignee_member_uuid !== filters.assignee_member_uuid)
      return false
    return true
  })
  return { issues: filtered, total: filtered.length }
}

export const demoIssue = (issueUuid: string): IssueRead =>
  ISSUES.find((i) => i.uuid === issueUuid) ?? firstOf(ISSUES)

// ---------------------------------------------------------------------------
// Comms Channels + Messages
// ---------------------------------------------------------------------------

const CHANNELS: readonly ChannelRead[] = [
  {
    uuid: 'demo-channel-general',
    workspace_uuid: WS,
    name: 'general',
    type: 'public',
    topic: '팀 전체 공지 및 잡담',
    is_archived: false,
    created_by_member_uuid: M.jiwoo,
    created_at: '2026-06-01T00:00:00Z',
    updated_at: '2026-06-26T08:00:00Z',
  },
  {
    uuid: 'demo-channel-product',
    workspace_uuid: WS,
    name: 'product',
    type: 'public',
    topic: '제품 기획 · 로드맵',
    is_archived: false,
    created_by_member_uuid: M.minseo,
    created_at: '2026-06-02T00:00:00Z',
    updated_at: '2026-06-25T11:00:00Z',
  },
  {
    uuid: 'demo-channel-eng',
    workspace_uuid: WS,
    name: 'engineering',
    type: 'private',
    topic: '개발 논의 (비공개)',
    is_archived: false,
    created_by_member_uuid: M.hyun,
    created_at: '2026-06-03T00:00:00Z',
    updated_at: '2026-06-26T02:00:00Z',
  },
  {
    uuid: 'demo-channel-design',
    workspace_uuid: WS,
    name: 'design',
    type: 'public',
    topic: 'UI/UX · 디자인 리뷰',
    is_archived: false,
    created_by_member_uuid: M.sora,
    created_at: '2026-06-04T00:00:00Z',
    updated_at: '2026-06-24T06:00:00Z',
  },
  {
    uuid: 'demo-channel-archive',
    workspace_uuid: WS,
    name: 'mvp-launch',
    type: 'public',
    topic: 'MVP 런칭 회고 (보관)',
    is_archived: true,
    created_by_member_uuid: M.jiwoo,
    created_at: '2026-05-10T00:00:00Z',
    updated_at: '2026-06-10T00:00:00Z',
  },
]

export const demoChannelList = (filters: ChannelListFilter = {}): ChannelListOutput => {
  const filtered = CHANNELS.filter((c) => {
    if (filters.type && c.type !== filters.type) return false
    if (!filters.include_archived && c.is_archived) return false
    return true
  })
  return { channels: filtered, total: filtered.length }
}

const MESSAGES: readonly MessageRead[] = [
  {
    uuid: 'demo-msg-1',
    workspace_uuid: WS,
    channel_uuid: 'demo-channel-general',
    thread_root_uuid: null,
    author_member_uuid: M.jiwoo,
    body: '안녕하세요! 데모 워크스페이스에 오신 걸 환영합니다 👋',
    attachments: [],
    mentions: [],
    created_at: '2026-06-26T07:00:00Z',
    edited_at: null,
  },
  {
    uuid: 'demo-msg-2',
    workspace_uuid: WS,
    channel_uuid: 'demo-channel-general',
    thread_root_uuid: null,
    author_member_uuid: M.minseo,
    body: '이번 주 목표는 랜딩 페이지 카피 확정이에요. product 채널에서 이어가요.',
    attachments: [],
    mentions: [],
    created_at: '2026-06-26T07:05:00Z',
    edited_at: null,
  },
  {
    uuid: 'demo-msg-3',
    workspace_uuid: WS,
    channel_uuid: 'demo-channel-product',
    thread_root_uuid: null,
    author_member_uuid: M.minseo,
    body: '히어로 문구 후보 3개 정리해 뒀습니다. 의견 주세요!',
    attachments: [],
    mentions: [],
    created_at: '2026-06-25T10:00:00Z',
    edited_at: null,
  },
  {
    uuid: 'demo-msg-4',
    workspace_uuid: WS,
    channel_uuid: 'demo-channel-eng',
    thread_root_uuid: null,
    author_member_uuid: M.hyun,
    body: 'OAuth 리다이렉트 이슈 인프라 권한 받으면 바로 풀립니다.',
    attachments: [],
    mentions: [],
    created_at: '2026-06-25T02:00:00Z',
    edited_at: null,
  },
]

export const demoMessageList = (filters: MessageListFilter): MessageListOutput => {
  const messages = MESSAGES.filter((m) => m.channel_uuid === filters.channel_uuid)
  return { messages, has_more: false }
}

// ---------------------------------------------------------------------------
// HR Employee Profiles
// ---------------------------------------------------------------------------

const PROFILES: readonly EmployeeProfileOutput[] = [
  {
    uuid: 'demo-profile-1',
    workspace_uuid: WS,
    member_uuid: M.jiwoo,
    title: '프로덕트 리드',
    org_unit_uuid: null,
    hired_at: '2025-01-06',
    manager_member_uuid: null,
    tenure_status: 'active',
    leave_balance_days: 12,
    employee_no: 'E-0001',
    employment_type: 'regular',
    birth_date: null,
    phone: null,
    insurance_consent_at: '2025-01-06T00:00:00Z',
    contract_signed_at: '2025-01-05T00:00:00Z',
    data_retention_expires_at: null,
    created_at: '2025-01-06T00:00:00Z',
    updated_at: '2026-06-20T00:00:00Z',
  },
  {
    uuid: 'demo-profile-2',
    workspace_uuid: WS,
    member_uuid: M.minseo,
    title: '프로덕트 매니저',
    org_unit_uuid: null,
    hired_at: '2025-03-02',
    manager_member_uuid: M.jiwoo,
    tenure_status: 'active',
    leave_balance_days: 9,
    employee_no: 'E-0002',
    employment_type: 'regular',
    birth_date: null,
    phone: null,
    insurance_consent_at: '2025-03-02T00:00:00Z',
    contract_signed_at: '2025-03-01T00:00:00Z',
    data_retention_expires_at: null,
    created_at: '2025-03-02T00:00:00Z',
    updated_at: '2026-06-18T00:00:00Z',
  },
  {
    uuid: 'demo-profile-3',
    workspace_uuid: WS,
    member_uuid: M.hyun,
    title: '백엔드 엔지니어',
    org_unit_uuid: null,
    hired_at: '2025-05-12',
    manager_member_uuid: M.jiwoo,
    tenure_status: 'active',
    leave_balance_days: 14,
    employee_no: 'E-0003',
    employment_type: 'contract',
    birth_date: null,
    phone: null,
    insurance_consent_at: null,
    contract_signed_at: '2025-05-10T00:00:00Z',
    data_retention_expires_at: null,
    created_at: '2025-05-12T00:00:00Z',
    updated_at: '2026-06-15T00:00:00Z',
  },
  {
    uuid: 'demo-profile-4',
    workspace_uuid: WS,
    member_uuid: M.sora,
    title: '프로덕트 디자이너',
    org_unit_uuid: null,
    hired_at: null,
    manager_member_uuid: M.minseo,
    tenure_status: 'pre_hire',
    leave_balance_days: null,
    employee_no: null,
    employment_type: 'intern',
    birth_date: null,
    phone: null,
    insurance_consent_at: null,
    contract_signed_at: null,
    data_retention_expires_at: null,
    created_at: '2026-06-10T00:00:00Z',
    updated_at: '2026-06-22T00:00:00Z',
  },
]

export const demoEmployeeList = (
  filters: EmployeeProfileListFilter = {},
): EmployeeProfileListOutput => {
  const filtered = PROFILES.filter((p) => {
    if (filters.tenure_status && p.tenure_status !== filters.tenure_status) return false
    return true
  })
  return { profiles: filtered, total: filtered.length }
}

export const demoEmployee = (profileUuid: string): EmployeeProfileOutput =>
  PROFILES.find((p) => p.uuid === profileUuid) ?? firstOf(PROFILES)

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

const DOCUMENTS: readonly DocumentInstanceOutput[] = [
  {
    uuid: 'demo-doc-1',
    workspace_uuid: WS,
    template_uuid: 'tpl-employment-cert',
    template_version: '1.2',
    subject_member_uuid: M.hyun,
    requester_member_uuid: M.minseo,
    variables_snapshot: { purpose: '은행 제출용', issued_to: '재직증명서' },
    rendered_pdf_uri: null,
    state: 'pending_review',
    review_workflow_uuid: 'wf-1',
    signature_request_uuid: null,
    retention_policy_uuid: 'ret-default',
    retention_expires_at: null,
    issued_at: null,
    void_reason: null,
    created_at: '2026-06-24T00:00:00Z',
    updated_at: '2026-06-25T00:00:00Z',
  },
  {
    uuid: 'demo-doc-2',
    workspace_uuid: WS,
    template_uuid: 'tpl-nda',
    template_version: '2.0',
    subject_member_uuid: M.sora,
    requester_member_uuid: M.jiwoo,
    variables_snapshot: { counterpart: '외주사 A', term_months: 12 },
    rendered_pdf_uri: null,
    state: 'pending_review',
    review_workflow_uuid: 'wf-2',
    signature_request_uuid: null,
    retention_policy_uuid: 'ret-default',
    retention_expires_at: null,
    issued_at: null,
    void_reason: null,
    created_at: '2026-06-23T00:00:00Z',
    updated_at: '2026-06-24T00:00:00Z',
  },
  {
    uuid: 'demo-doc-3',
    workspace_uuid: WS,
    template_uuid: 'tpl-employment-cert',
    template_version: '1.2',
    subject_member_uuid: M.minseo,
    requester_member_uuid: M.minseo,
    variables_snapshot: { purpose: '관공서 제출용' },
    rendered_pdf_uri: 'https://example.com/demo/cert-3.pdf',
    state: 'issued',
    review_workflow_uuid: 'wf-3',
    signature_request_uuid: 'sig-3',
    retention_policy_uuid: 'ret-default',
    retention_expires_at: '2031-06-01T00:00:00Z',
    issued_at: '2026-06-20T00:00:00Z',
    void_reason: null,
    created_at: '2026-06-15T00:00:00Z',
    updated_at: '2026-06-20T00:00:00Z',
  },
  {
    uuid: 'demo-doc-4',
    workspace_uuid: WS,
    template_uuid: 'tpl-offer',
    template_version: '1.0',
    subject_member_uuid: M.sora,
    requester_member_uuid: M.jiwoo,
    variables_snapshot: { position: '프로덕트 디자이너', start_date: '2026-07-01' },
    rendered_pdf_uri: null,
    state: 'draft',
    review_workflow_uuid: null,
    signature_request_uuid: null,
    retention_policy_uuid: 'ret-default',
    retention_expires_at: null,
    issued_at: null,
    void_reason: null,
    created_at: '2026-06-22T00:00:00Z',
    updated_at: '2026-06-22T00:00:00Z',
  },
]

export const demoDocumentList = (
  filters: DocumentInstanceListFilter = {},
): DocumentInstanceListOutput => {
  const filtered = DOCUMENTS.filter((d) => {
    if (filters.state && d.state !== filters.state) return false
    return true
  })
  return { instances: filtered, total: filtered.length }
}

export const demoDocument = (instanceUuid: string): DocumentInstanceOutput =>
  DOCUMENTS.find((d) => d.uuid === instanceUuid) ?? firstOf(DOCUMENTS)

// ---------------------------------------------------------------------------
// A2UI Tool catalog
// ---------------------------------------------------------------------------

export const demoToolCatalog = (): ToolCatalogOutput => ({
  tools: [
    {
      id: 'pm.create_issue',
      domain: 'pm',
      description: '제목/담당자/우선순위로 새 이슈를 생성합니다.',
      min_tier: 'free',
      permission_required: 'pm:write',
      cross_domain: false,
      phase: 3,
      input_schema: {
        type: 'object',
        properties: { title: { type: 'string' }, priority: { type: 'string' } },
        required: ['title'],
      },
      output_schema: { type: 'object', properties: { uuid: { type: 'string' } } },
      tags: ['pm', 'write'],
    },
    {
      id: 'comms.summarize_channel',
      domain: 'comms',
      description: '채널 최근 메시지를 요약합니다.',
      min_tier: 'team',
      permission_required: 'comms:read',
      cross_domain: false,
      phase: 4,
      input_schema: {
        type: 'object',
        properties: { channel_uuid: { type: 'string' } },
        required: ['channel_uuid'],
      },
      output_schema: { type: 'object', properties: { summary: { type: 'string' } } },
      tags: ['comms', 'ai'],
    },
    {
      id: 'hr.list_pending_offboarding',
      domain: 'hr',
      description: '오프보딩 예정 구성원을 조회합니다.',
      min_tier: 'business',
      permission_required: 'hr:read',
      cross_domain: false,
      phase: 5,
      input_schema: { type: 'object', properties: {} },
      output_schema: { type: 'object', properties: { members: { type: 'array' } } },
      tags: ['hr'],
    },
    {
      id: 'documents.issue_certificate',
      domain: 'documents',
      description: '승인된 재직증명서를 발급합니다.',
      min_tier: 'business',
      permission_required: 'documents:issue',
      cross_domain: true,
      phase: 6,
      input_schema: {
        type: 'object',
        properties: { instance_uuid: { type: 'string' } },
        required: ['instance_uuid'],
      },
      output_schema: { type: 'object', properties: { pdf_uri: { type: 'string' } } },
      tags: ['documents', 'write'],
    },
  ],
})
