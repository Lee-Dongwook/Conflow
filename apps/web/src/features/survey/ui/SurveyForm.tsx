import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Select,
  Textarea,
} from '@conflow/ui'
import { useState } from 'react'

import { surveyApi, type RespondentRole } from '../api'

const SURVEY_KEY = 'conflow_phase0_v1'

const ROLE_OPTIONS: ReadonlyArray<{ value: RespondentRole; label: string }> = [
  { value: 'capstone_leader', label: '대학생 — 캡스톤/팀플 팀장' },
  { value: 'capstone_member', label: '대학생 — 캡스톤/팀플 팀원' },
  { value: 'club_operator', label: '창업 동아리 운영진 (SOPT/CEOS/멋사 등)' },
  { value: 'club_member', label: '창업 동아리 팀원' },
  { value: 'startup_founder', label: '신생 스타트업 (시드~프리시드)' },
  { value: 'side_project_leader', label: '직장인 — 사이드 프로젝트 리더' },
  { value: 'other', label: '기타' },
]

const FREQUENCY_OPTIONS = [
  { value: 'every_project', label: '매 프로젝트마다' },
  { value: 'often', label: '자주' },
  { value: 'sometimes', label: '가끔' },
  { value: 'rarely', label: '거의 없음' },
  { value: 'never', label: '없음' },
]

const TOOL_OPTIONS = [
  { value: 'kakaotalk', label: '카카오톡' },
  { value: 'notion', label: 'Notion' },
  { value: 'google_sheets', label: '구글 시트/캘린더' },
  { value: 'slack_discord', label: 'Slack / Discord' },
  { value: 'linear_jira_trello', label: 'Linear / Jira / Trello' },
  { value: 'github_projects', label: 'GitHub Projects' },
  { value: 'figma', label: 'Figma' },
  { value: 'other_tool', label: '기타' },
]

const isOperator = (role: RespondentRole): boolean =>
  role === 'club_operator' || role === 'startup_founder'

