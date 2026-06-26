/**
 * IssueList widget — fetches & renders issues for the current workspace.
 *
 * Card list (mobile-friendly). Status / priority shown as colored badges.
 * Loading / error / empty states all in-place. Click handler exposed so
 * the host page can route to a detail view once Phase 3.4 ships.
 */

import { isAPIError } from '@conflow/core'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useIssues } from 'app/entities/issue'
import type {
  IssuePriority,
  IssueRead,
  IssueStatus,
} from 'app/shared/types/api'

const STATUS_BADGE: Record<IssueStatus, string> = {
  backlog: 'bg-slate-100 text-slate-700',
  todo: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-indigo-100 text-indigo-800',
  blocked: 'bg-rose-100 text-rose-800',
  done: 'bg-emerald-100 text-emerald-800',
  cancelled: 'bg-slate-200 text-slate-500 line-through',
}

const PRIORITY_BADGE: Record<IssuePriority, string> = {
  urgent: 'bg-rose-600 text-white',
  high: 'bg-orange-500 text-white',
  medium: 'bg-amber-200 text-amber-900',
  low: 'bg-slate-200 text-slate-700',
}

interface IssueListProps {
  readonly onIssueClick?: (issue: IssueRead) => void
}

const formatDateTime = (iso: string): string => {
  try {
    return new Intl.DateTimeFormat('ko-KR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

const IssueCard = ({
  issue,
  onClick,
}: {
  readonly issue: IssueRead
  readonly onClick: (() => void) | undefined
}) => (
  <button
    type="button"
    onClick={onClick}
    disabled={!onClick}
    className="w-full rounded-lg border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-slate-300 hover:shadow disabled:cursor-default disabled:hover:border-slate-200 disabled:hover:shadow-sm"
  >
    <div className="flex items-start justify-between gap-3">
      <h3 className="flex-1 text-sm font-semibold text-slate-900">
        {issue.title}
      </h3>
      <span
        className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${STATUS_BADGE[issue.status]}`}
      >
        {issue.status.replace('_', ' ')}
      </span>
    </div>
    {issue.description && (
      <p className="mt-2 line-clamp-2 text-xs text-slate-600">
        {issue.description}
      </p>
    )}
    <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px]">
      <span
        className={`rounded px-1.5 py-0.5 font-semibold uppercase tracking-wide ${PRIORITY_BADGE[issue.priority]}`}
      >
        {issue.priority}
      </span>
      {issue.assignee_member_uuid ? (
        <span className="font-mono text-slate-500">
          @{issue.assignee_member_uuid.slice(0, 8)}
        </span>
      ) : (
        <span className="text-slate-400">미배정</span>
      )}
      <span className="ml-auto text-slate-400">
        {formatDateTime(issue.created_at)}
      </span>
    </div>
    {issue.status === 'blocked' && issue.blocked_reason && (
      <p className="mt-2 rounded bg-rose-50 px-2 py-1 text-xs text-rose-700">
        {issue.blocked_reason}
      </p>
    )}
  </button>
)

export const IssueList = ({ onIssueClick }: IssueListProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const query = useIssues(workspaceUuid, { limit: 50 })

  if (query.isPending) {
    return <div className="py-12 text-center text-sm text-slate-500">로딩 중…</div>
  }

  if (query.isError) {
    const msg = isAPIError(query.error)
      ? query.error.message
      : '이슈 목록을 불러올 수 없습니다.'
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {msg}
      </div>
    )
  }

  if (query.data.issues.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
        <p className="text-sm text-slate-600">아직 이슈가 없습니다.</p>
        <p className="mt-1 text-xs text-slate-500">
          "새 이슈" 버튼으로 첫 이슈를 만들어 보세요.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-slate-500">
        총 {query.data.total}개 (최근 {query.data.issues.length}개 표시)
      </p>
      {query.data.issues.map((issue) => (
        <IssueCard
          key={issue.uuid}
          issue={issue}
          onClick={onIssueClick ? () => onIssueClick(issue) : undefined}
        />
      ))}
    </div>
  )
}
