import type { ReactNode } from "react";

import {
  Avatar,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Separator,
} from "@conflow/ui";

import { MOCK_USER } from "../data/mock-user";

const boolBadge = (on: boolean) =>
  on ? (
    <Badge variant="success" className="text-[10px]">
      켜짐
    </Badge>
  ) : (
    <Badge variant="secondary" className="text-[10px]">
      꺼짐
    </Badge>
  );

export const UserPage = () => (
  <div className="mx-auto flex max-w-3xl flex-col gap-6">
    <Card className="overflow-hidden">
      <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:gap-8">
        <Avatar label={MOCK_USER.displayName} size="lg" />
        <div className="min-w-0 flex-1 space-y-2">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              {MOCK_USER.displayName}
            </h2>
            <p className="text-sm text-slate-500">{MOCK_USER.email}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">{MOCK_USER.jobTitle}</Badge>
            <Badge variant="secondary">목 데이터</Badge>
          </div>
        </div>
        <div className="flex shrink-0 flex-col gap-2 sm:items-end">
          <Button type="button" variant="secondary" disabled title="로그인 연동 후 사용">
            프로필 수정
          </Button>
          <p className="text-[11px] text-slate-400">아직 인증 없음</p>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>기본 정보</CardTitle>
        <CardDescription>계정에 묶이는 정적인 필드 예시입니다.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <Row label="표시 언어" value={MOCK_USER.localeLabel} />
        <Separator />
        <Row label="타임존" value={MOCK_USER.timezone} />
        <Separator />
        <Row label="워크스페이스 가입일" value={MOCK_USER.joinedLabel} />
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>소속</CardTitle>
        <CardDescription>팀·역할은 나중에 서버에서 내려옵니다.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {MOCK_USER.teams.map((team) => (
          <div
            key={team.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-100 bg-slate-50/80 px-3 py-2"
          >
            <span className="font-medium text-slate-900">{team.name}</span>
            <Badge variant="outline">{team.roleLabel}</Badge>
          </div>
        ))}
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>알림 (더미)</CardTitle>
        <CardDescription>토글은 아직 동작하지 않습니다.</CardDescription>
      </CardHeader>
      <CardContent className="divide-y divide-slate-100">
        <NotifyRow
          label="일간 요약 메일"
          value={boolBadge(MOCK_USER.notificationSummary.emailDigest)}
        />
        <NotifyRow
          label="스프린트 시작 알림"
          value={boolBadge(MOCK_USER.notificationSummary.sprintReminder)}
        />
        <NotifyRow
          label="멘션 푸시"
          value={boolBadge(MOCK_USER.notificationSummary.mentionPush)}
        />
      </CardContent>
    </Card>
  </div>
);

const Row = ({
  label,
  value,
}: {
  readonly label: string;
  readonly value: string;
}) => (
  <div className="flex flex-wrap items-center justify-between gap-2">
    <span className="text-slate-500">{label}</span>
    <span className="font-medium text-slate-900">{value}</span>
  </div>
);

const NotifyRow = ({
  label,
  value,
}: {
  readonly label: string;
  readonly value: ReactNode;
}) => (
  <div className="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
    <span className="text-sm text-slate-700">{label}</span>
    {value}
  </div>
);
