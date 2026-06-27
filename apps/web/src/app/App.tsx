import { AuthProvider } from 'app/entities/session'
import { QueryProvider } from 'app/app/providers'
import { AppRouter } from 'app/app/router'
import { GuestLandingPage } from 'app/pages/GuestLandingPage'
import { AppAnalytics } from 'app/shared/analytics'

export const App = () => (
  <QueryProvider>
    <AuthProvider>
      <AppRouter guestLanding={<GuestLandingPage />} />
      <AppAnalytics />
    </AuthProvider>
  </QueryProvider>
)
