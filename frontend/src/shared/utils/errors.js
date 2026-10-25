export function getFirstFieldError(fieldErrors, fieldName) {
  const messages = fieldErrors?.[fieldName]
  return Array.isArray(messages) ? messages[0] ?? '' : ''
}

export function getErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  return error instanceof Error && error.message ? error.message : fallback
}
