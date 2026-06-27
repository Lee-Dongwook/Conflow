/**
 * A2UI demo examples.
 *
 * The A2UI tool surface is hard to demo cold — a visitor has no idea what
 * JSON to type. This module supplies, per tool, a ready-to-run example input
 * (pre-filled into the invoke form) and a canned example result ("example
 * documents") so pressing 실행 in the demo workspace returns something
 * meaningful instead of hitting the write guard.
 */

import type { ToolInvokeOutput } from 'app/shared/types/api'

export interface ToolExample {
  /** A working sample input, pre-filled into the invoke textarea. */
  readonly input: Record<string, unknown>
  /** Canned result returned by `demoInvokeTool` for this tool. */
  readonly result: Record<string, unknown>
}

export const DEMO_TOOL_EXAMPLES: Record<string, ToolExample> = {
  'pm.create_issue': {
    input: {
      title: '온보딩 문서 자동 발급 파이프라인 구축',
      priority: 'high',
      assignee: '이민서',
    },
    result: {
      uuid: 'demo-issue-128',
      key: 'CON-128',
      title: '온보딩 문서 자동 발급 파이프라인 구축',
      status: 'todo',
      priority: 'high',
      assignee: '이민서',
      created_at: '2026-06-27T06:42:00Z',
      url: '/w/demo/pm/issues/demo-issue-128',
    },
  },
  'comms.summarize_channel': {
    input: {
      channel_uuid: 'demo-channel-general',
      limit: 20,
    },
    result: {
      channel: 'general',
      period: '최근 20개 메시지',
      summary:
        '이번 주 핵심은 랜딩 페이지 카피 확정과 스테이징 배포입니다. 히어로 문구는 2안("팀의 모든 대화가 실행이 되는 곳")으로 가닥이 잡혔고, 백엔드는 스테이징 배포를 마쳐 확인 요청이 올라온 상태입니다. 디자인 QA가 마무리되면 공유 예정입니다.',
      highlights: [
        '히어로 카피 2안 채택, 서브 문구만 추가 다듬기',
        '백엔드 스테이징 배포 완료 — 검증 필요',
        '디자인 QA 진행 중',
      ],
      action_items: [
        { owner: '이민서', task: '서브 카피 최종 확정' },
        { owner: '박현', task: '스테이징 회귀 테스트' },
        { owner: '정소라', task: '버튼 호버 상태 QA' },
      ],
      message_count: 18,
    },
  },
  'hr.list_pending_offboarding': {
    input: {},
    result: {
      total: 2,
      members: [
        {
          member_uuid: 'demo-member-hyun',
          name: '박현',
          title: '백엔드 엔지니어',
          employment_type: 'contract',
          last_day: '2026-07-15',
          checklist_progress: '3/7',
          pending: ['장비 반납', '계정 회수', '인수인계 문서'],
        },
        {
          member_uuid: 'demo-member-sora',
          name: '정소라',
          title: '프로덕트 디자이너',
          employment_type: 'intern',
          last_day: '2026-07-31',
          checklist_progress: '1/7',
          pending: ['포트폴리오 권한 정리', '계정 회수'],
        },
      ],
    },
  },
  'documents.issue_certificate': {
    input: {
      instance_uuid: 'demo-doc-0001',
      format: 'pdf',
    },
    result: {
      document_uuid: 'demo-doc-0001',
      type: '재직증명서',
      subject: '이민서',
      title: '프로덕트 매니저',
      issued_at: '2026-06-27T06:45:00Z',
      state: 'issued',
      verification_code: 'CF-2026-0627-A1B2',
      pdf_uri: 'https://demo.conflow.app/documents/demo-doc-0001.pdf',
    },
  },
}

/** Demo invoke — returns the canned example result for the given tool. */
export const demoInvokeTool = (
  toolId: string,
  rawInput: Record<string, unknown>,
): Promise<ToolInvokeOutput> => {
  const example = DEMO_TOOL_EXAMPLES[toolId]
  const result = example?.result ?? {
    ok: true,
    note: '이 도구의 예시 결과가 아직 준비되지 않았습니다.',
    echo: rawInput,
  }
  // Small delay so the invoke feels like a real round-trip.
  return new Promise((resolve) =>
    setTimeout(() => resolve({ tool_id: toolId, result }), 550),
  )
}
