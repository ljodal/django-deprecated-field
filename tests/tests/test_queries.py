import logging

import pytest
from django.test import override_settings

from deprecated_field import DeprecatedFieldAccessError

from ..models import Genre


def test_create_without_deprecated_field_not_in_db(db, caplog):
    """
    Ensure that we can created objects even if a deprecated field on the model
    does not exist in the database.
    """

    Genre.objects.create()
    assert not caplog.records


def test_create_with_deprecated_field_not_in_db(db, caplog):
    """
    Ensure that we can created objects even if a deprecated field that does
    not exist in the database is specified.
    """

    caplog.set_level(logging.ERROR)

    Genre.objects.create(name="test")
    assert (
        'Tried to set deprecated field "name" on instance of "tests.models.Genre"'
        in caplog.text
    )


def test_create_with_deprecated_field_not_in_db_strict(db, caplog):

    with override_settings(STRICT_DEPRECATED_FIELD=True):
        Genre.objects.create()


def test_create_with_deprecated_field_not_in_db_strict(db, caplog):

    with pytest.raises(DeprecatedFieldAccessError):
        with override_settings(STRICT_DEPRECATED_FIELD=True):
            Genre.objects.create(name="test")


def test_bulk_create_with_deprecated_field_not_in_db(db, caplog):
    """
    Ensure that we can created objects even if a deprecated field that does
    not exist in the database is specified.
    """

    genre = [Genre(name="rock"), Genre(name="roll")]

    caplog.set_level(logging.ERROR)
    caplog.clear()

    Genre.objects.bulk_create(genre)
    assert not caplog.records
