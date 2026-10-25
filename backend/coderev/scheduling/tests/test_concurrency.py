from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

from django.db import close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot
from scheduling.services import (
    ReviewSlotAlreadyBookedError,
    ReviewSlotOverlapError,
    create_booking,
    create_review_slot,
)


class SchedulingConcurrencyTests(TransactionTestCase):
    """Tests for race-sensitive scheduling operations against PostgreSQL."""

    reset_sequences = True

    def setUp(self):
        self.base = timezone.now() + timedelta(days=5)
        self.base = self.base.replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

    #======================================
    # REVIEW SLOT CONCURRENCY
    #======================================

    def test_concurrent_overlapping_review_slot_creation_allows_only_one(self):
        barrier = Barrier(2)

        def create_slot():
            close_old_connections()

            try:
                barrier.wait()

                create_review_slot(
                    start_at=self.base,
                    end_at=self.base + timedelta(minutes=30),
                )

                return "created"
            except ReviewSlotOverlapError:
                return "overlap"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: create_slot(), range(2)))

        self.assertCountEqual(
            results,
            ["created", "overlap"],
        )
        self.assertEqual(ReviewSlot.objects.count(), 1)

    #======================================
    # BOOKING CONCURRENCY
    #======================================

    def test_concurrent_booking_attempts_allow_only_one_booking(self):
        slot = ReviewSlot.objects.create(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        barrier = Barrier(2)

        def book_slot(index):
            close_old_connections()

            try:
                barrier.wait()

                create_booking(
                    review_slot_uuid=slot.uuid,
                    name=f"Developer {index}",
                    email=f"developer{index}@example.com",
                    review_topic="Concurrent booking test",
                )

                return "booked"
            except ReviewSlotAlreadyBookedError:
                return "already_booked"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(book_slot, range(2)))

        self.assertCountEqual(
            results,
            ["booked", "already_booked"],
        )
        self.assertEqual(Booking.objects.filter(review_slot=slot).count(), 1)
