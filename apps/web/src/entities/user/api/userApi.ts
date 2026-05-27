import { apiClient } from 'app/shared/api'

import {
  TokenResponseSchema,
  UserReadSchema,
  UserWithTeamsReadSchema,
  type TokenResponse,
  type UserCreate,
  type UserRead,
  type UserUpdate,
  type UserWithTeamsRead,
} from './schemas'

const BASE = '/users'

export const userApi = {
  async getToken(refreshToken?: string): Promise<TokenResponse> {
    const params = refreshToken ? { refresh_token: refreshToken } : undefined
    const { data } = await apiClient.get(`${BASE}/token`, { params })
    return TokenResponseSchema.parse(data)
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const { data } = await apiClient.post(`${BASE}/refresh_token`, {
      refresh_token: refreshToken,
    })
    return TokenResponseSchema.parse(data)
  },

  async create(payload: UserCreate): Promise<UserRead> {
    const { data } = await apiClient.post(BASE, payload)
    return UserReadSchema.parse(data)
  },

  async list(includeDeleted = false): Promise<readonly UserRead[]> {
    const { data } = await apiClient.get(BASE, {
      params: { include_deleted: includeDeleted },
    })
    return UserReadSchema.array().parse(data)
  },

  async getByUuid(userUuid: string): Promise<UserWithTeamsRead> {
    const { data } = await apiClient.get(`${BASE}/${userUuid}`)
    return UserWithTeamsReadSchema.parse(data)
  },

  async update(userUuid: string, payload: UserUpdate): Promise<UserRead> {
    const { data } = await apiClient.patch(`${BASE}/${userUuid}`, payload)
    return UserReadSchema.parse(data)
  },

  async delete(userUuid: string): Promise<void> {
    await apiClient.delete(`${BASE}/${userUuid}`)
  },
} as const
