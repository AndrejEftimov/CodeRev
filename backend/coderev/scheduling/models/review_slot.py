from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary, RangeOperators
from django.db import models
from django.db.models import F, Func, Q

from core.models import BaseModel
from scheduling.querysets import ReviewSlotQuerySet


# PostgreSQL range helper
class TsTzRange(Func):
    """Build a PostgreSQL tstzrange from ReviewSlot start/end datetimes."""

    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


class ReviewSlot(BaseModel):
    """Represents a dedicated code-review availability window."""

    start_at = models.DateTimeField()

    end_at = models.DateTimeField()

    #======================================
    # MANAGER
    #======================================

    objects = ReviewSlotQuerySet.as_manager()

    #======================================
    class Meta:
        ordering = ["start_at"]

        constraints = [
            models.CheckConstraint(
                condition=Q(end_at__gt=F("start_at")),
                name="review_slot_end_after_start",
            ),
            ExclusionConstraint(
                name="exclude_overlapping_review_slots",
                expressions=[
                    (
                        # [) allows adjacent slots while rejecting true overlaps.
                        TsTzRange(
                            "start_at",
                            "end_at",
                            RangeBoundary(),
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
            ),
        ]

    #======================================
    def __str__(self):
        return f"{self.start_at} - {self.end_at}"

    #======================================
    # HELPERS
    #======================================

    # Scheduling/status helpers will be added here only when model-local behavior is required.
