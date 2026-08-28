"""StateT — state monad transformer over any monad.

>>> from funstruct.monad.state_t import StateT
>>> from returns.result import Result
>>> inc = StateT(lambda s: Result.from_value((s + 1, s)))
>>> inc.run(0)
<Success: (1, 0)>
>>> StateT.pure(42, Result).run(0)
<Success: (0, 42)>
>>> inc.then(inc).run(0)
<Success: (2, 1)>
"""

from _funstruct._state_t import *  # noqa F403
