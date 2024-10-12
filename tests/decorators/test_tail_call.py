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


def test_tailrec_recurses_beyond_decorated_1():
    @TailCaller
    def recurse(remaining: int, acc: int = 0):
        if remaining == 0:
            return acc
        return tailcall(recurse)(remaining - 1, acc + 1)

    limit = RECURSION_LIMIT * 2
    count = recurse(limit)
    assert count == limit


def test_tailrec_recurses_beyond_decorated_2():
    def recurse(n: int):
        @TailCaller
        def inner(remaining: int, acc: int):
            if remaining == 0:
                return acc
            return tailcall(inner)(remaining - 1, acc + 1)

        return inner(n, 0)

    limit = RECURSION_LIMIT * 2
    count = recurse(limit)
    assert count == limit


# def test_tailrec_recurses_beyond_decorated_yo():
#   limit = RECURSION_LIMIT * 2
#   count = recurse_n_times(limit)
#   assert count == limit
