/** 팀플·스터디 팀 기준 대시보드 더미 — 담당자에 {@link CURRENT_USER} 포함 */

import { CURRENT_USER } from "./current-session";

export type MockTaskStatus = "todo" | "doing" | "done";

export type MockTask = {
  readonly id: string;
  readonly title: string;
  readonly assignee: string;
  readonly status: MockTaskStatus;
};

export const MOCK_TEAM_DASHBOARD = {
  courseLabel: "소프트웨어공학 팀플",
  teamName: "404찾는중",
  weekLabel: "3주차",
  periodLabel: "3/10 ~ 3/23",
  nextDeadlineLabel: "중간 발표 · 3월 18일 (화) 23:59",
  oneLineGoal: "요구사항 정리 + 와이어프레임 + 역할 분담 확정까지 맞추기",
  progressPercent: 58,
  tasks: [
    {
      id: "t1",
      title: "와이어프레임 초안",
      assignee: CURRENT_USER.displayName,
      status: "doing" as const,
    },
    {
      id: "t2",
      title: "유저 스토리 5개 정리",
      assignee: CURRENT_USER.displayName,
      status: "todo" as const,
    },
    {
      id: "t3",
      title: "발표 슬라이드 뼈대",
      assignee: "박서연",
      status: "todo" as const,
    },
    {
      id: "t4",
      title: "Notion에 역할표 올리기",
      assignee: CURRENT_USER.displayName,
      status: "done" as const,
    },
    {
      id: "t5",
      title: "API 목업 연동",
      assignee: "이준호",
      status: "doing" as const,
    },
  ],
  blockerNote: "피그마 초대만 정해지면 디자인 태스크 시작 가능",
} as const satisfies {
  readonly courseLabel: string;
  readonly teamName: string;
  readonly weekLabel: string;
  readonly periodLabel: string;
  readonly nextDeadlineLabel: string;
  readonly oneLineGoal: string;
  readonly progressPercent: number;
  readonly tasks: readonly MockTask[];
  readonly blockerNote: string;
};
