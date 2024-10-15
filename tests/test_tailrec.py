import pytest
from funstruct.tailrec import tco, tail_call

# pytest affects the default of 1000
RECURSION_LIMIT = 700


def test_no_tailrec_under_limit():
    def recurse(remaining: int):
        if remaining == 0:
            return 0
        return 1 + recurse(remaining - 1)

    limit = RECURSION_LIMIT
    total = recurse(limit)
    assert total == limit


def test_no_tailrec_stack_overflow():
    def recurse(remaining: int):
        if remaining == 0:
            return 0
        return 1 + recurse(remaining - 1)

    limit = RECURSION_LIMIT
    with pytest.raises(RecursionError):
        recurse(limit * 2)


def test_tailrec_recurses_beyond_decorated_1():
    @tco
    def recurse(remaining: int, acc: int = 0):
        if remaining == 0:
            return acc
        return tail_call(recurse)(remaining - 1, acc + 1)

    limit = RECURSION_LIMIT * 2
    count = recurse(limit)
    assert count == limit


def test_tailrec_recurses_beyond_decorated_2():
    def recurse(n: int):
        @tco
        def inner(remaining: int, acc: int):
            if remaining == 0:
                return acc
            return tail_call(inner)(remaining - 1, acc + 1)

        return inner(n, 0)

    limit = RECURSION_LIMIT * 2
    count = recurse(limit)
    assert count == limit


def test_no_tco_returns_trampoline():
    def recurse(n: int):
        def inner(remaining: int, acc: int):
            if remaining == 0:
                return acc
            return tail_call(inner)(remaining - 1, acc + 1)

        return inner(n, 0)

    limit = RECURSION_LIMIT * 2
    count = recurse(limit)
    assert type(count) != int


def test_no_tail_call_stack_overflow():
    def recurse(n: int):
        @tco
        def inner(remaining: int, acc: int):
            if remaining == 0:
                return acc
            return inner(remaining - 1, acc + 1)

        return inner(n, 0)

    with pytest.raises(RecursionError):
        recurse(RECURSION_LIMIT * 2)
