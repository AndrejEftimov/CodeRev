from django.db import models

from core.models import BaseModel
from scheduling.constants import (
    BOOKING_NAME_MAX_LENGTH,
    BOOKING_REVIEW_TOPIC_MAX_LENGTH,
)


class Booking(BaseModel):
    """Represents a developer reservation for a ReviewSlot."""

    review_slot = models.OneToOneField(
        "ReviewSlot",
        on_delete=models.CASCADE,
        related_name="booking",
    )

    name = models.CharField(
        max_length=BOOKING_NAME_MAX_LENGTH,
    )

    email = models.EmailField()

    review_topic = models.CharField(
        max_length=BOOKING_REVIEW_TOPIC_MAX_LENGTH,
    )

    review_description = models.TextField(
        blank=True,
    )

    #======================================
    def __str__(self):
        return f"{self.name} - {self.review_topic}"

    #======================================
    # HELPERS
    #======================================

    # Booking-specific helpers will be added here only when required.
