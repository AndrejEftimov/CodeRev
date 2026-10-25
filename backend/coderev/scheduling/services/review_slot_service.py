from datetime import timezone as datetime_timezone

from django.db import IntegrityError, transaction

from scheduling.models import ReviewSlot

from .exceptions import ReviewSlotOverlapError
from .review_slot_validation import validate_review_slot_range


# Database constraint names
REVIEW_SLOT_OVERLAP_CONSTRAINT = "exclude_overlapping_review_slots"


#======================================
# HELPERS
#======================================

def _has_overlap(start_at, end_at):
    """Check for an existing half-open [start_at, end_at) overlap."""

    return ReviewSlot.objects.filter(
        start_at__lt=end_at,
        end_at__gt=start_at,
    ).exists()


def _get_constraint_name(error):
    """Return the PostgreSQL constraint name for an IntegrityError."""

    cause = error.__cause__
    diagnostics = getattr(cause, "diag", None)

    return getattr(diagnostics, "constraint_name", None)


#======================================
# SERVICES
#======================================

def create_review_slot(*, start_at, end_at):
    """Create a future, non-overlapping ReviewSlot."""

    validate_review_slot_range(start_at, end_at)

    # Normalize persistence/comparison values to UTC.
    start_at = start_at.astimezone(datetime_timezone.utc)
    end_at = end_at.astimezone(datetime_timezone.utc)

    with transaction.atomic():
        # Friendly pre-flight check; the DB constraint remains race-safe.
        if _has_overlap(start_at, end_at):
            raise ReviewSlotOverlapError(
                "This review slot overlaps existing availability."
            )

        try:
            return ReviewSlot.objects.create(
                start_at=start_at,
                end_at=end_at,
            )
        except IntegrityError as error:
            if _get_constraint_name(error) == REVIEW_SLOT_OVERLAP_CONSTRAINT:
                raise ReviewSlotOverlapError(
                    "This review slot overlaps existing availability."
                ) from error

            raise
