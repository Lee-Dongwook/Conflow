/**
 * `/w/:workspaceUuid/pm/issues/:issueUuid` — single issue + transitions.
 *
 * Mirrors the backend `_VALID_TRANSITIONS` map exactly. BLOCKED requires
 * a reason so the input shows inline; other transitions fire on click.
 *
 * Out of scope (later): inline title/description edit, comments thread,
 * assignee picker, EntityLink to Comms message.
 */

import { isAPIError } from '@conflow/core'
import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useIssue, useTransitionIssue } from 'app/entities/issue'
import type {
  IssuePriority,
  IssueRead,
  IssueStatus,
} from 'app/shared/types/api'

const STATUS_LABEL: Record<IssueStatus, string> = {
  backlog: 'Backlog',
  todo: 'To Do',
  in_progress: 'In Progress',
  blocked: 'Blocked',
  done: 'Done',
  cancelled: 'Cancelled',
}

const STATUS_PILL: Record<IssueStatus, string> = {
  backlog: 'bg-slate-100 text-slate-700',
  todo: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-indigo-100 text-indigo-800',
  blocked: 'bg-rose-100 text-rose-800',
  done: 'bg-emerald-100 text-emerald-800',
  cancelled: 'bg-slate-200 text-slate-500',
}

const PRIORITY_PILL: Record<IssuePriority, string> = {
  urgent: 'bg-rose-600 text-white',
  high: 'bg-orange-500 text-white',
  medium: 'bg-amber-200 text-amber-900',
  low: 'bg-slate-200 text-slate-700',
}

// Mirror of `server/src/app/pm/service.py::_VALID_TRANSITIONS`.
// Keep in sync if backend changes.
const VALID_TRANSITIONS: Record<IssueStatus, readonly IssueStatus[]> = {
  backlog: ['todo', 'cancelled'],
  todo: ['in_progress', 'blocked', 'cancelled', 'backlog'],
  in_progress: ['blocked', 'done', 'cancelled', 'todo'],
  blocked: ['in_progress', 'cancelled'],
  done: [],
  cancelled: [],
}

const formatDateTime = (iso: string): string => {
  try {
    return new Intl.DateTimeFormat('ko-KR', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

interface TransitionBarProps {
  readonly workspaceUuid: string
  readonly issue: IssueRead
}

const TransitionBar = ({ workspaceUuid, issue }: TransitionBarProps) => {
  const transition = useTransitionIssue(workspaceUuid)
  const [reason, setReason] = useState('')
  const allowed = VALID_TRANSITIONS[issue.status]

  if (allowed.length === 0) {
    return (
      <p className="text-xs italic text-slate-500">
        종결 상태 — 전이할 수 없습니다.
      </p>
    )
  }

  const fire = async (e: FormEvent, newStatus: IssueStatus) => {
    e.preventDefault()
    if (newStatus === 'blocked' && !reason.trim()) {
      return
    }
    await transition.mutateAsync({
      issueUuid: issue.uuid,
      payload: {
        new_status: newStatus,
        ...(newStatus === 'blocked' ? { blocked_reason: reason.trim() } : {}),
      },
    })
    if (newStatus !== 'blocked') {
      setReason('')
    }
  }

  return (
    <div className="space-y-3">
      {allowed.includes('blocked') && (
        <input
          type="text"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="BLOCKED 사유 (BLOCKED 클릭 전 필수)"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-rose-500 focus:outline-none"
        />
      )}
      <div className="flex flex-wrap gap-2">
        {allowed.map((target) => {
          const isBlock = target === 'blocked'
          const disabled = transition.isPending || (isBlock && !reason.trim())
          return (
            <button
              key={target}
              type="button"
              onClick={(e) => fire(e, target)}
              disabled={disabled}
              className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              → {STATUS_LABEL[target]}
            </button>
          )
        })}
      </div>
      {transition.error && (
        <p className="text-xs text-rose-700">
          {isAPIError(transition.error)
            ? transition.error.message
            : '전이 실패'}
        </p>
      )}
    </div>
  )
}

export const PMIssueDetailPage = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const { issueUuid } = useParams<{ issueUuid: string }>()
  const navigate = useNavigate()
  const query = useIssue(workspaceUuid, issueUuid)

  if (query.isPending) {
    return <div className="py-12 text-center text-sm text-slate-500">로딩 중…</div>
  }
  if (query.isError) {
    const msg = isAPIError(query.error)
      ? query.error.message
      : '이슈를 불러올 수 없습니다.'
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {msg}
      </div>
    )
  }
  const issue = query.data

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <header className="space-y-2">
        <Link
          to={`/w/${workspaceUuid}/pm/issues`}
          onClick={(e) => {
            e.preventDefault()
            navigate(-1)
          }}
          className="text-xs text-slate-500 hover:text-slate-900"
        >
          ← 이슈 목록
        </Link>
        <div className="flex items-start gap-3">
          <h1 className="flex-1 text-xl font-semibold text-slate-900">
            {issue.title}
          </h1>
          <span
            className={`rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${STATUS_PILL[issue.status]}`}
          >
            {STATUS_LABEL[issue.status]}
          </span>
          <span
            className={`rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${PRIORITY_PILL[issue.priority]}`}
          >
            {issue.priority}
          </span>
        </div>
      </header>

      {issue.description && (
        <article className="whitespace-pre-wrap rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-800">
          {issue.description}
        </article>
      )}

      {issue.status === 'blocked' && issue.blocked_reason && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <p className="text-xs font-semibold uppercase tracking-wide">
            blocked reason
          </p>
          <p className="mt-1">{issue.blocked_reason}</p>
          {issue.blocked_since && (
            <p className="mt-1 text-xs text-rose-700">
              since {formatDateTime(issue.blocked_since)}
            </p>
          )}
        </div>
      )}

      <dl className="grid grid-cols-2 gap-x-6 gap-y-2 rounded-lg border border-slate-200 bg-white p-4 text-xs">
        <dt className="text-slate-500">Reporter</dt>
        <dd className="font-mono text-slate-700">
          {issue.reporter_member_uuid.slice(0, 12)}…
        </dd>
        <dt className="text-slate-500">Assignee</dt>
        <dd className="font-mono text-slate-700">
          {issue.assignee_member_uuid
            ? `${issue.assignee_member_uuid.slice(0, 12)}…`
            : '미배정'}
        </dd>
        <dt className="text-slate-500">Created</dt>
        <dd>{formatDateTime(issue.created_at)}</dd>
        <dt className="text-slate-500">Updated</dt>
        <dd>{formatDateTime(issue.updated_at)}</dd>
        {issue.due_date && (
          <>
            <dt className="text-slate-500">Due</dt>
            <dd>{formatDateTime(issue.due_date)}</dd>
          </>
        )}
      </dl>

      <section className="space-y-2 rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          상태 전이
        </h2>
        <TransitionBar workspaceUuid={workspaceUuid} issue={issue} />
      </section>
    </div>
  )
}
