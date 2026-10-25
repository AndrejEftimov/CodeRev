import { Eye, Trash2, XCircle } from 'lucide-react'
import Button from '../../shared/components/Button.jsx'
import StatusBadge from '../../shared/components/StatusBadge.jsx'
import { formatLocalDate, formatTimeRange } from '../../shared/utils/dateTime.js'

function BookingDetails({ booking }) {
  if (!booking) return null

  return (
    <dl className="host-booking-details">
      <div>
        <dt>Developer</dt>
        <dd>{booking.name}</dd>
      </div>
      <div>
        <dt>Email</dt>
        <dd><a href={`mailto:${booking.email}`}>{booking.email}</a></dd>
      </div>
      <div>
        <dt>Topic</dt>
        <dd>{booking.reviewTopic}</dd>
      </div>
      {booking.reviewDescription && (
        <div className="host-booking-details__description">
          <dt>Context</dt>
          <dd>{booking.reviewDescription}</dd>
        </div>
      )}
    </dl>
  )
}

function HostReviewSlotCard({ reviewSlot, onDelete, onViewDetails }) {
  const canDelete = reviewSlot.status === 'available' || reviewSlot.status === 'taken'
  const ActionIcon = reviewSlot.status === 'taken' ? XCircle : Trash2

  return (
    <article className="host-review-slot-card surface">
      <div className="host-review-slot-card__header">
        <div className="host-review-slot-card__meta">
          <div className="host-review-slot-card__time">
            <span>{formatLocalDate(reviewSlot.startDate)}</span>
            <strong>{formatTimeRange(reviewSlot.startTime, reviewSlot.endTime)}</strong>
            <span>{reviewSlot.durationMinutes} min</span>
          </div>

          <StatusBadge status={reviewSlot.status} />
        </div>

        <div className="host-review-slot-card__actions">
          {reviewSlot.booking && (
            <Button variant="secondary" onClick={() => onViewDetails(reviewSlot)}>
              <Eye size={14} aria-hidden="true" />
              Details
            </Button>
          )}

          {canDelete && (
            <Button variant="secondary" onClick={() => onDelete(reviewSlot)}>
              <ActionIcon size={14} aria-hidden="true" />
              {reviewSlot.status === 'taken' ? 'Cancel' : 'Delete'}
            </Button>
          )}
        </div>
      </div>

      {reviewSlot.booking ? (
        <BookingDetails booking={reviewSlot.booking} />
      ) : (
        <p className="host-review-slot-card__empty">No booking yet.</p>
      )}
    </article>
  )
}

export default HostReviewSlotCard
