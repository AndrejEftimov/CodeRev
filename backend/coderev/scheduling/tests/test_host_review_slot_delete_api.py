from datetime import timedelta
from uuid import uuid4

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


class HostReviewSlotDeleteApiTests(TestCase):
    """Tests for host ReviewSlot deletion."""

    def setUp(self):
        self.future = timezone.now() + timedelta(days=3)

    #======================================
    # SUCCESS
    #======================================

    def test_delete_available_slot_returns_204(self):
        slot = self._create_future_slot()

        response = self.client.delete(
            self._url(slot.uuid)
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )

    def test_delete_taken_slot_returns_204_and_cascades_booking(self):
        slot = self._create_future_slot()

        booking = Booking.objects.create(
            review_slot=slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Authentication flow",
        )

        booking_uuid = booking.uuid

        response = self.client.delete(
            self._url(slot.uuid)
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )
        self.assertFalse(
            Booking.objects.filter(uuid=booking_uuid).exists()
        )

    #======================================
    # FAILURE
    #======================================

    def test_delete_missing_slot_returns_404(self):
        response = self.client.delete(
            self._url(uuid4())
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "review_slot_not_found",
        )

    def test_delete_started_slot_returns_410(self):
        slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(minutes=10),
            end_at=timezone.now() + timedelta(minutes=20),
        )

        response = self.client.delete(
            self._url(slot.uuid)
        )

        self.assertEqual(response.status_code, 410)
        self.assertEqual(
            response.json()["error"]["code"],
            "review_slot_gone",
        )
        self.assertTrue(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )

    def test_delete_expired_slot_returns_410(self):
        slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(hours=1),
            end_at=timezone.now() - timedelta(minutes=30),
        )

        response = self.client.delete(
            self._url(slot.uuid)
        )

        self.assertEqual(response.status_code, 410)
        self.assertEqual(
            response.json()["error"]["code"],
            "review_slot_gone",
        )
        self.assertTrue(
            ReviewSlot.objects.filter(uuid=slot.uuid).exists()
        )

    #======================================
    # HTTP BEHAVIOR
    #======================================

    def test_non_delete_method_returns_405(self):
        slot = self._create_future_slot()

        response = self.client.get(
            self._url(slot.uuid)
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "code": "method_not_allowed",
                    "message": "This endpoint only supports DELETE requests.",
                },
            },
        )

    #======================================
    # HELPERS
    #======================================

    def _create_future_slot(self):
        return ReviewSlot.objects.create(
            start_at=self.future,
            end_at=self.future + timedelta(minutes=30),
        )

    def _url(self, review_slot_uuid):
        return reverse(
            "scheduling-api:host-review-slot-detail",
            kwargs={
                "review_slot_uuid": review_slot_uuid,
            },
        )
