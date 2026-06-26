/**
 * EmployeeList widget — renders privacy-masked EmployeeProfile cards.
 *
 * Visible-field convention: anything `null` is rendered as "—" (or simply
 * omitted) since we can't distinguish "no value" from "masked by privacy
 * layer". Tenure status pill always present (public layer).
 *
 * Filter UI is minimal: tenure_status dropdown only. Org/manager filters
 * land once we have OrgUnit / Member pickers.
 */

import { isAPIError } from '@conflow/core'
import { useState } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useEmployeeProfiles } from 'app/entities/employee-profile'
import type {
  EmployeeProfileOutput,
  TenureStatus,
} from 'app/shared/types/api'

const TENURE_PILL: Record<TenureStatus, string> = {
  candidate: 'bg-slate-100 text-slate-700',
  pre_hire: 'bg-blue-100 text-blue-800',
  active: 'bg-emerald-100 text-emerald-800',
  on_leave: 'bg-amber-100 text-amber-800',
  pre_offboarding: 'bg-orange-100 text-orange-800',
  offboarded: 'bg-slate-200 text-slate-500',
  archived_legal: 'bg-slate-200 text-slate-400 italic',
}

const TENURE_LABEL: Record<TenureStatus, string> = {
  candidate: 'Candidate',
  pre_hire: 'Pre-hire',
  active: 'Active',
  on_leave: 'On leave',
  pre_offboarding: 'Pre-offboarding',
  offboarded: 'Offboarded',
  archived_legal: 'Archived (법정 보존)',
}

const TENURE_FILTER_OPTIONS: readonly { value: TenureStatus | ''; label: string }[] = [
  { value: '', label: '전체' },
  ...(Object.keys(TENURE_LABEL) as TenureStatus[]).map((s) => ({
    value: s,
    label: TENURE_LABEL[s],
  })),
]

interface EmployeeListProps {
  readonly onProfileClick?: (profile: EmployeeProfileOutput) => void
}

const EmployeeCard = ({
  profile,
  onClick,
}: {
  readonly profile: EmployeeProfileOutput
  readonly onClick: (() => void) | undefined
}) => (
  <button
    type="button"
    onClick={onClick}
    disabled={!onClick}
    className="w-full rounded-lg border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-slate-300 hover:shadow disabled:cursor-default disabled:hover:border-slate-200 disabled:hover:shadow-sm"
  >
    <div className="flex items-start justify-between gap-3">
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-slate-900">
          {profile.title || <span className="italic text-slate-400">직책 없음</span>}
        </p>
        <p className="mt-0.5 truncate font-mono text-[11px] text-slate-500">
          member: {profile.member_uuid.slice(0, 12)}…
        </p>
      </div>
      <span
        className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${TENURE_PILL[profile.tenure_status]}`}
      >
        {TENURE_LABEL[profile.tenure_status]}
      </span>
    </div>
    <div className="mt-3 grid grid-cols-2 gap-y-1 text-[11px]">
      <span className="text-slate-500">입사</span>
      <span className="text-slate-700">{profile.hired_at ?? '—'}</span>
      <span className="text-slate-500">고용 유형</span>
      <span className="text-slate-700">{profile.employment_type ?? '—'}</span>
      <span className="text-slate-500">매니저</span>
      <span className="font-mono text-slate-700">
        {profile.manager_member_uuid
          ? profile.manager_member_uuid.slice(0, 12) + '…'
          : '—'}
      </span>
    </div>
  </button>
)

export const EmployeeList = ({ onProfileClick }: EmployeeListProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const [statusFilter, setStatusFilter] = useState<TenureStatus | ''>('')
  const query = useEmployeeProfiles(workspaceUuid, {
    ...(statusFilter ? { tenure_status: statusFilter } : {}),
    limit: 100,
  })

  if (query.isPending) {
    return <div className="py-12 text-center text-sm text-slate-500">로딩 중…</div>
  }

  if (query.isError) {
    const msg = isAPIError(query.error)
      ? query.error.message
      : '직원 목록을 불러올 수 없습니다.'
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {msg}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs text-slate-500">총 {query.data.total}명</p>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as TenureStatus | '')}
          className="rounded-md border border-slate-300 px-2 py-1 text-xs shadow-sm focus:border-slate-500 focus:outline-none"
        >
          {TENURE_FILTER_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      {query.data.profiles.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center text-sm text-slate-600">
          조건에 맞는 직원이 없습니다.
        </div>
      ) : (
        <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {query.data.profiles.map((p) => (
            <li key={p.uuid}>
              <EmployeeCard
                profile={p}
                onClick={onProfileClick ? () => onProfileClick(p) : undefined}
              />
            </li>
          ))}
        </ul>
      )}
      <p className="text-[11px] italic text-slate-400">
        ※ 빈 칸은 "값이 없음" 또는 "권한이 없어서 보이지 않음" 둘 중 하나입니다 (프라이버시 마스킹).
      </p>
    </div>
  )
}
