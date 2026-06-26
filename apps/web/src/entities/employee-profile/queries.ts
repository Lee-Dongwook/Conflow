/**
 * TanStack Query hooks for EmployeeProfile.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { hrKeys } from 'app/shared/api'
import type {
  EmployeeProfileListFilter,
  EmployeeProfileListOutput,
  EmployeeProfileOutput,
} from 'app/shared/types/api'

import {
  getEmployeeProfile,
  listEmployeeProfiles,
  transitionTenure,
} from './api'

export function useEmployeeProfiles(
  workspaceUuid: string,
  filters: EmployeeProfileListFilter = {},
) {
  return useQuery<EmployeeProfileListOutput>({
    queryKey: hrKeys.profileList(
      workspaceUuid,
      filters as Record<string, unknown>,
    ),
    queryFn: () => listEmployeeProfiles({ workspaceUuid, filters }),
  })
}

export function useEmployeeProfile(
  workspaceUuid: string,
  profileUuid: string | null | undefined,
) {
  return useQuery<EmployeeProfileOutput>({
    queryKey: hrKeys.profileDetail(workspaceUuid, profileUuid ?? ''),
    queryFn: () =>
      getEmployeeProfile({
        workspaceUuid,
        profileUuid: profileUuid as string,
      }),
    enabled: Boolean(profileUuid),
  })
}

export function useTransitionTenure(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (args: {
      readonly profileUuid: string
      readonly payload: Parameters<typeof transitionTenure>[0]['payload']
    }) =>
      transitionTenure({
        workspaceUuid,
        profileUuid: args.profileUuid,
        payload: args.payload,
      }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: hrKeys.profiles(workspaceUuid) })
      qc.setQueryData(hrKeys.profileDetail(workspaceUuid, data.uuid), data)
    },
  })
}
