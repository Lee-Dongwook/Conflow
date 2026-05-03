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

import type { BacklogItem, BacklogPriority } from "../data/mock-backlog";
import { CURRENT_USER } from "../data/current-session";
import { MOCK_BACKLOG } from "../data/mock-backlog";

const priorityLabel = (p: BacklogPriority): string => {
  if (p === "p0") {
    return "P0";
  }
  if (p === "p1") {
    return "P1";
  }
  return "P2";
};

const priorityBadgeVariant = (
  p: BacklogPriority,
): "destructive" | "warning" | "secondary" => {
  if (p === "p0") {
    return "destructive";
  }
  if (p === "p1") {
    return "warning";
  }
  return "secondary";
};

export const BacklogPage = () => {
  const bl = MOCK_BACKLOG;
  const p0Count = bl.items.filter((i) => i.priority === "p0").length;

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">{bl.contextLine}</p>
          <p className="text-xs text-slate-400">{bl.wireNote}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="tabular-nums">
            총 {String(bl.items.length)}건
          </Badge>
          <Badge variant="destructive" className="tabular-nums">
            P0 {String(p0Count)}건
          </Badge>
          <Button type="button" variant="secondary" disabled title="추후">
            우선순위 필터
          </Button>
          <Button type="button" variant="ghost" disabled title="추후">
            항목 추가
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">백로그 목록</CardTitle>
          <CardDescription>
            스프린트·보드에 넣기 전 아이디어·작업 풀. 컬럼은 코어 설계 시
            entities와 맞출 예정.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-0 p-0">
          <div className="hidden grid-cols-[88px_1fr_140px_120px] gap-3 border-b border-slate-100 bg-slate-50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500 md:grid">
            <span>우선</span>
            <span>제목</span>
            <span>담당</span>
            <span className="text-right">비고</span>
          </div>
          <ul className="divide-y divide-slate-100">
            {bl.items.map((item: BacklogItem) => {
              const isMine = item.assignee === CURRENT_USER.displayName;
              return (
                <li
                  key={item.id}
                  className="flex flex-col gap-3 px-4 py-4 md:grid md:grid-cols-[88px_1fr_140px_120px] md:items-center md:gap-3"
                >
                  <div className="flex items-center gap-2 md:block">
                    <span className="text-xs text-slate-400 md:hidden">
                      우선
                    </span>
                    <Badge
                      variant={priorityBadgeVariant(item.priority)}
                      className="w-fit text-[10px] tabular-nums"
                    >
                      {priorityLabel(item.priority)}
                    </Badge>
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium text-slate-900">{item.title}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Avatar label={item.assignee} size="sm" />
                    <span className="truncate text-sm text-slate-700">
                      {item.assignee}
                    </span>
                    {isMine ? (
                      <Badge variant="default" className="shrink-0 text-[10px]">
                        나
                      </Badge>
                    ) : null}
                  </div>
                  <div className="text-right text-xs text-slate-500 md:pl-0">
                    {item.note ?? "—"}
                  </div>
                </li>
              );
            })}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
