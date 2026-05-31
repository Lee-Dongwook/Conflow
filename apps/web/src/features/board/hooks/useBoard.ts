import { useCallback, useEffect, useState } from 'react'

import {
  boardApi,
  type BoardCardCreate,
  type BoardCardMove,
  type BoardCardRead,
  type BoardCardUpdate,
} from 'app/entities/board'

type BoardState =
  | { readonly status: 'idle' }
  | { readonly status: 'loading' }
  | { readonly status: 'success'; readonly cards: readonly BoardCardRead[] }
  | { readonly status: 'error'; readonly error: string }

export const useBoard = (sprintUuid: string | null) => {
  const [state, setState] = useState<BoardState>({ status: 'idle' })

  const fetchCards = useCallback(async () => {
    if (!sprintUuid) return
    setState({ status: 'loading' })
    try {
      const cards = await boardApi.listBySprint(sprintUuid)
      setState({ status: 'success', cards })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load board'
      setState({ status: 'error', error: message })
    }
  }, [sprintUuid])

  useEffect(() => {
    fetchCards()
  }, [fetchCards])

  const create = useCallback(
    async (payload: BoardCardCreate) => {
      const card = await boardApi.create(payload)
      setState((prev) =>
        prev.status === 'success'
          ? { ...prev, cards: [...prev.cards, card] }
          : prev,
      )
      return card
    },
    [],
  )

  const update = useCallback(
    async (cardUuid: string, payload: BoardCardUpdate) => {
      const updated = await boardApi.update(cardUuid, payload)
      setState((prev) =>
        prev.status === 'success'
          ? {
              ...prev,
              cards: prev.cards.map((c) => (c.uuid === cardUuid ? updated : c)),
            }
          : prev,
      )
      return updated
    },
    [],
  )

  const move = useCallback(
    async (cardUuid: string, payload: BoardCardMove) => {
      const moved = await boardApi.move(cardUuid, payload)
      setState((prev) =>
        prev.status === 'success'
          ? {
              ...prev,
              cards: prev.cards.map((c) => (c.uuid === cardUuid ? moved : c)),
            }
          : prev,
      )
      return moved
    },
    [],
  )

  const remove = useCallback(
    async (cardUuid: string) => {
      await boardApi.delete(cardUuid)
      setState((prev) =>
        prev.status === 'success'
          ? { ...prev, cards: prev.cards.filter((c) => c.uuid !== cardUuid) }
          : prev,
      )
    },
    [],
  )

  return { ...state, refetch: fetchCards, create, update, move, remove } as const
}
