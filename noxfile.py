import pathlib

import nox


def get_requirements_file(session) -> str:
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

    return requirements_file


@nox.session()
@nox.parametrize("django", ["3.1", "3.2"])
def tests(session, django):
    session.install(
        "pip",
        "install",
        # Using --constraints ensures that we install
        # the version of the dependencies that we have
        # specified in that requirements file.
        "--constraint",
        get_requirements_file(session),
        "pytest",
        "pytest-django",
    )
    session.install(f"django=={django}")
    session.run("python", "-m", "pytest")
