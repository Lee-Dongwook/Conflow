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
import { useEffect, useMemo, useState } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useInvokeTool } from 'app/entities/a2ui'
import { DEMO_TOOL_EXAMPLES } from 'app/shared/demo'
import type { ToolCatalogEntry } from 'app/shared/types/api'

interface ToolInvokeFormProps {
  readonly tool: ToolCatalogEntry
}

const EMPTY_INPUT = '{\n  \n}'

export const ToolInvokeForm = ({ tool }: ToolInvokeFormProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const invoke = useInvokeTool(workspaceUuid)

  // A ready-to-run example for this tool, if we have one.
  const example = useMemo(() => DEMO_TOOL_EXAMPLES[tool.id], [tool.id])
  const exampleJson = useMemo(
    () => (example ? JSON.stringify(example.input, null, 2) : EMPTY_INPUT),
    [example],
  )

  const [raw, setRaw] = useState(exampleJson)
  const [parseError, setParseError] = useState<string | null>(null)

  // Reset to the example (or empty) when the tool changes.
  useEffect(() => {
    setRaw(exampleJson)
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
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-700">JSON input</span>
          {example && (
            <button
              type="button"
              onClick={() => {
                setRaw(exampleJson)
                setParseError(null)
              }}
              className="text-xs font-medium text-slate-500 underline-offset-2 hover:text-slate-800 hover:underline"
            >
              예시 입력 채우기
            </button>
          )}
        </div>
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          rows={10}
          spellCheck={false}
          placeholder={exampleJson}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-xs shadow-sm focus:border-slate-500 focus:outline-none"
        />
        {example && (
          <p className="mt-1 text-[11px] text-slate-400">
            예시 명령이 채워져 있습니다. <span className="font-medium text-slate-500">실행</span>을
            누르면 아래에 예시 결과 문서가 나타납니다.
          </p>
        )}
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
          <div className="flex items-center justify-between">
            <h3 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-emerald-800">
              <span className="flex size-4 items-center justify-center rounded-full bg-emerald-600 text-[9px] text-white">
                ✓
              </span>
              결과 문서 (예시)
            </h3>
            <code className="font-mono text-[10px] text-emerald-700">
              {invoke.data.tool_id}
            </code>
          </div>
          <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded bg-white p-3 font-mono text-[11px] leading-relaxed text-slate-800">
            {JSON.stringify(invoke.data.result, null, 2)}
          </pre>
        </section>
      )}
    </div>
  )
}
