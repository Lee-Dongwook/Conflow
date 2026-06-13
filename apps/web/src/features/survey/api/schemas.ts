import { z } from 'zod'

export const RespondentRoleSchema = z.enum([
  'capstone_leader',
  'capstone_member',
  'club_operator',
  'club_member',
  'startup_founder',
  'side_project_leader',
  'other',
])
export type RespondentRole = z.infer<typeof RespondentRoleSchema>

export const SurveySubmitSchema = z.object({
  survey_key: z.string().min(1).max(64),
  respondent_role: RespondentRoleSchema,
  organization: z.string().max(200).optional().nullable(),
  contact_email: z.string().email().optional().nullable(),
  consents_to_followup: z.boolean(),
  answers: z.record(z.string(), z.unknown()),
})
export type SurveySubmit = z.infer<typeof SurveySubmitSchema>

export const SurveyResponseReadSchema = z.object({
  uuid: z.string(),
  created_at: z.string(),
  survey_key: z.string(),
  respondent_role: z.string(),
  organization: z.string().nullable(),
  contact_email: z.string().nullable(),
  consents_to_followup: z.boolean(),
  answers: z.record(z.string(), z.unknown()),
})
export type SurveyResponseRead = z.infer<typeof SurveyResponseReadSchema>
