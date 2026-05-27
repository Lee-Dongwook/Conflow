import { useCallback, useState } from 'react'

import { Badge, Button, Spinner, cn } from '@conflow/ui'

import {
  meetingSummaryApi,
  type MeetingSummaryOutput,
} from 'app/features/meeting-summary'

type MeetingRow = {
  readonly id: string
  readonly title: string
  readonly source: string
  readonly when: string
  readonly durationMin: number
  readonly status: 'ready' | 'processing'
  readonly detail: MeetingSummaryOutput | null
}

const emptyDetail: MeetingSummaryOutput = {
  overview: '처리 중입니다. 전사 텍스트를 입력하고 요약을 생성해 주세요.',
  bullets: [],
  decisions: [],
  actions: [],
  nextSteps: [],
}

export const MeetingSummaryPage = () => {
  const [meetings, setMeetings] = useState<MeetingRow[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [titleValue, setTitleValue] = useState('')
  const [transcriptValue, setTranscriptValue] = useState('')

  const activeRow = meetings.find((m) => m.id === activeId)
  const detail = activeRow?.detail ?? emptyDetail

  const handleSubmit = useCallback(async () => {
    const title = titleValue.trim()
    const transcript = transcriptValue.trim()

    if (!title || !transcript) {
      setError('회의 제목과 전사 텍스트를 모두 입력해 주세요.')
      return
    }

    const id = `m-${Date.now()}`
    const newRow: MeetingRow = {
      id,
      title,
      source: '직접 입력',
      when: new Date().toLocaleString('ko-KR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }),
      durationMin: 0,
      status: 'processing',
      detail: null,
    }

    setMeetings((prev) => [newRow, ...prev])
    setActiveId(id)
    setError(null)
    setLoading(true)

    try {
      const result = await meetingSummaryApi.summarize({
        meetingTitle: title,
        transcript,
        teamContext: null,
      })

      setMeetings((prev) =>
        prev.map((m) =>
          m.id === id ? { ...m, status: 'ready' as const, detail: result } : m,
        ),
      )

      setTitleValue('')
      setTranscriptValue('')
    } catch (err) {
      const message =
        err instanceof Error ? err.message : '요약 생성에 실패했습니다.'
      setError(message)
      setMeetings((prev) => prev.filter((m) => m.id !== id))
      setActiveId(meetings[0]?.id ?? null)
    } finally {
      setLoading(false)
    }
  }, [meetings, titleValue, transcriptValue])

  return (
    <div className="flex min-h-[min(70vh,680px)] flex-col gap-3">
      <p className="text-xs text-slate-500">
        A2UI 데모 — 전사 텍스트를 입력하면 LangGraph meeting_summary 에이전트가
        구조화된 회의록을 생성합니다.
      </p>

      <div className="flex min-h-[580px] flex-1 overflow-hidden rounded-xl border-2 border-slate-200 bg-white">
        {/* Left panel: input form + meeting list */}
        <section
          className="flex w-[min(100%,340px)] shrink-0 flex-col border-r border-slate-200"
          aria-label="회의 입력 및 목록"
        >
          <div className="space-y-2 border-b border-slate-200 p-3">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              새 회의록 생성
            </span>
            <input
              type="text"
              value={titleValue}
              onChange={(e) => setTitleValue(e.target.value)}
              placeholder="회의 제목"
              className="w-full rounded-md border border-slate-200 bg-slate-50 px-2.5 py-2 text-sm outline-none focus:border-slate-400"
              disabled={loading}
            />
            <textarea
              value={transcriptValue}
              onChange={(e) => setTranscriptValue(e.target.value)}
              placeholder="전사 텍스트를 붙여넣으세요..."
              className="min-h-[120px] w-full resize-none rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={loading}
            />
            {error ? (
              <p className="text-xs text-red-500">{error}</p>
            ) : null}
            <Button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Spinner className="h-3.5 w-3.5" />
                  요약 생성 중...
                </span>
              ) : (
                'AI 요약 생성'
              )}
            </Button>
          </div>

          <ul className="flex-1 overflow-y-auto p-2">
            {meetings.length === 0 ? (
              <li className="px-2.5 py-4 text-center text-xs text-slate-400">
                아직 생성된 회의록이 없습니다.
              </li>
            ) : null}
            {meetings.map((m) => {
              const on = m.id === activeId
              return (
                <li key={m.id}>
                  <button
                    type="button"
                    onClick={() => {
                      setActiveId(m.id)
                    }}
                    className={cn(
                      'mb-1 flex w-full flex-col gap-1 rounded-lg border px-2.5 py-2 text-left text-sm transition-colors',
                      on
                        ? 'border-slate-400 bg-slate-100'
                        : 'border-transparent hover:bg-slate-50',
                    )}
                  >
                    <span className="font-medium text-slate-900">
                      {m.title}
                    </span>
                    <span className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-500">
                      <span>{m.when}</span>
                      {m.status === 'processing' ? (
                        <Badge variant="outline" className="text-[10px]">
                          처리 중
                        </Badge>
                      ) : (
                        <Badge
                          variant="outline"
                          className="border-emerald-200 bg-emerald-50 text-[10px] text-emerald-800"
                        >
                          요약 완료
                        </Badge>
                      )}
                    </span>
                  </button>
                </li>
              )
            })}
          </ul>
        </section>

        {/* Right panel: summary detail */}
        <section
          className="flex min-w-0 flex-1 flex-col"
          aria-label="AI 회의록 요약 상세"
        >
          {!activeRow ? (
            <div className="flex flex-1 items-center justify-center text-sm text-slate-400">
              왼쪽에서 전사 텍스트를 입력하고 AI 요약을 생성해 보세요.
            </div>
          ) : (
            <>
              <header className="border-b border-slate-200 px-5 py-4">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                  AI 회의록
                </p>
                <h2 className="mt-1 truncate text-base font-semibold text-slate-900">
                  {activeRow.title}
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  {activeRow.source} · {activeRow.when}
                </p>
              </header>

              <div className="flex-1 overflow-y-auto px-5 py-4">
                {activeRow.status === 'processing' ? (
                  <div className="flex items-center gap-3 rounded-lg border border-amber-200 bg-amber-50/80 px-4 py-3 text-sm text-amber-900">
                    <Spinner className="h-4 w-4" />
                    <p className="font-medium">요약 생성 중...</p>
                  </div>
                ) : null}

                {activeRow.detail ? (
                  <div className="mt-1 space-y-4">
                    <article className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        한 줄 요약
                      </h3>
                      <p className="mt-2 text-sm leading-relaxed text-slate-800">
                        {detail.overview}
                      </p>
                    </article>

                    {detail.bullets.length > 0 ? (
                      <article className="rounded-xl border border-slate-200 p-4">
                        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          핵심 논의
                        </h3>
                        <ul className="mt-2 list-inside list-disc space-y-1.5 text-sm text-slate-700">
                          {detail.bullets.map((b) => (
                            <li key={b}>{b}</li>
                          ))}
                        </ul>
                      </article>
                    ) : null}

                    <div className="grid gap-4 md:grid-cols-2">
                      <article className="rounded-xl border border-slate-200 p-4">
                        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          결정
                        </h3>
                        {detail.decisions.length > 0 ? (
                          <ul className="mt-2 space-y-2 text-sm text-slate-700">
                            {detail.decisions.map((d) => (
                              <li
                                key={d}
                                className="rounded-md border border-slate-100 bg-white px-2.5 py-2"
                              >
                                {d}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="mt-2 text-xs text-slate-400">없음</p>
                        )}
                      </article>

                      <article className="rounded-xl border border-slate-200 p-4">
                        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          액션
                        </h3>
                        {detail.actions.length > 0 ? (
                          <ul className="mt-2 space-y-2 text-sm">
                            {detail.actions.map((a) => (
                              <li
                                key={`${a.task}-${a.owner}`}
                                className="flex items-start justify-between gap-2 rounded-md border border-slate-100 bg-white px-2.5 py-2"
                              >
                                <span className="text-slate-800">
                                  {a.task}
                                </span>
                                <span className="shrink-0 text-xs text-slate-500">
                                  {a.owner}
                                </span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="mt-2 text-xs text-slate-400">없음</p>
                        )}
                      </article>
                    </div>

                    {detail.nextSteps.length > 0 ? (
                      <article className="rounded-xl border border-slate-200 p-4">
                        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          다음 단계
                        </h3>
                        <ul className="mt-2 space-y-1.5 text-sm text-slate-700">
                          {detail.nextSteps.map((n) => (
                            <li key={n} className="flex gap-2">
                              <span
                                className="text-slate-300"
                                aria-hidden
                              >
                                →
                              </span>
                              <span>{n}</span>
                            </li>
                          ))}
                        </ul>
                      </article>
                    ) : null}
                  </div>
                ) : null}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
