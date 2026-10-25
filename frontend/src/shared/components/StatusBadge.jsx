import { CircleCheck, Clock3, LockKeyhole } from 'lucide-react'

const STATUS_CONFIG = {
  available: {
    label: 'Available',
    icon: CircleCheck,
  },
  taken: {
    label: 'Taken',
    icon: LockKeyhole,
  },
  started: {
    label: 'In progress',
    icon: Clock3,
  },
}

function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status]
  const label = config?.label ?? status
  const Icon = config?.icon

  return (
    <span className={`status-badge status-badge--${status}`}>
      {Icon && <Icon size={13} strokeWidth={2} aria-hidden="true" />}
      {label}
    </span>
  )
}

export default StatusBadge
