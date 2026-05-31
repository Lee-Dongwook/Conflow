import { useCallback, useEffect, useState } from 'react'

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Select,
  Spinner,
  Textarea,
} from '@conflow/ui'

import type { BacklogItemRead, BacklogPriority } from 'app/entities/backlog'
import { useSession } from 'app/entities/session'
import { sprintApi, type SprintRead } from 'app/entities/sprint'
import { userApi, type UserWithTeamsRead } from 'app/entities/user'
import { useBacklog } from 'app/features/backlog'

const PRIORITY_CONFIG: Record<
  BacklogPriority,
  {
    readonly label: string
    readonly variant: 'destructive' | 'warning' | 'secondary' | 'outline'
  }
> = {
  critical: { label: 'Critical', variant: 'destructive' },
  high: { label: 'High', variant: 'warning' },
  medium: { label: 'Medium', variant: 'secondary' },
  low: { label: 'Low', variant: 'outline' },
}

const PRIORITIES: readonly BacklogPriority[] = ['critical', 'high', 'medium', 'low']

type CreateFormState = {
  readonly title: string
  readonly priority: BacklogPriority
  readonly note: string
}

const INITIAL_FORM: CreateFormState = { title: '', priority: 'medium', note: '' }

type EditFormState = {
  readonly uuid: string
  readonly title: string
  readonly priority: BacklogPriority
  readonly note: string
}

