import FeedbackState from '../../shared/components/FeedbackState.jsx'
import HostReviewSlotCard from './HostReviewSlotCard.jsx'

function SlotGroup({ title, status, reviewSlots, onDelete, onViewDetails }) {
  return (
    <section className="host-slot-group" aria-labelledby={`host-${title.toLowerCase()}-title`}>
      <div className={`host-slot-group__heading host-slot-group__heading--${status}`}>
        <h2 id={`host-${title.toLowerCase()}-title`}>
          {title}
          <span className="host-slot-group__count">{reviewSlots.length}</span>
        </h2>
      </div>

      {reviewSlots.length > 0 ? (
        <div className="host-slot-stack">
          {reviewSlots.map((reviewSlot) => (
            <HostReviewSlotCard
              key={reviewSlot.uuid}
              reviewSlot={reviewSlot}
              onDelete={onDelete}
              onViewDetails={onViewDetails}
            />
          ))}
        </div>
      ) : (
        <p className="host-slot-group__empty">No {title.toLowerCase()} slots on this page.</p>
      )}
    </section>
  )
}

function HostReviewSlotCollection({ reviewSlots, viewMode, onDelete, onViewDetails }) {
  if (reviewSlots.length === 0) {
    return (
      <FeedbackState
        eyebrow="No active slots"
        title="No review availability is published."
        message="Create a future slot to make review time available to booking developers."
      />
    )
  }

  if (viewMode === 'list') {
    return (
      <div className="host-slot-stack" aria-label="Host slots">
        {reviewSlots.map((reviewSlot) => (
          <HostReviewSlotCard
            key={reviewSlot.uuid}
            reviewSlot={reviewSlot}
            onDelete={onDelete}
            onViewDetails={onViewDetails}
          />
        ))}
      </div>
    )
  }

  const availableSlots = reviewSlots.filter((reviewSlot) => !reviewSlot.booking)
  const takenSlots = reviewSlots.filter((reviewSlot) => Boolean(reviewSlot.booking))

  if (viewMode === 'columns') {
    return (
      <div className="host-slot-columns">
        <SlotGroup title="Available" status="available" reviewSlots={availableSlots} onDelete={onDelete} onViewDetails={onViewDetails} />
        <SlotGroup title="Taken" status="taken" reviewSlots={takenSlots} onDelete={onDelete} onViewDetails={onViewDetails} />
      </div>
    )
  }

  return (
    <div className="host-slot-sections">
      <SlotGroup title="Available" status="available" reviewSlots={availableSlots} onDelete={onDelete} onViewDetails={onViewDetails} />
      <SlotGroup title="Taken" status="taken" reviewSlots={takenSlots} onDelete={onDelete} onViewDetails={onViewDetails} />
    </div>
  )
}

export default HostReviewSlotCollection
