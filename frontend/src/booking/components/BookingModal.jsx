import Modal from '../../shared/components/Modal.jsx'
import { formatLocalDate, formatTimeRange } from '../../shared/utils/dateTime.js'
import BookingForm from './BookingForm.jsx'

function BookingModal({ reviewSlot, open, onClose, onSubmit, submitting }) {
  if (!reviewSlot) return null

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Book review session"
      description="Add a little context so the host can prepare for a focused review."
      busy={submitting}
    >
      <div className="booking-slot-summary card-sunken">
        <div>
          <span className="booking-slot-summary__label">Date</span>
          <strong>{formatLocalDate(reviewSlot.startDate)}</strong>
        </div>
        <div>
          <span className="booking-slot-summary__label">Time</span>
          <strong>{formatTimeRange(reviewSlot.startTime, reviewSlot.endTime)}</strong>
        </div>
        <div>
          <span className="booking-slot-summary__label">Duration</span>
          <strong>{reviewSlot.durationMinutes} min</strong>
        </div>
      </div>

      <BookingForm
        onSubmit={onSubmit}
        onCancel={onClose}
        submitting={submitting}
      />
    </Modal>
  )
}

export default BookingModal
