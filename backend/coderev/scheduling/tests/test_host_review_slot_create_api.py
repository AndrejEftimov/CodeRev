import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scheduling.models import ReviewSlot


class HostReviewSlotCreateApiTests(TestCase):
    """Tests for host ReviewSlot creation through the API."""

    def setUp(self):
        self.url = reverse(
            "scheduling-api:host-review-slot-list"
        )

        self.start = timezone.localtime(
            timezone.now() + timedelta(days=3)
        ).replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

    #======================================
    # SUCCESS
    #======================================

    def test_post_creates_slot_with_explicit_end(self):
        response = self._post(
            {
                "startDate": self.start.strftime("%Y-%m-%d"),
                "startTime": self.start.strftime("%H:%M"),
                "endDate": self.start.strftime("%Y-%m-%d"),
                "endTime": (
                    self.start + timedelta(minutes=30)
                ).strftime("%H:%M"),
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ReviewSlot.objects.count(), 1)

        payload = response.json()["reviewSlot"]

        self.assertEqual(payload["status"], "available")
        self.assertEqual(payload["durationMinutes"], 30)
        self.assertIsNone(payload["booking"])

    def test_post_creates_slot_from_duration(self):
        response = self._post(
            {
                "startDate": self.start.strftime("%Y-%m-%d"),
                "startTime": self.start.strftime("%H:%M"),
                "durationMinutes": 45,
            }
        )

        self.assertEqual(response.status_code, 201)

        slot = ReviewSlot.objects.get()

        self.assertEqual(
            slot.end_at - slot.start_at,
            timedelta(minutes=45),
        )

    def test_post_accepts_matching_explicit_end_and_duration(self):
        response = self._post(
            {
                "startDate": self.start.strftime("%Y-%m-%d"),
                "startTime": self.start.strftime("%H:%M"),
                "endDate": self.start.strftime("%Y-%m-%d"),
                "endTime": (
                    self.start + timedelta(minutes=30)
                ).strftime("%H:%M"),
                "durationMinutes": 30,
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ReviewSlot.objects.count(), 1)

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

    def test_post_rejects_missing_start_fields(self):
        response = self._post(
            {
                "durationMinutes": 30,
            }
        )

        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]

        self.assertEqual(
            error["code"],
            "validation_error",
        )
        self.assertIn("startDate", error["fields"])
        self.assertIn("startTime", error["fields"])

    def test_post_rejects_partial_explicit_end(self):
        response = self._post(
            {
                "startDate": self.start.strftime("%Y-%m-%d"),
                "startTime": self.start.strftime("%H:%M"),
                "endDate": self.start.strftime("%Y-%m-%d"),
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "validation_error",
        )
        self.assertIn(
            "endTime",
            response.json()["error"]["fields"],
        )

    def test_post_rejects_when_neither_end_nor_duration_is_provided(self):
        response = self._post(
            {
                "startDate": self.start.strftime("%Y-%m-%d"),
                "startTime": self.start.strftime("%H:%M"),
            }
        )

        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]
        fields = error["fields"]

        self.assertEqual(
            error["code"],
            "validation_error",
        )
        self.assertIn("endDate", fields)
        self.assertIn("endTime", fields)
        self.assertIn("durationMinutes", fields)

    def test_post_rejects_non_positive_duration(self):
        response = self._post(
            {
                "startDate": self.start.strftime("%Y-%m-%d"),
                "startTime": self.start.strftime("%H:%M"),
                "durationMinutes": 0,
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "validation_error",
        )
        self.assertIn(
            "durationMinutes",
            response.json()["error"]["fields"],
        )

    def test_post_rejects_mismatched_end_and_duration(self):
        response = self._post(
            {
                "startDate": self.start.strftime("%Y-%m-%d"),
                "startTime": self.start.strftime("%H:%M"),
                "endDate": self.start.strftime("%Y-%m-%d"),
                "endTime": (
                    self.start + timedelta(minutes=30)
                ).strftime("%H:%M"),
                "durationMinutes": 45,
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "validation_error",
        )
        self.assertIn(
            "durationMinutes",
            response.json()["error"]["fields"],
        )
        self.assertEqual(ReviewSlot.objects.count(), 0)

    def test_post_rejects_invalid_date_or_time_format(self):
        response = self._post(
            {
                "startDate": "24-10-2030",
                "startTime": "10.00",
                "durationMinutes": 30,
            }
        )

        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]
        fields = error["fields"]

        self.assertEqual(
            error["code"],
            "validation_error",
        )
        self.assertIn("startDate", fields)
        self.assertIn("startTime", fields)

    #======================================
    # SERVICE ERROR TRANSLATION
    #======================================

    def test_post_translates_past_start_to_400(self):
        past = timezone.localtime(
            timezone.now() - timedelta(days=1)
        )

        response = self._post(
            {
                "startDate": past.strftime("%Y-%m-%d"),
                "startTime": past.strftime("%H:%M"),
                "durationMinutes": 30,
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "validation_error",
        )

    def test_post_translates_overlap_to_409(self):
        ReviewSlot.objects.create(
            start_at=self.start,
            end_at=self.start + timedelta(minutes=30),
        )

        response = self._post(
            {
                "startDate": (
                    self.start + timedelta(minutes=15)
                ).strftime("%Y-%m-%d"),
                "startTime": (
                    self.start + timedelta(minutes=15)
                ).strftime("%H:%M"),
                "durationMinutes": 30,
            }
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["error"]["code"],
            "review_slot_overlap",
        )
        self.assertEqual(ReviewSlot.objects.count(), 1)

    #======================================
    # HELPERS
    #======================================

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )
