import { useCallback, useEffect, useState } from 'react'

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
} from '@conflow/ui'

import { MOCK_BOARD, type BoardCardRead, type BoardColumn } from 'app/entities/board'
import { CURRENT_USER, useSession } from 'app/entities/session'
import { sprintApi, type SprintRead } from 'app/entities/sprint'
import { userApi } from 'app/entities/user'
import { useBoard } from 'app/features/board'

const COLUMNS: readonly { readonly id: string; readonly title: string; readonly hint: string }[] = [
  { id: 'todo', title: '할 일', hint: '아직 손 안 댄 작업' },
  { id: 'doing', title: '하는 중', hint: '지금 진행 중' },
  { id: 'done', title: '완료', hint: '이번 주 안에 끝낸 것' },
]

const buildDemoColumns = (): readonly BoardColumn[] => MOCK_BOARD.columns

export const BoardPage = () => {
  const session = useSession()
  const isAuthenticated = session.status === 'authenticated'

  const [teamUuid, setTeamUuid] = useState<string | null>(null)
  const [sprint, setSprint] = useState<SprintRead | null>(null)
  const [initLoading, setInitLoading] = useState(isAuthenticated)

  useEffect(() => {
    if (!isAuthenticated) {
      setInitLoading(false)
      return
    }
    const init = async () => {
      try {
        const user = await userApi.me()
        const firstTeamUuid = user.teamMemberships?.[0]?.teamUuid
        if (firstTeamUuid) {
          setTeamUuid(firstTeamUuid)
          const sprints = await sprintApi.listByTeam(firstTeamUuid)
          if (sprints[0]) {
            setSprint(sprints[0])
          }
        }
      } catch {
        // silently fail
      }
      setInitLoading(false)
    }
    init()
  }, [isAuthenticated])

  const board = useBoard(sprint?.uuid ?? null)

  const [createCol, setCreateCol] = useState<string | null>(null)
  const [createTitle, setCreateTitle] = useState('')

  const handleCreate = useCallback(async () => {
    if (!createCol || !createTitle.trim() || !teamUuid || !sprint) return
    try {
      await board.create({
        teamUuid,
        sprintUuid: sprint.uuid,
        title: createTitle.trim(),
        columnKey: createCol,
      })
      setCreateTitle('')
      setCreateCol(null)
    } catch {
      // keep form open on error
    }
  }, [createCol, createTitle, teamUuid, sprint, board])

  const handleDelete = useCallback(
    async (cardUuid: string) => {
      try {
        await board.remove(cardUuid)
      } catch {
        // silently fail
      }
    },
    [board],
  )

  const handleMove = useCallback(
    async (cardUuid: string, targetColumn: string) => {
      try {
        await board.move(cardUuid, { columnKey: targetColumn, position: 0 })
      } catch {
        // silently fail
      }
    },
    [board],
  )

  const isDemo = !isAuthenticated
  const currentUserName = isAuthenticated
    ? (session.user.user_metadata?.name ?? '나')
    : CURRENT_USER.displayName

  if (initLoading) {
    return <p className="text-center text-sm text-slate-400">보드를 불러오는 중...</p>
  }

  if (isDemo) {
    return <DemoBoardView currentUserName={currentUserName} />
  }

  if (board.status === 'loading') {
    return <p className="text-center text-sm text-slate-400">보드를 불러오는 중...</p>
  }

  if (board.status === 'error' && 'error' in board) {
    return <p className="text-center text-sm text-red-500">{board.error}</p>
  }

  const cards: readonly BoardCardRead[] =
    board.status === 'success' ? board.cards : []

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">
            {sprint?.label ?? '스프린트 없음'}
          </p>
        </div>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-3 md:overflow-visible">
        {COLUMNS.map((col) => {
          const colCards = cards.filter((c) => c.columnKey === col.id)
          return (
            <Card
              key={col.id}
              className="flex min-w-[280px] shrink-0 flex-col md:min-w-0"
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between gap-2">
                  <CardTitle className="text-base">{col.title}</CardTitle>
                  <Badge variant="secondary" className="tabular-nums">
                    {String(colCards.length)}
                  </Badge>
                </div>
                <CardDescription>{col.hint}</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-1 flex-col gap-3 pt-0">
                {colCards.map((card) => (
                  <div
                    key={card.uuid}
                    className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm"
                  >
                    <p className="text-sm font-medium leading-snug text-slate-900">
                      {card.title}
                    </p>
                    <div className="mt-3 flex items-center justify-between gap-2">
                      <div className="flex min-w-0 items-center gap-2">
                        <Avatar label={card.assigneeUserUuid ?? '?'} size="sm" />
                      </div>
                      <div className="flex gap-1">
                        {col.id !== 'done' ? (
                          <Button
                            type="button"
                            variant="ghost"
                            className="h-6 px-2 text-[10px]"
                            onClick={() =>
                              handleMove(
                                card.uuid,
                                col.id === 'todo' ? 'doing' : 'done',
                              )
                            }
                          >
                            {col.id === 'todo' ? '시작' : '완료'}
                          </Button>
                        ) : null}
                        <Button
                          type="button"
                          variant="ghost"
                          className="h-6 px-2 text-[10px] text-red-500"
                          onClick={() => handleDelete(card.uuid)}
                        >
                          삭제
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}

                {createCol === col.id ? (
                  <div className="space-y-2 rounded-lg border border-slate-200 bg-white p-3">
                    <Input
                      placeholder="카드 제목"
                      value={createTitle}
                      onChange={(e) => setCreateTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleCreate()
                        if (e.key === 'Escape') setCreateCol(null)
                      }}
                      autoFocus
                    />
                    <div className="flex gap-2">
                      <Button
                        type="button"
                        variant="primary"
                        className="h-7 text-xs"
                        onClick={handleCreate}
                      >
                        추가
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        className="h-7 text-xs"
                        onClick={() => setCreateCol(null)}
                      >
                        취소
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Button
                    type="button"
                    variant="ghost"
                    className="w-full text-xs text-slate-400"
                    onClick={() => {
                      setCreateCol(col.id)
                      setCreateTitle('')
                    }}
                  >
                    + 카드 추가
                  </Button>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

const DemoBoardView = ({
  currentUserName,
}: {
  readonly currentUserName: string
}) => {
  const columns = buildDemoColumns()
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div className="rounded-lg border border-blue-200 bg-blue-50/60 px-4 py-3 text-sm text-blue-800">
        데모 데이터를 보고 있습니다. 로그인하면 실제 보드를 사용할 수 있어요.
      </div>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">{MOCK_BOARD.contextLine}</p>
        </div>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-3 md:overflow-visible">
        {columns.map((col) => (
          <Card
            key={col.id}
            className="flex min-w-[280px] shrink-0 flex-col md:min-w-0"
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between gap-2">
                <CardTitle className="text-base">{col.title}</CardTitle>
                <Badge variant="secondary" className="tabular-nums">
                  {String(col.cards.length)}
                </Badge>
              </div>
              <CardDescription>{col.hint}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col gap-3 pt-0">
              {col.cards.map((task) => {
                const isMine = task.assignee === currentUserName
                return (
                  <div
                    key={task.id}
                    className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm"
                  >
                    <p className="text-sm font-medium leading-snug text-slate-900">
                      {task.title}
                    </p>
                    {task.tag !== undefined ? (
                      <Badge variant="outline" className="mt-2 text-[10px]">
                        {task.tag}
                      </Badge>
                    ) : null}
                    <div className="mt-3 flex items-center justify-between gap-2">
                      <div className="flex min-w-0 items-center gap-2">
                        <Avatar label={task.assignee} size="sm" />
                        <span className="truncate text-xs text-slate-600">
                          {task.assignee}
                        </span>
                      </div>
                      {isMine ? (
                        <Badge variant="default" className="shrink-0 text-[10px]">
                          나
                        </Badge>
                      ) : null}
                    </div>
                  </div>
                )
              })}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
