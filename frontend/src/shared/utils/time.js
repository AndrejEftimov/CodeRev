function parseTimeValue(timeValue) {
  const [hours, minutes] = timeValue.split(':').map(Number)

  if (!Number.isInteger(hours) || !Number.isInteger(minutes)) {
    return null
  }

  return (hours * 60) + minutes
}

export function addMinutesToTime(timeValue, minutesToAdd) {
  const startMinutes = parseTimeValue(timeValue)
  const duration = Number(minutesToAdd)

  if (startMinutes === null || !Number.isFinite(duration)) {
    return ''
  }

  const totalMinutes = startMinutes + duration

  if (totalMinutes < 0 || totalMinutes >= 24 * 60) {
    return ''
  }

  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

export function getDurationMinutes(startTime, endTime) {
  const startMinutes = parseTimeValue(startTime)
  const endMinutes = parseTimeValue(endTime)

  if (startMinutes === null || endMinutes === null || endMinutes <= startMinutes) {
    return null
  }

  return endMinutes - startMinutes
}