export const SurveyForm = () => {
  const [role, setRole] = useState<RespondentRole | ''>('')
  const [organization, setOrganization] = useState('')
  const [teamSize, setTeamSize] = useState('')
  const [painFrequency, setPainFrequency] = useState('')
  const [painIntensity, setPainIntensity] = useState<number | null>(null)
  const [topPainText, setTopPainText] = useState('')
  const [tools, setTools] = useState<readonly string[]>([])
  const [hasSilentTeamExperience, setHasSilentTeamExperience] = useState<boolean | null>(null)
  const [willingnessToTry, setWillingnessToTry] = useState<number | null>(null)
  const [operatorPricing, setOperatorPricing] = useState('')
  const [contactEmail, setContactEmail] = useState('')
  const [consentsToFollowup, setConsentsToFollowup] = useState(false)

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)

  const toggleTool = (value: string) => {
    setTools((prev) =>
      prev.includes(value) ? prev.filter((t) => t !== value) : [...prev, value],
    )
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!role) {
      setError('역할을 선택해주세요.')
      return
    }
    if (!painFrequency || painIntensity === null || willingnessToTry === null) {
      setError('필수 항목(빈도·강도·의향)을 모두 응답해주세요.')
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      await surveyApi.submit({
        survey_key: SURVEY_KEY,
        respondent_role: role,
        organization: organization.trim() || null,
        contact_email: consentsToFollowup && contactEmail.trim()
          ? contactEmail.trim()
          : null,
        consents_to_followup: consentsToFollowup,
        answers: {
          team_size: teamSize || null,
          pain_frequency: painFrequency,
          pain_intensity: painIntensity,
          top_pain_text: topPainText.trim() || null,
          tools,
          has_silent_team_experience: hasSilentTeamExperience,
          willingness_to_try: willingnessToTry,
          operator_pricing_korean_won: operatorPricing || null,
        },
      })
      setSubmitted(true)
    } catch (err) {
      const message = err instanceof Error ? err.message : '제출 중 오류가 발생했습니다.'
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="mx-auto max-w-2xl">
        <Card className="border-teal-200 bg-teal-50/50">
          <CardHeader>
            <CardTitle className="text-teal-950">응답 감사합니다</CardTitle>
            <CardDescription className="text-teal-900/80">
              당신의 응답은 Conflow가 무엇을 만들지 결정하는 데 직접 쓰입니다.
              {consentsToFollowup
                ? ' 후속 인터뷰 의향에 체크해주셔서 곧 연락드리겠습니다.'
                : ''}
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  const showOperatorBranch = role !== '' && isOperator(role)

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Conflow Phase 0 설문</CardTitle>
          <CardDescription>
            팀 협업에서 막혔던 경험을 짧게 알려주세요. 약 3분 소요, 익명입니다.
            모든 응답은 Conflow 제품 결정에만 쓰입니다.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            <section className="flex flex-col gap-2">
              <Label htmlFor="role">1. 본인은 다음 중 어디에 가깝나요? *</Label>
              <Select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value as RespondentRole)}
                required
              >
                <option value="" disabled>
                  선택해주세요
                </option>
                {ROLE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </section>

            <section className="flex flex-col gap-2">
              <Label htmlFor="organization">
                2. 소속 (학교/동아리/회사명, 선택)
              </Label>
              <Input
                id="organization"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                placeholder="예: 서울대 컴공 / SOPT 35기 / 회사명"
                maxLength={200}
              />
            </section>

            <section className="flex flex-col gap-2">
              <Label htmlFor="team_size">3. 최근 팀 인원 (선택)</Label>
              <Input
                id="team_size"
                value={teamSize}
                onChange={(e) => setTeamSize(e.target.value)}
                placeholder="예: 4명"
                maxLength={20}
              />
            </section>

            <section className="flex flex-col gap-2">
              <Label>
                4. 지난 팀 프로젝트에서 "누가 어디서 막혔는지 모르는" 상황이 얼마나 자주? *
              </Label>
              <div className="flex flex-col gap-1.5">
                {FREQUENCY_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-200 px-3 py-2 hover:bg-slate-50"
                  >
                    <input
                      type="radio"
                      name="pain_frequency"
                      value={opt.value}
                      checked={painFrequency === opt.value}
                      onChange={(e) => setPainFrequency(e.target.value)}
                    />
                    <span className="text-sm">{opt.label}</span>
                  </label>
                ))}
              </div>
            </section>

            <section className="flex flex-col gap-2">
              <Label>5. 이 문제가 팀에 미친 영향 강도? * (1: 없음 — 5: 매우 심각)</Label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setPainIntensity(n)}
                    className={`flex h-10 w-10 items-center justify-center rounded-md border text-sm font-semibold ${
                      painIntensity === n
                        ? 'border-teal-500 bg-teal-50 text-teal-950'
                        : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </section>

            <section className="flex flex-col gap-2">
              <Label htmlFor="top_pain">
                6. 지난 팀 프로젝트에서 가장 힘들었던 일 3가지 (자유 응답)
              </Label>
              <Textarea
                id="top_pain"
                value={topPainText}
                onChange={(e) => setTopPainText(e.target.value)}
                placeholder="예: 1) 누가 뭘 하는지 몰랐다 2) 막힌 사람이 말 안 함 3) ..."
                rows={4}
                maxLength={2000}
              />
              <p className="text-xs text-slate-500">
                해결책이 아닌 "있었던 일"을 적어주세요.
              </p>
            </section>

            <section className="flex flex-col gap-2">
              <Label>7. 지금 쓰는 협업 도구 (해당되는 것 모두)</Label>
              <div className="grid grid-cols-2 gap-2">
                {TOOL_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-200 px-3 py-2 hover:bg-slate-50"
                  >
                    <input
                      type="checkbox"
                      value={opt.value}
                      checked={tools.includes(opt.value)}
                      onChange={() => toggleTool(opt.value)}
                    />
                    <span className="text-sm">{opt.label}</span>
                  </label>
                ))}
              </div>
            </section>

            {showOperatorBranch ? (
              <>
                <section className="flex flex-col gap-2 rounded-lg border border-amber-200 bg-amber-50/50 p-4">
                  <Label>
                    8. (운영진/창업자만) "진행 멈춘 팀/구성원을 못 찾아 데모데이/마일스톤을 놓친"
                    경험이 있나요?
                  </Label>
                  <div className="flex gap-3">
                    {[
                      { value: true, label: '있다' },
                      { value: false, label: '없다' },
                    ].map((opt) => (
                      <label
                        key={String(opt.value)}
                        className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 hover:bg-slate-50"
                      >
                        <input
                          type="radio"
                          name="silent_team"
                          checked={hasSilentTeamExperience === opt.value}
                          onChange={() => setHasSilentTeamExperience(opt.value)}
                        />
                        <span className="text-sm">{opt.label}</span>
                      </label>
                    ))}
                  </div>
                </section>

                <section className="flex flex-col gap-2 rounded-lg border border-amber-200 bg-amber-50/50 p-4">
                  <Label htmlFor="pricing">
                    9. (운영진/창업자만) 팀 진행 가시화 도구에 얼마면 결제 의사가 있나요?
                    (학기/분기당)
                  </Label>
                  <Select
                    id="pricing"
                    value={operatorPricing}
                    onChange={(e) => setOperatorPricing(e.target.value)}
                  >
                    <option value="">선택해주세요</option>
                    <option value="0">결제 의사 없음</option>
                    <option value="100000">~10만원</option>
                    <option value="300000">~30만원</option>
                    <option value="500000">~50만원</option>
                    <option value="1000000">100만원+</option>
                  </Select>
                </section>
              </>
            ) : null}

            <section className="flex flex-col gap-2">
              <Label>
                10. "팀 작업 가시화 도구"가 있다면 다음 학기/프로젝트에 써볼 의향? *
                (1: 전혀 없음 — 5: 매우 있음)
              </Label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setWillingnessToTry(n)}
                    className={`flex h-10 w-10 items-center justify-center rounded-md border text-sm font-semibold ${
                      willingnessToTry === n
                        ? 'border-teal-500 bg-teal-50 text-teal-950'
                        : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </section>

            <section className="flex flex-col gap-2 rounded-lg border border-slate-200 bg-slate-50 p-4">
              <label className="flex cursor-pointer items-start gap-2">
                <input
                  type="checkbox"
                  checked={consentsToFollowup}
                  onChange={(e) => setConsentsToFollowup(e.target.checked)}
                  className="mt-1"
                />
                <span className="text-sm">
                  후속 인터뷰(20~30분)에 참여 의향이 있습니다. 이메일로 연락받을게요.
                </span>
              </label>
              {consentsToFollowup ? (
                <Input
                  type="email"
                  value={contactEmail}
                  onChange={(e) => setContactEmail(e.target.value)}
                  placeholder="이메일"
                  required={consentsToFollowup}
                />
              ) : null}
            </section>

            {error ? (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900">
                {error}
              </div>
            ) : null}

            <Button type="submit" disabled={submitting}>
              {submitting ? '제출 중...' : '응답 보내기'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
