from django.db import models  # type: ignore

from .expressions import Null
from .utils import log_or_raise


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
        This is where the magic happens. Instead of returning a copye of this
        field we return a copy of the underlaying field. This method is called
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
