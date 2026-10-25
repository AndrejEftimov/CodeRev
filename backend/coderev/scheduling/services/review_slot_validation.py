from django.utils import timezone

from core.validation import validate_aware_datetime

from .exceptions import ReviewSlotValidationError


#======================================
# REVIEW SLOT VALIDATION
#======================================

def validate_review_slot_range(start_at, end_at):
    """Validate ReviewSlot scheduling rules before persistence."""

    validate_aware_datetime(
        start_at,
        "start_at",
        error_class=ReviewSlotValidationError,
    )

    validate_aware_datetime(
        end_at,
        "end_at",
        error_class=ReviewSlotValidationError,
    )

    if end_at <= start_at:
        raise ReviewSlotValidationError(
            "ReviewSlot end time must be after its start time."
        )

    if start_at <= timezone.now():
        raise ReviewSlotValidationError(
            "ReviewSlot start time must be in the future."
        )
