import { useEffect, useState } from 'react'
import type { TFunction } from 'i18next'

import {
  Avatar,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Progress,
  Separator,
  Skeleton,
} from '@conflow/ui'

import type { DashboardTaskRead, TeamDashboardRead } from 'app/entities/dashboard'
import { MOCK_TEAM_DASHBOARD } from 'app/entities/dashboard'
import { CURRENT_USER, useSession } from 'app/entities/session'
import { userApi } from 'app/entities/user'
import { useDashboard } from 'app/features/dashboard'
import { useTranslation } from 'app/shared/i18n'

const StatusBadge = ({ status }: { readonly status: string }) => {
  const { t } = useTranslation()
  if (status === 'done') {
    return (
      <Badge variant="success" className="text-[10px]">
        {t('dashboard.status.done')}
      </Badge>
    )
  }
  if (status === 'doing') {
    return (
      <Badge variant="warning" className="text-[10px]">
        {t('dashboard.status.doing')}
      </Badge>
    )
  }
  return (
    <Badge variant="secondary" className="text-[10px]">
      {t('dashboard.status.waiting')}
    </Badge>
  )
}

const DEMO_DASHBOARD: TeamDashboardRead = (() => {
  const d = MOCK_TEAM_DASHBOARD
  return {
    teamUuid: 'demo-team-001',
    teamName: d.teamName,
    teamDescription: d.courseLabel,
    sprint: {
      uuid: 'demo-sprint-001',
      label: d.weekLabel,
      sharedGoal: d.oneLineGoal,
      periodLabel: d.periodLabel,
      startsOn: '2025-03-10T00:00:00Z',
      endsOn: '2025-03-23T00:00:00Z',
    },
    tasks: d.tasks.map((t) => ({
      uuid: t.id,
      title: t.title,
      columnKey: t.status,
      assigneeUserUuid: null,
      assigneeName: t.assignee,
    })),
    members: [],
    progressPercent: d.progressPercent,
    totalTasks: d.tasks.length,
    doneTasks: d.tasks.filter((t) => t.status === 'done').length,
    blockerNote: d.blockerNote,
    courseLabel: d.courseLabel,
    nextDeadlineLabel: d.nextDeadlineLabel,
  }
})()

