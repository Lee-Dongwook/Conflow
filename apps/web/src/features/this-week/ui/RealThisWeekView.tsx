import {
  Avatar,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Spinner,
} from '@conflow/ui'
import { useEffect, useState } from 'react'

import { weekApi, type WeekMilestoneRead } from 'app/entities/week'

import { fetchCurrentUser, type CurrentUser } from '../api'

const formatDate = (iso: string | null): string => {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${String(d.getMonth() + 1)}/${String(d.getDate())}`
}

const shortLabel = (owner: string, currentUuid: string | null): string => {
  if (currentUuid && owner === currentUuid) return '나'
  return owner.slice(0, 8)
}

type Props = {
  readonly sprintUuid: string
}

export const RealThisWeekView = ({ sprintUuid }: Props) => {
  const [milestones, setMilestones] = useState<readonly WeekMilestoneRead[]>([])
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [newTitle, setNewTitle] = useState('')
  const [newDueOn, setNewDueOn] = useState('')
  const [newOwnerUuid, setNewOwnerUuid] = useState('')
  const [creating, setCreating] = useState(false)

  const reload = async () => {
    setError(null)
    try {
      const list = await weekApi.listBySprint(sprintUuid)
      setMilestones(list)
    } catch (err) {
      setError(err instanceof Error ? err.message : '목표를 불러오지 못했습니다.')
    }
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      try {
        const [user] = await Promise.all([fetchCurrentUser(), reload()])
        setCurrentUser(user)
        setNewOwnerUuid(user.uuid)
      } catch (err) {
        setError(err instanceof Error ? err.message : '초기화 실패')
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [sprintUuid])

  const handleCreate = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!newTitle.trim()) return
    setCreating(true)
    setError(null)
    try {
      await weekApi.create({
        sprint_uuid: sprintUuid,
        owner_user_uuid: newOwnerUuid || (currentUser?.uuid ?? ''),
        title: newTitle.trim(),
        due_on: newDueOn ? new Date(newDueOn).toISOString() : null,
      })
      setNewTitle('')
      setNewDueOn('')
      await reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : '목표 등록 실패')
    } finally {
      setCreating(false)
    }
  }

  const handleToggleComplete = async (m: WeekMilestoneRead) => {
    try {
      if (m.completed_at) {
        await weekApi.uncomplete(m.uuid)
      } else {
        await weekApi.complete(m.uuid)
      }
      await reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : '상태 변경 실패')
    }
  }

  const handleDelete = async (m: WeekMilestoneRead) => {
    if (!confirm(`"${m.title}" 목표를 삭제할까요?`)) return
    try {
      await weekApi.remove(m.uuid)
      await reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : '삭제 실패')
    }
  }

  if (loading) {
    return (
      <div className="mx-auto flex max-w-3xl items-center justify-center py-12">
        <Spinner />
      </div>
    )
  }

  const open = milestones.filter((m) => !m.completed_at)
  const done = milestones.filter((m) => m.completed_at)

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">새 목표 등록</CardTitle>
          <CardDescription>
            이번 주 우리 팀이 해낼 것 1줄로 등록. 담당자는 본인 기본.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="flex flex-col gap-3">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="title">목표</Label>
              <Input
                id="title"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="예: 와이어프레임 초안"
                maxLength={512}
                required
              />
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="flex flex-1 flex-col gap-1.5">
                <Label htmlFor="due_on">마감일 (선택)</Label>
                <Input
                  id="due_on"
                  type="date"
                  value={newDueOn}
                  onChange={(e) => setNewDueOn(e.target.value)}
                />
              </div>
              <div className="flex flex-1 flex-col gap-1.5">
                <Label htmlFor="owner">담당자 UUID</Label>
                <Input
                  id="owner"
                  value={newOwnerUuid}
                  onChange={(e) => setNewOwnerUuid(e.target.value)}
                  placeholder={currentUser?.uuid ?? ''}
                />
              </div>
            </div>
            {error ? (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900">
                {error}
              </div>
            ) : null}
            <Button type="submit" disabled={creating || !newTitle.trim()}>
              {creating ? '등록 중...' : '+ 목표 등록'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">진행 중 ({open.length})</CardTitle>
          <CardDescription>
            마감일 임박순 정렬. 체크박스로 완료/미완료 토글.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {open.length === 0 ? (
            <p className="text-sm text-slate-500">등록된 목표가 없습니다.</p>
          ) : (
            <ul className="flex flex-col gap-2">
              {open.map((m) => (
                <li
                  key={m.uuid}
                  className="flex items-center gap-3 rounded-md border border-slate-200 bg-white px-3 py-2"
                >
                  <input
                    type="checkbox"
                    checked={false}
                    onChange={() => handleToggleComplete(m)}
                    aria-label="완료 처리"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-slate-900">
                      {m.title}
                    </p>
                    <p className="text-xs text-slate-500">
                      마감 {formatDate(m.due_on)}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-slate-600">
                    <Avatar
                      label={shortLabel(m.owner_user_uuid, currentUser?.uuid ?? null)}
                      size="sm"
                    />
                    <span>{shortLabel(m.owner_user_uuid, currentUser?.uuid ?? null)}</span>
                    {currentUser && m.owner_user_uuid === currentUser.uuid ? (
                      <Badge variant="default" className="text-[10px]">나</Badge>
                    ) : null}
                  </div>
                  <button
                    onClick={() => handleDelete(m)}
                    className="text-xs text-slate-400 hover:text-red-600"
                  >
                    삭제
                  </button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {done.length > 0 ? (
        <Card className="opacity-80">
          <CardHeader>
            <CardTitle className="text-base">완료 ({done.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-2">
              {done.map((m) => (
                <li
                  key={m.uuid}
                  className="flex items-center gap-3 rounded-md border border-slate-100 bg-slate-50 px-3 py-2"
                >
                  <input
                    type="checkbox"
                    checked={true}
                    onChange={() => handleToggleComplete(m)}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-slate-500 line-through">
                      {m.title}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(m)}
                    className="text-xs text-slate-400 hover:text-red-600"
                  >
                    삭제
                  </button>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
