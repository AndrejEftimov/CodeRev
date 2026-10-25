import { CalendarDays, LayoutDashboard } from 'lucide-react'
import { NavLink, Outlet } from 'react-router'
import ThemeToggle from '../shared/components/ThemeToggle.jsx'
import { APP } from '../shared/config/app.js'
import { ROUTES } from '../shared/routing/routes.js'

function AppShell() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="page-container topbar__inner">
          <NavLink className="brand" to={ROUTES.home} aria-label={`${APP.name} home`}>
            <img
              className="brand__logo"
              src="/images/brand/coderev-icon.png"
              alt=""
            />
            <span className="brand__name text-brand-gradient">{APP.name}</span>
          </NavLink>

          <div className="topbar__actions">
            <nav className="topbar__nav" aria-label="Primary navigation">
              <NavLink
                className={({ isActive }) => `nav-link${isActive ? ' nav-link--active' : ''}`}
                to={ROUTES.booking}
                end
              >
                <CalendarDays size={16} strokeWidth={1.9} aria-hidden="true" />
                Slots
              </NavLink>
              <NavLink
                className={({ isActive }) => `nav-link${isActive ? ' nav-link--active' : ''}`}
                to={ROUTES.host}
              >
                <LayoutDashboard size={16} strokeWidth={1.9} aria-hidden="true" />
                Host
              </NavLink>
            </nav>

            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="page-container page-content">
        <Outlet />
      </main>
    </div>
  )
}

export default AppShell
