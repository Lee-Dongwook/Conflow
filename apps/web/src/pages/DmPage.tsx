import { useState } from "react";

import { cn } from "@conflow/ui";

type Conversation = {
  readonly id: string;
  readonly title: string;
  readonly preview: string;
  readonly meta: string;
};

const CONVERSATIONS: readonly Conversation[] = [
  {
    id: "w1",
    title: "김○○",
    preview: "오늘 회의 안건만 정리해 두면…",
    meta: "어제",
  },
  {
    id: "w2",
    title: "팀 — 스터디",
    preview: "다음 주 범위부터 쪼개볼까요",
    meta: "월",
  },
  {
    id: "w3",
    title: "Conflow 봇",
    preview: "알림: 마감 1일 전",
    meta: "8:12",
  },
];

export const DmPage = () => {
  const [activeId, setActiveId] = useState(CONVERSATIONS[0]?.id ?? "w1");
  const active =
    CONVERSATIONS.find((c) => c.id === activeId) ?? CONVERSATIONS[0];

  return (
    <div className="flex min-h-[min(70vh,640px)] flex-col gap-3">
      <p className="text-xs text-slate-500">
        와이어 — 실제 전송·검색·알림 연동 없음. 레이아웃 검토용입니다.
      </p>

      <div className="flex min-h-[560px] flex-1 overflow-hidden rounded-xl border-2 border-dashed border-slate-300 bg-white">
        <section
          className="flex w-[min(100%,280px)] shrink-0 flex-col border-r border-dashed border-slate-300"
          aria-label="대화 목록 영역 (와이어)"
        >
          <header className="border-b border-dashed border-slate-300 px-3 py-2.5">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              목록
            </span>
            <div className="mt-2 h-9 rounded-md border border-dashed border-slate-300 bg-slate-50 px-2 text-xs leading-9 text-slate-400">
              검색 (미연동)
            </div>
          </header>
          <ul className="flex-1 overflow-y-auto p-2">
            {CONVERSATIONS.map((c) => {
              const on = c.id === activeId;
              return (
                <li key={c.id}>
                  <button
                    type="button"
                    onClick={() => {
                      setActiveId(c.id);
                    }}
                    className={cn(
                      "mb-1 flex w-full gap-2 rounded-lg border px-2 py-2 text-left text-sm transition-colors",
                      on
                        ? "border-slate-400 bg-slate-100"
                        : "border-transparent hover:bg-slate-50",
                    )}
                  >
                    <span
                      className="flex size-9 shrink-0 items-center justify-center rounded-full border border-dashed border-slate-300 bg-slate-100 text-[10px] font-medium text-slate-500"
                      aria-hidden
                    >
                      상
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate font-medium text-slate-800">
                        {c.title}
                      </span>
                      <span className="mt-0.5 block truncate text-xs text-slate-500">
                        {c.preview}
                      </span>
                    </span>
                    <span className="shrink-0 text-[10px] text-slate-400">
                      {c.meta}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </section>

        <section
          className="flex min-w-0 flex-1 flex-col"
          aria-label="선택한 대화 스레드 (와이어)"
        >
          <header className="flex shrink-0 items-center gap-2 border-b border-dashed border-slate-300 px-4 py-3">
            <span
              className="flex size-9 shrink-0 items-center justify-center rounded-full border border-dashed border-slate-300 bg-slate-100 text-[10px] font-medium text-slate-500"
              aria-hidden
            >
              상
            </span>
            <div className="min-w-0">
              <h2 className="truncate text-sm font-semibold text-slate-900">
                {active?.title ?? "—"}
              </h2>
              <p className="truncate text-xs text-slate-500">
                부제·상태 줄 (미정)
              </p>
            </div>
          </header>

          <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4">
            <div className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-3 py-2 text-xs text-slate-600">
                받은 쪽 placeholder 블록 — 줄바꿈·링크·파일은 기능 연결 후.
              </div>
            </div>
            <div className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl border border-dashed border-slate-400 bg-slate-100/80 px-3 py-2 text-xs text-slate-600">
                보낸 쪽 placeholder 블록.
              </div>
            </div>
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-3 py-2 text-xs text-slate-500">
                날짜 구분선 / 시스템 메시지 자리
              </div>
            </div>
          </div>

          <footer className="shrink-0 border-t border-dashed border-slate-300 px-4 py-3">
            <div
              className="flex min-h-[44px] items-end rounded-lg border border-dashed border-slate-400 bg-slate-50 px-3 py-2 text-xs text-slate-400"
              aria-disabled="true"
            >
              메시지 입력 (전송·첨부 미연동)
            </div>
          </footer>
        </section>
      </div>
    </div>
  );
};
