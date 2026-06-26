/**
 * App-wide router.
 *
 * Two trees coexist until the migration is done:
 *   `/`                     → legacy state-based AppContent
 *   `/legal`                → legacy LegalPage
 *   `/survey`               → SurveyPage (one-off marketing route)
 *   `/w/:workspaceUuid/...` → new workspace-scoped domain pages
 *
 * Legacy pages do NOT need react-router; the catch-all returns the
 * existing AppContent so removing pages happens piecewise.
 */

import { BrowserRouter, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'

import { CommsChannelDetailPage } from 'app/pages/CommsChannelDetailPage'
import { CommsChannelsPage } from 'app/pages/CommsChannelsPage'
import { CreateWorkspacePage } from 'app/pages/CreateWorkspacePage'
import { LandingRedirectPage } from 'app/pages/LandingRedirectPage'
import { LegalPage } from 'app/pages/legal'
import { PMIssueDetailPage } from 'app/pages/PMIssueDetailPage'
import { PMIssuesPage } from 'app/pages/PMIssuesPage'
import { SurveyPage } from 'app/pages/SurveyPage'

import {
  A2UIToolsPlaceholder,
  DocumentsInstancesPlaceholder,
  HrEmployeesPlaceholder,
  WorkspaceIndexPlaceholder,
} from './placeholders'
import { WorkspaceShell } from './WorkspaceShell'

interface AppRouterProps {
  readonly legacyApp: ReactNode
}

export const AppRouter = ({ legacyApp }: AppRouterProps) => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<LandingRedirectPage fallback={legacyApp} />} />
      <Route path="/survey" element={<SurveyPage />} />
      <Route path="/legal" element={<LegalPage />} />
      <Route path="/workspace/new" element={<CreateWorkspacePage />} />

      <Route path="/w/:workspaceUuid" element={<WorkspaceShell />}>
        <Route index element={<WorkspaceIndexPlaceholder />} />
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
        <Route path="hr/profiles" element={<HrEmployeesPlaceholder />} />
        <Route
          path="documents/instances"
          element={<DocumentsInstancesPlaceholder />}
        />
        <Route path="a2ui/tools" element={<A2UIToolsPlaceholder />} />
      </Route>

      {/* Catch-all: legacy state-based UI keeps working until pages migrate. */}
      <Route path="*" element={legacyApp} />
    </Routes>
  </BrowserRouter>
)
