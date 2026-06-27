/**
 * App-wide router.
 *
 *   `/`                     → auth-aware landing (guest → GuestLandingPage)
 *   `/legal`                → LegalPage
 *   `/survey`               → SurveyPage (one-off marketing route)
 *   `/workspace/new`        → CreateWorkspacePage
 *   `/w/:workspaceUuid/...` → workspace-scoped domain pages
 *   `*`                     → redirect to `/`
 *
 * The legacy state-based AppContent tree has been retired; guests see the
 * GuestLandingPage and everything unmatched redirects home.
 */

import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'

import { CommsChannelDetailPage } from 'app/pages/CommsChannelDetailPage'
import { CommsChannelsPage } from 'app/pages/CommsChannelsPage'
import { CreateWorkspacePage } from 'app/pages/CreateWorkspacePage'
import { DocumentsInstancesPage } from 'app/pages/DocumentsInstancesPage'
import { HREmployeesPage } from 'app/pages/HREmployeesPage'
import { LandingRedirectPage } from 'app/pages/LandingRedirectPage'
import { LegalPage } from 'app/pages/legal'
import { A2UIToolsPage } from 'app/pages/A2UIToolsPage'
import { PMIssueDetailPage } from 'app/pages/PMIssueDetailPage'
import { PMIssuesPage } from 'app/pages/PMIssuesPage'
import { SurveyPage } from 'app/pages/SurveyPage'
import { WorkspaceOverviewPage } from 'app/pages/WorkspaceOverviewPage'

import { WorkspaceShell } from './WorkspaceShell'

interface AppRouterProps {
  readonly guestLanding: ReactNode
}

export const AppRouter = ({ guestLanding }: AppRouterProps) => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<LandingRedirectPage fallback={guestLanding} />} />
      <Route path="/survey" element={<SurveyPage />} />
      <Route path="/legal" element={<LegalPage />} />
      <Route path="/workspace/new" element={<CreateWorkspacePage />} />

      <Route path="/w/:workspaceUuid" element={<WorkspaceShell />}>
        <Route index element={<WorkspaceOverviewPage />} />
        <Route path="pm/issues" element={<PMIssuesPage />} />
        <Route
          path="pm/issues/:issueUuid"
          element={<PMIssueDetailPage />}
        />
        <Route path="comms/channels" element={<CommsChannelsPage />} />
        <Route
          path="comms/channels/:channelUuid"
          element={<CommsChannelDetailPage />}
        />
        <Route path="hr/profiles" element={<HREmployeesPage />} />
        <Route
          path="documents/instances"
          element={<DocumentsInstancesPage />}
        />
        <Route path="a2ui/tools" element={<A2UIToolsPage />} />
      </Route>

      {/* Anything unmatched returns to the auth-aware landing. */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
)
