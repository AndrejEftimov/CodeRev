import {
  ArrowRight,
  BrainCircuit,
  CalendarClock,
  CheckCircle2,
  Code2,
  GitPullRequest,
  MessageSquareText,
  SearchCode,
  ShieldCheck,
  Users,
} from 'lucide-react'
import { Link } from 'react-router'
import { ROUTES } from '../../shared/routing/routes.js'

const BENEFITS = [
  {
    icon: ShieldCheck,
    title: 'Catch issues earlier.',
    copy: 'A second set of eyes can surface correctness, security, maintainability, and edge-case problems before they spread.',
  },
  {
    icon: BrainCircuit,
    title: 'Share engineering context.',
    copy: 'Reviews spread knowledge about architecture, conventions, tradeoffs, and unfamiliar areas of the codebase.',
  },
  {
    icon: Users,
    title: 'Build shared ownership.',
    copy: 'Good reviews make code a team responsibility instead of leaving important decisions with one developer.',
  },
  {
    icon: GitPullRequest,
    title: 'Improve change quality.',
    copy: 'Focused feedback helps changes become easier to understand, test, maintain, and evolve after they merge.',
  },
]

const REVIEW_STEPS = [
  {
    icon: Code2,
    title: 'Bring focused context.',
    copy: 'Keep the change understandable and explain the goal, important constraints, and the areas where feedback matters most.',
  },
  {
    icon: SearchCode,
    title: 'Review the change, not the author.',
    copy: 'Check behavior, design, tests, edge cases, readability, and maintainability. Separate required fixes from optional suggestions.',
  },
  {
    icon: MessageSquareText,
    title: 'Discuss unclear tradeoffs.',
    copy: 'Use synchronous review time when comments alone are becoming slow, ambiguous, or difficult to resolve.',
  },
  {
    icon: CheckCircle2,
    title: 'Close with clear outcomes.',
    copy: 'Leave the session knowing what should change, what is accepted, and whether another review pass is actually needed.',
  },
]

function LandingPage() {
  return (
    <section className="landing-page" aria-labelledby="landing-title">
      <div className="landing-hero">
        <p className="eyebrow">Focused engineering collaboration</p>
        <h1 id="landing-title">Make code review time intentional.</h1>
        <p className="landing-hero__description">
          CodeRev gives developers a simple place to publish dedicated review windows and reserve focused time for code, architecture, debugging, and implementation feedback.
        </p>

        <div className="landing-hero__actions">
          <Link className="button button--primary" to={ROUTES.booking}>
            <CalendarClock size={17} aria-hidden="true" />
            Book a review
          </Link>
          <Link className="button button--secondary" to={ROUTES.host}>
            Host workspace
            <ArrowRight size={17} aria-hidden="true" />
          </Link>
        </div>
      </div>

      <div className="landing-paths" aria-label="CodeRev workflows">
        <article className="landing-path-card surface">
          <span className="landing-path-card__index">01</span>
          <h2>Find focused review time.</h2>
          <p>Browse active slots, choose an available session, and reserve it with the context the reviewer needs.</p>
          <Link className="landing-path-card__link" to={ROUTES.booking}>
            View slots
            <ArrowRight size={15} aria-hidden="true" />
          </Link>
        </article>

        <article className="landing-path-card surface">
          <span className="landing-path-card__index">02</span>
          <h2>Publish availability.</h2>
          <p>Create slots, inspect booking details, and manage upcoming review sessions from one host workspace.</p>
          <Link className="landing-path-card__link" to={ROUTES.host}>
            Open host workspace
            <ArrowRight size={15} aria-hidden="true" />
          </Link>
        </article>
      </div>

      <section className="landing-section" aria-labelledby="benefits-title">
        <div className="landing-section__heading">
          <p className="eyebrow">Why review code</p>
          <h2 id="benefits-title">Better changes through shared understanding.</h2>
          <p>
            Code review is more than defect detection. Done well, it improves the code while also improving how the team understands and owns the system.
          </p>
        </div>

        <div className="landing-feature-layout">
          <div className="landing-benefits">
            {BENEFITS.map(({ icon: BenefitIcon, title, copy }) => (
              <article className="landing-benefit" key={title}>
                <div className="landing-feature-icon" aria-hidden="true">
                  <BenefitIcon size={18} />
                </div>
                <div>
                  <h3>{title}</h3>
                  <p>{copy}</p>
                </div>
              </article>
            ))}
          </div>

          <div className="landing-feature-image">
            <img
              src="/images/landing/code-review-collaboration.png"
              alt="Two developers reviewing a focused code change together."
            />
          </div>
        </div>
      </section>

      <section className="landing-section" aria-labelledby="how-title">
        <div className="landing-section__heading">
          <p className="eyebrow">How to review well</p>
          <h2 id="how-title">Keep feedback focused, specific, and actionable.</h2>
          <p>
            The best review sessions have enough context to make useful decisions without turning into a broad redesign of everything around the change.
          </p>
        </div>

        <div className="landing-feature-layout landing-feature-layout--reverse">
          <div className="landing-feature-image">
            <img
              src="/images/landing/code-review-workflow.png"
              alt="Code review workflow from context through discussion to a clear outcome."
            />
          </div>

          <div className="landing-review-steps">
            {REVIEW_STEPS.map(({ icon: StepIcon, title, copy }, index) => (
              <article className="landing-review-step" key={title}>
                <div className="landing-review-step__marker">
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <StepIcon size={17} aria-hidden="true" />
                </div>
                <div>
                  <h3>{title}</h3>
                  <p>{copy}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </section>
  )
}

export default LandingPage
