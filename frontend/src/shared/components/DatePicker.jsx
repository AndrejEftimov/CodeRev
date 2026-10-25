import { CalendarDays } from 'lucide-react'
import PickerTrigger from './PickerTrigger.jsx'
import ReactDatePicker from 'react-datepicker'
import {
  fromLocalDateValue,
  toLocalDateValue,
} from '../utils/dateTime.js'

function DatePicker({
  id,
  name,
  value,
  onChange,
  disabled = false,
  required = false,
  minDate = null,
  className = '',
  ...inputProps
}) {
  const selectedDate = fromLocalDateValue(value)

  return (
    <ReactDatePicker
      {...inputProps}
      id={id}
      name={name}
      selected={selectedDate}
      onChange={(date) => onChange(toLocalDateValue(date))}
      minDate={minDate}
      dateFormat="dd MMM yyyy"
      placeholderText="Select date"
      disabled={disabled}
      required={required}
      wrapperClassName="picker-input"
      customInput={
        <PickerTrigger
          icon={CalendarDays}
          displayValue={selectedDate ? new Intl.DateTimeFormat('en-GB', {
            day: '2-digit', month: 'short', year: 'numeric',
          }).format(selectedDate) : ''}
          placeholder="Select date"
          className={className}
        />
      }
      portalId="coderev-datepicker-portal"
      popperClassName="coderev-datepicker-popper"
      popperPlacement="bottom-start"
      showPopperArrow={false}
    />
  )
}

export default DatePicker
