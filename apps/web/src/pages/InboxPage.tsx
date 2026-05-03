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

import { CURRENT_USER } from "../data/current-session";
import type { InboxEntryType } from "../data/mock-inbox";
import { MOCK_INBOX } from "../data/mock-inbox";

const typeLabel = (t: InboxEntryType): string => {
  if (t === "mention") {
    return "멘션";
  }
  if (t === "deadline") {
    return "마감";
  }
  if (t === "file") {
    return "파일";
  }
  return "시스템";
};

const typeBadgeVariant = (
  t: InboxEntryType,
): "default" | "secondary" | "outline" | "destructive" => {
  if (t === "mention") {
    return "default";
  }
  if (t === "deadline") {
    return "destructive";
  }
  if (t === "file") {
    return "secondary";
  }
  return "outline";
};

export const InboxPage = () => {
  const box = MOCK_INBOX;
  const unread = box.entries.filter((e) => !e.read).length;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">{box.contextLine}</p>
          <p className="text-xs text-slate-400">{box.wireNote}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="tabular-nums">
            미읽음 {String(unread)}
          </Badge>
          <Button type="button" variant="secondary" disabled title="추후">
            모두 읽음
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">알림</CardTitle>
          <CardDescription>
            수신 대상:{" "}
            <span className="font-medium text-slate-700">
              {CURRENT_USER.displayName}
            </span>{" "}
            ({CURRENT_USER.email})
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <ul className="divide-y divide-slate-100">
            {box.entries.map((e) => (
              <li
                key={e.id}
                className={`flex gap-3 px-4 py-4 sm:gap-4 ${
                  e.read ? "bg-white" : "bg-slate-50/80"
                }`}
              >
                <Avatar
                  label={e.fromName}
                  size="sm"
                  className="mt-0.5 shrink-0"
                />
                <div className="min-w-0 flex-1 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant={typeBadgeVariant(e.type)}
                      className="text-[10px]"
                    >
                      {typeLabel(e.type)}
                    </Badge>
                    {!e.read ? (
                      <span className="h-1.5 w-1.5 rounded-full bg-slate-900" />
                    ) : null}
                    <span className="text-xs text-slate-400">
                      {e.timeLabel}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-slate-900">
                    {e.title}
                  </p>
                  <p className="text-sm leading-relaxed text-slate-600">
                    {e.body}
                  </p>
                  <p className="text-xs text-slate-500">
                    보낸 사람 · {e.fromName}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
