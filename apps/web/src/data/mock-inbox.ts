export type InboxEntryType = "mention" | "deadline" | "file" | "system";

export type InboxEntry = {
  readonly id: string;
  readonly type: InboxEntryType;
  readonly title: string;
  readonly body: string;
  readonly timeLabel: string;
  readonly read: boolean;
  readonly fromName: string;
};

/**
 * 수신함 와이어용 목 알림.
 */
export const MOCK_INBOX = {
  contextLine: "수신함 · 멘션·마감·파일 알림 (포폴 목)",
  wireNote: "푸시·실시간은 코어 연동 후. 지금은 목록 UI와 읽음 상태만 표시.",
  entries: [
    {
      id: "in-1",
      type: "mention",
      title: "보드 카드에서 멘션",
      body: "「API 스펙 초안」카드에서 @이땡땡 확인 부탁드려요.",
      timeLabel: "42분 전",
      read: false,
      fromName: "김대리",
    },
    {
      id: "in-2",
      type: "deadline",
      title: "마감 임박",
      body: "스프린트 목표 카드 2건이 48시간 안에 마감됩니다.",
      timeLabel: "3시간 전",
      read: false,
      fromName: "시스템",
    },
    {
      id: "in-3",
      type: "file",
      title: "파일 업로드",
      body: "주간 회의 녹취 요약본이 첨부되었습니다.",
      timeLabel: "어제",
      read: true,
      fromName: "박사원",
    },
    {
      id: "in-4",
      type: "system",
      title: "스프린트 리마인더",
      body: "일요일 23:59에 3주차 스프린트가 종료됩니다.",
      timeLabel: "2일 전",
      read: true,
      fromName: "Conflow",
    },
  ] satisfies readonly InboxEntry[],
} as const;
