/**
 * Create-workspace form (Phase 2.3).
 *
 * Minimal alpha UI: name + slug inputs, slug auto-derived from name unless
 * the user edits it. Submits via `useCreateWorkspace`; on success navigates
 * into the brand-new workspace shell at `/w/{uuid}`.
 *
 * Tier / region defaults to the server's (free / kr); upgrade selection
 * lands once the pricing page UI exists.
 */

import { isAPIError } from '@conflow/core'
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { useCreateWorkspace } from 'app/entities/workspace'

const SLUG_FORBIDDEN = /[^a-z0-9-]/g

function deriveSlug(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(SLUG_FORBIDDEN, '')
    .replace(/^-+|-+$/g, '')
    .slice(0, 64)
}

export const CreateWorkspaceForm = () => {
  const navigate = useNavigate()
  const create = useCreateWorkspace()

  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [slugDirty, setSlugDirty] = useState(false)

  const effectiveSlug = slugDirty ? slug : deriveSlug(name)
  const formError = create.error
    ? isAPIError(create.error)
      ? create.error.message
      : '워크스페이스 생성에 실패했습니다.'
    : null

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const ws = await create.mutateAsync({ name, slug: effectiveSlug })
    navigate(`/w/${ws.uuid}`, { replace: true })
  }

  const disabled = create.isPending || !name.trim() || !effectiveSlug

  return (
    <form
      onSubmit={submit}
      className="mx-auto w-full max-w-md space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
    >
      <header>
        <h2 className="text-lg font-semibold text-slate-900">새 워크스페이스</h2>
        <p className="mt-1 text-sm text-slate-600">
          생성자가 자동으로 OWNER 역할을 받습니다. 워크스페이스명은 사이드바에 표시되고,
          slug 는 URL 에 포함됩니다.
        </p>
      </header>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">이름</span>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
          required
          placeholder="예: Acme Team"
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
        />
      </label>

      <label className="block">
        <span className="block text-sm font-medium text-slate-700">Slug</span>
        <input
          type="text"
          value={effectiveSlug}
          onChange={(e) => {
            setSlug(e.target.value)
            setSlugDirty(true)
          }}
          maxLength={64}
          required
          pattern="^[a-z0-9][a-z0-9-]*$"
          placeholder="acme-team"
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-mono shadow-sm focus:border-slate-500 focus:outline-none"
        />
        <span className="mt-1 block text-xs text-slate-500">
          소문자 / 숫자 / 하이픈만. 이름에서 자동 생성되며, 직접 수정도 가능합니다.
        </span>
      </label>

      {formError && (
        <div className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {formError}
        </div>
      )}

      <button
        type="submit"
        disabled={disabled}
        className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white shadow-sm transition disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {create.isPending ? '생성 중…' : '워크스페이스 생성'}
      </button>
    </form>
  )
}
