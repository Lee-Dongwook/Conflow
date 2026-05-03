/** 로그인 없이 레이아웃만 볼 때 쓰는 더미 프로필 — {@link CURRENT_USER}와 동일 인물 */

import { CURRENT_USER } from "./current-session";

export type MockTeamMembership = {
  readonly id: string;
  readonly name: string;
  readonly roleLabel: string;
};

export type MockUser = {
  readonly displayName: string;
  readonly email: string;
  readonly jobTitle: string;
  readonly timezone: string;
  readonly localeLabel: string;
  readonly joinedLabel: string;
  readonly teams: readonly MockTeamMembership[];
  readonly notificationSummary: {
    readonly emailDigest: boolean;
    readonly sprintReminder: boolean;
    readonly mentionPush: boolean;
  };
};

export const MOCK_USER: MockUser = {
  displayName: CURRENT_USER.displayName,
  email: CURRENT_USER.email,
  jobTitle: "팀플 팀원 · 프론트",
  timezone: "Asia/Seoul",
  localeLabel: "한국어",
  joinedLabel: "2026년 5월 3일",
  teams: [
    {
      id: "team-sweng",
      name: "404찾는중",
      roleLabel: "멤버",
    },
    {
      id: "club-fe",
      name: "FE 스터디",
      roleLabel: "참여",
    },
  ],
  notificationSummary: {
    emailDigest: true,
    sprintReminder: true,
    mentionPush: false,
  },
};
