/**
 * 한눈에(메트릭) 와이어용 목 데이터.
 * 차트 라이브러리 없이 숫자·막대 정도만 표시.
 */
export const MOCK_METRICS = {
  contextLine: "Conflow 팀 · “한눈에” 스냅샷 (포폴 목)",
  wireNote:
    "실제 대시보드는 코어·집계 후 교체. 지금은 레이아웃·카피 검증용입니다.",
  weekLabel: "3주차",
  statCards: [
    {
      id: "sc-done",
      label: "이번 주 완료율",
      value: "62%",
      sub: "팀 전체 기준",
    },
    {
      id: "sc-left",
      label: "스프린트 종료까지",
      value: "5일",
      sub: "일요일 스프린트 마감",
    },
    {
      id: "sc-blockers",
      label: "막힘 (blocker)",
      value: "2건",
      sub: "해소 목표: 금~토",
    },
    {
      id: "sc-due",
      label: "이번 주 마감 예정",
      value: "8건",
      sub: "카드 마감일 기준",
    },
  ],
  progressBars: [
    { id: "pb-doc", label: "문서·요약", percent: 75 },
    { id: "pb-dev", label: "개발 태스크", percent: 48 },
    { id: "pb-meet", label: "회의·정리", percent: 88 },
  ],
  snapshotRows: [
    { label: "활성 카드", value: "14" },
    { label: "이번 주 완료 누적", value: "9" },
    { label: "내 담당 미완", value: "3" },
  ],
} as const;
