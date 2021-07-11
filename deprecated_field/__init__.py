from django.db import models

from .fields import DeprecatedField


def deprecated(original_field: models.Field) -> DeprecatedField:
    """
    Mark a field as deprecated. This removes the field from queries against the
    database, so we can safely remove it from the database after this change
    has been rolled out.
    """

    # Make sure the original field is nullable
    original_field.null = True

    return DeprecatedField(original_field=original_field)


__all__ = ["deprecated"]
