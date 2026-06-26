/**
 * TanStack Query provider — single root for all server-state.
 *
 * Defaults:
 *   - staleTime 30s: most list/detail views can tolerate a half-minute
 *     of staleness, and 0 would re-fetch on every focus/mount.
 *   - retry 1: backend gating (402/403/404/422) shouldn't be retried;
 *     the apiClient surfaces these as APIError with `code`, and we
 *     short-circuit in the retry callback.
 *   - refetchOnWindowFocus false: noisy in chat-heavy workspaces.
 */

import { isAPIError } from '@conflow/core'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'

const _NON_RETRYABLE_HTTP = new Set(['HTTP_400', 'HTTP_401', 'HTTP_402', 'HTTP_403', 'HTTP_404', 'HTTP_422'])

function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        gcTime: 5 * 60_000,
        refetchOnWindowFocus: false,
        retry: (failureCount, error) => {
          if (isAPIError(error) && _NON_RETRYABLE_HTTP.has(error.code)) {
            return false
          }
          return failureCount < 1
        },
      },
      mutations: {
        retry: false,
      },
    },
  })
}

interface QueryProviderProps {
  readonly children: ReactNode
}

export const QueryProvider = ({ children }: QueryProviderProps) => {
  // Hold the client in state so React Fast Refresh doesn't trash the cache.
  const [client] = useState(makeQueryClient)
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}
