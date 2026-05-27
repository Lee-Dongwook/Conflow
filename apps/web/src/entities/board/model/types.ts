/** 칸반 보드 목 데이터 — 드래그 없음, 정적 와이어 */

import { CURRENT_USER } from "app/entities/session";
import { MOCK_TEAM_DASHBOARD } from "app/entities/dashboard";

export type BoardColumnId = "todo" | "doing" | "done";

export type BoardTaskCard = {
  readonly id: string;
  readonly title: string;
  readonly assignee: string;
  readonly tag?: string;
};

export type BoardColumn = {
  readonly id: BoardColumnId;
  readonly title: string;
  readonly hint: string;
  readonly cards: readonly BoardTaskCard[];
};

export const MOCK_BOARD = {
  contextLine: `${MOCK_TEAM_DASHBOARD.teamName} · ${MOCK_TEAM_DASHBOARD.courseLabel}`,
  wireNote: "드래그·실시간 동기화 없음. 포폴·와이어용 정적 칸반.",
  columns: [
    {
      id: "todo",
      title: "할 일",
      hint: "아직 손 안 댄 작업",
      cards: [
        {
          id: "bc1",
          title: "발표 슬라이드 뼈대",
          assignee: "박서연",
          tag: "발표",
        },
        {
          id: "bc2",
          title: "유저 스토리 5개 정리",
          assignee: CURRENT_USER.displayName,
          tag: "기획",
        },
      ],
    },
    {
      id: "doing",
      title: "하는 중",
      hint: "지금 진행 중",
      cards: [
        {
          id: "bc3",
          title: "와이어프레임 초안",
          assignee: CURRENT_USER.displayName,
          tag: "디자인",
        },
        {
          id: "bc4",
          title: "API 목업 연동",
          assignee: "이준호",
          tag: "개발",
        },
      ],
    },
    {
      id: "done",
      title: "완료",
      hint: "이번 주 안에 끝낸 것",
      cards: [
        {
          id: "bc5",
          title: "Notion에 역할표 올리기",
          assignee: CURRENT_USER.displayName,
        },
        {
          id: "bc6",
          title: "요구사항 1차 정리",
          assignee: CURRENT_USER.displayName,
          tag: "기획",
        },
      ],
    },
  ],
} as const satisfies {
  readonly contextLine: string;
  readonly wireNote: string;
  readonly columns: readonly BoardColumn[];
};
