/**
 * `/w/:workspaceUuid/pm/issues` — list + create modal.
 *
 * Modal is a barebones overlay (no portal lib). Click outside or Cancel
 * to dismiss; create success closes the modal and the list refetches
 * via the mutation's `invalidateQueries` in `useCreateIssue`.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { IssueCreateForm } from 'app/features/issue-create'
import { IssueList } from 'app/widgets/issue-list'

export const PMIssuesPage = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const navigate = useNavigate()
  const [createOpen, setCreateOpen] = useState(false)

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">PM Issues</h1>
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          className="rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white shadow-sm hover:bg-slate-800"
        >
          새 이슈
        </button>
      </header>

      <IssueList
        onIssueClick={(issue) =>
          navigate(`/w/${workspaceUuid}/pm/issues/${issue.uuid}`)
        }
      />

      {createOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4"
          onClick={() => setCreateOpen(false)}
        >
          <div
            className="w-full max-w-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <IssueCreateForm
              onCreated={() => setCreateOpen(false)}
              onCancel={() => setCreateOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}
