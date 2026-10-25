from django.utils import timezone


#======================================
# REVIEW SLOT STATUS
#======================================

def get_review_slot_status(review_slot, *, now=None):
    """Derive the current ReviewSlot status without persisting it."""

    now = now or timezone.now()

    if now >= review_slot.end_at:
        return "expired"

    if now >= review_slot.start_at:
        return "started"

    if hasattr(review_slot, "booking"):
        return "taken"

    return "available"
