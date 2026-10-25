import { useState } from 'react'
import Button from '../../shared/components/Button.jsx'
import Input from '../../shared/components/Input.jsx'
import TextArea from '../../shared/components/TextArea.jsx'
import { getFirstFieldError, getErrorMessage } from '../../shared/utils/errors.js'
import { isBlank, isValidEmail, isWithinMaxLength } from '../../shared/utils/validation.js'

const INITIAL_VALUES = {
  name: '',
  email: '',
  reviewTopic: '',
  reviewDescription: '',
}

function validate(values) {
  const errors = {}

  if (isBlank(values.name)) {
    errors.name = 'Enter your name.'
  } else if (!isWithinMaxLength(values.name, 120)) {
    errors.name = 'Name must be 120 characters or fewer.'
  }

  if (isBlank(values.email)) {
    errors.email = 'Enter your email address.'
  } else if (!isValidEmail(values.email)) {
    errors.email = 'Enter a valid email address.'
  }

  if (isBlank(values.reviewTopic)) {
    errors.reviewTopic = 'Enter a review topic.'
  } else if (!isWithinMaxLength(values.reviewTopic, 160)) {
    errors.reviewTopic = 'Review topic must be 160 characters or fewer.'
  }

  return errors
}

function BookingForm({ onSubmit, onCancel, submitting = false }) {
  const [values, setValues] = useState(INITIAL_VALUES)
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setValues((current) => ({ ...current, [name]: value }))
    setFieldErrors((current) => ({ ...current, [name]: '' }))
    setFormError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const clientErrors = validate(values)
    if (Object.keys(clientErrors).length > 0) {
      setFieldErrors(clientErrors)
      return
    }

    setFieldErrors({})
    setFormError('')

    try {
      await onSubmit({
        name: values.name.trim(),
        email: values.email.trim(),
        reviewTopic: values.reviewTopic.trim(),
        reviewDescription: values.reviewDescription.trim(),
      })
    } catch (error) {
      if (error.code === 'validation_error') {
        setFieldErrors(error.fields ?? {})
        setFormError(error.message || 'Some booking details need attention.')
        return
      }

      if (error.code === 'slot_already_booked' || error.code === 'review_slot_gone') {
        throw error
      }

      setFormError(getErrorMessage(error, 'Unable to book this review slot. Please try again.'))
    }
  }

  return (
    <form className="booking-form" onSubmit={handleSubmit} noValidate>
      <div className="booking-form__fields">
        <Input
          id="booking-name"
          name="name"
          label="Name"
          value={values.name}
          onChange={handleChange}
          error={getFirstFieldError(fieldErrors, 'name') || fieldErrors.name || ''}
          autoComplete="name"
          maxLength={120}
          required
          disabled={submitting}
        />

        <Input
          id="booking-email"
          name="email"
          label="Email"
          type="email"
          value={values.email}
          onChange={handleChange}
          error={getFirstFieldError(fieldErrors, 'email') || fieldErrors.email || ''}
          autoComplete="email"
          required
          disabled={submitting}
        />

        <Input
          id="booking-topic"
          name="reviewTopic"
          label="Review topic"
          value={values.reviewTopic}
          onChange={handleChange}
          error={getFirstFieldError(fieldErrors, 'reviewTopic') || fieldErrors.reviewTopic || ''}
          maxLength={160}
          placeholder="e.g. Authentication flow"
          required
          disabled={submitting}
        />

        <TextArea
          id="booking-description"
          name="reviewDescription"
          label="Review context"
          value={values.reviewDescription}
          onChange={handleChange}
          error={getFirstFieldError(fieldErrors, 'reviewDescription')}
          hint="Optional — add code, architecture, bug, or implementation context that will help the review."
          rows={5}
          disabled={submitting}
        />
      </div>

      {formError && <p className="form-error-summary" role="alert">{formError}</p>}

      <div className="booking-form__actions">
        <Button variant="secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>
        <Button type="submit" loading={submitting}>
          Confirm booking
        </Button>
      </div>
    </form>
  )
}

export default BookingForm
