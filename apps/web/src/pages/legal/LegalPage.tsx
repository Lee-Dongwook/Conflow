import { useState } from 'react'

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, cn } from '@conflow/ui'

import { useMarkdown } from 'app/shared/lib'
import { MarkdownRenderer } from 'app/shared/ui'

type LegalTab = 'terms' | 'privacy'

const TABS: readonly { readonly id: LegalTab; readonly label: string }[] = [
  { id: 'terms', label: '이용약관' },
  { id: 'privacy', label: '개인정보 처리방침' },
]

const URL_MAP: Record<LegalTab, string> = {
  terms: '/legal/terms-of-service.md',
  privacy: '/legal/privacy-policy.md',
}

export const LegalPage = () => {
  const [activeTab, setActiveTab] = useState<LegalTab>('terms')
  const { content, isLoading } = useMarkdown(URL_MAP[activeTab])

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">법적 고지</h2>
          <p className="text-sm text-slate-500">
            서비스 이용약관 및 개인정보 처리방침을 확인할 수 있습니다.
          </p>
        </div>
        <Badge variant="outline">버전 1.0 · 2026.06.01 시행</Badge>
      </div>

      <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => {
              setActiveTab(tab.id)
            }}
            className={cn(
              'flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-700',
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader className="border-b border-slate-100">
          <CardTitle className="text-base">
            {activeTab === 'terms' ? '이용약관' : '개인정보 처리방침'}
          </CardTitle>
        </CardHeader>
        <CardContent className="max-h-[70vh] overflow-y-auto p-6">
          {isLoading ? (
            <p className="text-sm text-slate-400">문서를 불러오는 중...</p>
          ) : (
            <MarkdownRenderer content={content} />
          )}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button type="button" variant="secondary" disabled>
          PDF 다운로드 (추후 지원)
        </Button>
      </div>
    </div>
  )
}
