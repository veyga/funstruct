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

    handle_error_with — recover from Left:

    >>> EitherT(Some(Left("err"))).handle_error_with(
    ...     lambda e: EitherT(Some(Right(f"recovered: {e}")))
    ... ).run()
    Some(Right('recovered: err'))

    lift_f — bring F[A] into EitherT (wraps value in Right):

    >>> EitherT.lift_f(Some(42)).run()
    Some(Right(42))

    pure — lift_f a plain value into EitherT:

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

    def handle_error_with(
        self, f: Callable[[_E], EitherT[_F, _E, _A]]
    ) -> EitherT[_F, _E, _A]:
        """Recover from Left: f receives the error, returns a new EitherT."""

        def _step(either):
            match either:
                case Left(error):
                    return f(error).run()
                case _:
                    return self._value.__class__.pure(either)

        return EitherT(self._value.bind(_step))

    def left_map(self, f: Callable[[_E], _E]) -> EitherT:
        """Transform the error value. No-op on Right.

        >>> from funstruct.monad.option import Some
        >>> from funstruct.monad.either import Left
        >>> EitherT(Some(Left("err"))).left_map(str.upper).run()
        Some(Left('ERR'))
        """
        return EitherT(self._value.map(lambda either: either.left_map(f)))

    def bimap(self, on_left: Callable, on_right: Callable) -> EitherT:
        """Transform both sides.

        >>> from funstruct.monad.option import Some
        >>> from funstruct.monad.either import Right, Left
        >>> EitherT(Some(Right(5))).bimap(str, lambda x: x * 2).run()
        Some(Right(10))
        >>> EitherT(Some(Left("err"))).bimap(str.upper, lambda x: x * 2).run()
        Some(Left('ERR'))
        """
        return EitherT(self._value.map(lambda either: either.bimap(on_left, on_right)))

    def fold(self, on_left: Callable[[_E], _B], on_right: Callable[[_A], _B]) -> _F:
        """Eliminate the Either inside F, returning F[B].

        >>> from funstruct.monad.option import Some
        >>> from funstruct.monad.either import Right, Left
        >>> EitherT(Some(Right(5))).fold(lambda e: 0, lambda x: x * 2)
        Some(10)
        >>> EitherT(Some(Left("err"))).fold(lambda e: -1, lambda x: x * 2)
        Some(-1)
        """
        return self._value.map(lambda either: either.fold(on_left, on_right))

    def swap(self) -> EitherT:
        """Swap Left and Right inside F.

        >>> from funstruct.monad.option import Some
        >>> from funstruct.monad.either import Right, Left
        >>> EitherT(Some(Right(1))).swap().run()
        Some(Left(1))
        >>> EitherT(Some(Left("err"))).swap().run()
        Some(Right('err'))
        """
        return EitherT(self._value.map(lambda either: either.swap()))

    def get_or_else(self, default: _A) -> _F:
        """Extract the Right value or return default, inside F.

        >>> from funstruct.monad.option import Some
        >>> from funstruct.monad.either import Right, Left
        >>> EitherT(Some(Right(42))).get_or_else(0)
        Some(42)
        >>> EitherT(Some(Left("err"))).get_or_else(0)
        Some(0)
        """
        return self._value.map(lambda either: either.get_or_else(default))

    def and_then(self, other: EitherT) -> EitherT:
        """Kleisli composition: value from self feeds into other's context."""
        return self.bind(lambda _: other)

    @classmethod
    def pure(cls, value: _A, monad: type) -> EitherT:
        """Lift a plain value into EitherT via monad.pure(Right(value))."""
        return cls(monad.pure(Right(value)))

    @classmethod
    def from_error(cls, error: _E, monad: type) -> EitherT:
        """Lift an error into EitherT via monad.pure(Left(error))."""
        return cls(monad.pure(Left(error)))

    @classmethod
    def lift_f(cls, fa: _F) -> EitherT:
        """Lift F[A] into EitherT — wraps the value in Right.

        Haskell equivalent: ``lift :: m a -> EitherT e m a``
        """
        return cls(fa.map(lambda a: Right(a)))

    @classmethod
    def from_either(cls, either: Either, monad: type) -> EitherT:
        """Lift a plain Either into EitherT."""
        return cls(monad.pure(either))

    @classmethod
    def do(cls, gen_fn) -> Callable[..., EitherT]:
        """Do-notation via generators. Returns a callable.

        Each ``yield`` extracts the Right value from an EitherT.
        Short-circuits on Left (propagated through F).

        >>> from funstruct.monad.option import Some
        >>> from funstruct.monad.either import Right
        >>> def pipeline():
        ...     x = yield EitherT(Some(Right(1)))
        ...     y = yield EitherT(Some(Right(x + 10)))
        ...     return x + y
        >>> EitherT.do(pipeline)().run()
        Some(Right(12))
        """

        def _thunk(*args, **kwargs):
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

            gen = gen_fn(*args, **kwargs)
            try:
                first = next(gen)
            except StopIteration:
                raise ValueError("do block must yield at least once")
            return _bind_step(first, gen)

        return _thunk

    def __repr__(self) -> str:
        return f"EitherT({repr(self._value)})"


__all__ = [
    "EitherT",
]
