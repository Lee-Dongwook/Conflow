import { apiClient } from 'app/shared/api'

import { TeamDashboardReadSchema, type TeamDashboardRead } from './schemas'

export const dashboardApi = {
  async getTeamDashboard(teamUuid: string): Promise<TeamDashboardRead> {
    const { data } = await apiClient.get(`/teams/${teamUuid}/dashboard`)
    return TeamDashboardReadSchema.parse(data)
  },
} as const
