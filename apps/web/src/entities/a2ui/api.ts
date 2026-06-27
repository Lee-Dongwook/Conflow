/**
 * A2UI catalog + invoke HTTP wrappers.
 *
 * Catalog is tier-filtered server-side — listing returns only what the
 * caller's workspace tier is allowed to invoke.
 */

import { apiClient, a2uiPaths } from 'app/shared/api'
import { demoInvokeTool, demoToolCatalog, isDemoWorkspace } from 'app/shared/demo'
import {
  ToolCatalogOutput,
  type ToolCatalogOutput as ToolCatalogOutputType,
  ToolInvokeOutput,
  type ToolInvokeOutput as ToolInvokeOutputType,
} from 'app/shared/types/api'

export async function listTools(
  workspaceUuid: string,
): Promise<ToolCatalogOutputType> {
  if (isDemoWorkspace(workspaceUuid)) return demoToolCatalog()
  const { data } = await apiClient.get(a2uiPaths.tools(workspaceUuid))
  return ToolCatalogOutput.parse(data)
}

export async function invokeTool(args: {
  readonly workspaceUuid: string
  readonly toolId: string
  readonly rawInput: Record<string, unknown>
}): Promise<ToolInvokeOutputType> {
  // Demo exception: A2UI is a showcase surface — return a canned example
  // result instead of blocking, so visitors can see a tool "run".
  if (isDemoWorkspace(args.workspaceUuid)) {
    return demoInvokeTool(args.toolId, args.rawInput)
  }
  const { data } = await apiClient.post(
    a2uiPaths.invoke(args.workspaceUuid, args.toolId),
    args.rawInput,
  )
  return ToolInvokeOutput.parse(data)
}
