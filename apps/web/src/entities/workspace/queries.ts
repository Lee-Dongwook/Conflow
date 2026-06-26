/**
 * TanStack Query hooks for the workspace entity.
 *
 * `useCreateWorkspace` invalidates the workspace root key so any future
 * "my workspaces" query (lands once the backend list endpoint ships)
 * refetches automatically.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'

import { workspaceKeys } from 'app/shared/api'

import { acceptInvitation, createWorkspace } from './api'

export function useCreateWorkspace() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createWorkspace,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: workspaceKeys.root })
    },
  })
}

export function useAcceptInvitation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: acceptInvitation,
    onSuccess: (_data, vars) => {
      // After acceptance the caller is a Member; their workspace list
      // must refetch so the new tenant appears.
      qc.invalidateQueries({ queryKey: workspaceKeys.root })
      qc.invalidateQueries({
        queryKey: workspaceKeys.detail(vars.workspaceUuid),
      })
    },
  })
}
