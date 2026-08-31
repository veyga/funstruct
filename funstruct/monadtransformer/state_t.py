"""StateT — state monad transformer over any monad.

Examples:
    >>> from funstruct.monadtransformer import StateT
    >>> from funstruct.monad.either import Either, Right, Left
    >>> inc = StateT(lambda s: Right((s + 1, s)))
    >>> inc.run(0)
    Right((1, 0))
    >>> StateT.pure(42, Either).run(0)
    Right((0, 42))
    >>> inc.then(inc).run(0)
    Right((2, 1))
"""

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses._monad_transformer import MonadTransformer


def _pure(monad_cls, value):
    """Lift a plain value into a monad via pure."""
    return monad_cls.pure(value)


_F = TypeVar("_F")
_A = TypeVar("_A")
_B = TypeVar("_B")

# class StateT(MonadTransformer[_F, _A, _B]):


class StateT(MonadTransformer, Generic[_F, _A]):
    """Generic state transformer: ``S -> F[(S, A)]``.

    ``F`` is the wrapping monad (Result, FutureResult, Maybe, etc.).
    Composition uses duck-typed ``.bind()`` / ``.map()`` / ``.or_else()``
    on whatever ``F`` returns — one implementation for all monads.

    Haskell: ``StateT m s a``
    Scala:   ``StateT[F[_], S, A]``
    """

    __slots__ = ("_run",)

    def __init__(self, run: Callable) -> None:
        self._run = run

    def run(self, initial_state):
        """Execute with initial state.

        Returns ``F[(final_state, value)]``.
        """
        return self._run(initial_state)

    def bind(self, f: Callable[[_A], "StateT[_F, _B]"]) -> "StateT[_F, _B]":
        """FlatMap: thread state, pass value to ``f``.

        >>> from funstruct.monad.option import Option, Some
        >>> StateT.pure(1, Option).bind(lambda x: StateT.pure(x + 10, Option)).run(0)
        Some((0, 11))
        """

        def inner(s):
            return self._run(s).bind(lambda sa: f(sa[1]).run(sa[0]))

        return StateT(inner)

    def map(self, f: Callable[[_A], _B]) -> "StateT[_F, _B]":
        """Transform the produced value without touching state.

        >>> from funstruct.monad.option import Option, Some
        >>> StateT.pure(5, Option).map(lambda x: x * 2).run(0)
        Some((0, 10))
        """

        def inner(s):
            return self._run(s).map(lambda sa: (sa[0], f(sa[1])))

        return StateT(inner)

    def or_else(self, f: Callable) -> "StateT":
        """Recover from failure.

        ``f`` receives the error, returns a recovery StateT.
        Only works when ``F`` supports ``.or_else()``.
        """

        def inner(s):
            return self._run(s).or_else(lambda err: f(err).run(s))

        return StateT(inner)

    def ap(self, other) -> "StateT":
        """Applicative ap: run both, tuple the values."""
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    def and_then(self, other: "StateT") -> "StateT":
        """Kleisli composition: value from self becomes initial state for other.

        Short-circuits on inner monad failure.
        """
        return StateT(lambda s: self._run(s).bind(lambda sa: other._run(sa[1])))

    def then(self, next_state: "StateT[_F, _B]") -> "StateT[_F, _B]":
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: next_state)

    # Constructors — monad class passed explicitly, StateT knows nothing about it

    @classmethod
    def do(cls, gen_fn) -> "StateT":
        """Do-notation via generators. Flattens nested binds.

        Each `yield` extracts the value from a StateT.
        State threads through, short-circuits on inner monad failure.

        >>> from funstruct.monad.either import Either, Right
        >>> def pipeline():
        ...     x = yield StateT(lambda s: Right((s + 1, s)))
        ...     y = yield StateT(lambda s: Right((s + 1, s)))
        ...     return x + y
        >>> StateT.do(pipeline).run(0)
        Right((2, 1))
        """

        def _run(s):
            gen = gen_fn()
            try:
                first = next(gen)
            except StopIteration:
                raise ValueError("do block must yield at least once")

            def step(sa):
                new_s, value = sa
                try:
                    next_val = gen.send(value)
                    return next_val.run(new_s).bind(step)
                except StopIteration as e:
                    monad_cls = first.run(s).__class__
                    return _pure(monad_cls, (new_s, e.value))

            return first.run(s).bind(step)

        return cls(_run)

    @classmethod
    def pure(cls, value, monad: type) -> "StateT":
        """Lift a value into StateT. State unchanged.

        >>> from funstruct.monad.option import Option, Some
        >>> StateT.pure("hello", Option).run(99)
        Some((99, 'hello'))
        """
        return cls(lambda s: _pure(monad, (s, value)))

    @classmethod
    def fail(cls, err, monad) -> "StateT":
        """Lift an error. Uses ``monad.from_error``."""
        return cls(lambda _: monad.from_error(err))

    @classmethod
    def get(cls, monad) -> "StateT":
        """Produce current state as the value.

        >>> from funstruct.monad.option import Option, Some
        >>> StateT.get(Option).run(42)
        Some((42, 42))
        """
        return cls(lambda s: _pure(monad, (s, s)))

    @classmethod
    def modify(cls, f: Callable, monad) -> "StateT":
        """Modify state, produce None.

        >>> from funstruct.monad.option import Option, Some
        >>> StateT.modify(lambda s: s + 1, Option).run(5)
        Some((6, None))
        """
        return cls(lambda s: _pure(monad, (f(s), None)))

    @classmethod
    def lift_f(cls, inner) -> "StateT":
        """Lift F[A] into StateT — state unchanged.

        Haskell equivalent: ``lift :: m a -> StateT s m a``

        >>> from funstruct.monad.option import Option, Some, Nothing
        >>> StateT.lift_f(Some(42)).run(0)
        Some((0, 42))
        >>> StateT.lift_f(Nothing()).run(0)
        Nothing()
        """
        return cls(lambda s: inner.map(lambda a: (s, a)))

    def __repr__(self) -> str:
        return f"StateT({self._run})"


__all__ = [
    "StateT",
]
