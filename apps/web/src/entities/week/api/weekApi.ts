import { apiClient } from 'app/shared/api'

import {
  WeekMilestoneReadSchema,
  type WeekMilestoneCreate,
  type WeekMilestoneRead,
  type WeekMilestoneUpdate,
} from './schemas'

const BASE = '/week-milestones'

export const weekApi = {
  async listBySprint(
    sprintUuid: string,
    options: { includeCompleted?: boolean } = {},
  ): Promise<readonly WeekMilestoneRead[]> {
    const { data } = await apiClient.get(BASE, {
      params: {
        sprint_uuid: sprintUuid,
        include_completed: options.includeCompleted ?? true,
      },
    })
    return WeekMilestoneReadSchema.array().parse(data)
  },

  async create(payload: WeekMilestoneCreate): Promise<WeekMilestoneRead> {
    const { data } = await apiClient.post(BASE, payload)
    return WeekMilestoneReadSchema.parse(data)
  },

  async update(uuid: string, payload: WeekMilestoneUpdate): Promise<WeekMilestoneRead> {
    const { data } = await apiClient.patch(`${BASE}/${uuid}`, payload)
    return WeekMilestoneReadSchema.parse(data)
  },

  async complete(uuid: string): Promise<WeekMilestoneRead> {
    const { data } = await apiClient.post(`${BASE}/${uuid}/complete`)
    return WeekMilestoneReadSchema.parse(data)
  },

  async uncomplete(uuid: string): Promise<WeekMilestoneRead> {
    const { data } = await apiClient.post(`${BASE}/${uuid}/uncomplete`)
    return WeekMilestoneReadSchema.parse(data)
  },

  async remove(uuid: string): Promise<void> {
    await apiClient.delete(`${BASE}/${uuid}`)
  },
} as const
