function FormField({ id, label, error = '', hint = '', required = false, children }) {
  const errorId = error ? `${id}-error` : undefined
  const hintId = hint && !error ? `${id}-hint` : undefined

  return (
    <div className="form-field">
      <label className="form-field__label" htmlFor={id}>
        {label}
        {required && <span className="form-field__required" aria-hidden="true"> *</span>}
      </label>

      {children({
        id,
        'aria-invalid': error ? true : undefined,
        'aria-describedby': errorId ?? hintId,
      })}

      {error ? (
        <p className="form-field__error" id={errorId} role="alert">{error}</p>
      ) : hint ? (
        <p className="form-field__hint" id={hintId}>{hint}</p>
      ) : null}
    </div>
  )
}

export default FormField
