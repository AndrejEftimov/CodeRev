import { CalendarDays, Clock3, Timer } from 'lucide-react'
import { useState } from 'react'
import Button from '../../shared/components/Button.jsx'
import DatePicker from '../../shared/components/DatePicker.jsx'
import FormField from '../../shared/components/FormField.jsx'
import TimePicker from '../../shared/components/TimePicker.jsx'
import {
  getNextLocalTimeInterval,
  toLocalDateValue,
  toLocalTimeValue,
} from '../../shared/utils/dateTime.js'
import { getFirstFieldError, getErrorMessage } from '../../shared/utils/errors.js'
import { addMinutesToTime, getDurationMinutes } from '../../shared/utils/time.js'

const DURATION_PRESETS = [15, 30, 45, 60]

function createInitialValues() {
  const start = getNextLocalTimeInterval(5)
  const startDate = toLocalDateValue(start)
  const startTime = toLocalTimeValue(start)

  return {
    startDate,
    startTime,
    endTime: addMinutesToTime(startTime, 30),
    durationMinutes: '30',
  }
}

function validate(values) {
  const errors = {}
  const duration = Number(values.durationMinutes)

  if (!values.startDate) {
    errors.startDate = 'Choose a date.'
  }

  if (!values.startTime) {
    errors.startTime = 'Choose a start time.'
  }

  if (!values.endTime) {
    errors.endTime = 'Choose an end time.'
  }

  if (!Number.isInteger(duration) || duration <= 0) {
    errors.durationMinutes = 'Duration must be a positive whole number of minutes.'
  }

  if (
    values.startTime
    && values.endTime
    && getDurationMinutes(values.startTime, values.endTime) === null
  ) {
    errors.endTime = 'End time must be later than start time on the same day.'
  }

  if (values.startDate && values.startTime) {
    const start = new Date(`${values.startDate}T${values.startTime}`)

    if (!Number.isNaN(start.getTime()) && start <= new Date()) {
      errors.startTime = 'Start time must be in the future.'
    }
  }

  return errors
}

function SchedulePickerField({
  id,
  label,
  error,
  required = false,
  children,
}) {
  return (
    <FormField id={id} label={label} error={error} required={required}>
      {(fieldProps) => children(fieldProps)}
    </FormField>
  )
}

function ScheduleNumberInput({
  id,
  label,
  error,
  suffix = '',
  required = false,
  ...props
}) {
  return (
    <FormField id={id} label={label} error={error} required={required}>
      {(fieldProps) => (
        <div className="host-schedule-input">
          <Timer
            className="host-schedule-input__icon"
            size={16}
            strokeWidth={1.9}
            aria-hidden="true"
          />

          <input
            {...fieldProps}
            {...props}
            className="form-control host-schedule-input__control"
            required={required}
          />

          {suffix && (
            <span className="host-schedule-input__suffix">{suffix}</span>
          )}
        </div>
      )}
    </FormField>
  )
}

