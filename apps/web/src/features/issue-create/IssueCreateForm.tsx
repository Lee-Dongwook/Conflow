/**
 * Issue create form (Phase 3.2).
 *
 * Alpha scope: title (required), description (markdown), priority,
 * optional assignee_member_uuid as a raw text field. A proper member
 * picker lands once `entities/member` has the list endpoint (backend
 * deferred — alpha workaround is "type the UUID you got from
 * `/api/workspaces/{uuid}/members/invite`").
 *
 * The form is dumb: it doesn't own its open/close state. Hosting widgets
 * call `onCreated(issue)` to refetch their list and dismiss any modal.
 */

import { isAPIError } from '@conflow/core'
import { useState, type FormEvent } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useCreateIssue } from 'app/entities/issue'
import type { IssuePriority, IssueRead } from 'app/shared/types/api'

const PRIORITY_OPTIONS: readonly { value: IssuePriority; label: string }[] = [
  { value: 'urgent', label: 'Urgent' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

interface IssueCreateFormProps {
  readonly onCreated?: (issue: IssueRead) => void
  readonly onCancel?: () => void
}

export const IssueCreateForm = ({
  onCreated,
  onCancel,
}: IssueCreateFormProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const create = useCreateIssue(workspaceUuid)

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<IssuePriority>('medium')
  const [assigneeUuid, setAssigneeUuid] = useState('')

  const formError = create.error
    ? isAPIError(create.error)
      ? create.error.message
      : '이슈 생성에 실패했습니다.'
    : null

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const created = await create.mutateAsync({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      assignee_member_uuid: assigneeUuid.trim() || undefined,
    })
    setTitle('')
    setDescription('')
    setPriority('medium')
    setAssigneeUuid('')
    onCreated?.(created)
  }

  const disabled = create.isPending || !title.trim()

  return (
    <form
      onSubmit={submit}
      className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
    >
      <header>
        <h2 className="text-base font-semibold text-slate-900">새 이슈</h2>
      </header>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">제목</span>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          required
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
        />
      </label>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">설명 (선택)</span>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
        />
      </label>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">우선순위</span>
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value as IssuePriority)}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
        >
          {PRIORITY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">
          담당자 Member UUID (선택)
        </span>
        <input
          type="text"
          value={assigneeUuid}
          onChange={(e) => setAssigneeUuid(e.target.value)}
          placeholder="00000000-0000-0000-0000-000000000000"
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-xs shadow-sm focus:border-slate-500 focus:outline-none"
        />
        <span className="mt-1 block text-xs text-slate-500">
          멤버 선택 UI 는 다음 단위에 추가됩니다. 비워두면 미배정 이슈로 생성됩니다.
        </span>
      </label>

      {formError && (
        <div className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {formError}
        </div>
      )}

      <div className="flex items-center justify-end gap-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            취소
          </button>
        )}
        <button
          type="submit"
          disabled={disabled}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {create.isPending ? '생성 중…' : '이슈 생성'}
        </button>
      </div>
    </form>
  )
}
