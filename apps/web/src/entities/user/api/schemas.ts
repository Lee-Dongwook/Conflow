import { z } from 'zod'

export const UserRole = z.enum(['admin', 'user'])
export type UserRole = z.infer<typeof UserRole>

export const TeamMemberRole = z.enum(['owner', 'admin', 'member'])
export type TeamMemberRole = z.infer<typeof TeamMemberRole>

export const UserReadSchema = z.object({
  createdAt: z.string(),
  updatedAt: z.string(),
  deletedAt: z.string().nullable(),
  uuid: z.string(),
  name: z.string(),
  email: z.string().email(),
  profileImageUrl: z.string().nullable(),
  role: UserRole,
  authId: z.string().nullable(),
})
export type UserRead = z.infer<typeof UserReadSchema>

export const TeamMembershipReadSchema = z.object({
  uuid: z.string(),
  userUuid: z.string(),
  teamUuid: z.string(),
  role: TeamMemberRole,
  joinedAt: z.string(),
})
export type TeamMembershipRead = z.infer<typeof TeamMembershipReadSchema>

export const UserWithTeamsReadSchema = UserReadSchema.extend({
  teamMemberships: z.array(TeamMembershipReadSchema).nullable(),
})
export type UserWithTeamsRead = z.infer<typeof UserWithTeamsReadSchema>

export const UserCreateSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  profileImageUrl: z.string().nullable().optional(),
  supabaseUuid: z.string().nullable().optional(),
  authId: z.string().nullable().optional(),
  accessToken: z.string().nullable().optional(),
})
export type UserCreate = z.infer<typeof UserCreateSchema>

export const UserUpdateSchema = z.object({
  name: z.string().min(1).optional(),
  email: z.string().email().optional(),
  profileImageUrl: z.string().nullable().optional(),
  authId: z.string().nullable().optional(),
})
export type UserUpdate = z.infer<typeof UserUpdateSchema>

export const TokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
  expires_in: z.number(),
  refresh_token: z.string().optional(),
})
export type TokenResponse = z.infer<typeof TokenResponseSchema>
