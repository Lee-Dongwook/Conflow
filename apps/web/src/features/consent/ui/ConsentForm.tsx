import { useState, useCallback } from 'react'

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, cn } from '@conflow/ui'

import { useMarkdown } from 'app/shared/lib'
import { MarkdownRenderer } from 'app/shared/ui'

interface IConsentItem {
  readonly id: string
  readonly label: string
  readonly required: boolean
  readonly docUrl: string
  readonly description: string
}

const CONSENT_ITEMS: readonly IConsentItem[] = [
  {
    id: 'terms',
    label: '이용약관',
    required: true,
    docUrl: '/legal/terms-of-service.md',
    description: '서비스 이용 조건에 동의합니다.',
  },
  {
    id: 'privacy',
    label: '개인정보 수집·이용',
    required: true,
    docUrl: '/legal/privacy-policy.md',
    description: '개인정보 수집·이용에 동의합니다.',
  },
  {
    id: 'third_party',
    label: '제3자 제공 (OpenAI)',
    required: true,
    docUrl: '/legal/privacy-policy.md',
    description: 'AI 기능 제공을 위한 OpenAI 데이터 전송에 동의합니다.',
  },
  {
    id: 'marketing',
    label: '마케팅 수신',
    required: false,
    docUrl: '',
    description: '서비스 업데이트 및 이벤트 알림 수신에 동의합니다.',
  },
]

interface IConsentFormProps {
  readonly onComplete?: (consents: Record<string, boolean>) => void
}

export const ConsentForm = ({ onComplete }: IConsentFormProps) => {
  const [checked, setChecked] = useState<Record<string, boolean>>({})
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const expandedItem = CONSENT_ITEMS.find((item) => item.id === expandedId)
  const { content: docContent, isLoading: docLoading } = useMarkdown(expandedItem?.docUrl ?? '')

  const allRequiredChecked = CONSENT_ITEMS.filter((item) => item.required).every(
    (item) => checked[item.id] === true,
  )

  const handleToggle = useCallback((id: string) => {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }))
  }, [])

  const handleAllToggle = useCallback(() => {
    const allChecked = CONSENT_ITEMS.every((item) => checked[item.id] === true)
    const next: Record<string, boolean> = {}
    for (const item of CONSENT_ITEMS) {
      next[item.id] = !allChecked
    }
    setChecked(next)
  }, [checked])

  const handleSubmit = useCallback(() => {
    if (allRequiredChecked) {
      onComplete?.(checked)
    }
  }, [allRequiredChecked, checked, onComplete])

  const allChecked = CONSENT_ITEMS.every((item) => checked[item.id] === true)

  return (
    <Card className="mx-auto max-w-lg">
      <CardHeader>
        <CardTitle className="text-lg">서비스 이용 동의</CardTitle>
        <p className="text-sm text-slate-500">서비스 이용을 위해 아래 항목에 동의해 주세요.</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <label className="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
          <input
            type="checkbox"
            checked={allChecked}
            onChange={handleAllToggle}
            className="size-4 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
          />
          <span className="text-sm font-semibold text-slate-900">전체 동의</span>
        </label>

        <div className="space-y-2">
          {CONSENT_ITEMS.map((item) => (
            <div key={item.id} className="rounded-lg border border-slate-100 bg-white">
              <div className="flex items-center gap-3 px-4 py-3">
                <input
                  type="checkbox"
                  id={`consent-${item.id}`}
                  checked={checked[item.id] === true}
                  onChange={() => {
                    handleToggle(item.id)
                  }}
                  className="size-4 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                />
                <label
                  htmlFor={`consent-${item.id}`}
                  className="flex min-w-0 flex-1 cursor-pointer items-center gap-2"
                >
                  <span className="text-sm text-slate-700">{item.description}</span>
                  <Badge
                    variant={item.required ? 'default' : 'secondary'}
                    className="shrink-0 text-[10px]"
                  >
                    {item.required ? '필수' : '선택'}
                  </Badge>
                </label>
                {item.docUrl ? (
                  <button
                    type="button"
                    onClick={() => {
                      setExpandedId(expandedId === item.id ? null : item.id)
                    }}
                    className="shrink-0 text-xs text-teal-600 hover:text-teal-800"
                  >
                    {expandedId === item.id ? '접기' : '보기'}
                  </button>
                ) : null}
              </div>

              {expandedId === item.id && item.docUrl ? (
                <div className="max-h-60 overflow-y-auto border-t border-slate-100 bg-slate-50/50 px-4 py-3">
                  {docLoading ? (
                    <p className="text-xs text-slate-400">문서를 불러오는 중...</p>
                  ) : (
                    <MarkdownRenderer content={docContent} />
                  )}
                </div>
              ) : null}
            </div>
          ))}
        </div>

        <Button
          type="button"
          className={cn('w-full', !allRequiredChecked && 'cursor-not-allowed opacity-50')}
          disabled={!allRequiredChecked}
          onClick={handleSubmit}
        >
          동의하고 시작하기
        </Button>

        <p className="text-center text-[11px] text-slate-400">
          필수 항목에 동의하지 않으면 서비스를 이용할 수 없습니다.
        </p>
      </CardContent>
    </Card>
  )
}
