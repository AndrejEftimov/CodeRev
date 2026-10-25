from django.utils import timezone

from core.api import (
    empty_response,
    error_response,
    json_response,
)
from core.api.pagination import PaginationError, paginate_queryset
from scheduling.models import ReviewSlot
from scheduling.services import (
    BookingValidationError,
    ReviewSlotAlreadyBookedError,
    ReviewSlotGoneError,
    ReviewSlotNotFoundError,
    ReviewSlotOverlapError,
    ReviewSlotValidationError,
    create_booking,
    create_review_slot,
    delete_review_slot,
)

from .mappers import (
    map_host_review_slot,
    map_public_review_slot,
)
from .parsers import (
    ApiRequestError,
    ApiValidationError,
    parse_booking_input,
    parse_json_body,
    parse_review_slot_input,
)


#======================================
# HELPERS
#======================================

def _get_active_review_slots(*, now):
    """Return active ReviewSlots with Booking state loaded."""

    return (
        ReviewSlot.objects
        .active(now=now)
        .with_booking()
    )


def _validation_error_response(error):
    """Translate validation failures into the stable API contract."""

    return error_response(
        code="validation_error",
        message=error.message,
        fields=error.fields,
        status=400,
    )


#======================================
# PUBLIC REVIEW SLOTS
#======================================

def public_review_slot_list(request):
    """Return paginated active ReviewSlots using the public-safe representation."""

    if request.method != "GET":
        return error_response(
            code="method_not_allowed",
            message="This endpoint only supports GET requests.",
            status=405,
        )

    now = timezone.now()
    review_slots = _get_active_review_slots(now=now)

    try:
        review_slots, pagination = paginate_queryset(
            review_slots,
            request,
            default_page_size=6,
        )
    except PaginationError as error:
        return error_response(
            code="invalid_request",
            message=str(error),
            status=400,
        )

    return json_response(
        {
            "reviewSlots": [
                map_public_review_slot(
                    review_slot,
                    now=now,
                )
                for review_slot in review_slots
            ],
            "pagination": pagination,
        }
    )


def public_review_slot_book(request, review_slot_uuid):
    """Book an available ReviewSlot from the public interface."""

    if request.method != "POST":
        return error_response(
            code="method_not_allowed",
            message="This endpoint only supports POST requests.",
            status=405,
        )

    try:
        payload = parse_json_body(request)
        booking_data = parse_booking_input(payload)

        booking = create_booking(
            review_slot_uuid=review_slot_uuid,
            **booking_data,
        )

    except ApiRequestError as error:
        return error_response(
            code=error.code,
            message=error.message,
            status=400,
        )

    except ApiValidationError as error:
        return _validation_error_response(error)

    except BookingValidationError as error:
        return _validation_error_response(error)

    except ReviewSlotNotFoundError as error:
        return error_response(
            code=error.code,
            message=error.message,
            fields=error.fields,
            status=404,
        )

    except ReviewSlotAlreadyBookedError as error:
        return error_response(
            code=error.code,
            message=error.message,
            fields=error.fields,
            status=409,
        )

    except ReviewSlotGoneError as error:
        return error_response(
            code=error.code,
            message=error.message,
            fields=error.fields,
            status=410,
        )

    return json_response(
        {
            "reviewSlot": map_public_review_slot(
                booking.review_slot,
                now=timezone.now(),
            ),
        },
        status=201,
    )


#======================================
# HOST REVIEW SLOTS
#======================================

def host_review_slot_list(request):
    """List or create ReviewSlots for the host interface."""

    if request.method == "GET":
        return _host_review_slot_list_get(request)

    if request.method == "POST":
        return _host_review_slot_list_post(request)

    return error_response(
        code="method_not_allowed",
        message="This endpoint only supports GET and POST requests.",
        status=405,
    )


def _host_review_slot_list_get(request):
    now = timezone.now()
    review_slots = _get_active_review_slots(now=now)

    try:
        review_slots, pagination = paginate_queryset(
            review_slots,
            request,
            default_page_size=8,
        )
    except PaginationError as error:
        return error_response(
            code="invalid_request",
            message=str(error),
            status=400,
        )

    return json_response(
        {
            "reviewSlots": [
                map_host_review_slot(
                    review_slot,
                    now=now,
                )
                for review_slot in review_slots
            ],
            "pagination": pagination,
        }
    )


def _host_review_slot_list_post(request):
    try:
        payload = parse_json_body(request)
        review_slot_data = parse_review_slot_input(payload)

        review_slot = create_review_slot(
            **review_slot_data,
        )

    except ApiRequestError as error:
        return error_response(
            code=error.code,
            message=error.message,
            status=400,
        )

    except ApiValidationError as error:
        return _validation_error_response(error)

    except ReviewSlotValidationError as error:
        return _validation_error_response(error)

    except ReviewSlotOverlapError as error:
        return error_response(
            code=error.code,
            message=error.message,
            fields=error.fields,
            status=409,
        )

    return json_response(
        {
            "reviewSlot": map_host_review_slot(
                review_slot,
                now=timezone.now(),
            ),
        },
        status=201,
    )


def host_review_slot_detail(request, review_slot_uuid):
    """Delete a future ReviewSlot from the host interface."""

    if request.method != "DELETE":
        return error_response(
            code="method_not_allowed",
            message="This endpoint only supports DELETE requests.",
            status=405,
        )

    try:
        delete_review_slot(
            review_slot_uuid=review_slot_uuid,
        )

    except ReviewSlotNotFoundError as error:
        return error_response(
            code=error.code,
            message=error.message,
            fields=error.fields,
            status=404,
        )

    except ReviewSlotGoneError as error:
        return error_response(
            code=error.code,
            message=error.message,
            fields=error.fields,
            status=410,
        )

    return empty_response(status=204)
