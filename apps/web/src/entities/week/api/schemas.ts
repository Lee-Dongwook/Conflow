import { z } from 'zod'

export const WeekMilestoneCreateSchema = z.object({
  sprint_uuid: z.string(),
  owner_user_uuid: z.string(),
  title: z.string().min(1).max(512),
  due_on: z.string().nullable().optional(),
})
export type WeekMilestoneCreate = z.infer<typeof WeekMilestoneCreateSchema>

export const WeekMilestoneUpdateSchema = z.object({
  title: z.string().min(1).max(512).optional(),
  owner_user_uuid: z.string().optional(),
  due_on: z.string().nullable().optional(),
})
export type WeekMilestoneUpdate = z.infer<typeof WeekMilestoneUpdateSchema>

export const WeekMilestoneReadSchema = z.object({
  uuid: z.string(),
  sprint_uuid: z.string(),
  owner_user_uuid: z.string(),
  title: z.string(),
  due_on: z.string().nullable(),
  completed_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type WeekMilestoneRead = z.infer<typeof WeekMilestoneReadSchema>
