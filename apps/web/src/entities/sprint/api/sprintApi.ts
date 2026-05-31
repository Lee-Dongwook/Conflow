import { apiClient } from 'app/shared/api'

import {
  SprintReadSchema,
  type SprintCreate,
  type SprintRead,
  type SprintUpdate,
} from './schemas'

const BASE = '/sprints'

export const sprintApi = {
  async create(payload: SprintCreate): Promise<SprintRead> {
    const { data } = await apiClient.post(BASE, payload)
    return SprintReadSchema.parse(data)
  },

  async listByTeam(teamUuid: string): Promise<readonly SprintRead[]> {
    const { data } = await apiClient.get(`${BASE}/team/${teamUuid}`)
    return SprintReadSchema.array().parse(data)
  },

  async get(sprintUuid: string): Promise<SprintRead> {
    const { data } = await apiClient.get(`${BASE}/${sprintUuid}`)
    return SprintReadSchema.parse(data)
  },

  async update(
    sprintUuid: string,
    payload: SprintUpdate,
  ): Promise<SprintRead> {
    const { data } = await apiClient.patch(
      `${BASE}/${sprintUuid}`,
      payload,
    )
    return SprintReadSchema.parse(data)
  },

  async remove(sprintUuid: string): Promise<void> {
    await apiClient.delete(`${BASE}/${sprintUuid}`)
  },
} as const
