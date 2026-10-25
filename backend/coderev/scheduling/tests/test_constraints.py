from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


class SchedulingConstraintTests(TestCase):
    """Tests for database-level scheduling integrity guarantees."""

    def setUp(self):
        self.base = timezone.now() + timedelta(days=4)
        self.base = self.base.replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

    #======================================
    # REVIEW SLOT CONSTRAINTS
    #======================================

    def test_database_allows_adjacent_review_slots(self):
        ReviewSlot.objects.create(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        ReviewSlot.objects.create(
            start_at=self.base + timedelta(minutes=30),
            end_at=self.base + timedelta(minutes=60),
        )

        self.assertEqual(ReviewSlot.objects.count(), 2)

    def test_database_rejects_overlapping_review_slots(self):
        ReviewSlot.objects.create(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ReviewSlot.objects.create(
                    start_at=self.base + timedelta(minutes=15),
                    end_at=self.base + timedelta(minutes=45),
                )

        self.assertEqual(ReviewSlot.objects.count(), 1)

    def test_database_rejects_zero_duration_review_slot(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ReviewSlot.objects.create(
                    start_at=self.base,
                    end_at=self.base,
                )

    def test_database_rejects_end_before_start(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ReviewSlot.objects.create(
                    start_at=self.base,
                    end_at=self.base - timedelta(minutes=30),
                )

    #======================================
    # BOOKING CONSTRAINTS
    #======================================

    def test_database_rejects_second_booking_for_same_slot(self):
        slot = self._create_slot()

        Booking.objects.create(
            review_slot=slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Authentication flow",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    review_slot=slot,
                    name="Another Developer",
                    email="another@example.com",
                    review_topic="Second booking",
                )

        self.assertEqual(Booking.objects.count(), 1)

    def test_deleting_review_slot_cascades_to_booking(self):
        slot = self._create_slot()

        booking = Booking.objects.create(
            review_slot=slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Authentication flow",
        )

        booking_uuid = booking.uuid
        slot.delete()

        self.assertFalse(
            Booking.objects.filter(uuid=booking_uuid).exists()
        )

    #======================================
    # HELPERS
    #======================================

    def _create_slot(self):
        return ReviewSlot.objects.create(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )
