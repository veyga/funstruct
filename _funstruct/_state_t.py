"""
Generic State monad transformer.

``StateT[F, A]`` wraps ``S -> F[(S, A)]`` where ``F`` is any monad with
``.bind()``, ``.map()``, and optionally ``.lash()``.


Example with Result::

    >>> from returns.result import Result
    >>> from funstruct.monad import StateT
    >>> inc = StateT(lambda s: Result.from_value((s + 1, s)))
    >>> inc.then(inc).then(inc).run(0)
    <Success: (3, 2)>

"""

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses._monad_transformer import MonadTransformer


def lift(monad_cls, value):
    """Lift a value into a monad — uses from_value if available, else pure."""
    if hasattr(monad_cls, "from_value"):
        return monad_cls.from_value(value)
    return monad_cls.pure(value)


_F = TypeVar("_F")
_A = TypeVar("_A")
_B = TypeVar("_B")

# class StateT(MonadTransformer[_F, _A, _B]):


class StateT(MonadTransformer, Generic[_F, _A]):
    """Generic state transformer: ``S -> F[(S, A)]``.

    ``F`` is the wrapping monad (Result, FutureResult, Maybe, etc.).
    Composition uses duck-typed ``.bind()`` / ``.map()`` / ``.lash()``
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

        >>> from returns.result import Result
        >>> StateT.from_value(1, Result).bind(lambda x: StateT.from_value(x + 10, Result)).run(0)
        <Success: (0, 11)>
        """

        def inner(s):
            return self._run(s).bind(lambda sa: f(sa[1]).run(sa[0]))

        return StateT(inner)

    def map(self, f: Callable[[_A], _B]) -> "StateT[_F, _B]":
        """Transform the produced value without touching state.

        >>> from returns.result import Result
        >>> StateT.from_value(5, Result).map(lambda x: x * 2).run(0)
        <Success: (0, 10)>
        """

        def inner(s):
            return self._run(s).map(lambda sa: (sa[0], f(sa[1])))

        return StateT(inner)

    def lash(self, f: Callable) -> "StateT":
        """
        Recover from failure. ``f`` receives the error, returns a recovery StateT.
        Only works when ``F`` supports ``.lash()`` (Result, IOResult, etc.).

        >>> from returns.result import Result
        >>> failing = StateT(lambda s: Result.from_failure(ValueError("oops")))
        >>> recovered = failing.lash(lambda e: StateT.from_value("ok", Result))
        >>> recovered.run(0)
        <Success: (0, 'ok')>

        """

        def inner(s):
            return self._run(s).lash(lambda err: f(err).run(s))

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
                    return first.run(s).__class__.from_value((new_s, e.value))

            return first.run(s).bind(step)

        return cls(_run)

    @classmethod
    def pure(cls, value, monad: type) -> "StateT":
        """Lift a value.

        State unchanged. Uses ``monad.from_value``.
                >>> from returns.result import Result
                >>> StateT.from_value("hello", Result).run(99)
                <Success: (99, 'hello')>
        """
        return cls(lambda s: monad.from_value((s, value)))

    @classmethod
    def fail(cls, err, monad) -> "StateT":
        """Lift an error.

        Uses ``monad.from_failure``.
                >>> from returns.result import Result
                >>> StateT.fail(ValueError("bad"), Result).run(0)
                <Failure: bad>
        """
        return cls(lambda _: monad.from_failure(err))

    @classmethod
    def get(cls, monad) -> "StateT":
        """Produce current state as the value.

        >>> from returns.result import Result
        >>> StateT.get(Result).run(42)
        <Success: (42, 42)>
        """
        return cls(lambda s: monad.from_value((s, s)))

    @classmethod
    def modify(cls, f: Callable, monad) -> "StateT":
        """Modify state, produce None.

        >>> from returns.result import Result
        >>> StateT.modify(lambda s: s + 1, Result).run(5)
        <Success: (6, None)>
        """
        return cls(lambda s: monad.from_value((f(s), None)))

    @classmethod
    def lift(cls, fa) -> "StateT":
        """Lift F[A] into StateT — state unchanged.

        Haskell: ``lift :: m a -> StateT s m a``

        >>> from returns.result import Result
        >>> StateT.lift(Result.from_value(42)).run(0)
        <Success: (0, 42)>
        >>> StateT.lift(Result.from_failure("err")).run(0)
        <Failure: err>
        """
        return cls(lambda s: fa.map(lambda a: (s, a)))

    def __repr__(self) -> str:
        return f"StateT({self._run})"


__all__ = [
    "StateT",
]
