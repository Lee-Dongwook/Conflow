import { useState } from "react";

import { BacklogPage } from "./pages/BacklogPage";
import { BoardPage } from "./pages/BoardPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DmPage } from "./pages/DmPage";
import { HuddlePage } from "./pages/HuddlePage";
import { MeetingSummaryPage } from "./pages/MeetingSummaryPage";
import { InboxPage } from "./pages/InboxPage";
import { MetricsPage } from "./pages/MetricsPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { RetroPage } from "./pages/RetroPage";
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
  dm: "다이렉트 메시지",
  huddle: "허들",
  meetingSummary: "AI 회의록",
};

const NAV_SUBTITLE: Record<string, string> = {
  dashboard: "팀플·스터디 팀용 · 목 세션 사용자 이땡땡 기준. (포폴 목 데이터)",
  sprint:
    "월~일 한 줄 스캔 · 가장 임박 강조. 간트 대신 가벼운 주간 뷰 (목 데이터)",
  board: "할 일 · 하는 중 · 완료 칸반. 드래그 없음 — 와이어·포폴용.",
  backlog:
    "보드에 넣기 전 작업 풀. 우선순위·담당만 표시 — 코어·스키마는 와이어 후.",
  metrics:
    "숫자·막대만 — 실제 차트·집계는 코어 연동 후. 포폴용 스냅샷 레이아웃.",
  retro: "KPT 블록 목 — 익명·투표·타임라인은 회고 기능 설계 후 연결 예정.",
  inbox: "멘션·마감·파일 알림 목록. 푸시·실시간은 인프라 붙인 뒤 교체.",
  profile: "목 프로필입니다. 로그인 붙이면 교체됩니다.",
  dm: "1:1·그룹 DM 레이아웃 와이어만 — 송수신·저장 없음.",
  huddle:
    "음성·영상 연동 전 축소 바·참가자·컨트롤 자리만 — WebRTC·시그널링 없음.",
  meetingSummary:
    "허들 기반 전사·AI 요약·액션 추출 목표 (A2UI). STT·모델·저장은 연동 전 — 와이어만.",
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
    ) : activeNavId === "backlog" ? (
      <BacklogPage />
    ) : activeNavId === "metrics" ? (
      <MetricsPage />
    ) : activeNavId === "retro" ? (
      <RetroPage />
    ) : activeNavId === "inbox" ? (
      <InboxPage />
    ) : activeNavId === "dm" ? (
      <DmPage />
    ) : activeNavId === "huddle" ? (
      <HuddlePage />
    ) : activeNavId === "meetingSummary" ? (
      <MeetingSummaryPage />
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
