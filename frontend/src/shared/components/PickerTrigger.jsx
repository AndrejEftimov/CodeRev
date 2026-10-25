import { forwardRef } from 'react'

// Keep the icon and label in normal layout flow so they cannot overlap.
const PickerTrigger = forwardRef(function PickerTrigger(
  { icon: Icon, displayValue, placeholder, className = '', ...props },
  ref,
) {
  return (
    <button
      {...props}
      ref={ref}
      type="button"
      className={['form-control', 'picker-input__trigger', className].filter(Boolean).join(' ')}
    >
      <Icon className="picker-input__icon" size={17} strokeWidth={1.9} aria-hidden="true" />
      <span className="picker-input__value">
        {displayValue || placeholder}
      </span>
    </button>
  )
})

export default PickerTrigger
