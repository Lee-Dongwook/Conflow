import { useCallback, useEffect, useState } from 'react'

import {
  backlogApi,
  type BacklogItemCreate,
  type BacklogItemRead,
  type BacklogItemUpdate,
} from 'app/entities/backlog'

type BacklogState =
  | { readonly status: 'idle' }
  | { readonly status: 'loading' }
  | { readonly status: 'success'; readonly items: readonly BacklogItemRead[] }
  | { readonly status: 'error'; readonly error: string }

export const useBacklog = (sprintUuid: string | null) => {
  const [state, setState] = useState<BacklogState>({ status: 'idle' })

  const fetch = useCallback(async () => {
    if (!sprintUuid) return
    setState({ status: 'loading' })
    try {
      const items = await backlogApi.listBySprint(sprintUuid)
      setState({ status: 'success', items })
    } catch (err) {
      const message = err instanceof Error ? err.message : '백로그를 불러오지 못했습니다'
      setState({ status: 'error', error: message })
    }
  }, [sprintUuid])

  useEffect(() => {
    fetch()
  }, [fetch])

  const create = useCallback(async (payload: BacklogItemCreate) => {
    const created = await backlogApi.create(payload)
    setState((prev) =>
      prev.status === 'success' ? { ...prev, items: [...prev.items, created] } : prev,
    )
    return created
  }, [])

  const update = useCallback(async (itemUuid: string, payload: BacklogItemUpdate) => {
    const updated = await backlogApi.update(itemUuid, payload)
    setState((prev) =>
      prev.status === 'success'
        ? {
            ...prev,
            items: prev.items.map((i) => (i.uuid === itemUuid ? updated : i)),
          }
        : prev,
    )
    return updated
  }, [])

  const remove = useCallback(async (itemUuid: string) => {
    await backlogApi.remove(itemUuid)
    setState((prev) =>
      prev.status === 'success'
        ? { ...prev, items: prev.items.filter((i) => i.uuid !== itemUuid) }
        : prev,
    )
  }, [])

  return { ...state, refetch: fetch, create, update, remove } as const
}
