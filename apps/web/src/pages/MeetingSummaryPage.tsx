import { useState } from "react";

import { Badge, cn } from "@conflow/ui";

type MeetingRow = {
  readonly id: string;
  readonly title: string;
  readonly source: string;
  readonly when: string;
  readonly durationMin: number;
  readonly status: "ready" | "processing";
};

type SummaryDetail = {
  readonly overview: string;
  readonly bullets: readonly string[];
  readonly decisions: readonly string[];
  readonly actions: readonly { readonly task: string; readonly owner: string }[];
  readonly next: readonly string[];
};

const MEETINGS: readonly MeetingRow[] = [
  {
    id: "m1",
    title: "FE 스터디 — 스프린트 계획",
    source: "허들 · 팀 채널",
    when: "오늘 14:02",
    durationMin: 32,
    status: "ready",
  },
  {
    id: "m2",
    title: "1:1 김○○",
    source: "허들 · DM",
    when: "어제 18:40",
    durationMin: 18,
    status: "ready",
  },
  {
    id: "m3",
    title: "주간 공유 (음소거 다수)",
    source: "허들 · 팀 채널",
    when: "월 10:15",
    durationMin: 45,
    status: "processing",
  },
];

const DETAIL_BY_ID: Readonly<Record<string, SummaryDetail>> = {
  m1: {
    overview:
      "이번 주 범위를 쪼개고, 보드 컬럼 기준을 맞추기로 했습니다. 문서화는 백로그 상단 3건만 우선.",
    bullets: [
      "데모는 금요일 오전, 리허설 없이 라이브 가정.",
      "‘완료’ 정의: 스테이징 배포 + 스크린샷 1장.",
    ],
    decisions: [
      "스프린트 길이 1주 유지, 금요일에만 회고 슬롯.",
      "백로그 상위 3건에 담당·마감 메타데이터 필수.",
    ],
    actions: [
      { task: "백로그 3건 메타데이터 보강", owner: "나" },
      { task: "보드 WIP 3으로 제한 제안", owner: "김○○" },
    ],
    next: [
      "수요일까지 범위 확정 PR 코멘트",
      "다음 허들에서 블로커만 10분 터치",
    ],
  },
  m2: {
    overview:
      "커리큘럼 속도와 개인 일정을 맞추기 위한 가벼운 정렬. 다음 체크인 날짜만 확정.",
    bullets: ["다음 주는 코드 리뷰 비중↑.", "문서는 최소한으로, 보드에만 남기기."],
    decisions: ["다음 1:1은 2주 뒤 같은 요일."],
    actions: [{ task: "학습 범위 2줄로 정리해 공유", owner: "김○○" }],
    next: ["슬랙/허들 외 비동기로만 팔로업"],
  },
};

const emptyDetail: SummaryDetail = {
  overview:
    "처리 중입니다. STT·요약 파이프라인 연결 후 이 영역이 채워집니다. (와이어)",
  bullets: ["세그먼트 분할", "발화자 추정(옵션)", "팀 용어 사전 반영"],
  decisions: [],
  actions: [],
  next: [],
};

