# List all available commands
_default:
  just --list

# debug an individual test under tests/
dtest TEST:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest tests/{{TEST}}

# debug an individual test with -k flag
dktest ARG:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest -k {{ARG}}

# debug a script
dscript FILE:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client {{FILE}}

# format the repo
format:
  poetry run ruff format

# install the pre-commit hooks
installhooks:
  poetry run pre-commit install

# lint the repo
lint:
  poetry run ruff check

# lint the repo (+ auto-fix)
lintfix:
  poetry run ruff check --fix

# Run all test suites
tests:
  pytest

# run an individual test under tests/
test TEST:
  pytest tests/{{TEST}}

# run an individual test with -k flag
ktest ARG:
  pytest -k {{ARG}}

# run typechecker
tc:
  poetry run mypy --enable-incomplete-feature=NewGenericSyntax # py3.12 generics
