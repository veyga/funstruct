import asyncio

import pytest

from funstruct.util.tailrec import tail_call, tco, tco_async

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
    assert type(count) is not int


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


class TestTcoAsync:
    def test_async_sum(self):
        @tco_async
        async def async_sum(n, acc=0):
            if n == 0:
                return acc
            return tail_call(async_sum)(n - 1, acc + n)

        assert asyncio.run(async_sum(100)) == 5050

    def test_async_beyond_recursion_limit(self):
        @tco_async
        async def async_sum(n, acc=0):
            if n == 0:
                return acc
            return tail_call(async_sum)(n - 1, acc + n)

        limit = RECURSION_LIMIT * 2
        result = asyncio.run(async_sum(limit))
        assert result == limit * (limit + 1) // 2

    def test_async_without_tco_returns_tail_call(self):
        """Without @tco_async, async functions return _tail_call objects."""

        async def async_sum(n, acc=0):
            if n == 0:
                return acc
            return tail_call(async_sum)(n - 1, acc + n)

        result = asyncio.run(async_sum(5))
        assert type(result) is not int
