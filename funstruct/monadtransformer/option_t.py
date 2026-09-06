"""OptionT — adds optionality to any monad F.

OptionT[F, A] wraps F[Option[A]]. bind short-circuits on Nothing,
map transforms the value inside Some.

Examples:
    >>> from funstruct.monadtransformer.option_t import OptionT
    >>> from funstruct.monad.either import Either, Right, Left
    >>> from funstruct.monad.option import Some, Nothing

    Wrapping Either — a computation that can fail OR be absent:

    >>> OptionT(Right(Some(1))).map(lambda x: x + 10).run()
    Right(Some(11))
    >>> OptionT(Right(Nothing())).map(lambda x: x + 10).run()
    Right(Nothing())
    >>> OptionT(Left("db error")).map(lambda x: x + 10).run()
    Left('db error')

    bind chains — short-circuits on Nothing OR Left:

    >>> OptionT(Right(Some(1))).bind(
    ...     lambda x: OptionT(Right(Some(x * 10)))
    ... ).run()
    Right(Some(10))
    >>> OptionT(Right(Nothing())).bind(
    ...     lambda x: OptionT(Right(Some(x * 10)))
    ... ).run()
    Right(Nothing())

    handle_error_with — recover from Nothing (not from Left):

    >>> OptionT(Right(Nothing())).handle_error_with(
    ...     lambda: OptionT(Right(Some(99)))
    ... ).run()
    Right(Some(99))

    lift_f — bring F[A] into OptionT (wraps in Some):

    >>> OptionT.lift_f(Right(42)).run()
    Right(Some(42))
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.monad.option import Nothing, Option, Some
from funstruct.typeclasses._monad_transformer import MonadTransformer

_F = TypeVar("_F")
_A = TypeVar("_A")
_B = TypeVar("_B")


class OptionT(MonadTransformer, Generic[_F, _A]):
    """OptionT: ``F[Option[A]]``.

    Adds optionality/absence to any monad F. bind delegates to F's bind,
    then pattern-matches the Option inside: Some(v) continues, Nothing
    short-circuits.

    Haskell: ``MaybeT m a``
    Scala:   ``OptionT[F[_], A]``
    """

    def __init__(self, run) -> None:
        self._run = run

    def run(self):
        """Unwrap to get F[Option[A]]."""
        return self._run

    def bind(self, f: Callable[[_A], OptionT[_F, _B]]) -> OptionT[_F, _B]:
        """FlatMap: unwrap F, match Option, chain on Some.

        >>> from funstruct.monad.either import Right
        >>> from funstruct.monad.option import Some, Nothing
        >>> OptionT(Right(Some(1))).bind(
        ...     lambda x: OptionT(Right(Some(x + 10)))
        ... ).run()
        Right(Some(11))
        >>> OptionT(Right(Nothing())).bind(
        ...     lambda x: OptionT(Right(Some(x + 10)))
        ... ).run()
        Right(Nothing())
        """

        def _handle(opt):
            match opt:
                case Some(v):
                    return f(v).run()
                case _:
                    return self._run.__class__.pure(Nothing())

        return OptionT(self._run.bind(_handle))

    def map(self, f: Callable[[_A], _B]) -> OptionT[_F, _B]:
        """Transform the value inside Some inside F.

        >>> from funstruct.monad.either import Right
        >>> from funstruct.monad.option import Some
        >>> OptionT(Right(Some(5))).map(lambda x: x * 2).run()
        Right(Some(10))
        """

        def _map_opt(opt):
            match opt:
                case Some(v):
                    return Some(f(v))
                case _:
                    return opt

        return OptionT(self._run.map(_map_opt))

    def handle_error_with(self, f: Callable[[], OptionT[_F, _A]]) -> OptionT[_F, _A]:
        """Recover from Nothing: if inner is Nothing, use fallback.

        >>> from funstruct.monad.either import Right
        >>> from funstruct.monad.option import Some, Nothing
        >>> OptionT(Right(Nothing())).handle_error_with(
        ...     lambda: OptionT(Right(Some(99)))
        ... ).run()
        Right(Some(99))
        >>> OptionT(Right(Some(1))).handle_error_with(
        ...     lambda: OptionT(Right(Some(99)))
        ... ).run()
        Right(Some(1))
        """

        def _handle(opt):
            match opt:
                case Nothing():
                    return f().run()
                case _:
                    return self._run.__class__.pure(opt)

        return OptionT(self._run.bind(_handle))

    def fold(self, on_nothing: Callable[[], _B], on_some: Callable[[_A], _B]) -> _F:
        """Eliminate the Option inside F, returning F[B].

        >>> from funstruct.monad.either import Right
        >>> from funstruct.monad.option import Some, Nothing
        >>> OptionT(Right(Some(5))).fold(lambda: 0, lambda x: x * 2)
        Right(10)
        >>> OptionT(Right(Nothing())).fold(lambda: 0, lambda x: x * 2)
        Right(0)
        """
        return self._run.map(lambda opt: opt.fold(on_nothing, on_some))

    def get_or_else(self, default: _A) -> _F:
        """Extract the Some value or return default, inside F.

        >>> from funstruct.monad.either import Right
        >>> from funstruct.monad.option import Some, Nothing
        >>> OptionT(Right(Some(42))).get_or_else(0)
        Right(42)
        >>> OptionT(Right(Nothing())).get_or_else(0)
        Right(0)
        """
        return self._run.map(lambda opt: opt.get_or_else(default))

    def filter(self, f: Callable[[_A], bool]) -> OptionT[_F, _A]:
        """Filter the value inside Some; becomes Nothing if predicate fails.

        >>> from funstruct.monad.either import Right
        >>> from funstruct.monad.option import Some, Nothing
        >>> OptionT(Right(Some(10))).filter(lambda x: x > 5).run()
        Right(Some(10))
        >>> OptionT(Right(Some(3))).filter(lambda x: x > 5).run()
        Right(Nothing())
        """
        return OptionT(self._run.map(lambda opt: opt.filter(f)))

    def and_then(self, other: OptionT) -> OptionT:
        """Kleisli composition: value from self becomes input for other's run."""
        return self.bind(lambda _: other)

    @classmethod
    def do(cls, gen_fn) -> Callable[..., OptionT]:
        """Do-notation via generators. Short-circuits on Nothing. Returns a callable.

        >>> from funstruct.monad.either import Right
        >>> from funstruct.monad.option import Some
        >>> def pipeline():
        ...     x = yield OptionT(Right(Some(1)))
        ...     y = yield OptionT(Right(Some(x + 10)))
        ...     return x + y
        >>> OptionT.do(pipeline)().run()
        Right(Some(12))
        """

        def _thunk(*args, **kwargs):
            def _run_do():
                gen = gen_fn(*args, **kwargs)
                try:
                    first = next(gen)
                except StopIteration:
                    raise ValueError("do block must yield at least once")

                def step(opt):
                    match opt:
                        case Nothing():
                            return first.run().__class__.pure(Nothing())
                        case Some(value):
                            try:
                                next_t = gen.send(value)
                                return next_t.run().bind(step)
                            except StopIteration as e:
                                return first.run().__class__.pure(Some(e.value))

                return first.run().bind(step)

            return cls(_run_do())

        return _thunk

    @classmethod
    def pure(cls, value, monad: type) -> OptionT:
        """Lift a plain value into OptionT.

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.monad.option import Some
        >>> OptionT.pure(42, Either).run()
        Right(Some(42))
        """
        return cls(monad.pure(Some(value)))

    @classmethod
    def none(cls, monad: type) -> OptionT:
        """Construct an OptionT holding Nothing.

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.monad.option import Nothing
        >>> OptionT.none(Either).run()
        Right(Nothing())
        """
        return cls(monad.pure(Nothing()))

    @classmethod
    def lift_f(cls, fa: _F) -> OptionT:
        """Lift F[A] into OptionT — wraps value in Some.

        Use when you have the outer monad but not the inner Option.

        Haskell equivalent: ``lift :: m a -> OptionT m a``

        >>> from funstruct.monad.either import Right, Left
        >>> from funstruct.monad.option import Some
        >>> OptionT.lift_f(Right(42)).run()
        Right(Some(42))
        >>> OptionT.lift_f(Left("err")).run()
        Left('err')
        """
        return cls(fa.map(lambda a: Some(a)))

    @classmethod
    def from_option(cls, option: Option[_A], monad: type) -> OptionT:
        """Lift Option[A] into OptionT — wraps in the outer monad.

        Use when you have the inner Option but not the outer monad.

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.monad.option import Some, Nothing
        >>> OptionT.from_option(Some(42), Either).run()
        Right(Some(42))
        >>> OptionT.from_option(Nothing(), Either).run()
        Right(Nothing())
        """
        return cls(monad.pure(option))

    def __repr__(self) -> str:
        return f"OptionT({repr(self._run)})"


__all__ = ["OptionT"]
