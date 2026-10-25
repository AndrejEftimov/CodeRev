import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


class SchedulingApiLifecycleTests(TestCase):
    """Tests the main CodeRev scheduling workflow across API boundaries."""

    def test_host_create_public_book_host_view_and_delete(self):
        start = timezone.localtime(
            timezone.now() + timedelta(days=3)
        ).replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        # Host creates a slot.
        create_response = self.client.post(
            reverse(
                "scheduling-api:host-review-slot-list"
            ),
            data=json.dumps(
                {
                    "startDate": start.strftime("%Y-%m-%d"),
                    "startTime": start.strftime("%H:%M"),
                    "durationMinutes": 30,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, 201)

        slot_uuid = create_response.json()["reviewSlot"]["uuid"]

        # Public listing exposes it as available.
        public_list_response = self.client.get(
            reverse(
                "scheduling-api:public-review-slot-list"
            )
        )

        public_slot = next(
            slot
            for slot in public_list_response.json()["reviewSlots"]
            if slot["uuid"] == slot_uuid
        )

        self.assertEqual(public_slot["status"], "available")
        self.assertNotIn("booking", public_slot)

        # A teammate books it.
        booking_response = self.client.post(
            reverse(
                "scheduling-api:public-review-slot-book",
                kwargs={
                    "review_slot_uuid": slot_uuid,
                },
            ),
            data=json.dumps(
                {
                    "name": "Andrej",
                    "email": "andrej@example.com",
                    "reviewTopic": "Authentication flow",
                    "reviewDescription": "Review token rotation.",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(booking_response.status_code, 201)
        self.assertEqual(
            booking_response.json()["reviewSlot"]["status"],
            "taken",
        )
        self.assertNotIn(
            "booking",
            booking_response.json()["reviewSlot"],
        )

        # Host listing exposes private booking details.
        host_list_response = self.client.get(
            reverse(
                "scheduling-api:host-review-slot-list"
            )
        )

        host_slot = next(
            slot
            for slot in host_list_response.json()["reviewSlots"]
            if slot["uuid"] == slot_uuid
        )

        self.assertEqual(host_slot["status"], "taken")
        self.assertEqual(
            host_slot["booking"]["email"],
            "andrej@example.com",
        )

        # Host deletes the taken slot and its Booking.
        delete_response = self.client.delete(
            reverse(
                "scheduling-api:host-review-slot-detail",
                kwargs={
                    "review_slot_uuid": slot_uuid,
                },
            )
        )

        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(
            ReviewSlot.objects.filter(uuid=slot_uuid).exists()
        )
        self.assertEqual(Booking.objects.count(), 0)

        # Public listing no longer contains the slot.
        final_public_response = self.client.get(
            reverse(
                "scheduling-api:public-review-slot-list"
            )
        )

        final_uuids = {
            slot["uuid"]
            for slot in final_public_response.json()["reviewSlots"]
        }

        self.assertNotIn(slot_uuid, final_uuids)
