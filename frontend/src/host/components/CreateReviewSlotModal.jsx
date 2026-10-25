import Modal from '../../shared/components/Modal.jsx'
import ReviewSlotForm from './ReviewSlotForm.jsx'

function CreateReviewSlotModal({ open, onClose, onSubmit, submitting }) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Create slot"
      description="Publish a focused code-review window for booking developers."
      size="lg"
      className="host-create-modal"
      busy={submitting}
    >
      <ReviewSlotForm
        onSubmit={onSubmit}
        onCancel={onClose}
        submitting={submitting}
      />
    </Modal>
  )
}

export default CreateReviewSlotModal
