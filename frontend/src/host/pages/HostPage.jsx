import { Plus } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { createHostReviewSlot, deleteHostReviewSlot, getHostReviewSlots } from '../api/reviewSlots.js'
import BookingDetailsModal from '../components/BookingDetailsModal.jsx'
import CreateReviewSlotModal from '../components/CreateReviewSlotModal.jsx'
import HostReviewSlotCollection from '../components/HostReviewSlotCollection.jsx'
import HostViewSwitcher from '../components/HostViewSwitcher.jsx'
import Button from '../../shared/components/Button.jsx'
import ConfirmModal from '../../shared/components/ConfirmModal.jsx'
import FeedbackState from '../../shared/components/FeedbackState.jsx'
import Pagination from '../../shared/components/Pagination.jsx'
import { useToast } from '../../shared/toast/useToast.js'
import { getErrorMessage } from '../../shared/utils/errors.js'

function HostTimelineSkeleton() {
  return (
    <div className="host-slot-stack" aria-hidden="true">
      {[0, 1, 2].map((item) => (
        <div className="host-review-slot-card host-review-slot-card--loading surface" key={item}>
          <div className="skeleton skeleton--wide" />
          <div className="skeleton skeleton--short" />
        </div>
      ))}
    </div>
  )
}

function HostPage() {
  const { showToast } = useToast()
  const [reviewSlots, setReviewSlots] = useState([])
  const [pagination, setPagination] = useState({ page: 1, pageSize: 8, totalItems: 0, totalPages: 1 })
  const [viewMode, setViewMode] = useState('list')
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [selectedBookingSlot, setSelectedBookingSlot] = useState(null)
  const [pendingDelete, setPendingDelete] = useState(null)
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
        const result = await getHostReviewSlots({
          page: pagination.page,
          signal: controller.signal,
        })
        setReviewSlots(result.reviewSlots)
        setPagination(result.pagination)
      } catch (error) {
        if (error.name !== 'AbortError') {
          setErrorMessage(getErrorMessage(error, 'Unable to load host slots.'))
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

  function closeCreate() {
    if (!isCreating) {
      setIsCreateOpen(false)
    }
  }

  async function handleCreate(values) {
    setIsCreating(true)

    try {
      await createHostReviewSlot(values)
      setIsCreateOpen(false)
      retry()
      showToast('Slot created successfully.', { variant: 'success' })
    } catch (error) {
      if (error.code === 'review_slot_overlap') {
        showToast('That slot overlaps existing availability.', { variant: 'warning' })
      }

      throw error
    } finally {
      setIsCreating(false)
    }
  }

  async function handleDelete() {
    if (!pendingDelete) return

    const reviewSlot = pendingDelete
    await deleteHostReviewSlot(reviewSlot.uuid)

    setPendingDelete(null)

    if (reviewSlots.length === 1 && pagination.page > 1) {
      setPagination((current) => ({ ...current, page: current.page - 1 }))
    } else {
      retry()
    }

    showToast(
      reviewSlot.status === 'taken'
        ? 'Booked review cancelled and removed.'
        : 'Slot deleted.',
      { variant: 'success' },
    )
  }

  const deleteTitle = pendingDelete?.status === 'taken'
    ? 'Cancel booked review?'
    : 'Delete slot?'

  const deleteMessage = pendingDelete?.status === 'taken'
    ? 'This permanently removes the slot and its booking details. The scheduled review will be cancelled and cannot be restored.'
    : 'This permanently removes the available slot. This action cannot be undone.'

  return (
    <section className="page-section" aria-labelledby="host-page-title">
      <div className="host-page-header">
        <div className="page-heading">
          <p className="eyebrow">Host workspace</p>
          <h1 id="host-page-title">Manage review availability.</h1>
          <p className="page-heading__description">
            Publish slots, inspect private booking details, and manage active review sessions.
          </p>
        </div>

        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus size={16} aria-hidden="true" />
          Create slot
        </Button>
      </div>

      <div className="host-toolbar">
        <div>
          <span className="host-toolbar__label">Active slots</span>
          <strong>{pagination.totalItems}</strong>
        </div>
        <HostViewSwitcher value={viewMode} onChange={setViewMode} />
      </div>

      {isLoading ? (
        <section aria-label="Loading host slots" aria-busy="true">
          <HostTimelineSkeleton />
        </section>
      ) : errorMessage ? (
        <FeedbackState
          eyebrow="Unable to load host workspace"
          title="Slots could not be loaded."
          message={errorMessage}
          actionLabel="Try again"
          onAction={retry}
          role="alert"
        />
      ) : (
        <>
          <HostReviewSlotCollection
            reviewSlots={reviewSlots}
            viewMode={viewMode}
            onDelete={setPendingDelete}
            onViewDetails={setSelectedBookingSlot}
          />

          <Pagination
            page={pagination.page}
            pageSize={pagination.pageSize}
            totalPages={pagination.totalPages}
            totalItems={pagination.totalItems}
            itemLabel="slots"
            onPageChange={(page) => setPagination((current) => ({ ...current, page }))}
          />
        </>
      )}

      <CreateReviewSlotModal
        open={isCreateOpen}
        onClose={closeCreate}
        onSubmit={handleCreate}
        submitting={isCreating}
      />

      <BookingDetailsModal
        reviewSlot={selectedBookingSlot}
        open={Boolean(selectedBookingSlot)}
        onClose={() => setSelectedBookingSlot(null)}
      />

      <ConfirmModal
        key={pendingDelete?.uuid ?? 'delete-review-slot'}
        open={Boolean(pendingDelete)}
        title={deleteTitle}
        message={deleteMessage}
        confirmLabel={pendingDelete?.status === 'taken' ? 'Cancel and delete' : 'Delete slot'}
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setPendingDelete(null)}
      />
    </section>
  )
}

export default HostPage
