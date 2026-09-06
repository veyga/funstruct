"""State monad — pure stateful computation without mutation.

Examples:
    >>> from funstruct.monad.state import State
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
from typing import Any, Generic, TypeVar

from funstruct.typeclasses._dot_notation import DotNotation

_A = TypeVar("_A")
_B = TypeVar("_B")


class State(DotNotation, Generic[_A]):
    """Pure State monad: ``S -> (S, A)``."""

    def __init__(self, run: Callable[[Any], tuple[Any, _A]]) -> None:
        self._run = run

    def run(self, initial_state) -> tuple:
        """Execute with initial state. Returns ``(final_state, value)``.

        >>> State.pure(10).run("any")
        ('any', 10)
        """
        return self._run(initial_state)

    def bind(self, f: Callable[[_A], State[_B]]) -> State[_B]:
        """>>> State.pure(1).bind(lambda x: State.pure(x + 10)).run(0)
        (0, 11)
        """
        def inner(s):
            new_s, a = self._run(s)
            return f(a).run(new_s)
        return State(inner)

    @classmethod
    def do(cls, gen_fn) -> Callable[..., State]:
        """Do-notation via generators. Returns a callable.

        >>> def pipeline():
        ...     x = yield State(lambda s: (s + 1, s))
        ...     y = yield State(lambda s: (s + 1, s))
        ...     return x + y
        >>> State.do(pipeline)().run(0)
        (2, 1)
        """
        def _thunk(*args, **kwargs):
            def _run(s):
                gen = gen_fn(*args, **kwargs)
                try:
                    monadic_val = next(gen)
                    while True:
                        new_s, result = monadic_val.run(s)
                        s = new_s
                        monadic_val = gen.send(result)
                except StopIteration as e:
                    return (s, e.value)
            return cls(_run)
        return _thunk

    @classmethod
    def pure(cls, value) -> State:
        """Lift a value without modifying state.

        >>> State.pure("hello").run(99)
        (99, 'hello')
        """
        return cls(lambda s: (s, value))

    @classmethod
    def get(cls) -> State:
        """Produce current state as the value.

        >>> State.get().run(42)
        (42, 42)
        """
        return cls(lambda s: (s, s))

    @classmethod
    def modify(cls, f: Callable[[Any], Any]) -> State:
        """Modify state, produce None.

        >>> State.modify(lambda s: s + 1).run(5)
        (6, None)
        """
        return cls(lambda s: (f(s), None))

    def __repr__(self) -> str:
        return f"State({self._run})"


State._type_constructor = State

import funstruct.monad.state.instances  # noqa: E402, F401

__all__ = [
    "State",
]
