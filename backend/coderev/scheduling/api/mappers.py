from django.utils import timezone

from scheduling.domain import get_review_slot_status


#======================================
# HELPERS
#======================================

def _duration_minutes(review_slot):
    """Return the derived ReviewSlot duration in minutes."""

    minutes = (
        review_slot.end_at - review_slot.start_at
    ).total_seconds() / 60

    return int(minutes) if minutes.is_integer() else minutes


def _map_review_slot_schedule(review_slot, *, now=None):
    """Map the shared ReviewSlot scheduling fields."""

    start_at = timezone.localtime(review_slot.start_at)
    end_at = timezone.localtime(review_slot.end_at)

    return {
        "uuid": str(review_slot.uuid),
        "startDate": start_at.strftime("%Y-%m-%d"),
        "startTime": start_at.strftime("%H:%M"),
        "endDate": end_at.strftime("%Y-%m-%d"),
        "endTime": end_at.strftime("%H:%M"),
        "durationMinutes": _duration_minutes(review_slot),
        "status": get_review_slot_status(
            review_slot,
            now=now,
        ),
    }


def _map_booking(booking):
    """Map private Booking details for the host API."""

    return {
        "uuid": str(booking.uuid),
        "name": booking.name,
        "email": booking.email,
        "reviewTopic": booking.review_topic,
        "reviewDescription": booking.review_description,
    }


#======================================
# PUBLIC MAPPERS
#======================================

def map_public_review_slot(review_slot, *, now=None):
    """Map a ReviewSlot to the public-safe API representation."""

    return _map_review_slot_schedule(
        review_slot,
        now=now,
    )


#======================================
# HOST MAPPERS
#======================================

def map_host_review_slot(review_slot, *, now=None):
    """Map a ReviewSlot to the host API representation."""

    payload = _map_review_slot_schedule(
        review_slot,
        now=now,
    )

    payload["booking"] = (
        _map_booking(review_slot.booking)
        if hasattr(review_slot, "booking")
        else None
    )

    return payload
