from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.utils import timezone

from scheduling.models import ReviewSlot
from scheduling.services import (
    ReviewSlotOverlapError,
    ReviewSlotValidationError,
    create_review_slot,
)


class ReviewSlotServiceTests(TestCase):
    """Tests for ReviewSlot creation and scheduling validation."""

    def setUp(self):
        self.base = timezone.now() + timedelta(days=3)
        self.base = self.base.replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

    #======================================
    # CREATION
    #======================================

    def test_create_review_slot_creates_valid_future_slot(self):
        slot = create_review_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        self.assertEqual(ReviewSlot.objects.count(), 1)
        self.assertEqual(slot.start_at, self.base)
        self.assertEqual(
            slot.end_at,
            self.base + timedelta(minutes=30),
        )

    def test_create_review_slot_allows_adjacent_slot(self):
        create_review_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        adjacent_slot = create_review_slot(
            start_at=self.base + timedelta(minutes=30),
            end_at=self.base + timedelta(minutes=60),
        )

        self.assertEqual(ReviewSlot.objects.count(), 2)
        self.assertEqual(
            adjacent_slot.start_at,
            self.base + timedelta(minutes=30),
        )

    def test_create_review_slot_normalizes_datetimes_to_utc(self):
        local_timezone = ZoneInfo("Europe/Skopje")

        local_start = datetime(
            2030,
            6,
            10,
            14,
            0,
            tzinfo=local_timezone,
        )
        local_end = local_start + timedelta(minutes=30)

        slot = create_review_slot(
            start_at=local_start,
            end_at=local_end,
        )

        self.assertEqual(slot.start_at.utcoffset(), timedelta(0))
        self.assertEqual(slot.end_at.utcoffset(), timedelta(0))
        self.assertEqual(
            slot.start_at,
            local_start.astimezone(ZoneInfo("UTC")),
        )

    #======================================
    # VALIDATION
    #======================================

    def test_create_review_slot_rejects_overlap(self):
        create_review_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        with self.assertRaises(ReviewSlotOverlapError) as context:
            create_review_slot(
                start_at=self.base + timedelta(minutes=15),
                end_at=self.base + timedelta(minutes=45),
            )

        self.assertEqual(
            context.exception.code,
            "review_slot_overlap",
        )
        self.assertEqual(ReviewSlot.objects.count(), 1)

    def test_create_review_slot_rejects_zero_duration(self):
        with self.assertRaises(ReviewSlotValidationError):
            create_review_slot(
                start_at=self.base,
                end_at=self.base,
            )

    def test_create_review_slot_rejects_end_before_start(self):
        with self.assertRaises(ReviewSlotValidationError):
            create_review_slot(
                start_at=self.base,
                end_at=self.base - timedelta(minutes=30),
            )

    def test_create_review_slot_rejects_past_start(self):
        start_at = timezone.now() - timedelta(minutes=10)

        with self.assertRaises(ReviewSlotValidationError):
            create_review_slot(
                start_at=start_at,
                end_at=start_at + timedelta(minutes=30),
            )

    def test_create_review_slot_rejects_naive_datetime(self):
        naive_start = datetime.now()
        naive_end = naive_start + timedelta(minutes=30)

        with self.assertRaises(ReviewSlotValidationError):
            create_review_slot(
                start_at=naive_start,
                end_at=naive_end,
            )
