from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email


#======================================
# EMAIL VALIDATION
#======================================

def validate_email(value, field_name):
    """Validate and normalize a required email address."""

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} is required."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            f"{field_name} is required."
        )

    try:
        django_validate_email(value)
    except ValidationError as error:
        raise ValueError(
            "Enter a valid email address."
        ) from error

    return value
