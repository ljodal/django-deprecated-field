import logging

import pytest
from django.test import override_settings

from deprecated_field.utils import DeprecatedFieldAccessError

from ..models import Genre


def test_init_without_deprecated_field_not_in_db(db, caplog):

    caplog.set_level(logging.ERROR)

    Genre()
    assert not caplog.records


def test_init_with_deprecated_field_not_in_db(db, caplog):

    caplog.set_level(logging.ERROR)

    Genre(name="test")
    assert (
        'Tried to set deprecated field "name" on instance of "tests.models.Genre"'
        in caplog.text
    )


def test_init_with_deprecated_field_not_in_db_strict(db, caplog):

    with pytest.raises(DeprecatedFieldAccessError):
        with override_settings(STRICT_DEPRECATED_FIELD=True):
            Genre(name="test")
