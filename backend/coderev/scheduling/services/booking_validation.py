from core.validation import (
    normalize_optional_text,
    normalize_required_text,
    validate_email,
)
from scheduling.constants import (
    BOOKING_NAME_MAX_LENGTH,
    BOOKING_REVIEW_TOPIC_MAX_LENGTH,
)

from .exceptions import BookingValidationError


#======================================
# BOOKING VALIDATION
#======================================

def validate_booking_details(
    name,
    email,
    review_topic,
    review_description=None,
):
    """Validate and normalize Booking input."""

    fields = {}

    normalized_name = _capture_validation(
        fields,
        "name",
        normalize_required_text,
        name,
        "Name",
        max_length=BOOKING_NAME_MAX_LENGTH,
    )

    normalized_email = _capture_validation(
        fields,
        "email",
        validate_email,
        email,
        "Email",
    )

    normalized_review_topic = _capture_validation(
        fields,
        "reviewTopic",
        normalize_required_text,
        review_topic,
        "Review topic",
        max_length=BOOKING_REVIEW_TOPIC_MAX_LENGTH,
    )

    normalized_review_description = _capture_validation(
        fields,
        "reviewDescription",
        normalize_optional_text,
        review_description,
        "Review description",
    )

    if fields:
        raise BookingValidationError(
            "Some booking fields are invalid.",
            fields=fields,
        )

    return {
        "name": normalized_name,
        "email": normalized_email,
        "review_topic": normalized_review_topic,
        "review_description": normalized_review_description,
    }


#======================================
# HELPERS
#======================================

def _capture_validation(
    fields,
    field_name,
    validator,
    *args,
    **kwargs,
):
    try:
        return validator(
            *args,
            **kwargs,
        )
    except ValueError as error:
        fields.setdefault(
            field_name,
            [],
        ).append(
            str(error)
        )

        return None
