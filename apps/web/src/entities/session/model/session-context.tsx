import type { Session, User } from '@supabase/supabase-js'
import { createContext, useContext, useEffect, useMemo, useState } from 'react'

import { supabase } from 'app/shared'

type SessionState =
  | { readonly status: 'loading' }
  | { readonly status: 'authenticated'; readonly session: Session; readonly user: User }
  | { readonly status: 'unauthenticated' }

const SessionContext = createContext<SessionState>({ status: 'loading' })

export const useSession = () => useContext(SessionContext)

export const AuthProvider = ({ children }: { readonly children: React.ReactNode }) => {
  const [state, setState] = useState<SessionState>({ status: 'loading' })

  useEffect(() => {
    const init = async () => {
      const { data } = await supabase.auth.getSession()
      if (data.session) {
        setState({ status: 'authenticated', session: data.session, user: data.session.user })
      } else {
        setState({ status: 'unauthenticated' })
      }
    }
    init()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setState({ status: 'authenticated', session, user: session.user })
      } else {
        setState({ status: 'unauthenticated' })
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const value = useMemo(() => state, [state])

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
}
