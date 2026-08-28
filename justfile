_default:
  just --list

# lint (--fix)
lint *args:
  uv run ruff check {{args}}

# format code
format:
  uv run ruff format
  uv run --group docs docformatter --in-place --config pyproject.toml _funstruct/ funstruct/

# run ty check
check:
  uv run ty check _funstruct/

# Serve docs locally at http://127.0.0.1:8000
docs:
  uv run --group docs mkdocs serve

# Format markdown docs
fmt-docs:
  uv run --group docs mdformat docs/ README.md

# run pytest
test *args:
  uv run pytest {{args}}

# debug a pytest
dtest *args:
  PYDEVD_DISABLE_FILE_VALIDATION=1 uv run python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest {{args}}

# Run tox (all versions, or specify: mise tox -e py312)
tox *args:
  uv run tox

# docs-build:
#   uv run mkdocs build
