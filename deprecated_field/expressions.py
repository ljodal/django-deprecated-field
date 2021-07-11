from django.db import models


class Null(models.Expression):
    """
    An expression that always returns None.
    """

    def as_sql(self, compiler, connection):
        return "NULL", []
