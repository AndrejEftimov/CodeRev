import json
from datetime import timedelta
from uuid import uuid4

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


class PublicBookingApiTests(TestCase):
    """Tests for public ReviewSlot booking."""

    def setUp(self):
        self.start = timezone.now() + timedelta(days=3)

        self.slot = ReviewSlot.objects.create(
            start_at=self.start,
            end_at=self.start + timedelta(minutes=30),
        )

        self.url = reverse(
            "scheduling-api:public-review-slot-book",
            kwargs={
                "review_slot_uuid": self.slot.uuid,
            },
        )

    #======================================
    # SUCCESS
    #======================================

    def test_post_books_available_review_slot(self):
        response = self._post(
            {
                "name": "Andrej",
                "email": "andrej@example.com",
                "reviewTopic": "Authentication flow",
                "reviewDescription": "Review token rotation.",
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)

        booking = Booking.objects.get()

        self.assertEqual(booking.review_slot, self.slot)
        self.assertEqual(booking.name, "Andrej")
        self.assertEqual(
            booking.review_topic,
            "Authentication flow",
        )

    def test_post_returns_public_safe_taken_slot(self):
        response = self._post(
            {
                "name": "Andrej",
                "email": "andrej@example.com",
                "reviewTopic": "Authentication flow",
            }
        )

        self.assertEqual(response.status_code, 201)

        payload = response.json()["reviewSlot"]

        self.assertEqual(payload["uuid"], str(self.slot.uuid))
        self.assertEqual(payload["status"], "taken")
        self.assertNotIn("booking", payload)
        self.assertNotIn("name", payload)
        self.assertNotIn("email", payload)
        self.assertNotIn("reviewTopic", payload)
        self.assertNotIn("reviewDescription", payload)

    def test_post_uses_service_normalization(self):
        self._post(
            {
                "name": "  Andrej  ",
                "email": "  andrej@example.com  ",
                "reviewTopic": "  API review  ",
                "reviewDescription": "  Check response handling.  ",
            }
        )

        booking = Booking.objects.get()

        self.assertEqual(booking.name, "Andrej")
        self.assertEqual(booking.email, "andrej@example.com")
        self.assertEqual(booking.review_topic, "API review")
        self.assertEqual(
            booking.review_description,
            "Check response handling.",
        )

    #======================================
    # REQUEST VALIDATION
    #======================================

    def test_post_rejects_malformed_json(self):
        response = self.client.post(
            self.url,
            data="{",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_request",
        )
        self.assertEqual(Booking.objects.count(), 0)

    def test_post_rejects_non_object_json(self):
        response = self.client.post(
            self.url,
            data=json.dumps([]),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_request",
        )

    def test_post_returns_field_errors_for_invalid_booking(self):
        response = self._post(
            {
                "name": "   ",
                "email": "invalid",
                "reviewTopic": "   ",
            }
        )

        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]

        self.assertEqual(
            error["code"],
            "validation_error",
        )

        fields = error["fields"]

        self.assertEqual(
            set(fields),
            {"name", "email", "reviewTopic"},
        )

        for messages in fields.values():
            self.assertIsInstance(messages, list)

    #======================================
    # SLOT STATE
    #======================================

    def test_post_returns_404_for_missing_slot(self):
        url = reverse(
            "scheduling-api:public-review-slot-book",
            kwargs={
                "review_slot_uuid": uuid4(),
            },
        )

        response = self.client.post(
            url,
            data=json.dumps(self._valid_payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "review_slot_not_found",
        )

    def test_post_returns_409_for_already_booked_slot(self):
        Booking.objects.create(
            review_slot=self.slot,
            name="Existing Developer",
            email="existing@example.com",
            review_topic="Existing booking",
        )

        response = self._post(
            self._valid_payload()
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["error"]["code"],
            "slot_already_booked",
        )
        self.assertEqual(Booking.objects.count(), 1)

    def test_post_returns_410_for_started_slot(self):
        slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(minutes=10),
            end_at=timezone.now() + timedelta(minutes=20),
        )

        url = reverse(
            "scheduling-api:public-review-slot-book",
            kwargs={
                "review_slot_uuid": slot.uuid,
            },
        )

        response = self.client.post(
            url,
            data=json.dumps(self._valid_payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 410)
        self.assertEqual(
            response.json()["error"]["code"],
            "review_slot_gone",
        )

    def test_post_returns_410_for_expired_slot(self):
        slot = ReviewSlot.objects.create(
            start_at=timezone.now() - timedelta(hours=1),
            end_at=timezone.now() - timedelta(minutes=30),
        )

        url = reverse(
            "scheduling-api:public-review-slot-book",
            kwargs={
                "review_slot_uuid": slot.uuid,
            },
        )

        response = self.client.post(
            url,
            data=json.dumps(self._valid_payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 410)
        self.assertEqual(
            response.json()["error"]["code"],
            "review_slot_gone",
        )

    #======================================
    # HTTP BEHAVIOR
    #======================================

    def test_non_post_method_returns_405(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "code": "method_not_allowed",
                    "message": "This endpoint only supports POST requests.",
                },
            },
        )

    #======================================
    # HELPERS
    #======================================

    def _valid_payload(self):
        return {
            "name": "Andrej",
            "email": "andrej@example.com",
            "reviewTopic": "Authentication flow",
            "reviewDescription": "Review token rotation.",
        }

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )
