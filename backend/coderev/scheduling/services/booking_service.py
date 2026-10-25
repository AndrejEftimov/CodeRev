from django.db import IntegrityError, transaction
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot

from .booking_validation import validate_booking_details
from .exceptions import (
    ReviewSlotAlreadyBookedError,
    ReviewSlotGoneError,
    ReviewSlotNotFoundError,
)


#======================================
# SERVICES
#======================================

def create_booking(
    *,
    review_slot_uuid,
    name,
    email,
    review_topic,
    review_description=None,
):
    """Book an available future ReviewSlot atomically."""

    booking_details = validate_booking_details(
        name=name,
        email=email,
        review_topic=review_topic,
        review_description=review_description,
    )

    with transaction.atomic():
        review_slot = _get_review_slot_for_booking(review_slot_uuid)
        _validate_review_slot_bookable(review_slot)

        try:
            # The nested savepoint lets us inspect the database after
            # a uniqueness failure without breaking the outer transaction.
            with transaction.atomic():
                return Booking.objects.create(
                    review_slot=review_slot,
                    **booking_details,
                )
        except IntegrityError as error:
            # The one-to-one constraint remains the final race-safe guarantee.
            if Booking.objects.filter(review_slot=review_slot).exists():
                raise ReviewSlotAlreadyBookedError(
                    "This review slot has already been booked."
                ) from error

            raise


#======================================
# HELPERS
#======================================

def _get_review_slot_for_booking(review_slot_uuid):
    """Lock and return the requested ReviewSlot for booking."""

    review_slot = (
        ReviewSlot.objects
        .select_for_update()
        .filter(uuid=review_slot_uuid)
        .first()
    )

    if review_slot is None:
        raise ReviewSlotNotFoundError(
            "This review slot does not exist."
        )

    return review_slot


def _validate_review_slot_bookable(review_slot):
    """Ensure the ReviewSlot is still future and available."""

    now = timezone.now()

    if now >= review_slot.end_at:
        raise ReviewSlotGoneError(
            "This review slot has already expired."
        )

    if now >= review_slot.start_at:
        raise ReviewSlotGoneError(
            "This review slot has already started."
        )

    if Booking.objects.filter(review_slot=review_slot).exists():
        raise ReviewSlotAlreadyBookedError(
            "This review slot has already been booked."
        )
