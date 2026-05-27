import { z } from 'zod'

export const MeetingActionItemSchema = z.object({
  task: z.string(),
  owner: z.string(),
})
export type MeetingActionItem = z.infer<typeof MeetingActionItemSchema>

export const MeetingSummaryOutputSchema = z.object({
  overview: z.string(),
  bullets: z.array(z.string()),
  decisions: z.array(z.string()),
  actions: z.array(MeetingActionItemSchema),
  nextSteps: z.array(z.string()),
})
export type MeetingSummaryOutput = z.infer<typeof MeetingSummaryOutputSchema>

export const MeetingSummaryInputSchema = z.object({
  meetingTitle: z.string().min(1).max(256),
  transcript: z.string().min(1),
  teamContext: z.string().nullable().optional(),
})
export type MeetingSummaryInput = z.infer<typeof MeetingSummaryInputSchema>