export const MeetingSummaryPage = () => {
  const firstId = MEETINGS[0]?.id ?? "m1";
  const [activeId, setActiveId] = useState(firstId);
  const activeRow = MEETINGS.find((m) => m.id === activeId) ?? MEETINGS[0];
  const detail = DETAIL_BY_ID[activeId] ?? emptyDetail;
  const isProcessing = activeRow?.status === "processing";

  return (
    <div className="flex min-h-[min(70vh,680px)] flex-col gap-3">
      <p className="text-xs text-slate-500">
        와이어 — A2UI 목표: 허들 종료 후 전사·요약·액션 추출 자동화. STT·모델·권한
        없음. 레이아웃·정보 구조만 잡았습니다.
      </p>

      <div className="flex min-h-[580px] flex-1 overflow-hidden rounded-xl border-2 border-dashed border-slate-300 bg-white">
        <section
          className="flex w-[min(100%,300px)] shrink-0 flex-col border-r border-dashed border-slate-300"
          aria-label="회의 목록 (와이어)"
        >
          <header className="border-b border-dashed border-slate-300 px-3 py-2.5">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              출처: 허들
            </span>
            <div className="mt-2 h-9 rounded-md border border-dashed border-slate-300 bg-slate-50 px-2 text-xs leading-9 text-slate-400">
              검색·필터 (미연동)
            </div>
          </header>
          <ul className="flex-1 overflow-y-auto p-2">
            {MEETINGS.map((m) => {
              const on = m.id === activeId;
              return (
                <li key={m.id}>
                  <button
                    type="button"
                    onClick={() => {
                      setActiveId(m.id);
                    }}
                    className={cn(
                      "mb-1 flex w-full flex-col gap-1 rounded-lg border px-2.5 py-2 text-left text-sm transition-colors",
                      on
                        ? "border-slate-400 bg-slate-100"
                        : "border-transparent hover:bg-slate-50",
                    )}
                  >
                    <span className="font-medium text-slate-900">{m.title}</span>
                    <span className="text-[11px] text-slate-500">{m.source}</span>
                    <span className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-500">
                      <span>{m.when}</span>
                      <span className="text-slate-300" aria-hidden>
                        ·
                      </span>
                      <span>{m.durationMin}분</span>
                      {m.status === "processing" ? (
                        <Badge variant="outline" className="text-[10px]">
                          처리 중
                        </Badge>
                      ) : (
                        <Badge
                          variant="outline"
                          className="border-emerald-200 bg-emerald-50 text-[10px] text-emerald-800"
                        >
                          요약 완료
                        </Badge>
                      )}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </section>

        <section
          className="flex min-w-0 flex-1 flex-col"
          aria-label="AI 회의록 요약 상세 (와이어)"
        >
          <header className="border-b border-dashed border-slate-300 px-5 py-4">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              AI 회의록
            </p>
            <h2 className="mt-1 truncate text-base font-semibold text-slate-900">
              {activeRow?.title ?? "회의"}
            </h2>
            <p className="mt-0.5 text-xs text-slate-500">
              {activeRow?.source} · {activeRow?.when} · 약 {activeRow?.durationMin}분
            </p>
          </header>

          <div className="flex-1 overflow-y-auto px-5 py-4">
            {isProcessing ? (
              <div className="rounded-lg border border-dashed border-amber-200 bg-amber-50/80 px-4 py-3 text-sm text-amber-900">
                <p className="font-medium">요약 생성 중 (목)</p>
                <p className="mt-1 text-xs text-amber-800/90">
                  전사 큐·모델 호출·저장은 미연동입니다. 완료되면 아래 블록이 같은
                  형태로 채워집니다.
                </p>
              </div>
            ) : null}

            <div className="mt-1 space-y-4">
              <article className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  한 줄 요약
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-800">
                  {detail.overview}
                </p>
              </article>

              <article className="rounded-xl border border-slate-200 p-4">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  핵심 논의
                </h3>
                <ul className="mt-2 list-inside list-disc space-y-1.5 text-sm text-slate-700">
                  {detail.bullets.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              </article>

              <div className="grid gap-4 md:grid-cols-2">
                <article className="rounded-xl border border-slate-200 p-4">
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    결정
                  </h3>
                  {detail.decisions.length > 0 ? (
                    <ul className="mt-2 space-y-2 text-sm text-slate-700">
                      {detail.decisions.map((d) => (
                        <li
                          key={d}
                          className="rounded-md border border-slate-100 bg-white px-2.5 py-2"
                        >
                          {d}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 text-xs text-slate-400">없음 (목)</p>
                  )}
                </article>

                <article className="rounded-xl border border-slate-200 p-4">
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    액션
                  </h3>
                  {detail.actions.length > 0 ? (
                    <ul className="mt-2 space-y-2 text-sm">
                      {detail.actions.map((a) => (
                        <li
                          key={`${a.task}-${a.owner}`}
                          className="flex items-start justify-between gap-2 rounded-md border border-slate-100 bg-white px-2.5 py-2"
                        >
                          <span className="text-slate-800">{a.task}</span>
                          <span className="shrink-0 text-xs text-slate-500">
                            {a.owner}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 text-xs text-slate-400">없음 (목)</p>
                  )}
                </article>
              </div>

              <article className="rounded-xl border border-dashed border-slate-300 p-4">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  다음 단계
                </h3>
                {detail.next.length > 0 ? (
                  <ul className="mt-2 space-y-1.5 text-sm text-slate-700">
                    {detail.next.map((n) => (
                      <li key={n} className="flex gap-2">
                        <span className="text-slate-300" aria-hidden>
                          →
                        </span>
                        <span>{n}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-xs text-slate-400">—</p>
                )}
              </article>

              <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-2.5 text-xs text-slate-500">
                전사 원문·타임스탬프·발화자 라벨은 이후 탭/접기 영역으로 붙일 수
                있습니다. (와이어)
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
