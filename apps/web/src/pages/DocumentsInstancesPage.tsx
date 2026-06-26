/**
 * `/w/:workspaceUuid/documents/instances` — instance list + actions.
 *
 * Template management UI lands separately (next slice). The page itself
 * is read+act; drafting a new instance currently happens via the API
 * directly (or via the next features/document-draft slice).
 */

import { DocumentInstanceList } from 'app/widgets/document-instance-list'

export const DocumentsInstancesPage = () => (
  <div className="mx-auto max-w-3xl space-y-6">
    <header>
      <h1 className="text-xl font-semibold text-slate-900">Documents</h1>
      <p className="mt-1 text-xs text-slate-500">
        발급 워크플로우: draft → pending_review → approved → issued. 각 상태에서 가능한
        액션만 표시됩니다.
      </p>
    </header>
    <DocumentInstanceList />
  </div>
)
