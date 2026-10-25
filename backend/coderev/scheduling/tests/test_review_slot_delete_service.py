from datetime import timedelta
from uuid import uuid4

from django.test import TestCase
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot
from scheduling.services import (
    ReviewSlotGoneError,
    ReviewSlotNotFoundError,
    delete_review_slot,
)


class ReviewSlotDeleteServiceTests(TestCase):
    """Tests for ReviewSlot deletion rules."""

    def setUp(self):
        self.future = timezone.now() + timedelta(days=3)

    #======================================
    # SUCCESS
    #======================================

    def test_delete_available_review_slot(self):
        slot = self._create_future_slot()

        delete_review_slot(
            review_slot_uuid=slot.uuid,
        )

        self.assertFalse(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )

    def test_delete_taken_review_slot_cascades_booking(self):
        slot = self._create_future_slot()

        booking = Booking.objects.create(
            review_slot=slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Authentication flow",
        )

        booking_uuid = booking.uuid

        delete_review_slot(
            review_slot_uuid=slot.uuid,
        )

        self.assertFalse(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )
        self.assertFalse(
            Booking.objects.filter(uuid=booking_uuid).exists()
        )

    #======================================
    # FAILURE
    #======================================

    def test_delete_missing_review_slot_raises_not_found(self):
        with self.assertRaises(ReviewSlotNotFoundError):
            delete_review_slot(
                review_slot_uuid=uuid4(),
            )

    def test_delete_started_review_slot_is_rejected(self):
        slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(minutes=10),
            end_at=timezone.now() + timedelta(minutes=20),
        )

        with self.assertRaises(ReviewSlotGoneError) as context:
            delete_review_slot(
                review_slot_uuid=slot.uuid,
            )

        self.assertIn(
            "started",
            context.exception.message,
        )
        self.assertTrue(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )

    def test_delete_expired_review_slot_is_rejected(self):
        slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(hours=1),
            end_at=timezone.now() - timedelta(minutes=30),
        )

        with self.assertRaises(ReviewSlotGoneError) as context:
            delete_review_slot(
                review_slot_uuid=slot.uuid,
            )

        self.assertIn(
            "expired",
            context.exception.message,
        )
        self.assertTrue(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )

    #======================================
    # HELPERS
    #======================================

    def _create_future_slot(self):
        return ReviewSlot.objects.create(
            start_at=self.future,
            end_at=self.future + timedelta(minutes=30),
        )
