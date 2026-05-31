import { z } from 'zod'

export const DashboardTaskReadSchema = z.object({
  uuid: z.string(),
  title: z.string(),
  columnKey: z.string(),
  assigneeUserUuid: z.string().nullable(),
  assigneeName: z.string().nullable(),
})
export type DashboardTaskRead = z.infer<typeof DashboardTaskReadSchema>

export const DashboardSprintReadSchema = z.object({
  uuid: z.string(),
  label: z.string(),
  sharedGoal: z.string().nullable(),
  periodLabel: z.string().nullable(),
  startsOn: z.string(),
  endsOn: z.string(),
})
export type DashboardSprintRead = z.infer<typeof DashboardSprintReadSchema>

export const DashboardMemberReadSchema = z.object({
  userUuid: z.string(),
  name: z.string(),
  email: z.string(),
  profileImageUrl: z.string().nullable(),
  role: z.string(),
})
export type DashboardMemberRead = z.infer<typeof DashboardMemberReadSchema>

export const TeamDashboardReadSchema = z.object({
  teamUuid: z.string(),
  teamName: z.string(),
  teamDescription: z.string().nullable(),
  sprint: DashboardSprintReadSchema.nullable(),
  tasks: z.array(DashboardTaskReadSchema),
  members: z.array(DashboardMemberReadSchema),
  progressPercent: z.number(),
  totalTasks: z.number(),
  doneTasks: z.number(),
  blockerNote: z.string().nullable(),
  courseLabel: z.string().nullable(),
  nextDeadlineLabel: z.string().nullable(),
})
export type TeamDashboardRead = z.infer<typeof TeamDashboardReadSchema>
