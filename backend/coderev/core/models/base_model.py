from django.db import models

from .timestamp_mixin import TimestampMixin

from uuid import uuid4


class BaseModel(TimestampMixin):
    """
    Abstract base model. Built for this project's needs.
    """

    uuid = models.UUIDField(
        default=uuid4,
        editable=False,
        unique=True,
    )

    ########################

    class Meta:
        abstract=True
