# List all available commands
_default:
  just --list

# debug an individual test under tests/
dtest TEST:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest tests/{{TEST}}

# debug a script
dscript FILE:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client {{FILE}}

# Run all test suites
tests:
  pytest

# run an individual test under tests/
test TEST:
  pytest tests/{{TEST}}
