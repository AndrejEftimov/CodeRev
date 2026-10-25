import { CalendarCheck2 } from 'lucide-react'
import Button from '../../shared/components/Button.jsx'
import StatusBadge from '../../shared/components/StatusBadge.jsx'
import { formatLocalDate, formatTimeRange } from '../../shared/utils/dateTime.js'

const STATUS_COPY = {
  available: 'Ready to reserve for a focused code-review session.',
  taken: 'This session has already been reserved.',
  started: 'This review session is currently in progress.',
}

function ReviewSlotCard({ reviewSlot, onBook }) {
  const isAvailable = reviewSlot.status === 'available'

  return (
    <article className="review-slot-card surface">
      <div className="review-slot-card__time">
        <span className="review-slot-card__date">{formatLocalDate(reviewSlot.startDate)}</span>
        <strong>{formatTimeRange(reviewSlot.startTime, reviewSlot.endTime)}</strong>
        <span className="review-slot-card__duration">{reviewSlot.durationMinutes} min</span>
      </div>

      <div className="review-slot-card__status">
        <StatusBadge status={reviewSlot.status} />

        <p>{STATUS_COPY[reviewSlot.status] ?? 'This slot is not currently bookable.'}</p>

        {isAvailable && (
          <Button className="review-slot-card__action" onClick={() => onBook(reviewSlot)}>
            <CalendarCheck2 size={16} aria-hidden="true" />
            Book review
          </Button>
        )}
      </div>
    </article>
  )
}

export default ReviewSlotCard
