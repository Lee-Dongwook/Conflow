/** 로그인 없이 레이아웃만 볼 때 쓰는 더미 프로필. */

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
  displayName: "이땡땡",
  email: "local@daengdaeng.dev",
  jobTitle: "프론트엔드 개발자",
  timezone: "Asia/Seoul",
  localeLabel: "한국어",
  joinedLabel: "2026년 5월 3일",
  teams: [
    { id: "team-platform", name: "플랫폼", roleLabel: "멤버" },
    { id: "team-alpha", name: "스프린트 알파", roleLabel: "참관" },
    { id: "team-design", name: "디자인 시스템", roleLabel: "게스트" },
  ],
  notificationSummary: {
    emailDigest: true,
    sprintReminder: true,
    mentionPush: false,
  },
};
