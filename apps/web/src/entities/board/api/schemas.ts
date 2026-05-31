import { z } from 'zod'

export const BoardCardReadSchema = z.object({
  uuid: z.string(),
  teamUuid: z.string(),
  sprintUuid: z.string(),
  title: z.string(),
  columnKey: z.string(),
  description: z.string().nullable(),
  position: z.number(),
  assigneeUserUuid: z.string().nullable(),
  reporterUserUuid: z.string().nullable(),
  createdAt: z.string(),
  updatedAt: z.string(),
})
export type BoardCardRead = z.infer<typeof BoardCardReadSchema>

export interface BoardCardCreate {
  readonly teamUuid: string
  readonly sprintUuid: string
  readonly title: string
  readonly columnKey?: string
  readonly description?: string | null
  readonly position?: number
  readonly assigneeUserUuid?: string | null
  readonly reporterUserUuid?: string | null
}

export interface BoardCardUpdate {
  readonly title?: string
  readonly columnKey?: string
  readonly description?: string | null
  readonly position?: number
  readonly assigneeUserUuid?: string | null
  readonly reporterUserUuid?: string | null
}

export interface BoardCardMove {
  readonly columnKey: string
  readonly position: number
}
