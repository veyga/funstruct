import nox

nox.options.default_venv_backend = "uv"


@nox.session(python=["3.10", "3.11", "3.12", "3.13", "3.14"])
def tests(session):
    """Run the test suite."""
    session.install(".", "--group", "dev")
    session.run("pytest", "tests/", "funstruct/")


@nox.session
def lint(session):
    """Run ruff linter."""
    session.install("ruff")
    session.run("ruff", "check", "funstruct/")


@nox.session
def typecheck(session):
    """Run type checker."""
    session.install(".", "--group", "dev")
    session.run("ty", "check")


@nox.session
def typecheck_compat(session):
    """Type-check core library against Python 3.10 (minimum supported)."""
    session.install(".", "--group", "dev")
    session.run(
        "ty", "check",
        "--python-version", "3.10",
        "--exclude", "funstruct/playground/",
        "--exclude", "tests/",
        "--exclude", "docs/",
        "--exclude", "benchmarks/",
    )


@nox.session
def docs(session):
    """Build documentation."""
    session.install(".", "--group", "docs")
    session.run("mkdocs", "build")
