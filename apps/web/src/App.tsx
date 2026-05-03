import { useState } from "react";

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Progress,
} from "@conflow/ui";

import { SideBar } from "./widgets/sidebar";

const NAV_TITLE: Record<string, string> = {
  dashboard: "대시보드",
  sprint: "스프린트",
  board: "보드",
  backlog: "백로그",
  metrics: "지표",
  retro: "회고",
};

export const App = () => {
  const [activeNavId, setActiveNavId] = useState("dashboard");
  const navTitle = NAV_TITLE[activeNavId] ?? activeNavId;

  return (
    <div className="flex min-h-screen bg-slate-50">
      <SideBar activeNavId={activeNavId} onNavChange={setActiveNavId} />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-slate-200 bg-white px-8 py-6">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            현재 메뉴
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">{navTitle}</h1>
          <p className="mt-1 text-sm text-slate-600">
            화면만 잡는 단계예요. 다음에 같이 정할 건 “이 제품이 줄여 줄 하루” 한 문장입니다.
          </p>
        </header>
        <main className="flex-1 p-8">
          <Card className="max-w-2xl">
            <CardHeader>
              <CardTitle>스프린트 24</CardTitle>
              <CardDescription>
                React + Tailwind v4 + @conflow/ui + 사이드바 위젯
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="success">진행 중</Badge>
                <Badge variant="outline">2026-Q1</Badge>
              </div>
              <div>
                <p className="mb-2 text-xs font-medium text-slate-600">
                  스프린트 목표 달성
                </p>
                <Progress value={62} />
              </div>
              <Button type="button">보드 열기</Button>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
};
