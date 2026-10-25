import json
from datetime import datetime, timedelta

from django.utils import timezone


class ApiRequestError(ValueError):
    """Raised when an API request body cannot be interpreted."""

    code = "invalid_request"

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ApiValidationError(ValueError):
    """Raised when parsed API input contains invalid field values."""

    code = "validation_error"

    def __init__(self, message, *, fields=None):
        self.message = message
        self.fields = fields or {}
        super().__init__(message)


#======================================
# JSON
#======================================

def parse_json_body(request):
    """Parse a JSON request body into a dictionary."""

    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ApiRequestError(
            "The request body must contain valid JSON."
        ) from error

    if not isinstance(payload, dict):
        raise ApiRequestError(
            "The request body must be a JSON object."
        )

    return payload


#======================================
# REVIEW SLOT INPUT
#======================================

def parse_review_slot_input(payload):
    """Parse host ReviewSlot input into aware start/end datetimes."""

    fields = {}

    start_date = _required_string(
        payload,
        "startDate",
        fields,
    )
    start_time = _required_string(
        payload,
        "startTime",
        fields,
    )

    end_date = _optional_string(
        payload,
        "endDate",
        fields,
    )
    end_time = _optional_string(
        payload,
        "endTime",
        fields,
    )

    duration_minutes = _optional_positive_integer(
        payload,
        "durationMinutes",
        fields,
    )

    if fields:
        raise ApiValidationError(
            "Some review slot fields are invalid.",
            fields=fields,
        )

    if (end_date is None) != (end_time is None):
        missing_field = (
            "endDate"
            if end_date is None
            else "endTime"
        )

        raise ApiValidationError(
            "Some review slot fields are invalid.",
            fields={
                missing_field: [
                    "This field is required with the explicit end time."
                ],
            },
        )

    if end_date is None and duration_minutes is None:
        raise ApiValidationError(
            "Some review slot fields are invalid.",
            fields={
                "endDate": [
                    "Provide an explicit end date/time or durationMinutes."
                ],
                "endTime": [
                    "Provide an explicit end date/time or durationMinutes."
                ],
                "durationMinutes": [
                    "Provide durationMinutes or an explicit end date/time."
                ],
            },
        )

    start_at = _parse_local_datetime(
        start_date,
        start_time,
        date_field="startDate",
        time_field="startTime",
    )

    explicit_end_at = None

    if end_date is not None:
        explicit_end_at = _parse_local_datetime(
            end_date,
            end_time,
            date_field="endDate",
            time_field="endTime",
        )

    duration_end_at = None

    if duration_minutes is not None:
        duration_end_at = start_at + timedelta(
            minutes=duration_minutes,
        )

    if (
        explicit_end_at is not None
        and duration_end_at is not None
        and explicit_end_at != duration_end_at
    ):
        raise ApiValidationError(
            "Some review slot fields are invalid.",
            fields={
                "durationMinutes": [
                    "Does not match the provided end date/time."
                ],
            },
        )

    return {
        "start_at": start_at,
        "end_at": explicit_end_at or duration_end_at,
    }


#======================================
# BOOKING INPUT
#======================================

def parse_booking_input(payload):
    """
    Map public booking transport fields to service-layer arguments.

    Semantic validation and normalization remain the responsibility of
    the booking service.
    """

    return {
        "name": payload.get("name"),
        "email": payload.get("email"),
        "review_topic": payload.get("reviewTopic"),
        "review_description": payload.get("reviewDescription"),
    }


#======================================
# FIELD HELPERS
#======================================

def _required_string(payload, field_name, fields):
    value = payload.get(field_name)

    if not isinstance(value, str) or not value.strip():
        fields[field_name] = [
            "This field is required."
        ]
        return None

    return value.strip()


def _optional_string(payload, field_name, fields):
    value = payload.get(field_name)

    if value is None:
        return None

    if not isinstance(value, str) or not value.strip():
        fields[field_name] = [
            "This field must be a non-empty string."
        ]
        return None

    return value.strip()


def _optional_positive_integer(payload, field_name, fields):
    value = payload.get(field_name)

    if value is None:
        return None

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        fields[field_name] = [
            "This field must be a positive integer."
        ]
        return None

    return value


def _parse_local_datetime(
    date_value,
    time_value,
    *,
    date_field,
    time_field,
):
    fields = {}

    try:
        parsed_date = datetime.strptime(
            date_value,
            "%Y-%m-%d",
        ).date()
    except ValueError:
        fields[date_field] = [
            "Use YYYY-MM-DD."
        ]

    try:
        parsed_time = datetime.strptime(
            time_value,
            "%H:%M",
        ).time()
    except ValueError:
        fields[time_field] = [
            "Use HH:MM in 24-hour format."
        ]

    if fields:
        raise ApiValidationError(
            "Some review slot fields are invalid.",
            fields=fields,
        )

    naive_datetime = datetime.combine(
        parsed_date,
        parsed_time,
    )

    return timezone.make_aware(
        naive_datetime,
        timezone.get_current_timezone(),
    )
