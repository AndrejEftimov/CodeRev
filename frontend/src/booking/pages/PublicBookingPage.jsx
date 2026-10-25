import ReviewSlotTimeline from '../components/ReviewSlotTimeline.jsx'

function PublicBookingPage() {
  return (
    <section className="page-section" aria-labelledby="public-page-title">
      <div className="page-heading">
        <p className="eyebrow">Code review availability</p>
        <h1 id="public-page-title">Book focused review time.</h1>
        <p className="page-heading__description">
          Browse active slots for code, architecture, debugging, or implementation feedback.
        </p>
      </div>

      <ReviewSlotTimeline />
    </section>
  )
}

export default PublicBookingPage
