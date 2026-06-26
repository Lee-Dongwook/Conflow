/**
 * `/workspace/new` host. Centers the create form on a neutral background.
 */

import { CreateWorkspaceForm } from 'app/features/workspace-create'

export const CreateWorkspacePage = () => (
  <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12">
    <CreateWorkspaceForm />
  </div>
)
