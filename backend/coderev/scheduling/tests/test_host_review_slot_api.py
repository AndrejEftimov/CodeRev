from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


class HostReviewSlotApiTests(TestCase):
    """Tests for the host active ReviewSlot listing endpoint."""

    def setUp(self):
        self.url = reverse(
            "scheduling-api:host-review-slot-list"
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
                "pagination": {
                    "page": 1,
                    "pageSize": 8,
                    "totalItems": 0,
                    "totalPages": 1,
                },
            },
        )

    def test_get_returns_available_slot_with_null_booking(self):
        slot = self._create_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        payload = self._find_payload(
            response,
            slot.uuid,
        )

        self.assertEqual(payload["status"], "available")
        self.assertIsNone(payload["booking"])

    def test_get_returns_full_booking_details_for_booked_slot(self):
        slot = self._create_slot(
            start_at=self.base,
            end_at=self.base + timedelta(minutes=30),
        )

        booking = Booking.objects.create(
            review_slot=slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Authentication flow",
            review_description="Review refresh-token logic.",
        )

        response = self.client.get(self.url)

        payload = self._find_payload(
            response,
            slot.uuid,
        )

        self.assertEqual(payload["status"], "taken")
        self.assertEqual(
            payload["booking"],
            {
                "uuid": str(booking.uuid),
                "name": "Andrej",
                "email": "andrej@example.com",
                "reviewTopic": "Authentication flow",
                "reviewDescription": "Review refresh-token logic.",
            },
        )

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

    def test_get_includes_started_slot_with_booking_details(self):
        started_slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(minutes=10),
            end_at=timezone.now() + timedelta(minutes=20),
        )

        booking = Booking.objects.create(
            review_slot=started_slot,
            name="Andrej",
            email="andrej@example.com",
            review_topic="Started review",
            review_description="Still visible to the host.",
        )

        response = self.client.get(self.url)

        payload = self._find_payload(
            response,
            started_slot.uuid,
        )

        self.assertEqual(payload["status"], "started")
        self.assertEqual(
            payload["booking"]["uuid"],
            str(booking.uuid),
        )
        self.assertEqual(
            payload["booking"]["email"],
            "andrej@example.com",
        )


    #======================================
    # PAGINATION
    #======================================

    def test_get_paginates_review_slots(self):
        for index in range(9):
            self._create_slot(
                start_at=self.base + timedelta(hours=index),
                end_at=self.base + timedelta(hours=index, minutes=30),
            )

        response = self.client.get(
            self.url,
            {"page": 2, "pageSize": 4},
        )

        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["reviewSlots"]), 4)
        self.assertEqual(
            payload["pagination"],
            {
                "page": 2,
                "pageSize": 4,
                "totalItems": 9,
                "totalPages": 3,
            },
        )

    def test_get_clamps_page_beyond_last_page(self):
        for index in range(2):
            self._create_slot(
                start_at=self.base + timedelta(hours=index),
                end_at=self.base + timedelta(hours=index, minutes=30),
            )

        response = self.client.get(
            self.url,
            {"page": 99, "pageSize": 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["pagination"]["page"], 2)
        self.assertEqual(len(response.json()["reviewSlots"]), 1)

    def test_get_rejects_invalid_pagination_parameters(self):
        response = self.client.get(
            self.url,
            {"pageSize": 0},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_request",
        )

    #======================================
    # HTTP BEHAVIOR
    #======================================

    def test_unsupported_method_returns_standard_error_envelope(self):
        response = self.client.put(
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
                    "message": "This endpoint only supports GET and POST requests.",
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
