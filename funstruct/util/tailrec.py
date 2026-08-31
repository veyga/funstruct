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
    "tail_call",
]
