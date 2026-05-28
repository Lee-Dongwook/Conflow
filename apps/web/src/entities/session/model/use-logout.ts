import { useCallback } from 'react'

import { apiClient } from 'app/shared/api'
import { supabase } from 'app/shared/lib'

export const useLogout = () => {
  const logout = useCallback(async () => {
    try {
      await apiClient.post('/users/logout')
    } catch {
      // backend logout is best-effort; proceed with client-side cleanup
    }
    await supabase.auth.signOut()
  }, [])

  return logout
}
