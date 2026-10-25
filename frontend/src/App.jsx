import { Route, Routes } from 'react-router'
import PublicBookingPage from './booking/pages/PublicBookingPage.jsx'
import HostPage from './host/pages/HostPage.jsx'
import LandingPage from './landing/pages/LandingPage.jsx'
import AppShell from './layouts/AppShell.jsx'
import NotFoundPage from './shared/routing/NotFoundPage.jsx'
import { ROUTES } from './shared/routing/routes.js'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path={ROUTES.home} element={<LandingPage />} />
        <Route path={ROUTES.booking} element={<PublicBookingPage />} />
        <Route path={ROUTES.host} element={<HostPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App
