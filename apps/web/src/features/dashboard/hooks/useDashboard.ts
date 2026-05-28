import { useCallback, useEffect, useState } from 'react'

import { dashboardApi, type TeamDashboardRead } from 'app/entities/dashboard'

type DashboardState =
  | { readonly status: 'idle' }
  | { readonly status: 'loading' }
  | { readonly status: 'success'; readonly data: TeamDashboardRead }
  | { readonly status: 'error'; readonly error: string }

export const useDashboard = (teamUuid: string | null) => {
  const [state, setState] = useState<DashboardState>({ status: 'idle' })

  const fetch = useCallback(async () => {
    if (!teamUuid) return
    setState({ status: 'loading' })
    try {
      const data = await dashboardApi.getTeamDashboard(teamUuid)
      setState({ status: 'success', data })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load dashboard'
      setState({ status: 'error', error: message })
    }
  }, [teamUuid])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { ...state, refetch: fetch } as const
}
