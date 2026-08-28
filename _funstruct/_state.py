"""
Pure State monad.

``State[A]`` wraps ``S -> (S, A)``.
For stateful computation over monadic types, use ``StateT``.

Example::

    >>> from funstruct.monad import State
    >>> inc = State(lambda s: (s + 1, s))
    >>> inc.then(inc).then(inc).run(0)
    (3, 2)
    >>> (State.pure(1) >> (lambda x: State.pure(x + 10))).run(0)
    (0, 11)

"""

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad

_A = TypeVar("_A")
_B = TypeVar("_B")


class State(Monad, Generic[_A]):
    """Pure State monad: ``S -> (S, A)``.

    Always succeeds. No exceptions, no Result, no error rail.

    Haskell: ``State s a``
    Scala:   ``State[S, A]``
    """

    __slots__ = ("_run",)

    def __init__(self, run: Callable) -> None:
        self._run = run

    def run(self, initial_state) -> tuple:
        """Execute with initial state.

        Returns ``(final_state, value)``.
                >>> State.pure(10).run("any")
                ('any', 10)
        """
        return self._run(initial_state)

    def bind(self, f: Callable[[_A], "State[_B]"]) -> "State[_B]":
        """FlatMap: thread state, pass value to ``f`` returning next State.

        >>> State.pure(1).bind(lambda x: State.pure(x + 10)).run(0)
        (0, 11)
        >>> (State.pure(1) >> (lambda x: State.pure(x + 10))).run(0)
        (0, 11)
        """

        def inner(s):
            new_s, a = self._run(s)
            return f(a).run(new_s)

        return State(inner)

    __rshift__ = bind

    def map(self, f: Callable[[_A], _B]) -> "State[_B]":
        """Transform the produced value without touching state.

        >>> State.pure(5).map(lambda x: x * 2).run(0)
        (0, 10)
        """

        def inner(s):
            new_s, a = self._run(s)
            return (new_s, f(a))

        return State(inner)

    def ap(self, other) -> "State":
        """Applicative ap: run both, tuple the values."""
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    def then(self, next_state: "State[_B]") -> "State[_B]":
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: next_state)

    @classmethod
    def do(cls, gen_fn) -> "State":
        """Do-notation via generators. Flattens nested binds.

        Each `yield` extracts the value from a State (state threads through).
        """

        def _run(s):
            gen = gen_fn()
            try:
                monadic_val = next(gen)
                while True:
                    new_s, result = monadic_val.run(s)
                    s = new_s
                    monadic_val = gen.send(result)
            except StopIteration as e:
                return (s, e.value)

        return cls(_run)

    @classmethod
    def pure(cls, value) -> "State":
        """Lift a value without modifying state.

        >>> State.pure("hello").run(99)
        (99, 'hello')
        """
        return cls(lambda s: (s, value))

    @classmethod
    def get(cls) -> "State":
        """Produce current state as the value.

        >>> State.get().run(42)
        (42, 42)
        """
        return cls(lambda s: (s, s))

    @classmethod
    def modify(cls, f: Callable) -> "State":
        """Modify state, produce None.

        >>> State.modify(lambda s: s + 1).run(5)
        (6, None)
        """
        return cls(lambda s: (f(s), None))

    def __repr__(self) -> str:
        return f"State({self._run})"


__all__ = [
    "State",
]
