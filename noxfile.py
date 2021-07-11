import pathlib

import nox

DJANGO_VERSIONS = ["3.1", "3.2"]
LOCATIONS = ["deprecated_field", "tests"]


def install(*deps: str, session) -> None:
    """
    Helper to install dependencies constrained by Poetry's lock file.
    """

    tmpdir = pathlib.Path(session._runner.envdir) / "tmp"
    tmpdir.mkdir(exist_ok=True, parents=True)
    requirements_file = str(tmpdir / "requirements.txt")

    session.run(
        "poetry",
        "export",
        "--format",
        "requirements.txt",
        "--without-hashes",
        "-o",
        requirements_file,
        external=True,
    )

    session.install("--constraint", requirements_file, *deps)


@nox.session()
@nox.parametrize("django_version", DJANGO_VERSIONS)
def tests(session, django_version):
    install("pytest", "pytest-django", session=session)
    session.install(f"django=={django_version}")
    session.run("python", "-m", "pytest")


@nox.session()
@nox.parametrize("django_version", DJANGO_VERSIONS)
def mypy(session, django_version):
    install("mypy", "django-stubs", "pytest", session=session)
    session.install(f"django=={django_version}")
    session.run("mypy", *LOCATIONS)


@nox.session()
def black(session):
    install("black", session=session)
    session.run("black", *LOCATIONS)


@nox.session()
def flake8(session):
    install("flake8", session=session)
    session.run("flake8", *LOCATIONS)


@nox.session()
def isort(session):
    install("django", "isort", "pytest", session=session)
    session.run("isort", "--check-only", *LOCATIONS)
