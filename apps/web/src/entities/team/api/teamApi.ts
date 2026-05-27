import { apiClient } from 'app/shared/api'

import {
  TeamMembershipReadSchema,
  type TeamMembershipCreate,
  type TeamMembershipRead,
  type TeamMembershipUpdate,
} from './schemas'

const BASE = '/teams'

export const teamApi = {
  async addMembership(
    teamUuid: string,
    payload: TeamMembershipCreate,
  ): Promise<TeamMembershipRead> {
    const { data } = await apiClient.post(
      `${BASE}/${teamUuid}/memberships`,
      payload,
    )
    return TeamMembershipReadSchema.parse(data)
  },

  async listMemberships(
    teamUuid: string,
  ): Promise<readonly TeamMembershipRead[]> {
    const { data } = await apiClient.get(`${BASE}/${teamUuid}/memberships`)
    return TeamMembershipReadSchema.array().parse(data)
  },

  async getMembership(membershipUuid: string): Promise<TeamMembershipRead> {
    const { data } = await apiClient.get(
      `${BASE}/memberships/${membershipUuid}`,
    )
    return TeamMembershipReadSchema.parse(data)
  },

  async updateMembership(
    membershipUuid: string,
    payload: TeamMembershipUpdate,
  ): Promise<TeamMembershipRead> {
    const { data } = await apiClient.patch(
      `${BASE}/memberships/${membershipUuid}`,
      payload,
    )
    return TeamMembershipReadSchema.parse(data)
  },

  async removeMembership(membershipUuid: string): Promise<void> {
    await apiClient.delete(`${BASE}/memberships/${membershipUuid}`)
  },
} as const
