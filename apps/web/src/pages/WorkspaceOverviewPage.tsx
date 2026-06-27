/**
 * `/w/:workspaceUuid` — workspace overview (home).
 *
 * Mirrors the retired DashboardPage's card structure (header → 2-col stat
 * grid → list card → conditional alert card + skeleton/error states) but
 * the content is the new domain: PM issues, Comms channels, HR members,
 * Documents. Data comes from the per-entity TanStack Query hooks, so the
 * page stays in sync with the dedicated domain pages.
 */

import { useNavigate } from 'react-router-dom'

import {
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
  cn,
} from '@conflow/ui'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useChannels } from 'app/entities/channel'
import { useDocumentInstances } from 'app/entities/document-instance'
import { useEmployeeProfiles } from 'app/entities/employee-profile'
import { useIssues } from 'app/entities/issue'
import { useSession } from 'app/entities/session'
import type { IssueRead } from 'app/shared/types/api'

const STATUS_META: Record<IssueRead['status'], { label: string; variant: 'default' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline' }> = {
  backlog: { label: '백로그', variant: 'outline' },
  todo: { label: '할 일', variant: 'secondary' },
  in_progress: { label: '진행 중', variant: 'warning' },
  blocked: { label: '블로킹', variant: 'destructive' },
  done: { label: '완료', variant: 'success' },
  cancelled: { label: '취소', variant: 'outline' },
}

const IssueStatusBadge = ({ status }: { readonly status: IssueRead['status'] }) => {
  const meta = STATUS_META[status]
  return (
    <Badge variant={meta.variant} className="text-[10px]">
      {meta.label}
    </Badge>
  )
}

const StatTile = ({
  label,
  value,
  hint,
  onClick,
  accent,
}: {
  readonly label: string
  readonly value: string
  readonly hint?: string
  readonly onClick: () => void
  readonly accent?: boolean
}) => (
  <button
    type="button"
    onClick={onClick}
    className={cn(
      'flex flex-col items-start gap-1 rounded-lg border bg-white p-4 text-left transition-colors hover:border-slate-300',
      accent ? 'border-red-200 bg-red-50/50' : 'border-slate-200',
    )}
  >
    <span className="text-xs font-medium text-slate-500">{label}</span>
    <span className={cn('text-2xl font-semibold tabular-nums', accent ? 'text-red-700' : 'text-slate-900')}>
      {value}
    </span>
    {hint ? <span className="text-[11px] text-slate-400">{hint}</span> : null}
  </button>
)

