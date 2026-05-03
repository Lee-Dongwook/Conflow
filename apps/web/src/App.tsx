import { useState } from "react";

import { DashboardPage } from "./pages/DashboardPage";
import { UserPage } from "./pages/UserPage";
import { SideBar } from "./widgets/sidebar";

const NAV_TITLE: Record<string, string> = {
  dashboard: "대시보드",
  sprint: "스프린트",
  board: "보드",
  backlog: "백로그",
  metrics: "지표",
  retro: "회고",
  profile: "내 계정",
};

const NAV_SUBTITLE: Record<string, string> = {
  profile: "목 프로필입니다. 로그인 붙이면 교체됩니다.",
};

export const App = () => {
  const [activeNavId, setActiveNavId] = useState("dashboard");
  const navTitle = NAV_TITLE[activeNavId] ?? activeNavId;
  const navSubtitle =
    NAV_SUBTITLE[activeNavId] ??
    "화면만 잡는 단계예요. 다음에 같이 정할 건 “이 제품이 줄여 줄 하루” 한 문장입니다.";

  const main = activeNavId === "profile" ? <UserPage /> : <DashboardPage />;

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
