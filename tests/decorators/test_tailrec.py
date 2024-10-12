import pytest
import sys
from funstruct.decorators import tailrec


def test_no_tailrec_stack_overflow():
  def n_called(remaining: int):
    if remaining == 0:
      return 0
    return 1 + n_called(remaining - 1)

  total = n_called(100)
  assert total == 100

