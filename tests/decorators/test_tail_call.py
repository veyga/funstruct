import pytest
import sys
from funstruct.decorators import TailCaller, tailcall

# pytest affects the default of 1000
RECURSION_LIMIT = 700

def n_called(remaining: int):
  if remaining == 0:
    return 0
  return 1 + n_called(remaining - 1)

# @pytest.mark.skip()
# def test_no_tailrec_under_limit():
#   limit = RECURSION_LIMIT
#   total = n_called(limit)
#   assert total == limit

# @pytest.mark.skip()
# def test_no_tailrec_stack_overflow():
#   limit = RECURSION_LIMIT
#   with pytest.raises(RecursionError):  # Expecting a RecursionError
#       n_called(limit * 2)

# @pytest.mark.skip()
# def test_tailrec_recurses_beyond():
#   limit = RECURSION_LIMIT * 2
#   count = n_called_tailrec(limit)
#   assert count == limit 

@TailCaller
def n_called_tailrec(remaining: int, acc:int = 0):
  if remaining == 0:
    return acc
  return tailcall(n_called_tailrec)(remaining -1, acc + 1)

def test_tailrec_recurses_beyond_decorated():
  limit = RECURSION_LIMIT * 2
  count = n_called_tailrec(limit)
  assert count == limit 
  print("count = ", count)
