import nox

nox.options.default_venv_backend = "uv"


@nox.session(python=["3.10", "3.11", "3.12"])
def tests(session):
    """Run the test suite."""
    session.install(".", "--group", "dev")
    session.run("pytest", "tests/", "funstruct/")


@nox.session
def lint(session):
    """Run ruff linter."""
    session.install("ruff")
    session.run("ruff", "check", "_funstruct/", "funstruct/")


@nox.session
def typecheck(session):
    """Run type checker."""
    session.install(".", "--group", "dev")
    session.run("ty", "check", "_funstruct/")


@nox.session
def docs(session):
    """Build documentation."""
    session.install(".", "--group", "docs")
    session.run("mkdocs", "build")