export const DashboardPage = ({
  onNavigate,
}: {
  readonly onNavigate?: (navId: string) => void
}) => {
  const { t } = useTranslation()
  const session = useSession()
  const isAuthenticated = session.status === 'authenticated'

  const [teamUuid, setTeamUuid] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) return
    const init = async () => {
      try {
        const user = await userApi.me()
        const firstTeamUuid = user.teamMemberships?.[0]?.teamUuid ?? null
        setTeamUuid(firstTeamUuid)
      } catch {
        // silently fail — will show empty state
      }
    }
    init()
  }, [isAuthenticated])

  const { status, ...rest } = useDashboard(teamUuid)

  const isDemo = !isAuthenticated
  const d: TeamDashboardRead = isDemo
    ? DEMO_DASHBOARD
    : status === 'success' && 'data' in rest
      ? rest.data
      : {
          teamUuid: '',
          teamName: '',
          teamDescription: null,
          sprint: null,
          tasks: [],
          members: [],
          progressPercent: 0,
          totalTasks: 0,
          doneTasks: 0,
          blockerNote: null,
          courseLabel: null,
          nextDeadlineLabel: null,
        }

  const currentUserName = isAuthenticated
    ? (session.user.user_metadata?.name ?? t('common.me'))
    : CURRENT_USER.displayName
  const currentUserEmail = isAuthenticated ? (session.user.email ?? '') : CURRENT_USER.email

  const myTasks = d.tasks.filter((t) => t.assigneeName === currentUserName)

  const nextDeadlineLabel = d.nextDeadlineLabel ?? (d.sprint ? d.sprint.endsOn.slice(0, 10) : null)

  if (!isDemo && status === 'loading') {
    return <DashboardSkeleton />
  }

  if (!isDemo && status === 'error' && 'error' in rest) {
    return <p className="text-center text-sm text-red-500">{rest.error}</p>
  }

  if (!isDemo && status !== 'success' && teamUuid) {
    return null
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6">
      {isDemo ? (
        <div className="rounded-lg border border-blue-200 bg-blue-50/60 px-4 py-3 text-sm text-blue-800">
          {t('dashboard.demoNotice')}
        </div>
      ) : null}

      {/* Header card */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            {(d.courseLabel ?? d.teamDescription) ? (
              <Badge variant="outline">{d.courseLabel ?? d.teamDescription}</Badge>
            ) : null}
            {d.sprint ? <Badge variant="secondary">{d.sprint.label}</Badge> : null}
            <Badge variant="default" className="text-[10px]">
              {t('dashboard.viewerPrefix')}
              {currentUserName}
            </Badge>
          </div>
          <CardTitle className="mt-2 text-xl">{d.teamName}</CardTitle>
          <CardDescription>
            {d.sprint?.periodLabel ? `${d.sprint.periodLabel} · ` : ''}
            {t('dashboard.mockSessionLabel')}{' '}
            <span className="font-medium text-slate-700">{currentUserEmail}</span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm font-medium text-slate-700">{t('dashboard.weekGoal')}</p>
          <p className="text-base leading-relaxed text-slate-900">
            {d.sprint?.sharedGoal ?? t('dashboard.noGoal')}
          </p>
        </CardContent>
      </Card>

      {/* Deadline + Progress */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{t('dashboard.nextDeadline')}</CardTitle>
            <CardDescription>{t('dashboard.nextDeadlineSub')}</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-semibold text-rose-700">
              {nextDeadlineLabel ?? t('dashboard.noDeadline')}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{t('dashboard.progressTitle')}</CardTitle>
            <CardDescription>
              {t('dashboard.doneCountPrefix')}
              {String(d.doneTasks)}
              {t('dashboard.totalSeparator')}
              {String(d.totalTasks)}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Progress value={d.progressPercent} />
            <p className="text-xs text-slate-500">
              {String(d.progressPercent)}
              {t('dashboard.percentMineSuffix', { count: myTasks.length })}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tasks */}
      <Card>
        <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-4 pb-2">
          <div>
            <CardTitle className="text-base">{t('dashboard.tasksTitle')}</CardTitle>
            <CardDescription>
              {t('dashboard.tasksMineHint', {
                name: currentUserName,
                count: d.tasks.length,
              })}
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="secondary" onClick={() => onNavigate?.('board')}>
              {t('dashboard.goBoard')}
            </Button>
            <Button type="button" variant="ghost" onClick={() => onNavigate?.('backlog')}>
              {t('dashboard.backlog')}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-0">
          {d.tasks.map((task, index) => {
            const isMine = task.assigneeName === currentUserName
            return (
              <div key={task.uuid}>
                {index > 0 ? <Separator className="my-3" /> : null}
                <TaskRow task={task} isMine={isMine} t={t} />
              </div>
            )
          })}
          {d.tasks.length === 0 ? (
            <p className="py-4 text-center text-sm text-slate-400">{t('dashboard.noTasks')}</p>
          ) : null}
        </CardContent>
      </Card>

      {/* Blockers */}
      {d.blockerNote ? (
        <Card className="border-amber-200 bg-amber-50/40">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-amber-950">
              {t('dashboard.blockersTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-amber-950">{d.blockerNote}</p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}

const TaskRow = ({
  task,
  isMine,
  t,
}: {
  readonly task: DashboardTaskRead
  readonly isMine: boolean
  readonly t: TFunction
}) => (
  <div className="flex flex-wrap items-center gap-3">
    <Avatar label={task.assigneeName ?? '?'} size="sm" />
    <div className="min-w-0 flex-1">
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-medium text-slate-900">{task.title}</p>
        {isMine ? (
          <Badge variant="default" className="text-[10px]">
            {t('common.me')}
          </Badge>
        ) : null}
      </div>
      <p className="text-xs text-slate-500">{task.assigneeName ?? t('common.unassigned')}</p>
    </div>
    <StatusBadge status={task.columnKey} />
  </div>
)

const TaskRowSkeleton = () => (
  <div className="flex items-center gap-3">
    <Skeleton className="h-8 w-8 rounded-full" />
    <div className="min-w-0 flex-1 space-y-1.5">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-3 w-20" />
    </div>
    <Skeleton className="h-5 w-12 rounded-full" />
  </div>
)

const DashboardSkeleton = () => (
  <div className="mx-auto flex max-w-4xl flex-col gap-6">
    {/* Header card */}
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-center gap-2">
          <Skeleton className="h-5 w-20 rounded-full" />
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-28 rounded-full" />
        </div>
        <Skeleton className="mt-2 h-6 w-48" />
        <Skeleton className="h-4 w-64" />
      </CardHeader>
      <CardContent className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-5 w-72" />
      </CardContent>
    </Card>

    {/* Deadline + Progress */}
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader className="pb-2">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-3.5 w-32" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-4 w-24" />
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-3.5 w-28" />
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-2 w-full rounded-full" />
          <Skeleton className="h-3 w-36" />
        </CardContent>
      </Card>
    </div>

    {/* Tasks */}
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-4 pb-2">
        <div className="space-y-1.5">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-3.5 w-48" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-9 w-24 rounded-md" />
          <Skeleton className="h-9 w-16 rounded-md" />
        </div>
      </CardHeader>
      <CardContent className="space-y-0">
        {[0, 1, 2, 3].map((i) => (
          <div key={i}>
            {i > 0 ? <Separator className="my-3" /> : null}
            <TaskRowSkeleton />
          </div>
        ))}
      </CardContent>
    </Card>
  </div>
)
