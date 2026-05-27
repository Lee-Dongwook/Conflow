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
} from "@conflow/ui";

import { CURRENT_USER } from "app/entities/session";
import { MOCK_TEAM_DASHBOARD } from "app/entities/dashboard";

const statusBadge = (status: "todo" | "doing" | "done") => {
  if (status === "done") {
    return (
      <Badge variant="success" className="text-[10px]">
        완료
      </Badge>
    );
  }
  if (status === "doing") {
    return (
      <Badge variant="warning" className="text-[10px]">
        하는 중
      </Badge>
    );
  }
  return (
    <Badge variant="secondary" className="text-[10px]">
      대기
    </Badge>
  );
};

/** 팀플·스터디 ICP — 현재 세션 사용자({@link CURRENT_USER}) 기준 */
export const DashboardPage = () => {
  const d = MOCK_TEAM_DASHBOARD;
  const myTasks = d.tasks.filter(
    (t) => t.assignee === CURRENT_USER.displayName,
  );

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6">
      <Card>
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">{d.courseLabel}</Badge>
            <Badge variant="secondary">{d.weekLabel}</Badge>
            <Badge variant="default" className="text-[10px]">
              보는 사람: {CURRENT_USER.displayName}
            </Badge>
          </div>
          <CardTitle className="mt-2 text-xl">{d.teamName}</CardTitle>
          <CardDescription>
            {d.periodLabel} · 목 세션{" "}
            <span className="font-medium text-slate-700">
              {CURRENT_USER.email}
            </span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm font-medium text-slate-700">이번 주 목표</p>
          <p className="text-base leading-relaxed text-slate-900">
            {d.oneLineGoal}
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">다음 마감</CardTitle>
            <CardDescription>일정은 교수·과제 맞춰 넣을 예정</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-semibold text-rose-700">
              {d.nextDeadlineLabel}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">이번 주 진행</CardTitle>
            <CardDescription>팀이 정한 체크리스트 기준</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Progress value={d.progressPercent} />
            <p className="text-xs text-slate-500">
              {String(d.progressPercent)}% · 내 담당 {String(myTasks.length)}건
              포함
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-4 pb-2">
          <div>
            <CardTitle className="text-base">팀 할 일</CardTitle>
            <CardDescription>
              담당 &quot;나&quot;({CURRENT_USER.displayName})는 배지로 표시 ·
              전체 {String(d.tasks.length)}건
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="secondary"
              disabled
              title="보드 화면 연결 후"
            >
              보드로 이동
            </Button>
            <Button
              type="button"
              variant="ghost"
              disabled
              title="백로그 연결 후"
            >
              백로그
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-0">
          {d.tasks.map((task, index) => {
            const isMine = task.assignee === CURRENT_USER.displayName;
            return (
              <div key={task.id}>
                {index > 0 ? <Separator className="my-3" /> : null}
                <div className="flex flex-wrap items-center gap-3">
                  <Avatar label={task.assignee} size="sm" />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-medium text-slate-900">{task.title}</p>
                      {isMine ? (
                        <Badge variant="default" className="text-[10px]">
                          나
                        </Badge>
                      ) : null}
                    </div>
                    <p className="text-xs text-slate-500">{task.assignee}</p>
                  </div>
                  {statusBadge(task.status)}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Card className="border-amber-200 bg-amber-50/40">
        <CardHeader className="pb-2">
          <CardTitle className="text-base text-amber-950">막힌 것</CardTitle>
          <CardDescription className="text-amber-900/80">
            없으면 이 카드는 안 보이게 만들면 됨
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-amber-950">{d.blockerNote}</p>
        </CardContent>
      </Card>
    </div>
  );
};
