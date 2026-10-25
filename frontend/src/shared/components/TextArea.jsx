import FormField from './FormField.jsx'

function TextArea({ label, error, hint, required = false, id, className = '', rows = 4, ...props }) {
  return (
    <FormField id={id} label={label} error={error} hint={hint} required={required}>
      {(fieldProps) => (
        <textarea
          {...fieldProps}
          {...props}
          className={`form-control form-control--textarea ${className}`.trim()}
          required={required}
          rows={rows}
        />
      )}
    </FormField>
  )
}

export default TextArea
