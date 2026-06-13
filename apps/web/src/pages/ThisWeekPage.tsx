import {
  Avatar,
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Separator,
} from "@conflow/ui";

import { CURRENT_USER } from "app/entities/session";
import { MOCK_THIS_WEEK, type WeekMilestone } from "app/entities/week";
import { RealThisWeekView } from "app/features/this-week";

const useSprintUuidFromQuery = (): string | null => {
  if (typeof window === "undefined") return null;
  return new URLSearchParams(window.location.search).get("sprint");
};

/** 월~일 한 줄 스캔 + 임박 강조 (간트 대신 가벼운 주간 뷰) */
export const ThisWeekPage = () => {
  const sprintUuid = useSprintUuidFromQuery();
  if (sprintUuid) {
    return <RealThisWeekView sprintUuid={sprintUuid} />;
  }

  const w = MOCK_THIS_WEEK;

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div className="flex flex-col gap-2">
        <p className="text-sm text-slate-500">{w.contextLine}</p>
        <h2 className="text-lg font-semibold text-slate-900">{w.rangeLabel}</h2>
        <p className="text-base leading-relaxed text-slate-800">
          {w.sharedGoal}
        </p>
      </div>

      <Card className="border-teal-200 bg-teal-50/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-base text-teal-950">가장 임박</CardTitle>
          <CardDescription className="text-teal-900/80">
            오늘 기준 다음으로 붙은 마감/마일스톤 (목 데이터)
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-3">
          <Badge variant="destructive" className="text-[10px]">
            Critical path
          </Badge>
          <span className="font-medium text-teal-950">
            {w.nextUp.weekday} {String(w.nextUp.dayOfMonth)}일 ·{" "}
            {w.nextUp.title}
          </span>
          <span className="flex items-center gap-2 text-sm text-teal-900">
            <Avatar label={w.nextUp.assignee} size="sm" />
            {w.nextUp.assignee}
            {w.nextUp.assignee === CURRENT_USER.displayName ? (
              <Badge variant="default" className="text-[10px]">
                나
              </Badge>
            ) : null}
          </span>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">주간 타임라인</CardTitle>
          <CardDescription>
            월~일 한 줄로만 본다. 가로 스크롤은 좁은 화면용.
          </CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto pb-1">
          <div className="flex min-w-[640px] gap-2 md:min-w-0 md:grid md:grid-cols-7 md:gap-3">
            {w.days.map((day) => (
              <div
                key={`${day.weekday}-${String(day.dayOfMonth)}`}
                className={`flex min-w-[72px] flex-1 flex-col rounded-lg border p-2 md:min-w-0 ${
                  day.isToday
                    ? "border-teal-500 bg-teal-50 ring-2 ring-teal-400/40"
                    : "border-slate-200 bg-white"
                }`}
              >
                <div className="mb-2 text-center">
                  <p className="text-[11px] font-medium text-slate-500">
                    {day.weekday}
                  </p>
                  <p className="text-lg font-semibold tabular-nums text-slate-900">
                    {String(day.dayOfMonth)}
                  </p>
                  {day.isToday ? (
                    <Badge variant="default" className="mt-1 text-[10px]">
                      오늘
                    </Badge>
                  ) : null}
                </div>
                <div className="flex flex-col gap-2">
                  {day.milestones.length === 0 ? (
                    <p className="text-center text-[10px] text-slate-400">—</p>
                  ) : (
                    day.milestones.map((m: WeekMilestone, i) => (
                      <div
                        key={`${day.weekday}-${String(i)}-${m.title}`}
                        className={`rounded-md border px-1.5 py-1.5 text-[11px] leading-snug ${
                          m.critical
                            ? "border-amber-300 bg-amber-50 text-amber-950"
                            : "border-slate-100 bg-slate-50 text-slate-800"
                        }`}
                      >
                        <p className="font-medium">{m.title}</p>
                        <div className="mt-1 flex items-center gap-1">
                          <Avatar
                            label={m.assignee}
                            size="sm"
                            className="size-5 text-[9px]"
                          />
                          <span className="truncate text-slate-600">
                            {m.assignee}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">이번 주 마감·일정 목록</CardTitle>
          <CardDescription>타임라인과 같은 데이터를 리스트로.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-0">
          {w.days
            .filter((day) => day.milestones.length > 0)
            .map((day, idx) => (
              <div key={`list-${day.weekday}-${String(day.dayOfMonth)}`}>
                {idx > 0 ? <Separator className="my-4" /> : null}
                <p className="mb-2 text-xs font-semibold text-slate-500">
                  {day.weekday} {String(day.dayOfMonth)}일
                  {day.isToday ? (
                    <Badge variant="outline" className="ml-2 text-[10px]">
                      오늘
                    </Badge>
                  ) : null}
                </p>
                <ul className="space-y-2">
                  {day.milestones.map((m: WeekMilestone) => (
                    <li
                      key={`${day.weekday}-${m.title}`}
                      className="flex flex-wrap items-start gap-2 rounded-lg border border-slate-100 bg-slate-50/80 px-3 py-2 text-sm"
                    >
                      {m.critical ? (
                        <Badge
                          variant="warning"
                          className="shrink-0 text-[10px]"
                        >
                          중요
                        </Badge>
                      ) : null}
                      <span className="flex-1 font-medium text-slate-900">
                        {m.title}
                      </span>
                      <span className="flex items-center gap-1.5 text-slate-600">
                        <Avatar label={m.assignee} size="sm" />
                        {m.assignee}
                        {m.assignee === CURRENT_USER.displayName ? (
                          <Badge variant="default" className="text-[10px]">
                            나
                          </Badge>
                        ) : null}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
        </CardContent>
      </Card>
    </div>
  );
};
