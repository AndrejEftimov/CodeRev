import { useState } from 'react'
import Button from './Button.jsx'
import Modal from './Modal.jsx'
import { getErrorMessage } from '../utils/errors.js'

function ConfirmModal({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'danger',
  onConfirm,
  onCancel,
}) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  async function handleConfirm() {
    setIsSubmitting(true)
    setErrorMessage('')

    try {
      await onConfirm()
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onCancel}
      title={title}
      size="sm"
      busy={isSubmitting}
      footer={(
        <>
          <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>
            {cancelLabel}
          </Button>
          <Button variant={variant} onClick={handleConfirm} loading={isSubmitting}>
            {confirmLabel}
          </Button>
        </>
      )}
    >
      <p>{message}</p>
      {errorMessage && <p className="form-error-summary" role="alert">{errorMessage}</p>}
    </Modal>
  )
}

export default ConfirmModal
