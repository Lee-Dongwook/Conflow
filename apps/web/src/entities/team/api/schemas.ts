import { z } from 'zod'

import { TeamMemberRole } from 'app/entities/user/api/schemas'

export const TeamMembershipCreateSchema = z.object({
  userUuid: z.string(),
  role: TeamMemberRole.optional().default('member'),
})
export type TeamMembershipCreate = z.infer<typeof TeamMembershipCreateSchema>

export const TeamMembershipReadSchema = z.object({
  uuid: z.string(),
  userUuid: z.string(),
  teamUuid: z.string(),
  role: TeamMemberRole,
  joinedAt: z.string(),
})
export type TeamMembershipRead = z.infer<typeof TeamMembershipReadSchema>

export const TeamMembershipUpdateSchema = z.object({
  role: TeamMemberRole.optional(),
})
export type TeamMembershipUpdate = z.infer<typeof TeamMembershipUpdateSchema>
