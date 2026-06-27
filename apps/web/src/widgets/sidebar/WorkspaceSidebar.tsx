import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

import { Avatar, Badge, Button, cn } from '@conflow/ui'

import { useLogout, useSession } from 'app/entities/session'
import { useTheme } from 'app/shared'
import type { SidebarGlyph } from './icons'
import { SidebarIcon } from './icons'

export type WorkspaceSidebarProps = {
  /** Active workspace uuid — used to build domain route paths. */
  readonly workspaceUuid: string
  readonly onLoginRequest?: () => void
  readonly className?: string
}

type NavDef = {
  /** Path relative to `/w/:workspaceUuid` (no leading slash). */
  readonly to: string
  readonly label: string
  readonly icon: SidebarGlyph
}

type NavSection = {
  readonly label: string
  readonly items: readonly NavDef[]
}

/**
 * Domain taxonomy for the workspace-scoped router (`/w/:workspaceUuid/...`).
 * Mirrors the backend domains: PM, Comms, HR, Documents, A2UI.
 */
const SECTIONS: readonly NavSection[] = [
  {
    label: '작업 관리',
    items: [{ to: 'pm/issues', label: '이슈', icon: 'board' }],
  },
  {
    label: '커뮤니케이션',
    items: [{ to: 'comms/channels', label: '채널', icon: 'chat' }],
  },
  {
    label: '조직',
    items: [
      { to: 'hr/profiles', label: '구성원', icon: 'users' },
      { to: 'documents/instances', label: '문서', icon: 'clipboard' },
    ],
  },
  {
    label: 'AI',
    items: [{ to: 'a2ui/tools', label: 'A2UI 도구', icon: 'sparkles' }],
  },
]

const SectionLabel = ({ children }: { readonly children: ReactNode }) => (
  <p className="px-3 pb-1 pt-4 text-[10px] font-semibold uppercase tracking-wider text-slate-400 first:pt-1">
    {children}
  </p>
)

const navButtonClass = (active: boolean) =>
  cn(
    'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors',
    active ? 'bg-teal-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-50',
  )

const NavItem = ({ item, base }: { readonly item: NavDef; readonly base: string }) => (
  <NavLink to={`${base}/${item.to}`} className={({ isActive }) => navButtonClass(isActive)}>
    {({ isActive }) => (
      <>
        <SidebarIcon name={item.icon} className={isActive ? 'text-white' : 'text-slate-500'} />
        <span className="min-w-0 flex-1 truncate">{item.label}</span>
      </>
    )}
  </NavLink>
)

export const WorkspaceSidebar = ({
  workspaceUuid,
  onLoginRequest,
  className,
}: WorkspaceSidebarProps) => {
  const { theme, setTheme } = useTheme()
  const session = useSession()
  const logout = useLogout()

  const base = `/w/${workspaceUuid}`

  const displayName =
    session.status === 'authenticated'
      ? ((session.user.user_metadata?.name as string) ?? session.user.email ?? '사용자')
      : '사용자'
  const displayEmail = session.status === 'authenticated' ? (session.user.email ?? '') : ''

  const handleLogout = async () => {
    await logout()
  }

  return (
    <aside
      className={cn(
        'flex min-h-screen w-[240px] shrink-0 flex-col border-r border-slate-200 bg-white',
        className,
      )}
    >
      <div className="flex items-center justify-between gap-2 border-b border-slate-100 px-3 py-3">
        <NavLink to={base} end className="flex min-w-0 items-center gap-2">
          <span className="truncate font-semibold tracking-tight text-slate-900">Conflow</span>
          <Badge variant="outline" className="shrink-0 text-[10px]">
            워크스페이스
          </Badge>
        </NavLink>
        <Button
          type="button"
          variant="secondary"
          className="h-8 shrink-0 px-2 text-xs"
          aria-label="빠른 기록"
        >
          <SidebarIcon name="plus" className="size-4" />
          기록
        </Button>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-2 py-2">
        <NavLink
          to={base}
          end
          className={({ isActive }) =>
            cn(
              'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors',
              isActive ? 'bg-teal-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-50',
            )
          }
        >
          {({ isActive }) => (
            <>
              <SidebarIcon
                name="dashboard"
                className={isActive ? 'text-white' : 'text-slate-500'}
              />
              <span className="min-w-0 flex-1 truncate">개요</span>
            </>
          )}
        </NavLink>

        {SECTIONS.map((section) => (
          <div key={section.label} className="flex flex-col gap-0.5">
            <SectionLabel>{section.label}</SectionLabel>
            {section.items.map((item) => (
              <NavItem key={item.to} item={item} base={base} />
            ))}
          </div>
        ))}
      </nav>

      <div className="border-t border-slate-100 px-2 py-2">
        <p className="mb-1.5 px-2 text-[10px] font-medium uppercase tracking-wide text-slate-400">
          화면 모드
        </p>
        <div className="flex rounded-lg bg-slate-100 p-0.5 text-[11px] font-medium">
          {(
            [
              { id: 'light' as const, label: '라이트' },
              { id: 'system' as const, label: '자동' },
              { id: 'dark' as const, label: '다크' },
            ] as const
          ).map((seg) => (
            <button
              key={seg.id}
              type="button"
              onClick={() => {
                setTheme(seg.id)
              }}
              className={cn(
                'flex-1 rounded-md px-1.5 py-1.5 transition-colors',
                theme === seg.id
                  ? 'bg-white text-teal-800 shadow-sm'
                  : 'text-slate-500 hover:text-slate-800',
              )}
            >
              {seg.label}
            </button>
          ))}
        </div>
      </div>

      <div className="border-t border-slate-100 px-2 py-1">
        <NavLink
          to="/legal"
          className="flex w-full items-center gap-2 rounded-md px-3 py-1.5 text-[11px] text-slate-400 transition-colors hover:text-slate-600"
        >
          이용약관 · 개인정보처리방침
        </NavLink>
      </div>

      <div className="border-t border-slate-100 p-3">
        {session.status === 'authenticated' ? (
          <>
            <div className="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5">
              <div className="flex gap-2.5">
                <Avatar label={displayName} size="md" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-900">{displayName}</p>
                  <p className="truncate text-xs text-slate-500">{displayEmail}</p>
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="mt-2 w-full rounded-md px-3 py-1.5 text-xs text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
            >
              로그아웃
            </button>
          </>
        ) : (
          <Button
            type="button"
            variant="secondary"
            className="w-full text-sm"
            onClick={onLoginRequest}
          >
            로그인
          </Button>
        )}
      </div>
    </aside>
  )
}
