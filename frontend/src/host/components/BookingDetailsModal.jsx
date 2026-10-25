import {
  CalendarDays,
  Clock3,
  Code2,
  Mail,
  MessageSquareText,
  Timer,
  UserRound,
} from 'lucide-react'
import Modal from '../../shared/components/Modal.jsx'
import StatusBadge from '../../shared/components/StatusBadge.jsx'
import { formatLocalDate, formatTimeRange } from '../../shared/utils/dateTime.js'

function DetailItem({
  icon: Icon,
  label,
  children,
  className = '',
  tone = 'neutral',
}) {
  return (
    <div
      className={[
        'host-booking-modal__item',
        `host-booking-modal__item--${tone}`,
        className,
      ].filter(Boolean).join(' ')}
    >
      <dt>
        <Icon size={14} strokeWidth={1.9} aria-hidden="true" />
        {label}
      </dt>
      <dd>{children}</dd>
    </div>
  )
}

function BookingDetailsModal({
  reviewSlot,
  open,
  onClose,
}) {
  if (!reviewSlot?.booking) return null

  const { booking } = reviewSlot

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Booking details"
      description="Full context for this scheduled code review."
      size="lg"
      className="host-booking-details-modal"
    >
      <div className="host-booking-modal">
        <div className="host-booking-modal__summary">
          <StatusBadge status={reviewSlot.status} />

          <div>
            <span>{formatLocalDate(reviewSlot.startDate)}</span>
            <strong>{formatTimeRange(reviewSlot.startTime, reviewSlot.endTime)}</strong>
            <span>{reviewSlot.durationMinutes} min</span>
          </div>
        </div>

        <dl className="host-booking-modal__details">
          <DetailItem icon={UserRound} label="Developer" tone="accent">
            {booking.name}
          </DetailItem>

          <DetailItem icon={Mail} label="Email">
            <a href={`mailto:${booking.email}`}>{booking.email}</a>
          </DetailItem>

          <DetailItem
            icon={Code2}
            label="Topic"
            className="host-booking-modal__item--wide"
          >
            {booking.reviewTopic}
          </DetailItem>

          <DetailItem icon={CalendarDays} label="Date">
            {formatLocalDate(reviewSlot.startDate)}
          </DetailItem>

          <DetailItem icon={Clock3} label="Time">
            {formatTimeRange(reviewSlot.startTime, reviewSlot.endTime)}
          </DetailItem>

          <DetailItem icon={Timer} label="Duration">
            {reviewSlot.durationMinutes} min
          </DetailItem>

          <DetailItem
            icon={MessageSquareText}
            label="Context"
            className="host-booking-modal__item--context"
          >
            {booking.reviewDescription || 'No additional context provided.'}
          </DetailItem>
        </dl>
      </div>
    </Modal>
  )
}

export default BookingDetailsModal
