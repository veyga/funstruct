_default:
  just --list

# install project
install:
  uv sync

# lint (--fix)
lint *args:
  uv run ruff check {{args}}

# format code
format:
  uv run ruff format

# Serve docs locally at http://127.0.0.1:8000
docs:
  uv run mkdocs serve

# docs-build:
#   uv run mkdocs build

# run pytest
test *args:
  uv run pytest {{args}}

# debug a pytest
dtest *args:
  PYDEVD_DISABLE_FILE_VALIDATION=1 uv run python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest {{args}}
