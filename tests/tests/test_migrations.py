from django.apps import apps
from django.core.management import call_command
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.operations import AlterField
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.state import ProjectState
from django.db.models import CharField


def test_make_migrations_deprecated_field(db, capsys):

    call_command("makemigrations", "--dry-run", "--no-input", "tests")

    captured = capsys.readouterr()
    assert "Alter field name on artist" in captured.out


def test_state_introspection():
    loader = MigrationLoader(None, ignore_no_migrations=True)

    questioner = NonInteractiveMigrationQuestioner(
        specified_apps=["tests"], dry_run=True
    )
    # Set up autodetector
    autodetector = MigrationAutodetector(
        loader.project_state(),
        ProjectState.from_apps(apps),
        questioner,
    )

    # Detect changes
    changes = autodetector.changes(
        graph=loader.graph,
        trim_to_apps=["tests"],
        convert_apps=["tests"],
        migration_name=None,
    )

    assert "tests" in changes
    assert len(changes["tests"]) == 1

    migration = changes["tests"][0]
    operations = migration.operations

    for operation in operations:
        print(operation)

    assert len(operations) == 2

    operation = next(
        operation
        for operation in operations
        if isinstance(operation, AlterField)
        and operation.model_name == "artist"
        and operation.name == "name"
    )

    assert isinstance(operation.field, CharField)
    assert operation.field.null is True
    assert operation.field.max_length == 256
