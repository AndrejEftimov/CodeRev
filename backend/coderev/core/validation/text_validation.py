def normalize_required_text(value, field_name, *, max_length=None):
    """Trim and validate a required text value."""

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    value = value.strip()

    if not value:
        raise ValueError(f"{field_name} is required.")

    if max_length is not None and len(value) > max_length:
        raise ValueError(
            f"{field_name} must be at most {max_length} characters."
        )

    return value


def normalize_optional_text(value, field_name, *, max_length=None):
    """Trim and validate an optional text value."""

    if value is None:
        return ""

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    value = value.strip()

    if max_length is not None and len(value) > max_length:
        raise ValueError(
            f"{field_name} must be at most {max_length} characters."
        )

    return value
