/**
 * DocumentInstanceList widget — instance cards with state pill + action buttons.
 *
 * State machine actions visible per state (mirrors backend
 * `_VALID_INSTANCE_TRANSITIONS`):
 *   draft           → submit / void
 *   pending_review  → approve / reject / void
 *   approved        → issue / void
 *   signed          → issue
 *   issued / archived / archived_legal_only / void → no actions
 *
 * VOID requires a reason; the row swaps to a small input + confirm UI
 * when the user clicks Void.
 */

import { isAPIError } from '@conflow/core'
import { useState } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import {
  useApproveInstance,
  useDocumentInstances,
  useIssueInstance,
  useRejectInstance,
  useSubmitInstanceForReview,
  useVoidInstance,
} from 'app/entities/document-instance'
import type {
  DocumentInstanceOutput,
  DocumentInstanceState,
} from 'app/shared/types/api'

const STATE_PILL: Record<DocumentInstanceState, string> = {
  draft: 'bg-slate-100 text-slate-700',
  pending_review: 'bg-amber-100 text-amber-800',
  approved: 'bg-blue-100 text-blue-800',
  signed: 'bg-indigo-100 text-indigo-800',
  issued: 'bg-emerald-100 text-emerald-800',
  archived: 'bg-slate-200 text-slate-600',
  archived_legal_only: 'bg-slate-200 text-slate-500 italic',
  void: 'bg-rose-100 text-rose-700 line-through',
}

