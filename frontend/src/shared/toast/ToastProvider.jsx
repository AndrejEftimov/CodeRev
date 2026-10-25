import { useCallback, useMemo, useState } from 'react'
import { ToastContext } from './ToastContext.js'

let nextToastId = 1

function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismissToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const showToast = useCallback((message, options = {}) => {
    const id = nextToastId++
    const toast = {
      id,
      message,
      variant: options.variant ?? 'success',
    }

    setToasts((current) => [...current, toast])

    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== id))
    }, options.duration ?? 4000)

    return id
  }, [])

  const value = useMemo(() => ({ showToast, dismissToast }), [showToast, dismissToast])

  return (
    <ToastContext.Provider value={value}>
      {children}

      <div className="toast-region" aria-live="polite" aria-relevant="additions removals">
        {toasts.map((toast) => (
          <div className={`toast toast--${toast.variant}`} key={toast.id} role="status">
            <span>{toast.message}</span>
            <button
              className="toast__close"
              type="button"
              onClick={() => dismissToast(toast.id)}
              aria-label="Dismiss notification"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export default ToastProvider
