from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


class PublicReviewSlotApiTests(TestCase):
    """Tests for the public active ReviewSlot listing endpoint."""

    def setUp(self):
        self.url = reverse(
            "scheduling-api:public-review-slot-list"
        )

        self.base = timezone.now() + timedelta(days=3)
        self.base = self.base.replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

    #======================================
    # RESPONSE SHAPE
    #======================================

    def test_get_returns_empty_review_slot_collection(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "reviewSlots": [],
            },
        )

    def test_get_returns_public_review_slot_shape(self):
        slot = self._create_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        payload = response.json()["reviewSlots"][0]

        expected_start = timezone.localtime(self.base)
        expected_end = timezone.localtime(
            self.base + timedelta(minutes=30)
        )

        self.assertEqual(payload["uuid"], str(slot.uuid))
        self.assertEqual(
            payload["startDate"],
            expected_start.strftime("%Y-%m-%d"),
        )
        self.assertEqual(
            payload["startTime"],
            expected_start.strftime("%H:%M"),
        )
        self.assertEqual(
            payload["endDate"],
            expected_end.strftime("%Y-%m-%d"),
        )
        self.assertEqual(
            payload["endTime"],
            expected_end.strftime("%H:%M"),
        )
        self.assertEqual(payload["durationMinutes"], 30)
        self.assertEqual(payload["status"], "available")

    #======================================
    # ACTIVE QUERY BEHAVIOR
    #======================================

    def test_get_orders_active_review_slots_chronologically(self):
        later_slot = self._create_slot(
            start_at=self.base + timedelta(hours=1),
            end_at=self.base + timedelta(hours=1, minutes=30),
        )

        earlier_slot = self._create_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        response = self.client.get(self.url)

        uuids = [
            item["uuid"]
            for item in response.json()["reviewSlots"]
        ]

        self.assertEqual(
            uuids,
            [
                str(earlier_slot.uuid),
                str(later_slot.uuid),
            ],
        )

    def test_get_excludes_expired_review_slots(self):
        expired_slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(hours=1),
            end_at=timezone.now() - timedelta(minutes=30),
        )

        active_slot = self._create_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        response = self.client.get(self.url)

        uuids = {
            item["uuid"]
            for item in response.json()["reviewSlots"]
        }

        self.assertNotIn(str(expired_slot.uuid), uuids)
        self.assertIn(str(active_slot.uuid), uuids)

    def test_get_includes_started_review_slot_as_started(self):
        started_slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(minutes=10),
            end_at=timezone.now() + timedelta(minutes=20),
        )

        response = self.client.get(self.url)

        payload = self._find_payload(
            response,
            started_slot.uuid,
        )

        self.assertEqual(payload["status"], "started")

    #======================================
    # BOOKING STATUS / PRIVACY
    #======================================

    def test_get_marks_future_booked_slot_as_taken(self):
        slot = self._create_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        Booking.objects.create(
            review_slot=slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Authentication flow",
            review_description="Private booking context.",
        )

        response = self.client.get(self.url)

        payload = self._find_payload(
            response,
            slot.uuid,
        )

        self.assertEqual(payload["status"], "taken")

    def test_get_never_exposes_private_booking_details(self):
        slot = self._create_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        Booking.objects.create(
            review_slot=slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Authentication flow",
            review_description="Private booking context.",
        )

        response = self.client.get(self.url)

        payload = self._find_payload(
            response,
            slot.uuid,
        )

        self.assertNotIn("booking", payload)
        self.assertNotIn("name", payload)
        self.assertNotIn("email", payload)
        self.assertNotIn("reviewTopic", payload)
        self.assertNotIn("reviewDescription", payload)

    #======================================
    # HTTP BEHAVIOR
    #======================================

    def test_non_get_method_returns_standard_error_envelope(self):
        response = self.client.post(
            self.url,
            data={},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "code": "method_not_allowed",
                    "message": "This endpoint only supports GET requests.",
                },
            },
        )

    #======================================
    # HELPERS
    #======================================

    def _create_slot(self, *, start_at, end_at):
        return ReviewSlot.objects.create(
            start_at=start_at,
            end_at=end_at,
        )

    def _find_payload(self, response, review_slot_uuid):
        return next(
            item
            for item in response.json()["reviewSlots"]
            if item["uuid"] == str(review_slot_uuid)
        )
