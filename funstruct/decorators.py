

class TailCall(object):
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def handle(self):
        if type(self.call) is TailCaller:
            return self.call.f(*self.args, **self.kwargs)
        else:
            return self.call(*self.args, **self.kwargs)

class TailCaller(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        ret = self.f(*args, **kwargs)
        while type(ret) is TailCall:
            ret = ret.handle()
        return ret

# def tail_call(fn):
#     """
#     Allows a function as tail recursive call.
#     This allows recursive functions to not blow the call stack.
#     Use in conjunction with @tco
#     (use with caution)
#     """

#     def wrapper(*args, **kwargs):
#         return fn(*args, **kwargs)

#     return wrapper

def tailcall(f) :
    def _f(*args, **kwargs) :
        return TailCall(f, *args, **kwargs)
    return _f
