import { apiClient } from 'app/shared/api'

import {
  BacklogItemReadSchema,
  type BacklogItemCreate,
  type BacklogItemRead,
  type BacklogItemUpdate,
  type BacklogPriorityUpdate,
} from './schemas'

const BASE = '/backlogs'

export const backlogApi = {
  async create(payload: BacklogItemCreate): Promise<BacklogItemRead> {
    const { data } = await apiClient.post(BASE, payload)
    return BacklogItemReadSchema.parse(data)
  },

  async listBySprint(sprintUuid: string): Promise<readonly BacklogItemRead[]> {
    const { data } = await apiClient.get(`${BASE}/sprint/${sprintUuid}`)
    return BacklogItemReadSchema.array().parse(data)
  },

  async get(itemUuid: string): Promise<BacklogItemRead> {
    const { data } = await apiClient.get(`${BASE}/${itemUuid}`)
    return BacklogItemReadSchema.parse(data)
  },

  async update(itemUuid: string, payload: BacklogItemUpdate): Promise<BacklogItemRead> {
    const { data } = await apiClient.patch(`${BASE}/${itemUuid}`, payload)
    return BacklogItemReadSchema.parse(data)
  },

  async remove(itemUuid: string): Promise<void> {
    await apiClient.delete(`${BASE}/${itemUuid}`)
  },

  async bulkUpdatePriorities(payload: BacklogPriorityUpdate): Promise<readonly BacklogItemRead[]> {
    const { data } = await apiClient.patch(`${BASE}/priorities/bulk`, payload)
    return BacklogItemReadSchema.array().parse(data)
  },
} as const
