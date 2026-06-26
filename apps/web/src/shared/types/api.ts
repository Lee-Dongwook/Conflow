/**
 * Backend schema mirror — runtime Zod validation + inferred TS types.
 *
 * Every value coming from the Conflow API must pass through these schemas
 * (CLAUDE.md: "Zod validation 모든 외부 데이터 mandatory"). Hand-keep this
 * file in sync with `server/src/app/**\/schemas.py`; the structural map is:
 *
 *   server/src/app/core/shared/*.py       → Shared Core entity Read
 *   server/src/app/{pm,comms,hr,documents}/schemas.py → per-domain Read
 *
 * Only the alpha-Phase subset lives here. Add a schema when the consuming
 * feature/page lands; never speculatively model fields the UI doesn't use.
 */

import { z } from 'zod'

// ---------------------------------------------------------------------------
// Shared Core enums (mirror `core/shared/*.py`)
// ---------------------------------------------------------------------------

export const WorkspaceTier = z.enum(['free', 'team', 'business', 'enterprise'])
export type WorkspaceTier = z.infer<typeof WorkspaceTier>

export const WorkspaceRegion = z.enum(['kr', 'jp'])
export type WorkspaceRegion = z.infer<typeof WorkspaceRegion>

export const MemberStatus = z.enum(['invited', 'active', 'disabled', 'external'])
export type MemberStatus = z.infer<typeof MemberStatus>

export const RoleName = z.enum(['owner', 'admin', 'member', 'guest', 'external'])
export type RoleName = z.infer<typeof RoleName>

// ---------------------------------------------------------------------------
// PM enums (mirror `pm/model.py`)
// ---------------------------------------------------------------------------

export const IssueStatus = z.enum([
  'backlog',
  'todo',
  'in_progress',
  'blocked',
  'done',
  'cancelled',
])
export type IssueStatus = z.infer<typeof IssueStatus>

export const IssuePriority = z.enum(['urgent', 'high', 'medium', 'low'])
export type IssuePriority = z.infer<typeof IssuePriority>

// ---------------------------------------------------------------------------
// Comms enums (mirror `comms/model.py`)
// ---------------------------------------------------------------------------

export const ChannelType = z.enum(['public', 'private', 'dm', 'external'])
export type ChannelType = z.infer<typeof ChannelType>

// ---------------------------------------------------------------------------
// Shared Core Read schemas
// ---------------------------------------------------------------------------

export const WorkspaceRead = z.object({
  uuid: z.string(),
  name: z.string(),
  slug: z.string(),
  tier: WorkspaceTier,
  region: WorkspaceRegion,
  created_at: z.string(),
  updated_at: z.string(),
})
export type WorkspaceRead = z.infer<typeof WorkspaceRead>

export const WorkspaceCreateInput = z.object({
  name: z.string().min(1).max(100),
  slug: z
    .string()
    .min(1)
    .max(64)
    .regex(/^[a-z0-9][a-z0-9-]*$/, 'slug must be lowercase kebab'),
  tier: WorkspaceTier.optional(),
  region: WorkspaceRegion.optional(),
})
export type WorkspaceCreateInput = z.infer<typeof WorkspaceCreateInput>

export const MemberRead = z.object({
  uuid: z.string(),
  workspace_uuid: z.string(),
  user_uuid: z.string().nullable(),
  display_name: z.string(),
  email: z.string(),
  status: MemberStatus,
  joined_at: z.string().nullable(),
})
export type MemberRead = z.infer<typeof MemberRead>

export const MemberInviteInput = z.object({
  email: z.string().email(),
  display_name: z.string().max(64).optional(),
  role_name: RoleName.optional(),
})
export type MemberInviteInput = z.infer<typeof MemberInviteInput>

export const MemberInviteOutput = z.object({
  member_uuid: z.string(),
  email: z.string().email(),
  role_name: RoleName,
  invite_url: z.string(),
})
export type MemberInviteOutput = z.infer<typeof MemberInviteOutput>

// ---------------------------------------------------------------------------
// PM Issue (mirror `pm/schemas.py`)
// ---------------------------------------------------------------------------

