import { Link } from 'react-router'
import { ROUTES } from './routes.js'

function NotFoundPage() {
  return (
    <section className="page-section page-section--centered">
      <div className="surface empty-state">
        <div>
          <p className="eyebrow">404</p>
          <h1>Page not found.</h1>
        </div>
        <p>The page you requested does not exist.</p>
        <Link className="button button--primary" to={ROUTES.booking}>Back to review slots</Link>
      </div>
    </section>
  )
}

export default NotFoundPage
