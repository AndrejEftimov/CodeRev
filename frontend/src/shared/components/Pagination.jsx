import { ChevronLeft, ChevronRight } from 'lucide-react'
import Button from './Button.jsx'

function Pagination({
  page,
  pageSize,
  totalPages,
  totalItems,
  onPageChange,
  itemLabel = 'items',
}) {
  if (totalItems <= 0) return null

  const rangeStart = ((page - 1) * pageSize) + 1
  const rangeEnd = Math.min(page * pageSize, totalItems)
  const hasMultiplePages = totalPages > 1

  return (
    <nav className="pagination" aria-label={`${itemLabel} pagination`}>
      <div className="pagination__summary">
        <p className="pagination__range">
          Showing <strong>{rangeStart}–{rangeEnd}</strong> of <strong>{totalItems}</strong> {itemLabel}
        </p>
        <p className="pagination__page">
          Page <strong>{page}</strong> of <strong>{totalPages}</strong>
        </p>
      </div>

      {hasMultiplePages && (
        <div className="pagination__actions">
          <Button
            variant="secondary"
            className="pagination__button"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft size={16} aria-hidden="true" />
            Previous
          </Button>

          <Button
            variant="secondary"
            className="pagination__button"
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
          >
            Next
            <ChevronRight size={16} aria-hidden="true" />
          </Button>
        </div>
      )}
    </nav>
  )
}

export default Pagination
