from datetime import datetime, timedelta, timezone as datetime_timezone

from django.test import SimpleTestCase, override_settings

from core.timezones import (
    get_display_timezone,
    to_display_date_time_parts,
    to_display_datetime,
)


@override_settings(
    TIME_ZONE="UTC",
    USE_TZ=True,
    CODEREV_DISPLAY_TIME_ZONE="Europe/Skopje",
)
class TimezonePresentationTests(SimpleTestCase):
    """Regression tests for CodeRev display-timezone handling."""

    #======================================
    # CONFIGURATION
    #======================================

    def test_django_timezone_remains_utc(self):
        from django.conf import settings

        self.assertEqual(settings.TIME_ZONE, "UTC")
        self.assertTrue(settings.USE_TZ)
        self.assertEqual(
            settings.CODEREV_DISPLAY_TIME_ZONE,
            "Europe/Skopje",
        )

    def test_display_timezone_is_configured_separately(self):
        self.assertEqual(
            get_display_timezone().key,
            "Europe/Skopje",
        )

    #======================================
    # DST PRESENTATION
    #======================================

    def test_converts_utc_instant_after_dst_change_to_display_time(self):
        instant = datetime(
            2026,
            10,
            25,
            19,
            3,
            tzinfo=datetime_timezone.utc,
        )

        display_value = to_display_datetime(instant)

        self.assertEqual(
            display_value.strftime("%Y-%m-%d %H:%M %z"),
            "2026-10-25 20:03 +0100",
        )

    def test_distinguishes_repeated_wall_clock_hour(self):
        before_fallback = datetime(
            2026,
            10,
            25,
            0,
            30,
            tzinfo=datetime_timezone.utc,
        )
        after_fallback = datetime(
            2026,
            10,
            25,
            1,
            30,
            tzinfo=datetime_timezone.utc,
        )

        before_local = to_display_datetime(before_fallback)
        after_local = to_display_datetime(after_fallback)

        self.assertEqual(before_local.strftime("%H:%M %z"), "02:30 +0200")
        self.assertEqual(after_local.strftime("%H:%M %z"), "02:30 +0100")

    def test_api_parts_use_display_timezone(self):
        instant = datetime(
            2026,
            10,
            25,
            19,
            46,
            tzinfo=datetime_timezone.utc,
        )

        date_value, time_value = to_display_date_time_parts(instant)

        self.assertEqual(date_value, "2026-10-25")
        self.assertEqual(time_value, "20:46")

    #======================================
    # ABSOLUTE TIME
    #======================================

    def test_duration_across_dst_change_uses_absolute_instants(self):
        start_at = datetime(
            2026,
            10,
            25,
            0,
            45,
            tzinfo=datetime_timezone.utc,
        )
        end_at = start_at + timedelta(minutes=30)

        self.assertEqual(
            (end_at - start_at).total_seconds() / 60,
            30,
        )
