/**
 * ToolInvokeForm — JSON input + result panel for a single A2UI Tool.
 *
 * Alpha scope: raw JSON textarea. A Pydantic-schema-driven form
 * generator lands when the catalog response stabilises. Parse errors
 * surface inline before the request is sent.
 *
 * Result is rendered as pretty JSON. The host page provides the tool;
 * this form just invokes + displays.
 */

import { isAPIError } from '@conflow/core'
import { useEffect, useState } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useInvokeTool } from 'app/entities/a2ui'
import type { ToolCatalogEntry } from 'app/shared/types/api'

interface ToolInvokeFormProps {
  readonly tool: ToolCatalogEntry
}

export const ToolInvokeForm = ({ tool }: ToolInvokeFormProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const invoke = useInvokeTool(workspaceUuid)
  const [raw, setRaw] = useState('{\n  \n}')
  const [parseError, setParseError] = useState<string | null>(null)

  // Reset when tool changes.
  useEffect(() => {
    setRaw('{\n  \n}')
    setParseError(null)
    invoke.reset()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tool.id])

  const submit = async () => {
    let parsed: Record<string, unknown>
    try {
      parsed = JSON.parse(raw)
      if (
        typeof parsed !== 'object' ||
        parsed === null ||
        Array.isArray(parsed)
      ) {
        throw new Error('input must be a JSON object')
      }
      setParseError(null)
    } catch (err) {
      setParseError(err instanceof Error ? err.message : 'JSON 파싱 실패')
      return
    }
    await invoke.mutateAsync({ toolId: tool.id, rawInput: parsed })
  }

  const apiError = invoke.error
    ? isAPIError(invoke.error)
      ? `${invoke.error.code}: ${invoke.error.message}`
      : '호출 실패'
    : null

  return (
    <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <header className="space-y-1">
        <h2 className="font-mono text-base font-semibold text-slate-900">
          {tool.id}
        </h2>
        <p className="text-xs text-slate-600">{tool.description}</p>
      </header>

      <details className="rounded-md border border-slate-200 bg-slate-50 p-2 text-xs">
        <summary className="cursor-pointer font-medium text-slate-700">
          input schema (JSON Schema)
        </summary>
        <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap rounded bg-white p-2 font-mono text-[10px] text-slate-700">
          {JSON.stringify(tool.input_schema, null, 2)}
        </pre>
      </details>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">
          Raw JSON input
        </span>
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          rows={10}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-xs shadow-sm focus:border-slate-500 focus:outline-none"
        />
      </label>

      {parseError && (
        <p className="text-xs text-rose-700">JSON 오류: {parseError}</p>
      )}
      {apiError && <p className="text-xs text-rose-700">{apiError}</p>}

      <button
        type="button"
        onClick={() => void submit()}
        disabled={invoke.isPending}
        className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white shadow-sm transition disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {invoke.isPending ? '호출 중…' : '실행'}
      </button>

      {invoke.data && (
        <section className="space-y-2 rounded-md border border-emerald-200 bg-emerald-50 p-3">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-emerald-800">
            result
          </h3>
          <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded bg-white p-2 font-mono text-[11px] text-slate-800">
            {JSON.stringify(invoke.data.result, null, 2)}
          </pre>
        </section>
      )}
    </div>
  )
}
