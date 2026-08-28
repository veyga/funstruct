"""EitherT — monad transformer that adds typed errors to any monad F.

``EitherT[F, E, A]`` wraps ``F[Either[E, A]]``.

Examples:
    >>> from funstruct.monadtransformer.either_t import EitherT
    >>> from funstruct.monad.option import Option, Some, Nothing
    >>> from funstruct.monad.either import Right, Left

    EitherT over Option — combines "might not exist" with "might fail":

    >>> EitherT(Some(Right(1))).map(lambda x: x + 10).run()
    Some(Right(11))
    >>> EitherT(Some(Left("err"))).map(lambda x: x + 10).run()
    Some(Left('err'))
    >>> EitherT(Nothing()).map(lambda x: x + 10).run()
    Nothing()

    bind — chains that short-circuit on Left OR Nothing:

    >>> inc = lambda x: EitherT(Some(Right(x + 1)))
    >>> EitherT(Some(Right(1))).bind(inc).bind(inc).run()
    Some(Right(3))
    >>> EitherT(Some(Left("stop"))).bind(inc).run()
    Some(Left('stop'))

    or_else — recover from Left:

    >>> EitherT(Some(Left("err"))).or_else(
    ...     lambda e: EitherT(Some(Right(f"recovered: {e}")))
    ... ).run()
    Some(Right('recovered: err'))

    lift — bring F[A] into EitherT (wraps value in Right):

    >>> EitherT.lift(Some(42)).run()
    Some(Right(42))

    pure — lift a plain value:

    >>> EitherT.pure(99, Option).run()
    Some(Right(99))
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.monad.either import Either, Left, Right
from funstruct.typeclasses._monad_transformer import MonadTransformer

_F = TypeVar("_F")
_E = TypeVar("_E")
_A = TypeVar("_A")
_B = TypeVar("_B")


class EitherT(MonadTransformer, Generic[_F, _E, _A]):
    """EitherT: ``F[Either[E, A]]``.

    Adds typed error handling to any monad F. Delegates composition
    to F's bind/map — one implementation for all monads.

    Haskell: ``EitherT e m a`` (aka ``ExceptT``)
    Scala:   ``EitherT[F[_], E, A]``
    """

    __slots__ = ("_value",)

    def __init__(self, value) -> None:
        self._value = value

    def run(self):
        """Unwrap to get F[Either[E, A]]."""
        return self._value

    def map(self, f: Callable[[_A], _B]) -> EitherT[_F, _E, _B]:
        """Transform the success value inside F[Either[E, A]]."""
        return EitherT(self._value.map(lambda either: either.map(f)))

    def bind(self, f: Callable[[_A], EitherT[_F, _E, _B]]) -> EitherT[_F, _E, _B]:
        """Chain: unwrap Either inside F, apply f if Right."""

        def _step(either):
            match either:
                case Right(value):
                    return f(value).run()
                case _:
                    return self._value.__class__.pure(either)

        return EitherT(self._value.bind(_step))

    def or_else(self, f: Callable[[_E], EitherT[_F, _E, _A]]) -> EitherT[_F, _E, _A]:
        """Recover from Left: f receives the error, returns a new EitherT."""

        def _step(either):
            match either:
                case Left(error):
                    return f(error).run()
                case _:
                    return self._value.__class__.pure(either)

        return EitherT(self._value.bind(_step))

    def and_then(self, other: EitherT) -> EitherT:
        """Kleisli composition: value from self feeds into other's context."""
        return self.bind(lambda _: other)

    def ap(self, other: EitherT) -> EitherT:
        """Applicative: run both, tuple the values."""
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    def then(self, next_step: EitherT[_F, _E, _B]) -> EitherT[_F, _E, _B]:
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: next_step)

    @classmethod
    def pure(cls, value, monad) -> EitherT:
        """Lift a plain value into EitherT via monad.pure(Right(value))."""
        return cls(monad.pure(Right(value)))

    @classmethod
    def from_error(cls, error, monad) -> EitherT:
        """Lift an error into EitherT via monad.pure(Left(error))."""
        return cls(monad.pure(Left(error)))

    @classmethod
    def lift(cls, fa) -> EitherT:
        """Lift F[A] into EitherT — wraps the value in Right.

        Haskell: ``lift :: m a -> EitherT e m a``
        """
        return cls(fa.map(lambda a: Right(a)))

    @classmethod
    def from_either(cls, either: Either, monad) -> EitherT:
        """Lift a plain Either into EitherT."""
        return cls(monad.pure(either))

    @classmethod
    def do(cls, gen_fn) -> EitherT:
        """Do-notation via generators.

        Each ``yield`` extracts the Right value from an EitherT.
        Short-circuits on Left (propagated through F).
        """

        def _bind_step(either_t, gen):
            def _step(either):
                match either:
                    case Right(value):
                        try:
                            next_et = gen.send(value)
                            return _bind_step(next_et, gen).run()
                        except StopIteration as e:
                            return either_t.run().__class__.pure(Right(e.value))
                    case _:
                        return either_t.run().__class__.pure(either)

            return EitherT(either_t.run().bind(_step))

        gen = gen_fn()
        try:
            first = next(gen)
        except StopIteration:
            raise ValueError("do block must yield at least once")
        return _bind_step(first, gen)

    def __repr__(self) -> str:
        return f"EitherT({repr(self._value)})"


__all__ = ["EitherT"]
