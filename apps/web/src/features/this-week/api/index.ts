import { apiClient } from 'app/shared/api'
import { z } from 'zod'

const CurrentUserSchema = z
  .object({
    uuid: z.string(),
    name: z.string().nullable().optional(),
    email: z.string().nullable().optional(),
  })
  .passthrough()
export type CurrentUser = z.infer<typeof CurrentUserSchema>

export const fetchCurrentUser = async (): Promise<CurrentUser> => {
  const { data } = await apiClient.get('/users/me')
  return CurrentUserSchema.parse(data)
}
