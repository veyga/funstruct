"""ReaderT — reader monad transformer over any monad.

>>> from funstruct.monad.reader_t import ReaderT
>>> from returns.result import Result, Success
>>> step = ReaderT(lambda ctx: Result.from_value(ctx + 1))
>>> step.run(5)
<Success: 6>
>>> ReaderT.pure(42, Result).run("ignored")
<Success: 42>
"""

from _funstruct._reader_t import *  # noqa F403
