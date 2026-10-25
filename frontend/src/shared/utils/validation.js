export function isBlank(value) {
  return typeof value !== 'string' || value.trim().length === 0
}

export function isValidEmail(value) {
  if (typeof value !== 'string') return false

  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())
}

export function isWithinMaxLength(value, maxLength) {
  return typeof value === 'string' && value.trim().length <= maxLength
}