export const IssueRead = z.object({
  uuid: z.string(),
  workspace_uuid: z.string(),
  project_uuid: z.string().nullable(),
  sprint_uuid: z.string().nullable(),
  title: z.string(),
  description: z.string().nullable(),
  status: IssueStatus,
  priority: IssuePriority,
  reporter_member_uuid: z.string(),
  assignee_member_uuid: z.string().nullable(),
  due_date: z.string().nullable(),
  blocked_since: z.string().nullable(),
  blocked_reason: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type IssueRead = z.infer<typeof IssueRead>

export const IssueCreateInput = z.object({
  title: z.string().min(1).max(200),
  description: z.string().optional(),
  project_uuid: z.string().optional(),
  sprint_uuid: z.string().optional(),
  priority: IssuePriority.optional(),
  assignee_member_uuid: z.string().optional(),
  due_date: z.string().optional(),
})
export type IssueCreateInput = z.infer<typeof IssueCreateInput>

export const IssueTransitionInput = z.object({
  new_status: IssueStatus,
  blocked_reason: z.string().optional(),
})
export type IssueTransitionInput = z.infer<typeof IssueTransitionInput>

export const IssueListFilter = z.object({
  status: IssueStatus.optional(),
  assignee_member_uuid: z.string().optional(),
  sprint_uuid: z.string().optional(),
  project_uuid: z.string().optional(),
  limit: z.number().int().min(1).max(200).optional(),
  offset: z.number().int().min(0).optional(),
})
export type IssueListFilter = z.infer<typeof IssueListFilter>

export const IssueListOutput = z.object({
  issues: z.array(IssueRead),
  total: z.number().int(),
})
export type IssueListOutput = z.infer<typeof IssueListOutput>

// ---------------------------------------------------------------------------
// Comms Channel + Message (mirror `comms/schemas.py`)
// ---------------------------------------------------------------------------

export const ChannelRead = z.object({
  uuid: z.string(),
  workspace_uuid: z.string(),
  name: z.string(),
  type: ChannelType,
  topic: z.string().nullable(),
  is_archived: z.boolean(),
  created_by_member_uuid: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type ChannelRead = z.infer<typeof ChannelRead>

export const ChannelCreateInput = z.object({
  name: z.string().min(1).max(100),
  type: ChannelType,
  topic: z.string().optional(),
  initial_member_uuids: z.array(z.string()).optional(),
})
export type ChannelCreateInput = z.infer<typeof ChannelCreateInput>

export const ChannelListFilter = z.object({
  type: ChannelType.optional(),
  include_archived: z.boolean().optional(),
  member_only: z.boolean().optional(),
  limit: z.number().int().min(1).max(200).optional(),
  offset: z.number().int().min(0).optional(),
})
export type ChannelListFilter = z.infer<typeof ChannelListFilter>

export const ChannelListOutput = z.object({
  channels: z.array(ChannelRead),
  total: z.number().int(),
})
export type ChannelListOutput = z.infer<typeof ChannelListOutput>

export const MessageRead = z.object({
  uuid: z.string(),
  workspace_uuid: z.string(),
  channel_uuid: z.string(),
  thread_root_uuid: z.string().nullable(),
  author_member_uuid: z.string(),
  body: z.string(),
  attachments: z.array(z.record(z.string(), z.unknown())),
  mentions: z.array(z.string()),
  created_at: z.string(),
  edited_at: z.string().nullable(),
})
export type MessageRead = z.infer<typeof MessageRead>

export const MessagePostInput = z.object({
  channel_uuid: z.string(),
  body: z.string().min(1),
  thread_root_uuid: z.string().optional(),
  mentions: z.array(z.string()).optional(),
  attachments: z.array(z.record(z.string(), z.unknown())).optional(),
})
export type MessagePostInput = z.infer<typeof MessagePostInput>

export const MessageUpdateInput = z.object({
  body: z.string().min(1),
})
export type MessageUpdateInput = z.infer<typeof MessageUpdateInput>

export const MessageListFilter = z.object({
  channel_uuid: z.string(),
  thread_root_uuid: z.string().optional(),
  before: z.string().optional(),
  after: z.string().optional(),
  limit: z.number().int().min(1).max(200).optional(),
})
export type MessageListFilter = z.infer<typeof MessageListFilter>

export const MessageListOutput = z.object({
  messages: z.array(MessageRead),
  has_more: z.boolean(),
})
export type MessageListOutput = z.infer<typeof MessageListOutput>
