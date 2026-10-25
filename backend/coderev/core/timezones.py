from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone


def get_display_timezone():
    """Return CodeRev's configured presentation timezone."""

    return ZoneInfo(settings.CODEREV_DISPLAY_TIME_ZONE)


def to_display_datetime(value):
    """Convert an aware datetime to CodeRev's presentation timezone."""

    if timezone.is_naive(value):
        raise ValueError("Expected a timezone-aware datetime.")

    return timezone.localtime(
        value,
        get_display_timezone(),
    )


def to_display_date_time_parts(value):
    """Return API date/time strings in CodeRev's display timezone."""

    display_value = to_display_datetime(value)

    return (
        display_value.strftime("%Y-%m-%d"),
        display_value.strftime("%H:%M"),
    )