export const BacklogPage = () => {
  const session = useSession()
  const isAuthenticated = session.status === 'authenticated'

  const [me, setMe] = useState<UserWithTeamsRead | null>(null)
  const [sprints, setSprints] = useState<readonly SprintRead[]>([])
  const [selectedSprintUuid, setSelectedSprintUuid] = useState<string | null>(null)
  const [initLoading, setInitLoading] = useState(true)

  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState<CreateFormState>(INITIAL_FORM)
  const [creating, setCreating] = useState(false)

  const [editForm, setEditForm] = useState<EditFormState | null>(null)
  const [updating, setUpdating] = useState(false)

  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  const [priorityFilter, setPriorityFilter] = useState<BacklogPriority | 'all'>('all')

  const backlog = useBacklog(selectedSprintUuid)
  const items: readonly BacklogItemRead[] = backlog.status === 'success' ? backlog.items : []

  const teamUuid = me?.teamMemberships?.[0]?.teamUuid ?? null

  useEffect(() => {
    if (!isAuthenticated) {
      setInitLoading(false)
      return
    }
    const init = async () => {
      try {
        const user = await userApi.me()
        setMe(user)
        const firstTeamUuid = user.teamMemberships?.[0]?.teamUuid
        if (firstTeamUuid) {
          const sprintList = await sprintApi.listByTeam(firstTeamUuid)
          setSprints(sprintList)
          const first = sprintList[0]
          if (first) {
            setSelectedSprintUuid(first.uuid)
          }
        }
      } catch {
        // silently fail — page will show empty state
      }
      setInitLoading(false)
    }
    init()
  }, [isAuthenticated])

  const handleCreate = useCallback(async () => {
    if (!selectedSprintUuid || !teamUuid || !createForm.title.trim()) return
    setCreating(true)
    try {
      await backlog.create({
        teamUuid,
        sprintUuid: selectedSprintUuid,
        title: createForm.title.trim(),
        priority: createForm.priority,
        note: createForm.note.trim() || null,
      })
      setCreateForm(INITIAL_FORM)
      setShowCreate(false)
    } catch {
      // keep form open on error
    }
    setCreating(false)
  }, [selectedSprintUuid, teamUuid, createForm, backlog])

  const handleUpdate = useCallback(async () => {
    if (!editForm || !editForm.title.trim()) return
    setUpdating(true)
    try {
      await backlog.update(editForm.uuid, {
        title: editForm.title.trim(),
        priority: editForm.priority,
        note: editForm.note.trim() || null,
      })
      setEditForm(null)
    } catch {
      // keep form open on error
    }
    setUpdating(false)
  }, [editForm, backlog])

  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await backlog.remove(deleteTarget)
      setDeleteTarget(null)
    } catch {
      // keep dialog on error
    }
    setDeleting(false)
  }, [deleteTarget, backlog])

  const filteredItems =
    priorityFilter === 'all' ? items : items.filter((i) => i.priority === priorityFilter)

  const criticalCount = items.filter((i) => i.priority === 'critical').length

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-5xl py-12 text-center text-slate-500">
        로그인 후 백로그를 관리할 수 있습니다.
      </div>
    )
  }

  if (initLoading) {
    return (
      <div className="mx-auto flex max-w-5xl items-center justify-center py-12">
        <Spinner />
      </div>
    )
  }

  if (!teamUuid) {
    return (
      <div className="mx-auto max-w-5xl py-12 text-center text-slate-500">
        소속된 팀이 없습니다. 먼저 팀에 가입해주세요.
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex items-center gap-3">
          <Label className="text-sm text-slate-500">스프린트</Label>
          <Select
            value={selectedSprintUuid ?? ''}
            onChange={(e) => setSelectedSprintUuid(e.target.value || null)}
            className="w-48"
          >
            {sprints.length === 0 ? (
              <option value="">스프린트 없음</option>
            ) : (
              sprints.map((s) => (
                <option key={s.uuid} value={s.uuid}>
                  {s.label}
                </option>
              ))
            )}
          </Select>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="tabular-nums">
            총 {String(items.length)}건
          </Badge>
          {criticalCount > 0 ? (
            <Badge variant="destructive" className="tabular-nums">
              Critical {String(criticalCount)}건
            </Badge>
          ) : null}
          <Select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value as BacklogPriority | 'all')}
            className="w-32"
          >
            <option value="all">전체</option>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {PRIORITY_CONFIG[p].label}
              </option>
            ))}
          </Select>
          <Button
            type="button"
            variant="primary"
            onClick={() => setShowCreate(true)}
            disabled={!selectedSprintUuid}
          >
            + 항목 추가
          </Button>
        </div>
      </div>

      {/* Create Form */}
      {showCreate ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">새 백로그 항목</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>제목</Label>
              <Input
                value={createForm.title}
                onChange={(e) => setCreateForm((f) => ({ ...f, title: e.target.value }))}
                placeholder="백로그 항목 제목"
              />
            </div>
            <div className="flex gap-4">
              <div className="flex-1">
                <Label>우선순위</Label>
                <Select
                  value={createForm.priority}
                  onChange={(e) =>
                    setCreateForm((f) => ({
                      ...f,
                      priority: e.target.value as BacklogPriority,
                    }))
                  }
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {PRIORITY_CONFIG[p].label}
                    </option>
                  ))}
                </Select>
              </div>
            </div>
            <div>
              <Label>비고</Label>
              <Textarea
                value={createForm.note}
                onChange={(e) => setCreateForm((f) => ({ ...f, note: e.target.value }))}
                placeholder="메모 (선택)"
                rows={2}
              />
            </div>
            <div className="flex gap-2">
              <Button
                type="button"
                onClick={handleCreate}
                disabled={creating || !createForm.title.trim()}
              >
                {creating ? '저장 중...' : '저장'}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setShowCreate(false)
                  setCreateForm(INITIAL_FORM)
                }}
              >
                취소
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Backlog List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">백로그 목록</CardTitle>
        </CardHeader>
        <CardContent className="space-y-0 p-0">
          {backlog.status === 'loading' ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : backlog.status === 'error' ? (
            <div className="px-4 py-8 text-center text-sm text-red-500">{backlog.error}</div>
          ) : filteredItems.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-slate-400">
              {items.length === 0
                ? '백로그 항목이 없습니다. 새 항목을 추가해보세요.'
                : '필터 조건에 맞는 항목이 없습니다.'}
            </div>
          ) : (
            <>
              <div className="hidden grid-cols-[88px_1fr_100px_140px_80px] gap-3 border-b border-slate-100 bg-slate-50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500 md:grid">
                <span>우선</span>
                <span>제목</span>
                <span>비고</span>
                <span />
                <span />
              </div>
              <ul className="divide-y divide-slate-100">
                {filteredItems.map((item) => (
                  <li
                    key={item.uuid}
                    className="flex flex-col gap-3 px-4 py-4 md:grid md:grid-cols-[88px_1fr_100px_140px_80px] md:items-center md:gap-3"
                  >
                    <div>
                      <Badge
                        variant={PRIORITY_CONFIG[item.priority].variant}
                        className="w-fit text-[10px] tabular-nums"
                      >
                        {PRIORITY_CONFIG[item.priority].label}
                      </Badge>
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-slate-900">{item.title}</p>
                    </div>
                    <div className="text-xs text-slate-500">{item.note ?? '—'}</div>
                    <div className="flex items-center gap-1">
                      <Button
                        type="button"
                        variant="ghost"
                        className="h-7 px-2 text-xs"
                        onClick={() =>
                          setEditForm({
                            uuid: item.uuid,
                            title: item.title,
                            priority: item.priority,
                            note: item.note ?? '',
                          })
                        }
                      >
                        수정
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        className="h-7 px-2 text-xs text-red-500 hover:text-red-700"
                        onClick={() => setDeleteTarget(item.uuid)}
                      >
                        삭제
                      </Button>
                    </div>
                    <div />
                  </li>
                ))}
              </ul>
            </>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      {editForm ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-base">항목 수정</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>제목</Label>
                <Input
                  value={editForm.title}
                  onChange={(e) => setEditForm((f) => (f ? { ...f, title: e.target.value } : f))}
                />
              </div>
              <div>
                <Label>우선순위</Label>
                <Select
                  value={editForm.priority}
                  onChange={(e) =>
                    setEditForm((f) =>
                      f ? { ...f, priority: e.target.value as BacklogPriority } : f,
                    )
                  }
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {PRIORITY_CONFIG[p].label}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>비고</Label>
                <Textarea
                  value={editForm.note}
                  onChange={(e) => setEditForm((f) => (f ? { ...f, note: e.target.value } : f))}
                  rows={2}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  onClick={handleUpdate}
                  disabled={updating || !editForm.title.trim()}
                >
                  {updating ? '저장 중...' : '저장'}
                </Button>
                <Button type="button" variant="ghost" onClick={() => setEditForm(null)}>
                  취소
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Delete Confirmation */}
      {deleteTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <Card className="w-full max-w-sm">
            <CardHeader>
              <CardTitle className="text-base">삭제 확인</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-600">이 백로그 항목을 삭제하시겠습니까?</p>
              <div className="flex gap-2">
                <Button
                  type="button"
                  className="bg-red-600 text-white hover:bg-red-700"
                  onClick={handleDelete}
                  disabled={deleting}
                >
                  {deleting ? '삭제 중...' : '삭제'}
                </Button>
                <Button type="button" variant="ghost" onClick={() => setDeleteTarget(null)}>
                  취소
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  )
}
