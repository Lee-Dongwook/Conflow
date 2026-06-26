/**
 * Channel create form (Phase 4.2).
 *
 * Alpha scope: name, type (public/private/external), topic, optional
 * comma-separated initial_member_uuids. DM is intentionally absent —
 * docs/02-product/domain-comms.md says DM creation flows through a
 * dedicated `initiate_dm` call (not this entry point).
 *
 * external requires Admin on the backend; the form doesn't gate by role,
 * the dispatcher does — error surfaces as 403.
 */

import { isAPIError } from '@conflow/core'
import { useState, type FormEvent } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useCreateChannel } from 'app/entities/channel'
import type { ChannelRead, ChannelType } from 'app/shared/types/api'

const TYPE_OPTIONS: readonly { value: ChannelType; label: string; hint: string }[] = [
  { value: 'public', label: 'Public', hint: '워크스페이스 누구나 참여 가능' },
  { value: 'private', label: 'Private', hint: '초대받은 멤버만' },
  {
    value: 'external',
    label: 'External (노무사 등)',
    hint: 'Admin 권한 필요. 외부 협업자 전용',
  },
]

interface ChannelCreateFormProps {
  readonly onCreated?: (channel: ChannelRead) => void
  readonly onCancel?: () => void
}

export const ChannelCreateForm = ({
  onCreated,
  onCancel,
}: ChannelCreateFormProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const create = useCreateChannel(workspaceUuid)

  const [name, setName] = useState('')
  const [type, setType] = useState<ChannelType>('public')
  const [topic, setTopic] = useState('')
  const [initialMembersRaw, setInitialMembersRaw] = useState('')

  const formError = create.error
    ? isAPIError(create.error)
      ? create.error.message
      : '채널 생성에 실패했습니다.'
    : null

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const initial_member_uuids = initialMembersRaw
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    const channel = await create.mutateAsync({
      name: name.trim(),
      type,
      topic: topic.trim() || undefined,
      ...(initial_member_uuids.length > 0 ? { initial_member_uuids } : {}),
    })
    setName('')
    setType('public')
    setTopic('')
    setInitialMembersRaw('')
    onCreated?.(channel)
  }

  const disabled = create.isPending || !name.trim()

  return (
    <form
      onSubmit={submit}
      className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
    >
      <header>
        <h2 className="text-base font-semibold text-slate-900">새 채널</h2>
      </header>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">이름</span>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
          required
          placeholder="예: design-reviews"
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
        />
      </label>

      <fieldset className="space-y-2">
        <legend className="text-sm font-medium text-slate-700">유형</legend>
        {TYPE_OPTIONS.map((opt) => (
          <label
            key={opt.value}
            className="flex cursor-pointer items-start gap-3 rounded-md border border-slate-200 p-3 hover:bg-slate-50"
          >
            <input
              type="radio"
              name="channel-type"
              value={opt.value}
              checked={type === opt.value}
              onChange={() => setType(opt.value)}
              className="mt-0.5"
            />
            <span>
              <span className="block text-sm font-medium text-slate-800">
                {opt.label}
              </span>
              <span className="block text-xs text-slate-500">{opt.hint}</span>
            </span>
          </label>
        ))}
      </fieldset>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">토픽 (선택)</span>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
        />
      </label>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">
          초기 멤버 (선택)
        </span>
        <input
          type="text"
          value={initialMembersRaw}
          onChange={(e) => setInitialMembersRaw(e.target.value)}
          placeholder="member_uuid 1, member_uuid 2, …"
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-xs shadow-sm focus:border-slate-500 focus:outline-none"
        />
        <span className="mt-1 block text-xs text-slate-500">
          쉼표 구분 멤버 UUID. 생성자는 자동 포함. 멤버 picker UI 는 다음 단위.
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
          {create.isPending ? '생성 중…' : '채널 생성'}
        </button>
      </div>
    </form>
  )
}
