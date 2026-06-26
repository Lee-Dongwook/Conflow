/**
 * TanStack Query hooks for A2UI catalog + invoke.
 *
 * Invocation is a mutation (state-mutating action). The catalog is a
 * normal query, cached at the workspace level so domain pages can
 * cheaply check "is `<tool_id>` available to this tier".
 */

import { useMutation, useQuery } from '@tanstack/react-query'

import { a2uiKeys } from 'app/shared/api'
import type { ToolCatalogOutput } from 'app/shared/types/api'

import { invokeTool, listTools } from './api'

export function useToolCatalog(workspaceUuid: string) {
  return useQuery<ToolCatalogOutput>({
    queryKey: a2uiKeys.catalog(workspaceUuid),
    queryFn: () => listTools(workspaceUuid),
  })
}

export function useInvokeTool(workspaceUuid: string) {
  return useMutation({
    mutationFn: (args: {
      readonly toolId: string
      readonly rawInput: Record<string, unknown>
    }) =>
      invokeTool({
        workspaceUuid,
        toolId: args.toolId,
        rawInput: args.rawInput,
      }),
  })
}
