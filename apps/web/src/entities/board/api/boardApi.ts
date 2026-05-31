import { apiClient } from 'app/shared/api'

import {
  BoardCardReadSchema,
  type BoardCardCreate,
  type BoardCardMove,
  type BoardCardRead,
  type BoardCardUpdate,
} from './schemas'

const BASE = '/board-cards'

export const boardApi = {
  async listBySprint(sprintUuid: string): Promise<readonly BoardCardRead[]> {
    const { data } = await apiClient.get(`${BASE}/sprint/${sprintUuid}`)
    return BoardCardReadSchema.array().parse(data)
  },

  async create(payload: BoardCardCreate): Promise<BoardCardRead> {
    const { data } = await apiClient.post(BASE, payload)
    return BoardCardReadSchema.parse(data)
  },

  async update(cardUuid: string, payload: BoardCardUpdate): Promise<BoardCardRead> {
    const { data } = await apiClient.patch(`${BASE}/${cardUuid}`, payload)
    return BoardCardReadSchema.parse(data)
  },

  async move(cardUuid: string, payload: BoardCardMove): Promise<BoardCardRead> {
    const { data } = await apiClient.patch(`${BASE}/${cardUuid}/move`, payload)
    return BoardCardReadSchema.parse(data)
  },

  async delete(cardUuid: string): Promise<void> {
    await apiClient.delete(`${BASE}/${cardUuid}`)
  },
} as const
