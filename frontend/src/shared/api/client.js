const DEFAULT_HEADERS = {
  Accept: 'application/json',
  'Content-Type': 'application/json',
}

const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS', 'TRACE'])

let csrfToken = null
let csrfTokenRequest = null

export class ApiError extends Error {
  constructor({ code = 'request_failed', message, fields = {}, status = 0 }) {
    super(message || 'Something went wrong while communicating with the server.')
    this.name = 'ApiError'
    this.code = code
    this.fields = fields
    this.status = status
  }
}

async function requestCsrfToken() {
  if (csrfToken) {
    return csrfToken
  }

  if (!csrfTokenRequest) {
    csrfTokenRequest = fetch('/api/csrf/', {
      method: 'GET',
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
      },
    })
      .then(async (response) => {
        const payload = await response.json().catch(() => null)

        if (!response.ok || !payload?.csrfToken) {
          throw new ApiError({
            code: 'csrf_token_failed',
            message: 'Unable to prepare a secure request. Please try again.',
            status: response.status,
          })
        }

        csrfToken = payload.csrfToken
        return csrfToken
      })
      .finally(() => {
        csrfTokenRequest = null
      })
  }

  return csrfTokenRequest
}

export async function apiRequest(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = {
    ...DEFAULT_HEADERS,
    ...options.headers,
  }

  if (!SAFE_METHODS.has(method)) {
    headers['X-CSRFToken'] = await requestCsrfToken()
  }

  let response

  try {
    response = await fetch(path, {
      ...options,
      method,
      credentials: 'same-origin',
      headers,
    })
  } catch (error) {
    if (error.name === 'AbortError') {
      throw error
    }

    if (error instanceof ApiError) {
      throw error
    }

    throw new ApiError({
      code: 'network_error',
      message: 'Unable to reach the server. Please try again.',
    })
  }

  if (response.status === 204) {
    return null
  }

  const payload = await response.json().catch(() => null)

  if (!response.ok) {
    const error = payload?.error ?? {}

    throw new ApiError({
      code: error.code,
      message: error.message,
      fields: error.fields,
      status: response.status,
    })
  }

  return payload
}
