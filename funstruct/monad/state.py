"""State monad — pure stateful computation without mutation.

>>> from funstruct.monad.state import State
>>> inc = State(lambda s: (s + 1, s))
>>> inc.run(0)
(1, 0)
>>> (inc >> (lambda _: inc)).run(0)
(2, 1)
>>> State.pure(42).run(99)
(99, 42)
"""

from _funstruct._state import *  # noqa F403
