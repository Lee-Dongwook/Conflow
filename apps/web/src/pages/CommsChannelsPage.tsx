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
    <div className="mx-auto max-w-3xl space-y-5">
      <header className="flex items-end justify-between gap-3">
        <div className="space-y-1">
          <h1 className="text-xl font-semibold text-slate-900">채널</h1>
          <p className="text-sm text-slate-500">
            팀 대화가 주제별로 모이는 곳이에요. 채널을 열어 스레드를 확인하세요.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          className="flex shrink-0 items-center gap-1.5 rounded-lg bg-slate-900 px-3.5 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-700"
        >
          <span className="text-base leading-none">+</span>새 채널
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
