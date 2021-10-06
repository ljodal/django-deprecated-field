import logging

from django.conf import settings  # type: ignore
from django.db import models

logger = logging.getLogger(__name__)


class DeprecatedFieldAccessError(Exception):
    """
    Raised if a deprecated field is accessed in strict mode
    """


def log_or_raise(message_format: str, *args) -> None:
    """
    Either log an error message or if in strict mode raise an exception.
    """

    if getattr(settings, "STRICT_DEPRECATED_FIELD", None) is True:
        message = message_format % args
        raise DeprecatedFieldAccessError(message)

    logger.error(message_format, *args, stack_info=True)


class DeprecatedFieldDescriptor:
    """
    A descriptor for a deprecated field. Logs an error whenever it's accessed
    and always returns None.
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if instance:
            log_or_raise(
                'Accessed deprecated field "%s" on instance of "%s.%s"',
                self.field.name,
                instance.__class__.__module__,
                instance.__class__.__qualname__,
            )
        elif cls:
            log_or_raise(
                'Accessed deprecated field "%s" on model class "%s.%s"',
                self.field.name,
                cls.__module__,
                cls.__qualname__,
            )

    def __set__(self, instance, value) -> None:
        log_or_raise(
            'Tried to set deprecated field "%s" on instance of "%s.%s"',
            self.field.name,
            instance.__class__.__module__,
            instance.__class__.__qualname__,
        )


class Null(models.Expression):
    """
    An expression that always returns None.
    """

    def as_sql(self, compiler, connection):
        return "NULL", []


class DeprecatedField(models.Field):
    """
    A field that ensures a column can safely be removed from the database in
    a later deploy.

    This ensures that Django does not reference the field in queries by default,
    and if the field is explicitly referenced either an exception is raised or
    an error is raised. The column will still be referenced in the database if
    used in an .update() query, but in all other queries any reference to the
    column is replaced with a NULL literal.
    """

    concrete: bool
    descriptor_class = DeprecatedFieldDescriptor

    def __init__(self, original_field: models.Field) -> None:
        super().__init__()
        self.original_field = original_field

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only=private_only)
        self.concrete = False

    def clone(self):
        """
        This is where the magic happens. Instead of returning a copy of this
        field we return a copy of the underlying field. This method is called
        when the Django migrations system checks for changes, meaning that this
        ensures the deprecation is invisible to the migration system.
        """

        return self.original_field.clone()

    def get_col(self, alias, output_field=None):
        """
        Hook in to detect when the column is used in a query and replace the
        column reference with null literal in the query.

        Even though the field is marked as concrete=False, Django still allows
        it to be referenced in .values() and .values_list() queries. This will
        catch these cases and either raise an exception or log an error and
        set the selected value to "NULL" in the database query.
        """

        log_or_raise(
            'Deprecated field "%s" on "%s.%s" referenced in query',
            self.name,
            self.model.__module__,
            self.model.__qualname__,
        )
        return Null(output_field=output_field or self)

    def get_db_prep_save(self, value, connection):
        """
        Hook in to detect when the field is used in an update query.

        Even though the field is marked as concrete=False, Django still allows
        it to be referenced in .update(foo=bar) queries. This will catch these
        cases and log or raise an error.
        """

        log_or_raise(
            'Writing to deprecated field "%s" on "%s.%s"',
            self.name,
            self.model.__module__,
            self.model.__qualname__,
        )
        return self.get_db_prep_value(value, connection=connection, prepared=False)

    def get_default(self):
        """
        Hook into the logic Django uses to set a value on a model if one wasn't
        provided in __init__, create() or similar. This basically tells Django
        to not set a value, which we don't want for deprecated fields.
        """

        return models.DEFERRED


def deprecated(original_field: models.Field) -> DeprecatedField:
    """
    Mark a field as deprecated. This removes the field from queries against the
    database, so we can safely remove it from the database after this change
    has been rolled out.
    """

    # Make sure the original field is nullable
    original_field.null = True

    return DeprecatedField(original_field=original_field)


__all__ = ["deprecated", "DeprecatedFieldAccessError"]
