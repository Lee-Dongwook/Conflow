/**
 * "이번 주" 화면용 더미 — 대시보드 기간(3/10~)과 맞춤. 간트 대신 주간 스캔.
 */

import { CURRENT_USER } from "./current-session";
import { MOCK_TEAM_DASHBOARD } from "./mock-team-dashboard";

export type WeekMilestone = {
  readonly title: string;
  readonly assignee: string;
  readonly critical?: boolean;
};

export type WeekDayBlock = {
  readonly weekday: string;
  readonly dayOfMonth: number;
  readonly isToday: boolean;
  readonly milestones: readonly WeekMilestone[];
};

export const MOCK_THIS_WEEK = {
  rangeLabel: "3/10(월) ~ 3/16(일)",
  contextLine: `${MOCK_TEAM_DASHBOARD.courseLabel} · ${MOCK_TEAM_DASHBOARD.teamName} · ${MOCK_TEAM_DASHBOARD.weekLabel}`,
  sharedGoal: MOCK_TEAM_DASHBOARD.oneLineGoal,
  /** 화면 상단 "가장 임박" 한 건 (와이어용) */
  nextUp: {
    weekday: "화",
    dayOfMonth: 11,
    title: "요구사항 1차 정리",
    assignee: CURRENT_USER.displayName,
  },
  days: [
    {
      weekday: "월",
      dayOfMonth: 10,
      isToday: false,
      milestones: [{ title: "팀 킥오프 노션 만든 날", assignee: "이준호" }],
    },
    {
      weekday: "화",
      dayOfMonth: 11,
      isToday: false,
      milestones: [
        {
          title: "요구사항 1차 정리",
          assignee: CURRENT_USER.displayName,
          critical: true,
        },
      ],
    },
    {
      weekday: "수",
      dayOfMonth: 12,
      isToday: true,
      milestones: [
        {
          title: "와이어프레임 초안",
          assignee: CURRENT_USER.displayName,
          critical: true,
        },
      ],
    },
    {
      weekday: "목",
      dayOfMonth: 13,
      isToday: false,
      milestones: [{ title: "중간 점검 미팅", assignee: "박서연" }],
    },
    {
      weekday: "금",
      dayOfMonth: 14,
      isToday: false,
      milestones: [],
    },
    {
      weekday: "토",
      dayOfMonth: 15,
      isToday: false,
      milestones: [{ title: "슬라이드 초안 (선택)", assignee: "이준호" }],
    },
    {
      weekday: "일",
      dayOfMonth: 16,
      isToday: false,
      milestones: [],
    },
  ],
} as const satisfies {
  readonly rangeLabel: string;
  readonly contextLine: string;
  readonly sharedGoal: string;
  readonly nextUp: {
    readonly weekday: string;
    readonly dayOfMonth: number;
    readonly title: string;
    readonly assignee: string;
  };
  readonly days: readonly WeekDayBlock[];
};
