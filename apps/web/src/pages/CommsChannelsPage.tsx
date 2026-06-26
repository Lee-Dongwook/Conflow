/**
 * `/w/:workspaceUuid/comms/channels` — channel list + create modal.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { ChannelCreateForm } from 'app/features/channel-create'
import { ChannelList } from 'app/widgets/channel-list'

export const CommsChannelsPage = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const navigate = useNavigate()
  const [createOpen, setCreateOpen] = useState(false)

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">Channels</h1>
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          className="rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white shadow-sm hover:bg-slate-800"
        >
          새 채널
        </button>
      </header>

      <ChannelList
        onChannelClick={(channel) =>
          navigate(`/w/${workspaceUuid}/comms/channels/${channel.uuid}`)
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
            <ChannelCreateForm
              onCreated={(channel) => {
                setCreateOpen(false)
                navigate(`/w/${workspaceUuid}/comms/channels/${channel.uuid}`)
              }}
              onCancel={() => setCreateOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}
