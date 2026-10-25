import { useCallback, useEffect, useState } from 'react'
import { bookReviewSlot, getPublicReviewSlots } from '../api/reviewSlots.js'
import FeedbackState from '../../shared/components/FeedbackState.jsx'
import Pagination from '../../shared/components/Pagination.jsx'
import { useToast } from '../../shared/toast/useToast.js'
import { getErrorMessage } from '../../shared/utils/errors.js'
import BookingModal from './BookingModal.jsx'
import ReviewSlotCard from './ReviewSlotCard.jsx'

function TimelineSkeleton() {
  return (
    <div className="review-slot-list" aria-hidden="true">
      {[0, 1, 2].map((item) => (
        <div className="review-slot-card review-slot-card--loading surface" key={item}>
          <div className="skeleton skeleton--wide" />
          <div className="skeleton skeleton--short" />
        </div>
      ))}
    </div>
  )
}

function ReviewSlotTimeline() {
  const { showToast } = useToast()
  const [reviewSlots, setReviewSlots] = useState([])
  const [pagination, setPagination] = useState({ page: 1, pageSize: 6, totalItems: 0, totalPages: 1 })
  const [selectedReviewSlot, setSelectedReviewSlot] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isBooking, setIsBooking] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  const retry = useCallback(() => {
    setReloadKey((current) => current + 1)
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    async function loadReviewSlots() {
      setIsLoading(true)
      setErrorMessage('')

      try {
        const result = await getPublicReviewSlots({
          page: pagination.page,
          signal: controller.signal,
        })
        setReviewSlots(result.reviewSlots)
        setPagination(result.pagination)
      } catch (error) {
        if (error.name !== 'AbortError') {
          setErrorMessage(getErrorMessage(error, 'Unable to load review availability.'))
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    loadReviewSlots()

    return () => controller.abort()
  }, [pagination.page, reloadKey])

  function openBooking(reviewSlot) {
    setSelectedReviewSlot(reviewSlot)
  }

  function closeBooking() {
    if (!isBooking) {
      setSelectedReviewSlot(null)
    }
  }

  async function handleBooking(booking) {
    if (!selectedReviewSlot) return

    setIsBooking(true)

    try {
      const updatedReviewSlot = await bookReviewSlot(selectedReviewSlot.uuid, booking)

      setReviewSlots((current) => current.map((reviewSlot) => (
        reviewSlot.uuid === updatedReviewSlot.uuid ? updatedReviewSlot : reviewSlot
      )))

      setSelectedReviewSlot(null)
      showToast('Review session booked successfully.', { variant: 'success' })
    } catch (error) {
      if (error.code === 'slot_already_booked') {
        setSelectedReviewSlot(null)
        retry()
        showToast('That slot was just booked by someone else.', { variant: 'warning' })
        return
      }

      if (error.code === 'review_slot_gone') {
        setSelectedReviewSlot(null)
        retry()
        showToast('That slot has already started or expired.', { variant: 'warning' })
        return
      }

      throw error
    } finally {
      setIsBooking(false)
    }
  }

  if (isLoading) {
    return (
      <section aria-label="Loading review availability" aria-busy="true">
        <TimelineSkeleton />
      </section>
    )
  }

  if (errorMessage) {
    return (
      <FeedbackState
        eyebrow="Unable to load availability"
        title="Slots could not be loaded."
        message={errorMessage}
        actionLabel="Try again"
        onAction={retry}
        role="alert"
      />
    )
  }

  if (pagination.totalItems === 0) {
    return (
      <FeedbackState
        eyebrow="No active slots"
        title="No review time is available right now."
        message="Check back after the host publishes new code-review availability."
      />
    )
  }

  return (
    <>
      <section className="review-slot-list" aria-label="Slot timeline">
        {reviewSlots.map((reviewSlot) => (
          <ReviewSlotCard
            key={reviewSlot.uuid}
            reviewSlot={reviewSlot}
            onBook={openBooking}
          />
        ))}
      </section>

      <Pagination
        page={pagination.page}
        pageSize={pagination.pageSize}
        totalPages={pagination.totalPages}
        totalItems={pagination.totalItems}
        itemLabel="slots"
        onPageChange={(page) => setPagination((current) => ({ ...current, page }))}
      />

      <BookingModal
        reviewSlot={selectedReviewSlot}
        open={Boolean(selectedReviewSlot)}
        onClose={closeBooking}
        onSubmit={handleBooking}
        submitting={isBooking}
      />
    </>
  )
}

export default ReviewSlotTimeline
