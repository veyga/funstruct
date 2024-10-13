class _tail_call(object):
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def handle(self):
        if type(self.call) is tco:
            return self.call.f(*self.args, **self.kwargs)
        else:
            return self.call(*self.args, **self.kwargs)


class tco(object):
    """
    Marks a function as tail_call optimized
    [see tail_call]
    """

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        ret = self.f(*args, **kwargs)
        while type(ret) is _tail_call:
            ret = ret.handle()
        return ret


def tail_call(f):
    """
    Calls a f
    Allows a function as tail recursive call.
    This allows recursive functions to not blow the call stack.
    Use in conjunction with @tco
    (use with caution)
    Example:

    def sum_up_to(n: int):
        @tco
        def inner(remaining: int, acc: int):
            if remaining == 0:
                return acc
            return tail_call(inner)(remaining - 1, acc + 1)

        return inner(n, 0)
    """

    def _f(*args, **kwargs):
        return _tail_call(f, *args, **kwargs)

    return _f


__all__ = [
    "tco",
    "tail_call",
]
