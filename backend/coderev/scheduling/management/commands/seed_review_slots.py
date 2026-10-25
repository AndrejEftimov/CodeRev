from datetime import datetime, time, timedelta, timezone as utc_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from scheduling.models import Booking, ReviewSlot
from scheduling.services import create_booking, create_review_slot


# Representative booking details for the host cards and Details modal.
BOOKING_EXAMPLES = (
    ("Mila Petrova", "mila@example.com", "API validation", "Check field-level errors and response consistency."),
    ("Daniel Kim", "daniel@example.com", "Pagination", "Review page boundaries and empty states."),
    ("Sara Ahmed", "sara@example.com", "Concurrency", "Discuss booking races and database constraints."),
    ("Leo Martin", "leo@example.com", "Frontend components", "Review component boundaries and responsive layouts."),
    ("Nora Evans", "nora@example.com", "Accessibility", "Inspect keyboard navigation and modal focus."),
    ("Alex Rivera", "alex@example.com", "Timezones and DST", "Review absolute times and displayed local times."),
    ("Iva Novak", "iva@example.com", "Database constraints", "Check exclusion and uniqueness guarantees."),
    ("Owen Chen", "owen@example.com", "UI state", "Discuss loading, retry, and conflict handling."),
)

DAILY_SCHEDULE = (
    (time(9), 30),
    (time(10), 45),
    (time(11, 30), 60),
    (time(14), 15),
    (time(15), 30),
)


class Command(BaseCommand):
    """Seed representative scheduling data in a development database."""

    help = "Create demo slots and bookings (development only)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, metavar="N", help="Future days to seed (1-30; default: 7).")
        parser.add_argument("--dry-run", action="store_true", help="Validate without saving changes.")
        parser.add_argument("--reset", action="store_true", help="Replace all existing scheduling data.")
        parser.add_argument("--confirm-reset", action="store_true", help="Confirm permanent deletion with --reset.")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Seeding is disabled when DEBUG=False.")
        if not 1 <= options["days"] <= 30:
            raise CommandError("--days must be between 1 and 30.")
        if options["confirm_reset"] and not options["reset"]:
            raise CommandError("--confirm-reset requires --reset.")
        if options["reset"] and not options["confirm_reset"]:
            raise CommandError("--reset deletes all slots and bookings. Add --confirm-reset to proceed.")

        zone_name = getattr(settings, "CODEREV_DISPLAY_TIME_ZONE", "Europe/Skopje")
        try:
            zone = ZoneInfo(zone_name)
        except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
            raise CommandError(f"Invalid display timezone: {zone_name!r}.") from exc

        with transaction.atomic():
            if options["reset"]:
                ReviewSlot.objects.all().delete()  # Bookings cascade with their slots.
            elif ReviewSlot.objects.exists() or Booking.objects.exists():
                raise CommandError(
                    "Scheduling data already exists. No changes made. "
                    "To replace ALL scheduling data, use --reset --confirm-reset."
                )

            slot_count, booking_count = self._seed(zone, options["days"])
            if options["dry_run"]:
                transaction.set_rollback(True)

        outcome = "Dry run (rolled back)" if options["dry_run"] else "Seed complete"
        self.stdout.write(self.style.SUCCESS(
            f"{outcome}: {slot_count} slots, {booking_count} bookings "
            f"(1 historical, 1 started, {options['days'] * len(DAILY_SCHEDULE)} future) "
            f"across {options['days']} future days [{zone_name}]."
        ))

    def _seed(self, zone, days):
        now = timezone.now()
        today = now.astimezone(zone).date()
        bookings = 0

        # Historical/started slots cannot use the future-only creation/booking services.
        for start_at, end_at, example in (
            (now - timedelta(days=2, hours=1), now - timedelta(days=2), BOOKING_EXAMPLES[0]),
            (now - timedelta(minutes=10), now + timedelta(minutes=35), BOOKING_EXAMPLES[1]),
        ):
            slot = ReviewSlot.objects.create(start_at=start_at, end_at=end_at)
            self._book(slot, example, historical=True)
            bookings += 1

        for day_index in range(days):
            date = today + timedelta(days=day_index + 1)
            for slot_index, (start_time, minutes) in enumerate(DAILY_SCHEDULE):
                start_at = datetime.combine(date, start_time, tzinfo=zone)
                end_at = start_at.astimezone(utc_timezone.utc) + timedelta(minutes=minutes)
                slot = create_review_slot(start_at=start_at, end_at=end_at)

                if (day_index + slot_index) % 2 == 0:
                    example_index = (day_index * len(DAILY_SCHEDULE) + slot_index) % len(BOOKING_EXAMPLES)
                    self._book(slot, BOOKING_EXAMPLES[example_index])
                    bookings += 1

        return 2 + days * len(DAILY_SCHEDULE), bookings

    @staticmethod
    def _book(slot, example, *, historical=False):
        name, email, topic, description = example
        details = dict(name=name, email=email, review_topic=topic, review_description=description)
        if historical:
            Booking.objects.create(review_slot=slot, **details)
        else:
            create_booking(review_slot_uuid=slot.uuid, **details)
