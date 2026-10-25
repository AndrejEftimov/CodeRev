from datetime import datetime

from django.utils import timezone


#======================================
# DATETIME VALIDATION
#======================================

def validate_aware_datetime(value, field_name, *, error_class=ValueError):
    """Require a timezone-aware datetime value."""

    if not isinstance(value, datetime):
        raise error_class(
            f"{field_name} must be a valid datetime."
        )

    if timezone.is_naive(value):
        raise error_class(
            f"{field_name} must be timezone-aware."
        )
