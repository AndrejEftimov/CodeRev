import FormField from './FormField.jsx'

function Select({ label, error, hint, required = false, id, className = '', children, ...props }) {
  return (
    <FormField id={id} label={label} error={error} hint={hint} required={required}>
      {(fieldProps) => (
        <select
          {...fieldProps}
          {...props}
          className={`form-control form-control--select ${className}`.trim()}
          required={required}
        >
          {children}
        </select>
      )}
    </FormField>
  )
}

export default Select
