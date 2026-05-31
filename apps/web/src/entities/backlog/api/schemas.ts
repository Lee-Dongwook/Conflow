import { z } from 'zod'

export const BacklogPriority = z.enum(['low', 'medium', 'high', 'critical'])
export type BacklogPriority = z.infer<typeof BacklogPriority>

export const BacklogItemCreateSchema = z.object({
  teamUuid: z.string(),
  sprintUuid: z.string(),
  title: z.string(),
  assigneeUserUuid: z.string().nullable().optional(),
  priority: BacklogPriority.optional().default('medium'),
  note: z.string().nullable().optional(),
})
export type BacklogItemCreate = z.infer<typeof BacklogItemCreateSchema>

export const BacklogItemReadSchema = z.object({
  uuid: z.string(),
  teamUuid: z.string(),
  sprintUuid: z.string(),
  title: z.string(),
  assigneeUserUuid: z.string().nullable(),
  priority: BacklogPriority,
  note: z.string().nullable(),
  createdAt: z.string(),
  updatedAt: z.string(),
})
export type BacklogItemRead = z.infer<typeof BacklogItemReadSchema>

export const BacklogItemUpdateSchema = z.object({
  title: z.string().optional(),
  assigneeUserUuid: z.string().nullable().optional(),
  priority: BacklogPriority.optional(),
  note: z.string().nullable().optional(),
  sprintUuid: z.string().optional(),
})
export type BacklogItemUpdate = z.infer<typeof BacklogItemUpdateSchema>

export const BacklogPriorityItemSchema = z.object({
  uuid: z.string(),
  priority: BacklogPriority,
})

export const BacklogPriorityUpdateSchema = z.object({
  items: z.array(BacklogPriorityItemSchema),
})
export type BacklogPriorityUpdate = z.infer<typeof BacklogPriorityUpdateSchema>
