import { apiClient } from 'app/shared/api'

import {
  SurveyResponseReadSchema,
  type SurveyResponseRead,
  type SurveySubmit,
} from './schemas'

const BASE = '/surveys'

export const surveyApi = {
  async submit(payload: SurveySubmit): Promise<SurveyResponseRead> {
    const { data } = await apiClient.post(`${BASE}/responses`, payload)
    return SurveyResponseReadSchema.parse(data)
  },
} as const
