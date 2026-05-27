import { apiClient } from 'app/shared/api'

import {
  MeetingSummaryOutputSchema,
  type MeetingSummaryInput,
  type MeetingSummaryOutput,
} from './schemas'

const BASE = '/v1/agent'

export const meetingSummaryApi = {
  async summarize(input: MeetingSummaryInput): Promise<MeetingSummaryOutput> {
    const { data } = await apiClient.post(`${BASE}/meeting-summary`, input)
    return MeetingSummaryOutputSchema.parse(data)
  },
} as const
