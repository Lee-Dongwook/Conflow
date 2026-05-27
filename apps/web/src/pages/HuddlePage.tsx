import { Avatar, Button, cn } from "@conflow/ui";

import { MOCK_USER } from "app/entities/user";

const PARTICIPANTS: readonly { readonly id: string; readonly label: string }[] =
  [
    { id: "p1", label: MOCK_USER.displayName },
    { id: "p2", label: "김○○" },
    { id: "p3", label: "이○○" },
  ];

const WaveformBar = ({
  className,
  delayClass,
}: {
  readonly className?: string;
  readonly delayClass?: string;
}) => (
  <span
    className={cn(
      "inline-block w-1 rounded-full bg-white/80",
      delayClass,
      className,
    )}
    aria-hidden
  />
);

export const HuddlePage = () => {
  return (
    <div className="flex min-h-[min(72vh,680px)] flex-col gap-3">
      <p className="text-xs text-slate-500">
        와이어 — WebRTC·시그널링·권한 없음. 슬랙식 축소 바·참가자·컨트롤 자리만
        잡았습니다.
      </p>

      <div
        className="relative flex min-h-[540px] flex-1 flex-col overflow-hidden rounded-xl border-2 border-dashed border-slate-300 bg-slate-50/80"
        aria-label="허들 맥락·콘텐츠 영역 (와이어)"
      >
        <header className="shrink-0 border-b border-dashed border-slate-300 bg-white/90 px-5 py-4">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
            맥락
          </p>
          <h2 className="mt-1 text-sm font-semibold text-slate-900">
            팀 — FE 스터디
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            DM·채널에서 “들어가기”를 누르면 이 영역이 열리는 흐름을 가정합니다.
          </p>
        </header>

        <div className="flex flex-1 items-center justify-center px-6 py-10">
          <div className="max-w-md rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-6 text-center text-sm text-slate-600 shadow-sm">
            <p>화면 공유·캔버스·노트는 붙이기 전입니다.</p>
            <p className="mt-2 text-xs text-slate-500">
              아래 바는 앱 전역에 붙이는 “진행 중 허들” 축소 UI와 동일한
              형태입니다.
            </p>
          </div>
        </div>

        <div className="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center px-4 pb-5 pt-16">
          <div
            className="pointer-events-auto flex max-w-full items-center gap-3 rounded-full border border-slate-800/20 bg-slate-900 px-3 py-2.5 pl-4 text-white shadow-xl shadow-slate-900/25"
            role="group"
            aria-label="허들 컨트롤 (와이어)"
          >
            <div className="flex min-w-0 items-center gap-2">
              <span className="relative flex h-2.5 w-2.5 shrink-0" aria-hidden>
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400/70" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400" />
              </span>
              <span className="truncate text-sm font-semibold tracking-tight">
                허들
              </span>
              <span className="hidden text-xs text-white/60 sm:inline">
                · 12:34
              </span>
            </div>

            <div className="hidden h-8 w-px bg-white/15 sm:block" aria-hidden />

            <div className="flex -space-x-2">
              {PARTICIPANTS.map((p) => (
                <Avatar
                  key={p.id}
                  label={p.label}
                  size="sm"
                  className="ring-2 ring-slate-900"
                />
              ))}
              <span className="z-10 flex size-8 items-center justify-center rounded-full bg-white/10 text-[10px] font-semibold text-white/90 ring-2 ring-slate-900">
                +1
              </span>
            </div>

            <div className="hidden h-8 w-px bg-white/15 md:block" aria-hidden />

            <div
              className="hidden h-8 items-end gap-0.5 px-1 md:flex"
              aria-hidden
            >
              <WaveformBar className="h-3" />
              <WaveformBar className="h-5" delayClass="opacity-80" />
              <WaveformBar className="h-4" />
              <WaveformBar className="h-6" delayClass="opacity-90" />
              <WaveformBar className="h-3" />
            </div>

            <div className="ml-1 flex items-center gap-1 sm:ml-2">
              <Button
                type="button"
                variant="secondary"
                className="h-9 border-0 bg-white/10 px-2.5 text-white hover:bg-white/20"
                aria-pressed="false"
              >
                <span className="sr-only">마이크</span>
                <svg
                  viewBox="0 0 24 24"
                  className="size-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.75}
                  aria-hidden
                >
                  <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3z" />
                  <path d="M8 11v1a4 4 0 0 0 8 0v-1" />
                  <path d="M12 18v3" />
                </svg>
              </Button>
              <Button
                type="button"
                variant="secondary"
                className="hidden h-9 border-0 bg-white/10 px-2.5 text-white hover:bg-white/20 sm:inline-flex"
              >
                <span className="sr-only">카메라</span>
                <svg
                  viewBox="0 0 24 24"
                  className="size-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.75}
                  aria-hidden
                >
                  <path d="M15 10l4-2v8l-4-2v-4z" />
                  <rect x="3" y="8" width="12" height="8" rx="1.5" />
                </svg>
              </Button>
              <Button
                type="button"
                variant="secondary"
                className="hidden h-9 border-0 bg-white/10 px-2.5 text-white hover:bg-white/20 md:inline-flex"
              >
                <span className="sr-only">화면 공유</span>
                <svg
                  viewBox="0 0 24 24"
                  className="size-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.75}
                  aria-hidden
                >
                  <rect x="3" y="4" width="18" height="12" rx="2" />
                  <path d="M8 20h8M12 16v4" />
                </svg>
              </Button>
              <Button
                type="button"
                variant="secondary"
                className="h-9 border-0 bg-rose-500 px-3 text-white hover:bg-rose-600"
              >
                나가기
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
