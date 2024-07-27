tests:
  pytest

dtests:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest

test TEST:
  pytest {{TEST}}

dtest TEST:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m pytest {{TEST}}

dscript FILE:
  python -m debugpy --listen 0.0.0.0:5680 --wait-for-client {{FILE}}
