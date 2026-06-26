/**
 * Phase 1.3 placeholders for the new domain routes.
 *
 * Each `<DomainPlaceholder />` is the route target until Phase 3–6 lands
 * the real page. Replacing one is a one-file swap (drop the import in
 * `Router.tsx`, point it at `pages/<NewPage>`).
 */

interface PlaceholderProps {
  readonly title: string
  readonly note: string
}

const Placeholder = ({ title, note }: PlaceholderProps) => (
  <div className="mx-auto max-w-xl rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
    <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
    <p className="mt-2 text-sm text-slate-600">{note}</p>
  </div>
)

export const PmIssuesPlaceholder = () => (
  <Placeholder
    title="PM Issues"
    note="Phase 3 작업으로 list / create / transition UI 가 들어옵니다."
  />
)

export const CommsChannelsPlaceholder = () => (
  <Placeholder
    title="Comms Channels"
    note="Phase 4 작업으로 채널 리스트 / 메시지 스트림 UI 가 들어옵니다."
  />
)

export const HrEmployeesPlaceholder = () => (
  <Placeholder
    title="HR Employees"
    note="Phase 5 작업으로 EmployeeProfile 리스트 (privacy masked) 가 들어옵니다."
  />
)

export const DocumentsInstancesPlaceholder = () => (
  <Placeholder
    title="Documents Instances"
    note="Phase 6 작업으로 발급 워크플로우 UI 가 들어옵니다."
  />
)

export const A2UIToolsPlaceholder = () => (
  <Placeholder
    title="A2UI Tools"
    note="Phase 7 작업으로 Tool catalog + invoke UI 가 들어옵니다."
  />
)

export const WorkspaceIndexPlaceholder = () => (
  <Placeholder
    title="Workspace Home"
    note="좌측 네비게이션 (Phase 2) 가 들어오면 도메인 페이지로 이동합니다."
  />
)
