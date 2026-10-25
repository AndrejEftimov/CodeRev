function Button({
  children,
  className = '',
  variant = 'primary',
  loading = false,
  disabled = false,
  type = 'button',
  ...props
}) {
  const classes = ['button', `button--${variant}`, className].filter(Boolean).join(' ')

  return (
    <button
      className={classes}
      type={type}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading && <span className="button__spinner" aria-hidden="true" />}
      <span className="button__content">{children}</span>
    </button>
  )
}

export default Button
