from django.db import models
from django.utils import timezone


class ReviewSlotQuerySet(models.QuerySet):
    """Reusable queryset operations for ReviewSlot."""

    #======================================
    # LIFECYCLE
    #======================================

    def active(self, *, now=None):
        """Return ReviewSlots whose scheduled end has not passed."""

        now = now or timezone.now()

        return self.filter(
            end_at__gt=now,
        )

    def historical(self, *, now=None):
        """Return ReviewSlots whose scheduled end has passed."""

        now = now or timezone.now()

        return self.filter(
            end_at__lte=now,
        )

    #======================================
    # RELATED DATA
    #======================================

    def with_booking(self):
        """Load optional Booking data with each ReviewSlot."""

        return self.select_related("booking")
