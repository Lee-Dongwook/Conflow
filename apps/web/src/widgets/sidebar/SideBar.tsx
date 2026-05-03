import type { ReactNode } from "react";
import { useState } from "react";

import { Avatar, Badge, Button, Separator, cn } from "@conflow/ui";

import { MOCK_USER } from "../../data/mock-user";
import type { SidebarGlyph } from "./icons";
import { SidebarIcon } from "./icons";

export type SideBarProps = {
  readonly activeNavId?: string;
  readonly onNavChange?: (id: string) => void;
  readonly className?: string;
};

type NavDef = {
  readonly id: string;
  readonly label: string;
  readonly icon: SidebarGlyph;
  readonly badge?: number;
};

const WORK: readonly NavDef[] = [
  { id: "dashboard", label: "대시보드", icon: "dashboard" },
  { id: "sprint", label: "이번 주", icon: "calendar" },
  { id: "board", label: "보드", icon: "board" },
  { id: "backlog", label: "백로그", icon: "list" },
];

const INSIGHT: readonly NavDef[] = [
  { id: "metrics", label: "한눈에", icon: "chart" },
  { id: "retro", label: "회고", icon: "clock" },
];

type ThemeChoice = "light" | "system" | "dark";

const SectionLabel = ({ children }: { readonly children: ReactNode }) => (
  <p className="px-3 pb-1 pt-4 text-[10px] font-semibold uppercase tracking-wider text-slate-400 first:pt-1">
    {children}
  </p>
);

const NavButton = ({
  item,
  active,
  onSelect,
}: {
  readonly item: NavDef;
  readonly active: boolean;
  readonly onSelect: () => void;
}) => (
  <button
    type="button"
    onClick={onSelect}
    className={cn(
      "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors",
      active
        ? "bg-teal-600 text-white shadow-sm"
        : "text-slate-600 hover:bg-slate-50",
    )}
  >
    <SidebarIcon
      name={item.icon}
      className={active ? "text-white" : "text-slate-500"}
    />
    <span className="min-w-0 flex-1 truncate">{item.label}</span>
    {item.badge !== undefined && item.badge > 0 ? (
      <span
        className={cn(
          "flex min-h-5 min-w-5 shrink-0 items-center justify-center rounded-full px-1 text-[10px] font-semibold tabular-nums",
          active ? "bg-white/25 text-white" : "bg-rose-500 text-white",
        )}
      >
        {item.badge > 99 ? "99+" : String(item.badge)}
      </span>
    ) : null}
  </button>
);

export const SideBar = ({
  activeNavId = "dashboard",
  onNavChange,
  className,
}: SideBarProps) => {
  const [theme, setTheme] = useState<ThemeChoice>("system");

  const select = (id: string) => {
    onNavChange?.(id);
  };

  return (
    <aside
      className={cn(
        "flex h-screen w-[240px] shrink-0 flex-col border-r border-slate-200 bg-white",
        className,
      )}
    >
      <div className="flex items-center justify-between gap-2 border-b border-slate-100 px-3 py-3">
        <div className="flex min-w-0 items-center gap-2">
          <span className="truncate font-semibold tracking-tight text-slate-900">
            Conflow
          </span>
          <Badge variant="outline" className="shrink-0 text-[10px]">
            로컬
          </Badge>
        </div>
        <Button
          type="button"
          variant="secondary"
          className="h-8 shrink-0 px-2 text-xs"
          aria-label="빠른 기록"
        >
          <SidebarIcon name="plus" className="size-4" />
          기록
        </Button>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-2 py-2">
        <SectionLabel>작업</SectionLabel>
        <div className="flex flex-col gap-0.5">
          {WORK.map((item) => (
            <NavButton
              key={item.id}
              item={item}
              active={activeNavId === item.id}
              onSelect={() => {
                select(item.id);
              }}
            />
          ))}
        </div>

        <SectionLabel>살펴보기</SectionLabel>
        <div className="flex flex-col gap-0.5">
          {INSIGHT.map((item) => (
            <NavButton
              key={item.id}
              item={item}
              active={activeNavId === item.id}
              onSelect={() => {
                select(item.id);
              }}
            />
          ))}
        </div>

        <Separator className="my-3" />

        <button
          type="button"
          onClick={() => {
            select("inbox");
          }}
          className={cn(
            "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors",
            activeNavId === "inbox"
              ? "bg-teal-600 text-white shadow-sm"
              : "text-slate-600 hover:bg-slate-50",
          )}
        >
          <SidebarIcon
            name="bell"
            className={activeNavId === "inbox" ? "text-white" : "text-slate-500"}
          />
          <span className="min-w-0 flex-1 truncate">수신함</span>
          <span
            className={cn(
              "flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full px-1 text-[10px] font-semibold tabular-nums",
              activeNavId === "inbox" ? "bg-white/25 text-white" : "bg-rose-500 text-white",
            )}
          >
            3
          </span>
        </button>

        <button
          type="button"
          onClick={() => {
            select("workspace");
          }}
          className={cn(
            "mt-1 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors",
            activeNavId === "workspace"
              ? "bg-teal-600 font-medium text-white shadow-sm"
              : "text-slate-500 hover:bg-slate-50",
          )}
        >
          <SidebarIcon
            name="settings"
            className={cn(
              "size-4",
              activeNavId === "workspace" ? "text-white" : "text-slate-400",
            )}
          />
          <span>워크스페이스</span>
        </button>
      </nav>

      <div className="border-t border-slate-100 px-2 py-2">
        <p className="mb-1.5 px-2 text-[10px] font-medium uppercase tracking-wide text-slate-400">
          화면 모드
        </p>
        <div className="flex rounded-lg bg-slate-100 p-0.5 text-[11px] font-medium">
          {(
            [
              { id: "light" as const, label: "라이트" },
              { id: "system" as const, label: "자동" },
              { id: "dark" as const, label: "다크" },
            ] as const
          ).map((seg) => (
            <button
              key={seg.id}
              type="button"
              onClick={() => {
                setTheme(seg.id);
              }}
              className={cn(
                "flex-1 rounded-md px-1.5 py-1.5 transition-colors",
                theme === seg.id
                  ? "bg-white text-teal-800 shadow-sm"
                  : "text-slate-500 hover:text-slate-800",
              )}
            >
              {seg.label}
            </button>
          ))}
        </div>
      </div>

      <div className="border-t border-slate-100 p-3">
        <button
          type="button"
          onClick={() => {
            select("profile");
          }}
          className={cn(
            "w-full rounded-lg border bg-slate-50 p-2.5 text-left transition-shadow",
            activeNavId === "profile"
              ? "border-teal-400 ring-2 ring-teal-400/40"
              : "border-slate-200 hover:border-slate-300",
          )}
          aria-label="내 계정 페이지로 이동"
        >
          <div className="flex gap-2.5">
            <Avatar label={MOCK_USER.displayName} size="md" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-900">
                {MOCK_USER.displayName}
              </p>
              <p className="truncate text-xs text-slate-500">
                {MOCK_USER.email}
              </p>
            </div>
          </div>
        </button>
      </div>
    </aside>
  );
};
