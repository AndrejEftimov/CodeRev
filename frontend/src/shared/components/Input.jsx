import FormField from './FormField.jsx'

function Input({ label, error, hint, required = false, id, className = '', ...props }) {
  return (
    <FormField id={id} label={label} error={error} hint={hint} required={required}>
      {(fieldProps) => (
        <input
          {...fieldProps}
          {...props}
          className={`form-control ${className}`.trim()}
          required={required}
        />
      )}
    </FormField>
  )
}

export default Input
