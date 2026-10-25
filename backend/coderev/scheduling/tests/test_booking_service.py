from datetime import timedelta
from uuid import uuid4

from django.test import TestCase
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot
from scheduling.services import (
    BookingValidationError,
    ReviewSlotAlreadyBookedError,
    ReviewSlotGoneError,
    ReviewSlotNotFoundError,
    create_booking,
    create_review_slot,
)


class BookingServiceTests(TestCase):
    """Tests for Booking validation, lifecycle rules, and persistence."""

    def setUp(self):
        self.base = timezone.now() + timedelta(days=3)
        self.base = self.base.replace(
            hour=14,
            minute=0,
            second=0,
            microsecond=0,
        )

        self.slot = create_review_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

    #======================================
    # CREATION
    #======================================

    def test_create_booking_creates_booking_for_available_slot(self):
        booking = self._create_booking()

        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.review_slot, self.slot)
        self.assertEqual(
            Booking.objects.get(review_slot=self.slot).uuid,
            booking.uuid,
        )

    def test_create_booking_normalizes_text_fields(self):
        booking = create_booking(
            review_slot_uuid=self.slot.uuid,
            name="  Andrej  ",
            email="  andrej@example.com  ",
            review_topic="  Authentication flow  ",
            review_description="  Review refresh-token logic.  ",
        )

        self.assertEqual(booking.name, "Andrej")
        self.assertEqual(booking.email, "andrej@example.com")
        self.assertEqual(
            booking.review_topic,
            "Authentication flow",
        )
        self.assertEqual(
            booking.review_description,
            "Review refresh-token logic.",
        )

    def test_create_booking_defaults_missing_description_to_blank(self):
        booking = create_booking(
            review_slot_uuid=self.slot.uuid,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Architecture review",
        )

        self.assertEqual(booking.review_description, "")

    #======================================
    # FIELD VALIDATION
    #======================================

    def test_create_booking_rejects_invalid_email(self):
        with self.assertRaises(BookingValidationError) as context:
            create_booking(
                review_slot_uuid=self.slot.uuid,
                name="Andrej",
                email="not-an-email",
                review_topic="API review",
            )

        self.assertEqual(
            context.exception.code,
            "booking_validation_error",
        )
        self.assertIn("email", context.exception.fields)
        self.assertEqual(Booking.objects.count(), 0)

    def test_create_booking_collects_multiple_field_errors(self):
        with self.assertRaises(BookingValidationError) as context:
            create_booking(
                review_slot_uuid=self.slot.uuid,
                name="   ",
                email="invalid",
                review_topic="   ",
            )

        self.assertEqual(
            set(context.exception.fields),
            {"name", "email", "reviewTopic"},
        )
        self.assertEqual(Booking.objects.count(), 0)

    #======================================
    # SLOT STATE
    #======================================

    def test_create_booking_rejects_missing_review_slot(self):
        with self.assertRaises(ReviewSlotNotFoundError) as context:
            create_booking(
                review_slot_uuid=uuid4(),
                name="Andrej",
                email="andrej@example.com",
                review_topic="Architecture review",
            )

        self.assertEqual(
            context.exception.code,
            "review_slot_not_found",
        )

    def test_create_booking_rejects_already_booked_slot(self):
        self._create_booking()

        with self.assertRaises(ReviewSlotAlreadyBookedError) as context:
            self._create_booking(
                name="Another Developer",
                email="another@example.com",
                review_topic="Second booking",
            )

        self.assertEqual(
            context.exception.code,
            "slot_already_booked",
        )
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_rejects_started_slot(self):
        started_slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(minutes=10),
            end_at=timezone.now() + timedelta(minutes=20),
        )

        with self.assertRaises(ReviewSlotGoneError) as context:
            create_booking(
                review_slot_uuid=started_slot.uuid,
                name="Andrej",
                email="andrej@example.com",
                review_topic="Started slot test",
            )

        self.assertEqual(
            context.exception.code,
            "review_slot_gone",
        )
        self.assertIn("started", context.exception.message)

    def test_create_booking_rejects_expired_slot(self):
        expired_slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(hours=1),
            end_at=timezone.now() - timedelta(minutes=30),
        )

        with self.assertRaises(ReviewSlotGoneError) as context:
            create_booking(
                review_slot_uuid=expired_slot.uuid,
                name="Andrej",
                email="andrej@example.com",
                review_topic="Expired slot test",
            )

        self.assertEqual(
            context.exception.code,
            "review_slot_gone",
        )
        self.assertIn("expired", context.exception.message)

    #======================================
    # HELPERS
    #======================================

    def _create_booking(
        self,
        *,
        name="Andrej",
        email="andrej@example.com",
        review_topic="Authentication flow",
        review_description="Review refresh-token logic.",
    ):
        return create_booking(
            review_slot_uuid=self.slot.uuid,
            name=name,
            email=email,
            review_topic=review_topic,
            review_description=review_description,
        )
