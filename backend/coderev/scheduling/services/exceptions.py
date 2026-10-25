class SchedulingServiceError(Exception):
    """Base exception for expected scheduling service failures."""

    code = "scheduling_error"

    def __init__(self, message, *, fields=None):
        self.message = message
        self.fields = fields
        super().__init__(message)


#======================================
# REVIEW SLOT ERRORS
#======================================

class ReviewSlotValidationError(SchedulingServiceError):
    """Raised when ReviewSlot input violates scheduling rules."""

    code = "review_slot_validation_error"


class ReviewSlotOverlapError(SchedulingServiceError):
    """Raised when a ReviewSlot conflicts with existing availability."""

    code = "review_slot_overlap"


class ReviewSlotNotFoundError(SchedulingServiceError):
    """Raised when a requested ReviewSlot does not exist."""

    code = "review_slot_not_found"


class ReviewSlotGoneError(SchedulingServiceError):
    """Raised when a ReviewSlot has already started or expired."""

    code = "review_slot_gone"


#======================================
# BOOKING ERRORS
#======================================

class BookingValidationError(SchedulingServiceError):
    """Raised when Booking input is invalid."""

    code = "booking_validation_error"


class ReviewSlotAlreadyBookedError(SchedulingServiceError):
    """Raised when a future ReviewSlot already has a Booking."""

    code = "slot_already_booked"
