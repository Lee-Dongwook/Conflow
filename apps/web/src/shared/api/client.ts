import { createBaseAPIClient, isAPIError } from '@conflow/core'

import { supabase } from 'app/shared/lib'

export const apiClient = createBaseAPIClient({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
})

apiClient.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(undefined, async (error: unknown) => {
  if (isAPIError(error) && error.code === 'HTTP_401') {
    await supabase.auth.signOut()
  }
  return Promise.reject(error)
})
