from django.db import transaction
from django.utils import timezone

from scheduling.models import ReviewSlot

from .exceptions import (
    ReviewSlotGoneError,
    ReviewSlotNotFoundError,
)


#======================================
# REVIEW SLOT DELETION
#======================================

def delete_review_slot(*, review_slot_uuid):
    """
    Delete a future ReviewSlot.

    Taken slots are deleted together with their Booking through the
    model's cascade relationship. Started and expired slots are retained.
    """

    with transaction.atomic():
        review_slot = (
            ReviewSlot.objects
            .select_for_update()
            .filter(uuid=review_slot_uuid)
            .first()
        )

        if review_slot is None:
            raise ReviewSlotNotFoundError(
                "The review slot does not exist."
            )

        now = timezone.now()

        if now >= review_slot.end_at:
            raise ReviewSlotGoneError(
                "The review slot has already expired."
            )

        if now >= review_slot.start_at:
            raise ReviewSlotGoneError(
                "The review slot has already started."
            )

        review_slot.delete()
