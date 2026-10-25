import json
from datetime import timedelta

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


@override_settings(
    CSRF_TRUSTED_ORIGINS=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
)
class CsrfIntegrationTests(TestCase):
    """Exercise Django CSRF protection against the JSON API."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

        start = timezone.now() + timedelta(days=3)

        self.slot = ReviewSlot.objects.create(
            start_at=start,
            end_at=start + timedelta(minutes=30),
        )

        self.booking_url = reverse(
            "scheduling-api:public-review-slot-book",
            kwargs={
                "review_slot_uuid": self.slot.uuid,
            },
        )

    #======================================
    # TOKEN BOOTSTRAP
    #======================================

    def test_csrf_endpoint_returns_token_and_sets_cookie(self):
        response = self.client.get(
            reverse("core-api:csrf-token")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["csrfToken"])
        self.assertIn("csrftoken", response.cookies)

    #======================================
    # PROTECTED MUTATION
    #======================================

    def test_booking_without_csrf_token_is_rejected(self):
        response = self._post_booking()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Booking.objects.count(), 0)

    def test_booking_with_csrf_token_is_accepted(self):
        csrf_response = self.client.get(
            reverse("core-api:csrf-token")
        )
        csrf_token = csrf_response.json()["csrfToken"]

        response = self._post_booking(
            csrf_token=csrf_token,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)

    #======================================
    # HELPERS
    #======================================

    def _post_booking(self, *, csrf_token=None):
        headers = {
            "HTTP_ORIGIN": "http://localhost:5173",
        }

        if csrf_token:
            headers["HTTP_X_CSRFTOKEN"] = csrf_token

        return self.client.post(
            self.booking_url,
            data=json.dumps(
                {
                    "name": "Andrej",
                    "email": "andrej@example.com",
                    "reviewTopic": "CSRF integration",
                }
            ),
            content_type="application/json",
            **headers,
        )