export const WorkspaceOverviewPage = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const navigate = useNavigate()
  const session = useSession()

  const issuesQ = useIssues(workspaceUuid, { limit: 200 })
  const channelsQ = useChannels(workspaceUuid, {})
  const employeesQ = useEmployeeProfiles(workspaceUuid)
  const documentsQ = useDocumentInstances(workspaceUuid, { limit: 200 })

  const go = (path: string) => navigate(`/w/${workspaceUuid}/${path}`)

  const viewerName =
    session.status === 'authenticated'
      ? ((session.user.user_metadata?.name as string) ?? session.user.email ?? '사용자')
      : '게스트'

  if (issuesQ.isLoading) {
    return <OverviewSkeleton />
  }

  if (issuesQ.isError) {
    return (
      <p className="text-center text-sm text-red-500">
        개요를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.
      </p>
    )
  }

  const issues = issuesQ.data?.issues ?? []
  const issueTotal = issuesQ.data?.total ?? issues.length
  const doneCount = issues.filter((i) => i.status === 'done').length
  const inProgressCount = issues.filter((i) => i.status === 'in_progress').length
  const blockedIssues = issues.filter((i) => i.status === 'blocked')
  const progressPercent = issueTotal > 0 ? Math.round((doneCount / issueTotal) * 100) : 0

  const channelCount = channelsQ.data?.total
  const memberCount = employeesQ.data?.total
  const pendingDocCount = (documentsQ.data?.instances ?? []).filter(
    (d) => d.state === 'pending_review',
  ).length

  const recentIssues = [...issues]
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))
    .slice(0, 5)

  const fmt = (n: number | undefined) => (typeof n === 'number' ? String(n) : '—')

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6">
      {/* Header card */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary">워크스페이스</Badge>
            <Badge variant="default" className="text-[10px]">
              보는 사람 · {viewerName}
            </Badge>
          </div>
          <CardTitle className="mt-2 text-xl">워크스페이스 개요</CardTitle>
          <CardDescription className="font-mono text-xs">{workspaceUuid}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-slate-600">
            PM·커뮤니케이션·HR·문서 도메인을 한눈에 살펴보고 각 영역으로 이동하세요.
          </p>
        </CardContent>
      </Card>

      {/* Progress + Blockers */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">이슈 진행률</CardTitle>
            <CardDescription>
              완료 {doneCount} / 전체 {issueTotal}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Progress value={progressPercent} />
            <p className="text-xs text-slate-500">
              {progressPercent}% 완료 · 진행 중 {inProgressCount}건
            </p>
          </CardContent>
        </Card>
        <Card className={blockedIssues.length > 0 ? 'border-amber-200 bg-amber-50/40' : undefined}>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">블로킹 이슈</CardTitle>
            <CardDescription>해결이 필요한 막힌 작업</CardDescription>
          </CardHeader>
          <CardContent>
            <p
              className={cn(
                'text-2xl font-semibold tabular-nums',
                blockedIssues.length > 0 ? 'text-amber-800' : 'text-slate-900',
              )}
            >
              {blockedIssues.length}건
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Domain summary tiles */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label="진행 중 이슈"
          value={fmt(inProgressCount)}
          hint="PM · 이슈 보기"
          onClick={() => go('pm/issues')}
        />
        <StatTile
          label="채널"
          value={fmt(channelCount)}
          hint="커뮤니케이션"
          onClick={() => go('comms/channels')}
        />
        <StatTile
          label="구성원"
          value={fmt(memberCount)}
          hint="HR · 프로필"
          onClick={() => go('hr/profiles')}
        />
        <StatTile
          label="검토 대기 문서"
          value={fmt(pendingDocCount)}
          hint="문서 발급"
          onClick={() => go('documents/instances')}
          accent={pendingDocCount > 0}
        />
      </div>

      {/* Recent issues */}
      <Card>
        <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-4 pb-2">
          <div>
            <CardTitle className="text-base">최근 이슈</CardTitle>
            <CardDescription>최근 업데이트된 이슈 {recentIssues.length}건</CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="secondary" onClick={() => go('pm/issues')}>
              이슈 전체 보기
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-0">
          {recentIssues.map((issue, index) => (
            <div key={issue.uuid}>
              {index > 0 ? <Separator className="my-3" /> : null}
              <button
                type="button"
                onClick={() => go(`pm/issues/${issue.uuid}`)}
                className="flex w-full flex-wrap items-center gap-3 text-left"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-slate-900">{issue.title}</p>
                  <p className="text-xs text-slate-500">우선순위 · {issue.priority}</p>
                </div>
                <IssueStatusBadge status={issue.status} />
              </button>
            </div>
          ))}
          {recentIssues.length === 0 ? (
            <p className="py-4 text-center text-sm text-slate-400">아직 이슈가 없습니다.</p>
          ) : null}
        </CardContent>
      </Card>

      {/* Blocked issues alert */}
      {blockedIssues.length > 0 ? (
        <Card className="border-amber-200 bg-amber-50/40">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-amber-950">막힌 이슈</CardTitle>
            <CardDescription>블로킹 사유를 확인하고 풀어주세요.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {blockedIssues.slice(0, 4).map((issue) => (
              <button
                key={issue.uuid}
                type="button"
                onClick={() => go(`pm/issues/${issue.uuid}`)}
                className="flex w-full flex-col gap-0.5 rounded-md px-1 py-1 text-left hover:bg-amber-100/50"
              >
                <span className="truncate text-sm font-medium text-amber-950">{issue.title}</span>
                {issue.blocked_reason ? (
                  <span className="truncate text-xs text-amber-800">{issue.blocked_reason}</span>
                ) : null}
              </button>
            ))}
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}

const OverviewSkeleton = () => (
  <div className="mx-auto flex max-w-4xl flex-col gap-6">
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-center gap-2">
          <Skeleton className="h-5 w-24 rounded-full" />
          <Skeleton className="h-5 w-28 rounded-full" />
        </div>
        <Skeleton className="mt-2 h-6 w-48" />
        <Skeleton className="h-4 w-64" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-4 w-72" />
      </CardContent>
    </Card>

    <div className="grid gap-4 md:grid-cols-2">
      {[0, 1].map((i) => (
        <Card key={i}>
          <CardHeader className="pb-2">
            <Skeleton className="h-5 w-24" />
            <Skeleton className="h-3.5 w-32" />
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-2 w-full rounded-full" />
            <Skeleton className="h-3 w-36" />
          </CardContent>
        </Card>
      ))}
    </div>

    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {[0, 1, 2, 3].map((i) => (
        <Skeleton key={i} className="h-24 w-full rounded-lg" />
      ))}
    </div>

    <Card>
      <CardHeader className="pb-2">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-3.5 w-40" />
      </CardHeader>
      <CardContent className="space-y-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="min-w-0 flex-1 space-y-1.5">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-3 w-24" />
            </div>
            <Skeleton className="h-5 w-12 rounded-full" />
          </div>
        ))}
      </CardContent>
    </Card>
  </div>
)
