/**
 * Format an API local date value (YYYY-MM-DD) without applying a timezone shift.
 */
export function formatLocalDate(dateValue) {
  const [year, month, day] = dateValue.split('-').map(Number)
  const date = new Date(year, month - 1, day)

  const weekday = new Intl.DateTimeFormat('en-GB', { weekday: 'short' }).format(date)
  const monthLabel = new Intl.DateTimeFormat('en-GB', { month: 'short' }).format(date)

  return `${weekday}, ${day} ${monthLabel}, ${year}`
}

/**
 * Format an HH:MM API wall-clock value using a fixed 24-hour presentation.
 */
export function formatLocalTime(timeValue) {
  const [hours, minutes] = timeValue.split(':').map(Number)
  const date = new Date(2000, 0, 1, hours, minutes)

  return new Intl.DateTimeFormat('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date)
}

export function formatTimeRange(startTime, endTime) {
  return `${formatLocalTime(startTime)}–${formatLocalTime(endTime)}`
}


/**
 * Convert a local Date into the API date transport format without a UTC shift.
 */
export function toLocalDateValue(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return ''
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

/**
 * Parse an API/local date value (YYYY-MM-DD) as a browser-local calendar date.
 */
export function fromLocalDateValue(dateValue) {
  if (!dateValue) return null

  const [year, month, day] = dateValue.split('-').map(Number)
  const date = new Date(year, month - 1, day)

  return Number.isNaN(date.getTime()) ? null : date
}

/**
 * Convert a local Date into an HH:MM wall-clock value.
 */
export function toLocalTimeValue(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return ''
  }

  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${hours}:${minutes}`
}

/**
 * Parse an HH:MM wall-clock value into a local Date suitable for time-only pickers.
 */
export function fromLocalTimeValue(timeValue) {
  if (!timeValue) return null

  const [hours, minutes] = timeValue.split(':').map(Number)

  if (!Number.isInteger(hours) || !Number.isInteger(minutes)) {
    return null
  }

  return new Date(2000, 0, 1, hours, minutes, 0, 0)
}

/**
 * Build a future picker value from the current browser/system clock.
 */
export function getNextLocalTimeInterval(intervalMinutes = 5) {
  const now = new Date()
  const rounded = new Date(now)

  rounded.setSeconds(0, 0)

  const remainder = rounded.getMinutes() % intervalMinutes
  const minutesToAdd = remainder === 0 ? intervalMinutes : intervalMinutes - remainder
  rounded.setMinutes(rounded.getMinutes() + minutesToAdd)

  return rounded
}
