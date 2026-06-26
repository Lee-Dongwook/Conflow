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
