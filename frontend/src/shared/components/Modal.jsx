import { useEffect, useId, useRef } from 'react'
import { X } from 'lucide-react'
import { createPortal } from 'react-dom'

function Modal({
  open,
  onClose,
  title,
  description = '',
  children,
  footer = null,
  size = 'md',
  busy = false,
  className = '',
}) {
  const titleId = useId()
  const descriptionId = useId()
  const panelRef = useRef(null)
  const previousFocusRef = useRef(null)

  useEffect(() => {
    if (!open) return undefined

    previousFocusRef.current = document.activeElement
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    requestAnimationFrame(() => panelRef.current?.focus())

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !busy) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow

      if (previousFocusRef.current instanceof HTMLElement) {
        previousFocusRef.current.focus()
      }
    }
  }, [open, busy, onClose])

  if (!open) return null

  return createPortal(
    <div className="modal" role="presentation">
      <button
        className="modal__backdrop"
        type="button"
        aria-label="Close dialog"
        disabled={busy}
        onClick={onClose}
      />

      <section
        className={[
          'modal__panel',
          `modal__panel--${size}`,
          className,
        ].filter(Boolean).join(' ')}
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        tabIndex={-1}
      >
        <header className="modal__header">
          <div>
            <h2 id={titleId}>{title}</h2>
            {description && <p id={descriptionId}>{description}</p>}
          </div>

          <button
            className="icon-button"
            type="button"
            onClick={onClose}
            disabled={busy}
            aria-label="Close dialog"
          >
            <X size={24} strokeWidth={2} aria-hidden="true" />
          </button>
        </header>

        <div className="modal__body">{children}</div>

        {footer && <footer className="modal__footer">{footer}</footer>}
      </section>
    </div>,
    document.body,
  )
}

export default Modal
