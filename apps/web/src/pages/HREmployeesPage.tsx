/**
 * `/w/:workspaceUuid/hr/profiles` — employee list.
 *
 * Create / tenure-transition land as separate features when the
 * Member-picker UI is in place; for now this page is read-only.
 */

import { EmployeeList } from 'app/widgets/employee-list'

export const HREmployeesPage = () => (
  <div className="mx-auto max-w-4xl space-y-6">
    <header>
      <h1 className="text-xl font-semibold text-slate-900">HR Employees</h1>
      <p className="mt-1 text-xs text-slate-500">
        EmployeeProfile (Member의 HR 확장). 응답은 caller 권한별 프라이버시 4계층으로
        마스킹됩니다 — 직접 본인 / 매니저 / HR Admin / 외부 (public only).
      </p>
    </header>
    <EmployeeList />
  </div>
)
