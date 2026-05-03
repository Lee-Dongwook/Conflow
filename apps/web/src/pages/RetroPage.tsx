import { Badge, Card, CardContent, CardHeader, CardTitle } from "@conflow/ui";

import { MOCK_RETRO } from "../data/mock-retro";

const columnAccent = (
  accent: (typeof MOCK_RETRO)["columns"][number]["accent"],
): string => {
  if (accent === "emerald") {
    return "border-l-emerald-500 bg-emerald-50/50";
  }
  if (accent === "amber") {
    return "border-l-amber-500 bg-amber-50/50";
  }
  return "border-l-sky-500 bg-sky-50/50";
};

export const RetroPage = () => {
  const r = MOCK_RETRO;

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">{r.contextLine}</p>
          <p className="text-xs text-slate-400">{r.wireNote}</p>
        </div>
        <Badge variant="outline">{r.sprintLabel}</Badge>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {r.columns.map((col) => (
          <Card
            key={col.id}
            className={`border-l-4 shadow-sm ${columnAccent(col.accent)}`}
          >
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{col.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-0">
              <ul className="list-disc space-y-2 pl-5 text-sm leading-relaxed text-slate-700">
                {col.items.map((item, idx) => (
                  <li key={`${col.id}-${String(idx)}`}>{item}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="text-center text-xs text-slate-400">
        회고 입력·투표·익명 모드는 비즈니스 레이어 설계 후 연결 예정입니다.
      </p>
    </div>
  );
};
