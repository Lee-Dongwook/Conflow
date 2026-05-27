import { apiClient } from 'app/shared/api'

import {
  ConsentReadSchema,
  ConsentStatusReadSchema,
  type ConsentAccept,
  type ConsentRead,
  type ConsentStatusRead,
  type ConsentType,
} from './schemas'

const BASE = '/consents'

export const consentApi = {
  async getStatus(): Promise<ConsentStatusRead> {
    const { data } = await apiClient.get(`${BASE}/status`)
    return ConsentStatusReadSchema.parse(data)
  },

  async getHistory(): Promise<readonly ConsentRead[]> {
    const { data } = await apiClient.get(`${BASE}/history`)
    return ConsentReadSchema.array().parse(data)
  },

  async accept(consents: readonly ConsentAccept[]): Promise<readonly ConsentRead[]> {
    const { data } = await apiClient.post(`${BASE}/accept`, { consents })
    return ConsentReadSchema.array().parse(data)
  },

  async revoke(consentType: ConsentType): Promise<ConsentRead> {
    const { data } = await apiClient.delete(`${BASE}/${consentType}`)
    return ConsentReadSchema.parse(data)
  },
} as const