function ReviewSlotForm({ onSubmit, onCancel, submitting = false }) {
  const [values, setValues] = useState(createInitialValues)
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')

  function updateValue(name, value) {
    setValues((current) => ({ ...current, [name]: value }))
    setFieldErrors((current) => ({ ...current, [name]: '' }))
    setFormError('')
  }

  function handleDateChange(startDate) {
    updateValue('startDate', startDate)
  }

  function handleStartTimeChange(startTime) {
    setValues((current) => ({
      ...current,
      startTime,
      endTime: addMinutesToTime(
        startTime,
        Number(current.durationMinutes),
      ),
    }))
    setFieldErrors((current) => ({
      ...current,
      startTime: '',
      endTime: '',
    }))
    setFormError('')
  }

  function setDuration(durationMinutes) {
    const durationValue = String(durationMinutes)

    setValues((current) => ({
      ...current,
      durationMinutes: durationValue,
      endTime:
        addMinutesToTime(current.startTime, Number(durationMinutes))
        || current.endTime,
    }))
    setFieldErrors((current) => ({
      ...current,
      durationMinutes: '',
      endTime: '',
    }))
    setFormError('')
  }

  function handleDurationChange(event) {
    setDuration(event.target.value)
  }

  function applyDurationPreset(durationMinutes) {
    setDuration(durationMinutes)
  }

  function handleEndTimeChange(endTime) {
    const durationMinutes = getDurationMinutes(values.startTime, endTime)

    setValues((current) => ({
      ...current,
      endTime,
      durationMinutes:
        durationMinutes === null
          ? current.durationMinutes
          : String(durationMinutes),
    }))
    setFieldErrors((current) => ({
      ...current,
      endTime: '',
      durationMinutes: '',
    }))
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
        startDate: values.startDate,
        startTime: values.startTime,
        endDate: values.startDate,
        endTime: values.endTime,
        durationMinutes: Number(values.durationMinutes),
      })
    } catch (error) {
      if (error.code === 'validation_error') {
        setFieldErrors(error.fields ?? {})
        setFormError(error.message || 'Some slot details need attention.')
        return
      }

      setFormError(
        getErrorMessage(
          error,
          'Unable to create this slot. Please try again.',
        ),
      )
    }
  }

  return (
    <form className="host-create-form" onSubmit={handleSubmit} noValidate>
      <div className="host-schedule-builder">
        <section className="host-schedule-panel host-schedule-panel--date">
          <div className="host-schedule-panel__heading">
            <CalendarDays size={18} strokeWidth={1.9} aria-hidden="true" />
            <span>Date</span>
          </div>

          <SchedulePickerField
            id="host-slot-date"
            label="Review date"
            error={
              getFirstFieldError(fieldErrors, 'startDate')
              || fieldErrors.startDate
              || ''
            }
            required
          >
            {(fieldProps) => (
              <DatePicker
                {...fieldProps}
                name="startDate"
                value={values.startDate}
                onChange={handleDateChange}
                minDate={new Date()}
                required
                disabled={submitting}
              />
            )}
          </SchedulePickerField>
        </section>

        <section className="host-schedule-panel host-schedule-panel--time">
          <div className="host-schedule-panel__heading">
            <Clock3 size={18} strokeWidth={1.9} aria-hidden="true" />
            <span>Time window</span>
          </div>

          <div className="host-schedule-time-grid">
            <SchedulePickerField
              id="host-slot-start-time"
              label="Start"
              error={
                getFirstFieldError(fieldErrors, 'startTime')
                || fieldErrors.startTime
                || ''
              }
              required
            >
              {(fieldProps) => (
                <TimePicker
                  {...fieldProps}
                  name="startTime"
                  value={values.startTime}
                  onChange={handleStartTimeChange}
                  required
                  disabled={submitting}
                />
              )}
            </SchedulePickerField>

            <SchedulePickerField
              id="host-slot-end-time"
              label="End"
              error={
                getFirstFieldError(fieldErrors, 'endTime')
                || fieldErrors.endTime
                || ''
              }
              required
            >
              {(fieldProps) => (
                <TimePicker
                  {...fieldProps}
                  name="endTime"
                  value={values.endTime}
                  onChange={handleEndTimeChange}
                  required
                  disabled={submitting || !values.startTime}
                />
              )}
            </SchedulePickerField>
          </div>
        </section>

        <section className="host-schedule-panel host-schedule-panel--duration">
          <div className="host-schedule-panel__heading">
            <Timer size={18} strokeWidth={1.9} aria-hidden="true" />
            <span>Duration</span>
          </div>

          <ScheduleNumberInput
            id="host-slot-duration"
            label="Minutes"
            suffix="min"
            name="durationMinutes"
            type="number"
            min="1"
            step="1"
            value={values.durationMinutes}
            onChange={handleDurationChange}
            error={
              getFirstFieldError(fieldErrors, 'durationMinutes')
              || fieldErrors.durationMinutes
              || ''
            }
            required
            disabled={submitting}
          />

          <div className="host-duration-presets" aria-label="Duration presets">
            <span>Quick select</span>

            <div>
              {DURATION_PRESETS.map((duration) => (
                <button
                  key={duration}
                  className={[
                    'host-duration-preset',
                    Number(values.durationMinutes) === duration
                      ? 'host-duration-preset--active'
                      : '',
                  ].filter(Boolean).join(' ')}
                  type="button"
                  onClick={() => applyDurationPreset(duration)}
                  disabled={submitting}
                >
                  {duration} min
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>

      {formError && (
        <p className="form-error-summary" role="alert">
          {formError}
        </p>
      )}

      <div className="host-create-form__actions">
        <Button variant="secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>

        <Button type="submit" loading={submitting}>
          Create slot
        </Button>
      </div>
    </form>
  )
}

export default ReviewSlotForm
