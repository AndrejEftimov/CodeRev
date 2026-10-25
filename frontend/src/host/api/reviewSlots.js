import { apiRequest } from '../../shared/api/client.js'

const HOST_PAGE_SIZE = 8

export async function getHostReviewSlots({ page = 1, signal } = {}) {
  const query = new URLSearchParams({
    page: String(page),
    pageSize: String(HOST_PAGE_SIZE),
  })
  const payload = await apiRequest(`/api/host/review-slots/?${query}`, { signal })

  return {
    reviewSlots: payload.reviewSlots,
    pagination: payload.pagination,
  }
}

export async function createHostReviewSlot(reviewSlot) {
  const payload = await apiRequest('/api/host/review-slots/', {
    method: 'POST',
    body: JSON.stringify(reviewSlot),
  })

  return payload.reviewSlot
}

export async function deleteHostReviewSlot(reviewSlotUuid) {
  await apiRequest(`/api/host/review-slots/${reviewSlotUuid}/`, {
    method: 'DELETE',
  })
}
