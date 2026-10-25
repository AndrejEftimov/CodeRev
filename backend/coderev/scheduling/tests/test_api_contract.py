import json
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scheduling.constants import (
    BOOKING_NAME_MAX_LENGTH,
    BOOKING_REVIEW_TOPIC_MAX_LENGTH,
)
from scheduling.models import Booking, ReviewSlot
from scheduling.services import (
    BookingValidationError,
    create_booking,
)


class ApiErrorContractTests(TestCase):
    """Tests for stable API error codes and field-error shapes."""

    def setUp(self):
        self.start = timezone.now() + timedelta(days=3)

        self.slot = ReviewSlot.objects.create(
            start_at=self.start,
            end_at=self.start + timedelta(minutes=30),
        )

    #======================================
    # REQUEST VS VALIDATION ERRORS
    #======================================

    def test_malformed_json_uses_invalid_request(self):
        response = self.client.post(
            reverse(
                "scheduling-api:public-review-slot-book",
                kwargs={
                    "review_slot_uuid": self.slot.uuid,
                },
            ),
            data="{",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_request",
        )
        self.assertNotIn(
            "fields",
            response.json()["error"],
        )

    def test_booking_field_errors_use_validation_error_and_arrays(self):
        response = self.client.post(
            reverse(
                "scheduling-api:public-review-slot-book",
                kwargs={
                    "review_slot_uuid": self.slot.uuid,
                },
            ),
            data=json.dumps(
                {
                    "name": "   ",
                    "email": "invalid",
                    "reviewTopic": "   ",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]

        self.assertEqual(
            error["code"],
            "validation_error",
        )

        for messages in error["fields"].values():
            self.assertIsInstance(messages, list)
            self.assertTrue(messages)
            self.assertTrue(
                all(
                    isinstance(message, str)
                    for message in messages
                )
            )

    def test_review_slot_field_errors_use_validation_error_and_arrays(self):
        response = self.client.post(
            reverse(
                "scheduling-api:host-review-slot-list"
            ),
            data=json.dumps(
                {
                    "durationMinutes": 30,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]

        self.assertEqual(
            error["code"],
            "validation_error",
        )
        self.assertIsInstance(
            error["fields"]["startDate"],
            list,
        )
        self.assertIsInstance(
            error["fields"]["startTime"],
            list,
        )

    #======================================
    # REVIEW SLOT RANGE
    #======================================

    def test_end_before_start_uses_validation_error(self):
        local_start = timezone.localtime(
            timezone.now() + timedelta(days=4)
        ).replace(
            hour=11,
            minute=0,
            second=0,
            microsecond=0,
        )

        response = self.client.post(
            reverse(
                "scheduling-api:host-review-slot-list"
            ),
            data=json.dumps(
                {
                    "startDate": local_start.strftime("%Y-%m-%d"),
                    "startTime": local_start.strftime("%H:%M"),
                    "endDate": local_start.strftime("%Y-%m-%d"),
                    "endTime": (
                        local_start - timedelta(minutes=30)
                    ).strftime("%H:%M"),
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "validation_error",
        )

    #======================================
    # TIMEZONE BOUNDARY
    #======================================

    def test_api_uses_current_django_timezone_for_input_and_output(self):
        skopje = ZoneInfo("Europe/Skopje")

        with timezone.override(skopje):
            local_start = timezone.localtime(
                timezone.now() + timedelta(days=5)
            ).replace(
                hour=14,
                minute=0,
                second=0,
                microsecond=0,
            )

            response = self.client.post(
                reverse(
                    "scheduling-api:host-review-slot-list"
                ),
                data=json.dumps(
                    {
                        "startDate": local_start.strftime("%Y-%m-%d"),
                        "startTime": "14:00",
                        "durationMinutes": 30,
                    }
                ),
                content_type="application/json",
            )

            self.assertEqual(response.status_code, 201)

            payload = response.json()["reviewSlot"]

            self.assertEqual(
                payload["startDate"],
                local_start.strftime("%Y-%m-%d"),
            )
            self.assertEqual(
                payload["startTime"],
                "14:00",
            )
            self.assertEqual(
                payload["endTime"],
                "14:30",
            )

            slot = ReviewSlot.objects.get(
                uuid=payload["uuid"]
            )

            self.assertEqual(
                timezone.localtime(
                    slot.start_at,
                    skopje,
                ).strftime("%H:%M"),
                "14:00",
            )


class BookingLengthBoundaryTests(TestCase):
    """Tests exact Booking validation boundaries."""

    def setUp(self):
        start = timezone.now() + timedelta(days=6)

        self.slot = ReviewSlot.objects.create(
            start_at=start,
            end_at=start + timedelta(minutes=30),
        )

    #======================================
    # NAME
    #======================================

    def test_name_at_max_length_is_accepted(self):
        booking = self._create_booking(
            name="A" * BOOKING_NAME_MAX_LENGTH,
        )

        self.assertEqual(
            len(booking.name),
            BOOKING_NAME_MAX_LENGTH,
        )

    def test_name_above_max_length_is_rejected(self):
        with self.assertRaises(BookingValidationError) as context:
            self._create_booking(
                name="A" * (BOOKING_NAME_MAX_LENGTH + 1),
            )

        self.assertIn(
            "name",
            context.exception.fields,
        )

    #======================================
    # REVIEW TOPIC
    #======================================

    def test_review_topic_at_max_length_is_accepted(self):
        booking = self._create_booking(
            review_topic=(
                "T" * BOOKING_REVIEW_TOPIC_MAX_LENGTH
            ),
        )

        self.assertEqual(
            len(booking.review_topic),
            BOOKING_REVIEW_TOPIC_MAX_LENGTH,
        )

    def test_review_topic_above_max_length_is_rejected(self):
        with self.assertRaises(BookingValidationError) as context:
            self._create_booking(
                review_topic=(
                    "T" * (
                        BOOKING_REVIEW_TOPIC_MAX_LENGTH + 1
                    )
                ),
            )

        self.assertIn(
            "reviewTopic",
            context.exception.fields,
        )

    #======================================
    # HELPERS
    #======================================

    def _create_booking(
        self,
        *,
        name="Andrej",
        review_topic="API review",
    ):
        return create_booking(
            review_slot_uuid=self.slot.uuid,
            name=name,
            email="andrej@example.com",
            review_topic=review_topic,
        )
