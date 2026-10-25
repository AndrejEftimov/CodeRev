import { Columns3, List, Rows3 } from 'lucide-react'

const VIEW_MODES = [
  { value: 'list', label: 'List', icon: List },
  { value: 'columns', label: 'Columns', icon: Columns3 },
  { value: 'sections', label: 'Sections', icon: Rows3 },
]

function HostViewSwitcher({ value, onChange }) {
  return (
    <div className="host-view-switcher" role="group" aria-label="Slot view">
      {VIEW_MODES.map((viewMode) => {
        const ViewIcon = viewMode.icon

        return (
          <button
            key={viewMode.value}
            className={`host-view-switcher__button${value === viewMode.value ? ' host-view-switcher__button--active' : ''}`}
            type="button"
            aria-pressed={value === viewMode.value}
            onClick={() => onChange(viewMode.value)}
          >
            <ViewIcon size={14} aria-hidden="true" />
            <span>{viewMode.label}</span>
          </button>
        )
      })}
    </div>
  )
}

export default HostViewSwitcher
