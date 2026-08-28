_default:
  just --list

# lint (--fix)
lint *args:
  uv run ruff check {{args}}

# format code
format:
  uv run ruff format
  -uv run --group docs docformatter --in-place --config pyproject.toml funstruct/

# run ty check
check:
  uv run ty check funstruct/

# Serve docs locally at http://127.0.0.1:8000
docs:
  uv run --group docs mkdocs serve

# Format markdown docs
fmt-docs:
  uv run --group docs mdformat docs/ README.md

# run pytest
test *args:
  uv run pytest {{args}}

# run pytest with coverage (pass 'html' to open browser report)
cover *args:
  #!/usr/bin/env bash
  if [[ "{{args}}" == *"html"* ]]; then
    uv run pytest --cov --cov-report=html
    {{ if os() == "macos" { "open" } else { "xdg-open" } }} htmlcov/index.html
  else
    uv run pytest --cov --cov-report=term-missing {{args}}
  fi

# debug a pytest
dtest *args:
  PYDEVD_DISABLE_FILE_VALIDATION=1 uv run python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest {{args}}

# run benchmarks (pass 'html' to generate histogram and open in browser)
# --benchmark-disable-gc pauses GC only during each timed iteration,
# not the whole process. Prevents GC pauses from skewing measurements.
bench *args:
  #!/usr/bin/env bash
  if [[ "{{args}}" == *"html"* ]]; then
    uv run pytest benchmarks/ -v --benchmark-only --benchmark-disable-gc --benchmark-histogram=.benchmarks/histogram
    {{ if os() == "macos" { "open" } else { "xdg-open" } }} .benchmarks/histogram.svg
  else
    uv run pytest benchmarks/ -v --benchmark-only --benchmark-disable-gc {{args}}
  fi


# Run nox (all sessions, or specify: just nox -s tests)
nox *args:
  uv run nox {{args}}

# docs-build:
#   uv run mkdocs build
