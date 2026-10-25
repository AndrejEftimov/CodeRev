import { Clock3 } from 'lucide-react'
import PickerTrigger from './PickerTrigger.jsx'
import ReactDatePicker from 'react-datepicker'
import {
  fromLocalTimeValue,
  toLocalTimeValue,
} from '../utils/dateTime.js'

function TimePicker({
  id,
  name,
  value,
  onChange,
  disabled = false,
  required = false,
  intervalMinutes = 5,
  className = '',
  ...inputProps
}) {
  const selectedTime = fromLocalTimeValue(value)

  return (
    <ReactDatePicker
      {...inputProps}
      id={id}
      name={name}
      selected={selectedTime}
      onChange={(date) => onChange(toLocalTimeValue(date))}
      showTimeSelect
      showTimeSelectOnly
      timeIntervals={intervalMinutes}
      timeCaption="Time"
      timeFormat="HH:mm"
      dateFormat="HH:mm"
      placeholderText="Select time"
      disabled={disabled}
      required={required}
      wrapperClassName="picker-input picker-input--time"
      customInput={
        <PickerTrigger
          icon={Clock3}
          displayValue={value}
          placeholder="Select time"
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

export default TimePicker
