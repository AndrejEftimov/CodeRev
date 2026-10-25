from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot


@override_settings(DEBUG=True, CODEREV_DISPLAY_TIME_ZONE="Europe/Skopje")
class SeedReviewSlotsCommandTests(TestCase):
    """Verify demo coverage, rollback, and destructive-operation safeguards."""

    def run_seed(self, *arguments):
        output = StringIO()
        call_command("seed_review_slots", *arguments, stdout=output)
        return output.getvalue()

    def test_seed_creates_history_started_and_mixed_future_slots(self):
        self.run_seed("--days", "2")
        now = timezone.now()

        self.assertEqual(ReviewSlot.objects.count(), 12)
        self.assertEqual(Booking.objects.count(), 7)
        self.assertEqual(ReviewSlot.objects.filter(end_at__lte=now).count(), 1)
        self.assertEqual(ReviewSlot.objects.filter(start_at__lte=now, end_at__gt=now).count(), 1)
        self.assertEqual(ReviewSlot.objects.filter(start_at__gt=now).count(), 10)

    def test_nonempty_database_is_not_overwritten(self):
        self.run_seed("--days", "1")
        with self.assertRaisesMessage(CommandError, "Scheduling data already exists"):
            self.run_seed("--days", "1")
        self.assertEqual(ReviewSlot.objects.count(), 7)

    def test_reset_requires_explicit_confirmation(self):
        self.run_seed("--days", "2")
        with self.assertRaisesMessage(CommandError, "--confirm-reset"):
            self.run_seed("--reset", "--days", "1")
        self.assertEqual(ReviewSlot.objects.count(), 12)
        self.run_seed("--reset", "--confirm-reset", "--days", "1")
        self.assertEqual(ReviewSlot.objects.count(), 7)

    def test_dry_run_rolls_back_new_data(self):
        self.assertIn("rolled back", self.run_seed("--dry-run", "--days", "1"))
        self.assertEqual(ReviewSlot.objects.count(), 0)
        self.assertEqual(Booking.objects.count(), 0)

    def test_dry_run_reset_preserves_existing_data(self):
        self.run_seed("--days", "2")
        original_ids = set(ReviewSlot.objects.values_list("pk", flat=True))
        self.run_seed("--reset", "--confirm-reset", "--dry-run", "--days", "1")
        self.assertEqual(set(ReviewSlot.objects.values_list("pk", flat=True)), original_ids)

    def test_invalid_options_do_not_touch_database(self):
        for arguments in (("--days", "0"), ("--days", "31"), ("--confirm-reset",)):
            with self.subTest(arguments=arguments):
                with self.assertRaises(CommandError):
                    self.run_seed(*arguments)
        self.assertFalse(ReviewSlot.objects.exists())

    @override_settings(DEBUG=False)
    def test_refuses_non_debug_environment(self):
        with self.assertRaisesMessage(CommandError, "DEBUG=False"):
            self.run_seed("--days", "1")
