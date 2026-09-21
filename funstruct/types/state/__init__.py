"""State monad — pure stateful computation without mutation.

Examples:
    >>> from funstruct.types.state import State
    >>> inc = State(lambda s: (s + 1, s))
    >>> inc.run(0)
    (1, 0)
    >>> (inc >> (lambda _: inc)).run(0)
    (2, 1)
    >>> State.pure(42).run(99)
    (99, 42)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType

_S = TypeVar("_S")
_A = TypeVar("_A")
_B = TypeVar("_B")


class State(DataType, Generic[_S, _A]):
    """Pure State monad: ``S -> (S, A)``."""

    def __init__(self, run: Callable[[_S], tuple[_S, _A]]) -> None:
        self._run = run

    def run(self, initial_state: _S) -> tuple[_S, _A]:
        """Execute with initial state. Returns ``(final_state, value)``.

        >>> State.pure(10).run("any")
        ('any', 10)
        """
        return self._run(initial_state)

    @staticmethod
    def get() -> State[_S, _S]:
        """Produce current state as the value.

        >>> State.get().run(42)
        (42, 42)
        """
        return State(lambda s: (s, s))

    @staticmethod
    def modify(f: Callable[[_S], _S]) -> State[_S, None]:
        """Modify state, produce None.

        >>> State.modify(lambda s: s + 1).run(5)
        (6, None)
        """
        return State(lambda s: (f(s), None))


import funstruct.types.state.instances  # noqa: E402, F401

__all__ = [
    "State",
]
