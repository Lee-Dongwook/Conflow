import { SurveyForm } from 'app/features/survey'

export const SurveyPage = () => (
  <div className="min-h-screen bg-slate-50 px-4 py-10">
    <div className="mx-auto mb-6 max-w-2xl">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        Conflow Phase 0
      </p>
      <h1 className="mt-1 text-2xl font-semibold text-slate-900">팀 협업 페인 설문</h1>
      <p className="mt-1 text-sm text-slate-600">
        로그인 없이 익명으로 응답하실 수 있습니다.
      </p>
    </div>
    <SurveyForm />
  </div>
)
