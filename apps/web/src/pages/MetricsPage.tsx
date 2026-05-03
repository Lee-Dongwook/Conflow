import {
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Progress,
} from "@conflow/ui";

import { CURRENT_USER } from "../data/current-session";
import { MOCK_METRICS } from "../data/mock-metrics";

export const MetricsPage = () => {
  const m = MOCK_METRICS;

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">{m.contextLine}</p>
          <p className="text-xs text-slate-400">{m.wireNote}</p>
        </div>
        <Badge variant="outline" className="tabular-nums">
          {m.weekLabel}
        </Badge>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {m.statCards.map((c) => (
          <Card key={c.id}>
            <CardHeader className="pb-2">
              <CardDescription className="text-xs">{c.label}</CardDescription>
              <CardTitle className="text-3xl font-semibold tabular-nums">
                {c.value}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-xs text-slate-500">{c.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">영역별 진행 (목 시각화)</CardTitle>
            <CardDescription>
              진행률은 목 숫자입니다. 차트 라이브러리는 코어·디자인 확정 후.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {m.progressBars.map((row) => (
              <div key={row.id} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-800">
                    {row.label}
                  </span>
                  <span className="tabular-nums text-slate-500">
                    {String(row.percent)}%
                  </span>
                </div>
                <Progress value={row.percent} />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">숫자 스냅샷</CardTitle>
            <CardDescription>
              현재 사용자{" "}
              <span className="font-medium text-slate-700">
                {CURRENT_USER.displayName}
              </span>
              기준 행이 포함됩니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y divide-slate-100 rounded-lg border border-slate-100 bg-white">
              {m.snapshotRows.map((row) => (
                <li
                  key={row.label}
                  className="flex items-center justify-between px-4 py-3 text-sm"
                >
                  <span className="text-slate-600">{row.label}</span>
                  <span className="font-semibold tabular-nums text-slate-900">
                    {row.value}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
