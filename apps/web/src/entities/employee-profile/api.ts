/**
 * HR EmployeeProfile HTTP wrappers. Mandatory Zod validation.
 *
 * The response shape is privacy-masked — `null` fields can mean
 * "no value" OR "you're not authorized to see this". Components must
 * not infer absence from null.
 */

import { apiClient, hrPaths } from 'app/shared/api'
import { demoEmployee, demoEmployeeList, demoGuard, isDemoWorkspace } from 'app/shared/demo'
import {
  EmployeeProfileListFilter as EmployeeProfileListFilterSchema,
  type EmployeeProfileListFilter,
  EmployeeProfileListOutput,
  type EmployeeProfileListOutput as EmployeeProfileListOutputType,
  EmployeeProfileOutput,
  type EmployeeProfileOutput as EmployeeProfileOutputType,
  TenureTransitionInput as TenureTransitionInputSchema,
  type TenureTransitionInput,
} from 'app/shared/types/api'

export async function listEmployeeProfiles(args: {
  readonly workspaceUuid: string
  readonly filters: EmployeeProfileListFilter
}): Promise<EmployeeProfileListOutputType> {
  if (isDemoWorkspace(args.workspaceUuid)) return demoEmployeeList(args.filters)
  const parsed = EmployeeProfileListFilterSchema.parse(args.filters)
  const { data } = await apiClient.get(hrPaths.profiles(args.workspaceUuid), {
    params: parsed,
  })
  return EmployeeProfileListOutput.parse(data)
}

export async function getEmployeeProfile(args: {
  readonly workspaceUuid: string
  readonly profileUuid: string
}): Promise<EmployeeProfileOutputType> {
  if (isDemoWorkspace(args.workspaceUuid)) return demoEmployee(args.profileUuid)
  const { data } = await apiClient.get(
    hrPaths.profile(args.workspaceUuid, args.profileUuid),
  )
  return EmployeeProfileOutput.parse(data)
}

export async function transitionTenure(args: {
  readonly workspaceUuid: string
  readonly profileUuid: string
  readonly payload: TenureTransitionInput
}): Promise<EmployeeProfileOutputType> {
  if (isDemoWorkspace(args.workspaceUuid)) return demoGuard.blockWrite()
  const parsed = TenureTransitionInputSchema.parse(args.payload)
  const { data } = await apiClient.post(
    `${hrPaths.profile(args.workspaceUuid, args.profileUuid)}/transition`,
    parsed,
  )
  return EmployeeProfileOutput.parse(data)
}
