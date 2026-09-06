"""Trampoline-based tail recursion.

Examples:
    >>> from funstruct.util.tailrec import tco, tail_call
    >>> @tco
    ... def sum_up_to(n, acc=0):
    ...     if n == 0:
    ...         return acc
    ...     return tail_call(sum_up_to)(n - 1, acc + n)
    >>> sum_up_to(100)
    5050
"""


class _tail_call:
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def handle(self):
        if type(self.call) is tco:
            return self.call.f(*self.args, **self.kwargs)
        else:
            return self.call(*self.args, **self.kwargs)

    async def handle_async(self):
        if type(self.call) is tco_async:
            return await self.call.f(*self.args, **self.kwargs)
        else:
            return await self.call(*self.args, **self.kwargs)


class tco:
    """Marks a function as tail-call optimized.

    Use with tail_call to avoid blowing the call stack on recursive functions.
    """

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        ret = self.f(*args, **kwargs)
        while type(ret) is _tail_call:
            ret = ret.handle()
        return ret


class tco_async:
    """Marks an async function as tail-call optimized.

    Same as @tco but for async functions — awaits each step.

    Example::

        @tco_async
        async def async_sum(n, acc=0):
            if n == 0:
                return acc
            return tail_call(async_sum)(n - 1, acc + n)

        await async_sum(10000)  # no stack overflow
    """

    def __init__(self, f):
        self.f = f

    async def __call__(self, *args, **kwargs):
        ret = await self.f(*args, **kwargs)
        while type(ret) is _tail_call:
            ret = await ret.handle_async()
        return ret


def tail_call(f):
    """Call a tail-recursive function.

    Use in conjunction with @tco.

    Example::

        @tco
        def sum_up_to(n, acc=0):
            if n == 0:
                return acc
            return tail_call(sum_up_to)(n - 1, acc + n)

        sum_up_to(10000)  # no stack overflow
    """

    def _f(*args, **kwargs):
        return _tail_call(f, *args, **kwargs)

    return _f


__all__ = [
    "tco",
    "tco_async",
    "tail_call",
]
