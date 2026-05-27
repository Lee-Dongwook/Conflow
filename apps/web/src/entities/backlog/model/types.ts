/** 백로그 목록 — 보드·대시보드와 같은 팀 맥락. 코어 로직은 와이어 확정 후 연결 예정. */

import { CURRENT_USER } from 'app/entities/session'
import { MOCK_TEAM_DASHBOARD } from 'app/entities/dashboard'

export type BacklogPriority = 'p0' | 'p1' | 'p2'

export type BacklogItem = {
  readonly id: string
  readonly title: string
  readonly assignee: string
  readonly priority: BacklogPriority
  readonly note?: string
}

export const MOCK_BACKLOG = {
  contextLine: `${MOCK_TEAM_DASHBOARD.teamName} · ${MOCK_TEAM_DASHBOARD.courseLabel}`,
  wireNote: '정렬·드래그·저장 없음. 와이어 확정 후 entities / 코어 함수와 연결 예정.',
  items: [
    {
      id: 'bl1',
      title: '중간 발표 Q&A 예상 질문 리스트',
      assignee: '박서연',
      priority: 'p0' as const,
      note: '발표 3/18 전',
    },
    {
      id: 'bl2',
      title: 'ERD 초안',
      assignee: '이준호',
      priority: 'p0' as const,
    },
    {
      id: 'bl3',
      title: '사용자 인터뷰 2명 스크립트',
      assignee: CURRENT_USER.displayName,
      priority: 'p1' as const,
    },
    {
      id: 'bl4',
      title: '접근성 체크리스트',
      assignee: CURRENT_USER.displayName,
      priority: 'p1' as const,
    },
    {
      id: 'bl5',
      title: '대시보드 위젯 순서 A/B',
      assignee: '이준호',
      priority: 'p2' as const,
      note: '시간 남으면',
    },
    {
      id: 'bl6',
      title: '팀 노션 템플릿 정리',
      assignee: '박서연',
      priority: 'p2' as const,
    },
    {
      id: 'bl7',
      title: '디자인 토큰 이름 규칙',
      assignee: CURRENT_USER.displayName,
      priority: 'p2' as const,
    },
  ],
} as const satisfies {
  readonly contextLine: string
  readonly wireNote: string
  readonly items: readonly BacklogItem[]
}