const STATE_LABEL: Record<DocumentInstanceState, string> = {
  draft: 'Draft',
  pending_review: 'Pending Review',
  approved: 'Approved',
  signed: 'Signed',
  issued: 'Issued',
  archived: 'Archived',
  archived_legal_only: 'Archived (legal)',
  void: 'Void',
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

const InstanceCard = ({ instance }: { readonly instance: DocumentInstanceOutput }) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const submit = useSubmitInstanceForReview(workspaceUuid)
  const approve = useApproveInstance(workspaceUuid)
  const reject = useRejectInstance(workspaceUuid)
  const issue = useIssueInstance(workspaceUuid)
  const voidMut = useVoidInstance(workspaceUuid)
  const [voidMode, setVoidMode] = useState(false)
  const [voidReason, setVoidReason] = useState('')

  const pending =
    submit.isPending ||
    approve.isPending ||
    reject.isPending ||
    issue.isPending ||
    voidMut.isPending

  const lastError =
    submit.error ?? approve.error ?? reject.error ?? issue.error ?? voidMut.error
  const errorMsg = lastError
    ? isAPIError(lastError)
      ? lastError.message
      : '액션 실패'
    : null

  const Button = ({
    onClick,
    label,
    tone = 'neutral',
  }: {
    readonly onClick: () => void
    readonly label: string
    readonly tone?: 'neutral' | 'positive' | 'danger'
  }) => (
    <button
      type="button"
      onClick={onClick}
      disabled={pending}
      className={`rounded-md border px-2 py-1 text-xs font-medium shadow-sm transition disabled:cursor-not-allowed disabled:opacity-50 ${
        tone === 'positive'
          ? 'border-emerald-300 bg-white text-emerald-800 hover:bg-emerald-50'
          : tone === 'danger'
            ? 'border-rose-300 bg-white text-rose-800 hover:bg-rose-50'
            : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
      }`}
    >
      {label}
    </button>
  )

  const actions: React.ReactNode[] = []
  if (instance.state === 'draft') {
    actions.push(
      <Button
        key="submit"
        onClick={() => submit.mutate({ instanceUuid: instance.uuid })}
        label="검토 요청"
      />,
    )
  }
  if (instance.state === 'pending_review') {
    actions.push(
      <Button
        key="approve"
        onClick={() => approve.mutate({ instanceUuid: instance.uuid })}
        label="승인"
        tone="positive"
      />,
      <Button
        key="reject"
        onClick={() => reject.mutate({ instanceUuid: instance.uuid })}
        label="거절"
        tone="danger"
      />,
    )
  }
  if (instance.state === 'approved' || instance.state === 'signed') {
    actions.push(
      <Button
        key="issue"
        onClick={() => issue.mutate({ instanceUuid: instance.uuid })}
        label="발급"
        tone="positive"
      />,
    )
  }
  if (
    ['draft', 'pending_review', 'approved', 'signed'].includes(instance.state)
  ) {
    actions.push(
      <Button
        key="void"
        onClick={() => setVoidMode(true)}
        label="Void"
        tone="danger"
      />,
    )
  }

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <header className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate font-mono text-xs text-slate-500">
            template: {instance.template_uuid.slice(0, 12)}…@{instance.template_version}
          </p>
          {instance.subject_member_uuid && (
            <p className="mt-0.5 truncate text-xs text-slate-700">
              subject @{instance.subject_member_uuid.slice(0, 8)}
            </p>
          )}
        </div>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${STATE_PILL[instance.state]}`}
        >
          {STATE_LABEL[instance.state]}
        </span>
      </header>
      <dl className="mt-3 grid grid-cols-2 gap-y-1 text-[11px]">
        <dt className="text-slate-500">생성</dt>
        <dd>{formatDateTime(instance.created_at)}</dd>
        {instance.issued_at && (
          <>
            <dt className="text-slate-500">발급</dt>
            <dd>{formatDateTime(instance.issued_at)}</dd>
          </>
        )}
        {instance.retention_expires_at && (
          <>
            <dt className="text-slate-500">보존 만료</dt>
            <dd>{formatDateTime(instance.retention_expires_at)}</dd>
          </>
        )}
        {instance.void_reason && (
          <>
            <dt className="text-slate-500">void 사유</dt>
            <dd className="text-rose-700">{instance.void_reason}</dd>
          </>
        )}
      </dl>
      {voidMode ? (
        <div className="mt-3 space-y-2">
          <input
            type="text"
            value={voidReason}
            onChange={(e) => setVoidReason(e.target.value)}
            placeholder="Void 사유 (필수)"
            className="w-full rounded-md border border-rose-300 px-2 py-1 text-xs shadow-sm focus:border-rose-500 focus:outline-none"
          />
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => {
                setVoidMode(false)
                setVoidReason('')
              }}
              className="rounded-md px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
            >
              취소
            </button>
            <button
              type="button"
              disabled={!voidReason.trim() || pending}
              onClick={() =>
                voidMut.mutate(
                  {
                    instanceUuid: instance.uuid,
                    payload: { void_reason: voidReason.trim() },
                  },
                  {
                    onSuccess: () => {
                      setVoidMode(false)
                      setVoidReason('')
                    },
                  },
                )
              }
              className="rounded-md bg-rose-700 px-2 py-1 text-xs font-medium text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-50"
            >
              Void 실행
            </button>
          </div>
        </div>
      ) : actions.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">{actions}</div>
      ) : null}
      {errorMsg && (
        <p className="mt-2 text-xs text-rose-700">{errorMsg}</p>
      )}
    </article>
  )
}

interface DocumentInstanceListProps {
  readonly stateFilter?: DocumentInstanceState
}

const STATE_OPTIONS: readonly { value: DocumentInstanceState | ''; label: string }[] = [
  { value: '', label: '전체' },
  ...(Object.keys(STATE_LABEL) as DocumentInstanceState[]).map((s) => ({
    value: s,
    label: STATE_LABEL[s],
  })),
]

export const DocumentInstanceList = ({ stateFilter }: DocumentInstanceListProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const [localFilter, setLocalFilter] = useState<DocumentInstanceState | ''>(
    stateFilter ?? '',
  )
  const effective = stateFilter ?? localFilter
  const query = useDocumentInstances(workspaceUuid, {
    ...(effective ? { state: effective } : {}),
    limit: 50,
  })

  if (query.isPending) {
    return <div className="py-12 text-center text-sm text-slate-500">로딩 중…</div>
  }
  if (query.isError) {
    const msg = isAPIError(query.error)
      ? query.error.message
      : '문서 목록을 불러올 수 없습니다.'
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {msg}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-slate-500">총 {query.data.total}건</p>
        {!stateFilter && (
          <select
            value={localFilter}
            onChange={(e) =>
              setLocalFilter(e.target.value as DocumentInstanceState | '')
            }
            className="rounded-md border border-slate-300 px-2 py-1 text-xs shadow-sm focus:border-slate-500 focus:outline-none"
          >
            {STATE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )}
      </div>
      {query.data.instances.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center text-sm text-slate-600">
          조건에 맞는 문서가 없습니다.
        </div>
      ) : (
        <div className="space-y-3">
          {query.data.instances.map((instance) => (
            <InstanceCard key={instance.uuid} instance={instance} />
          ))}
        </div>
      )}
    </div>
  )
}
