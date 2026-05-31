import { z } from 'zod'

export const SprintCreateSchema = z.object({
  teamUuid: z.string(),
  label: z.string(),
  startsOn: z.string(),
  endsOn: z.string(),
  sharedGoal: z.string().nullable().optional(),
  periodLabel: z.string().nullable().optional(),
})
export type SprintCreate = z.infer<typeof SprintCreateSchema>

export const SprintReadSchema = z.object({
  uuid: z.string(),
  teamUuid: z.string(),
  label: z.string(),
  startsOn: z.string(),
  endsOn: z.string(),
  sharedGoal: z.string().nullable(),
  periodLabel: z.string().nullable(),
  createdAt: z.string(),
  updatedAt: z.string(),
})
export type SprintRead = z.infer<typeof SprintReadSchema>

export const SprintUpdateSchema = z.object({
  label: z.string().optional(),
  startsOn: z.string().optional(),
  endsOn: z.string().optional(),
  sharedGoal: z.string().nullable().optional(),
  periodLabel: z.string().nullable().optional(),
})
export type SprintUpdate = z.infer<typeof SprintUpdateSchema>
