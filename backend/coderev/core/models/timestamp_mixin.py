from django.db import models


class TimestampMixin(models.Model):
    """
    Abstract entity which contains basic timestamps:
    - created_at
    - updated_at
    """

    ########################

    created_at = models.DateTimeField(
        'Created at',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        'Updated at',
        auto_now=True
    )

    ########################

    class Meta:
        abstract=True
