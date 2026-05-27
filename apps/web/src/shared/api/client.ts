import { createBaseAPIClient } from '@conflow/core'

export const apiClient = createBaseAPIClient({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
})
