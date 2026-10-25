import { apiRequest } from '../../shared/api/client.js'

const PUBLIC_PAGE_SIZE = 6

export async function getPublicReviewSlots({ page = 1, signal } = {}) {
  const query = new URLSearchParams({
    page: String(page),
    pageSize: String(PUBLIC_PAGE_SIZE),
  })
  const payload = await apiRequest(`/api/review-slots/?${query}`, { signal })

  return {
    reviewSlots: payload.reviewSlots,
    pagination: payload.pagination,
  }
}

export async function bookReviewSlot(reviewSlotUuid, booking) {
  const payload = await apiRequest(`/api/review-slots/${reviewSlotUuid}/book/`, {
    method: 'POST',
    body: JSON.stringify(booking),
  })

  return payload.reviewSlot
}
