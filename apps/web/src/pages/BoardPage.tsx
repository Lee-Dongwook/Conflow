import {
  Avatar,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@conflow/ui";

import { CURRENT_USER } from "app/entities/session";
import { MOCK_BOARD, type BoardTaskCard } from "app/entities/board";

export const BoardPage = () => {
  const b = MOCK_BOARD;

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">{b.contextLine}</p>
          <p className="text-xs text-slate-400">{b.wireNote}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" disabled title="추후">
            필터
          </Button>
          <Button type="button" variant="ghost" disabled title="추후">
            카드 추가
          </Button>
        </div>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-3 md:overflow-visible">
        {b.columns.map((col) => (
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
              {col.cards.map((task: BoardTaskCard) => {
                const isMine = task.assignee === CURRENT_USER.displayName;
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
                        <Badge
                          variant="default"
                          className="shrink-0 text-[10px]"
                        >
                          나
                        </Badge>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
