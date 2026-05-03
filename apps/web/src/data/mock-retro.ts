/**
 * 스프린트 회고 와이어용 목 데이터 (KPT 스타일).
 */
export const MOCK_RETRO = {
  contextLine: "Conflow 팀 · 3주차 회고 요약 (포폴 목)",
  wireNote:
    "실제 회고는 보드·익명 투표 등 붙일 예정. 지금은 텍스트 블록 레이아웃만.",
  sprintLabel: "3주차 스프린트",
  columns: [
    {
      id: "keep",
      title: "Keep · 잘한 점",
      accent: "emerald" as const,
      items: [
        "데일리가 짧게 끝나서 집중 시간이 확보됐다.",
        "문서 템플릿 공유 덕분에 회의록 정리 속도가 올랐다.",
      ],
    },
    {
      id: "problem",
      title: "Problem · 아쉬운 점",
      accent: "amber" as const,
      items: [
        "마감 2~3일 전에야 우선순위가 모이는 경우가 있다.",
        "리뷰 대기 시간이 길어지면 다음 태스크 시작이 늦어진다.",
      ],
    },
    {
      id: "try",
      title: "Try · 다음에 시도",
      accent: "sky" as const,
      items: [
        "수요일 오전에 “이번 주 마감 3줄”만 공유하는 미니 싱크.",
        "blocker는 태그 + 슬랙 스레드 한 곳으로 모으기.",
      ],
    },
  ],
} as const;
