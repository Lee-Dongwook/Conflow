import { useState } from "react";

import { BoardPage } from "./pages/BoardPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { ThisWeekPage } from "./pages/ThisWeekPage";
import { UserPage } from "./pages/UserPage";
import { SideBar } from "./widgets/sidebar";

const NAV_TITLE: Record<string, string> = {
  dashboard: "대시보드",
  sprint: "이번 주",
  board: "보드",
  backlog: "백로그",
  metrics: "한눈에",
  retro: "회고",
  profile: "내 계정",
  inbox: "수신함",
  workspace: "워크스페이스",
};

const NAV_SUBTITLE: Record<string, string> = {
  dashboard: "팀플·스터디 팀용 · 목 세션 사용자 이땡땡 기준. (포폴 목 데이터)",
  sprint:
    "월~일 한 줄 스캔 · 가장 임박 강조. 간트 대신 가벼운 주간 뷰 (목 데이터)",
  board: "할 일 · 하는 중 · 완료 칸반. 드래그 없음 — 와이어·포폴용.",
  profile: "목 프로필입니다. 로그인 붙이면 교체됩니다.",
};

export const App = () => {
  const [activeNavId, setActiveNavId] = useState("dashboard");
  const navTitle = NAV_TITLE[activeNavId] ?? activeNavId;
  const navSubtitle =
    NAV_SUBTITLE[activeNavId] ??
    "와이어 단계입니다. 팀플 ICP에 맞춰 메뉴마다 채워 넣을 예정.";

  const main =
    activeNavId === "profile" ? (
      <UserPage />
    ) : activeNavId === "dashboard" ? (
      <DashboardPage />
    ) : activeNavId === "sprint" ? (
      <ThisWeekPage />
    ) : activeNavId === "board" ? (
      <BoardPage />
    ) : (
      <PlaceholderPage navId={activeNavId} />
    );

  return (
    <div className="flex min-h-screen bg-slate-50">
      <SideBar activeNavId={activeNavId} onNavChange={setActiveNavId} />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-slate-200 bg-white px-8 py-6">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            현재 화면
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">
            {navTitle}
          </h1>
          <p className="mt-1 text-sm text-slate-600">{navSubtitle}</p>
        </header>
        <main className="flex-1 p-8">{main}</main>
      </div>
    </div>
  );
};
