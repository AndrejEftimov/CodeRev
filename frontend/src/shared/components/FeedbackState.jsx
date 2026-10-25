import Button from './Button.jsx'

function FeedbackState({ eyebrow, title, message, actionLabel, onAction, role }) {
  return (
    <section className="surface feedback-state" role={role}>
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2>{title}</h2>
      </div>
      {message && <p>{message}</p>}
      {actionLabel && onAction && (
        <Button variant="secondary" onClick={onAction}>{actionLabel}</Button>
      )}
    </section>
  )
}

export default FeedbackState
