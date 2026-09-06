"""WriterT — writer monad transformer over any monad.

Adds accumulated output/logging to any monad F.
WriterT[F, W, A] wraps F[(A, W)].

Examples:
    >>> from funstruct.experimental.monadtransformer.writer_t import WriterT
    >>> from funstruct.monad.either import Either, Right, Left
    >>> from funstruct.typeclasses import Monoid

    >>> list_monoid = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
    >>> class LogT(WriterT):
    ...     _monoid = list_monoid

    bind accumulates output:

    >>> w = LogT.pure(1, Either).bind(lambda x: LogT(Right((x + 1, ["inc"]))))
    >>> w.run()
    Right((2, ['inc']))

    map doesn't touch output:

    >>> LogT(Right((5, ["init"]))).map(lambda x: x * 2).run()
    Right((10, ['init']))

    tell produces output:

    >>> LogT.tell(["hello"], Either).run()
    Right((None, ['hello']))

    lift_f wraps F[A] with empty output:

    >>> LogT.lift_f(Right(42)).run()
    Right((42, []))

    short-circuits on Left:

    >>> LogT(Left("err")).map(lambda x: x + 1).run()
    Left('err')
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.experimental.monadtransformer._typeclass import MonadTransformer
from funstruct.typeclasses._monoid import Monoid

_F = TypeVar("_F")
_W = TypeVar("_W")
_A = TypeVar("_A")
_B = TypeVar("_B")


class WriterT(MonadTransformer, Generic[_F, _W, _A]):
    """Generic writer transformer: ``F[(A, W)]``.

    ``F`` is the wrapping monad (Either, Option, etc.).
    ``W`` is the output type, combined via a class-level Monoid.

    Subclass and set ``_monoid`` to use.

    Haskell: ``WriterT w m a``
    Scala:   ``WriterT[F[_], W, A]``
    """

    _monoid: Monoid

    def __init__(self, run) -> None:
        self._run = run

    def run(self):
        """Execute, returning F[(A, W)]."""
        return self._run

    def map(self, f: Callable[[_A], _B]) -> WriterT[_F, _W, _B]:
        """Transform the value, keep the output."""
        cls = self.__class__
        return cls(self._run.map(lambda aw: (f(aw[0]), aw[1])))

    def bind(self, f: Callable[[_A], WriterT]) -> WriterT:
        """Chain: run f on the value, combine outputs via monoid."""
        cls = self.__class__
        monoid = cls._monoid

        def _step(aw):
            a, w1 = aw
            return f(a).run().map(lambda bw: (bw[0], monoid.combine(w1, bw[1])))

        return cls(self._run.bind(_step))

    def handle_error_with(self, f: Callable[..., WriterT]) -> WriterT:
        """Recover from failure via inner monad's handle_error_with."""
        cls = self.__class__
        return cls(self._run.handle_error_with(lambda err: f(err).run()))

    @classmethod
    def pure(cls, value, monad: type) -> WriterT:
        """Lift a value with empty output.

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.typeclasses._monoid import Monoid
        >>> list_m = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
        >>> class LT(WriterT):
        ...     _monoid = list_m
        >>> LT.pure(42, Either).run()
        Right((42, []))
        """
        return cls(monad.pure((value, cls._monoid.empty)))

    @classmethod
    def tell(cls, output: _W, monad: type) -> WriterT:
        """Produce output with no meaningful value.

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.typeclasses._monoid import Monoid
        >>> list_m = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
        >>> class LT(WriterT):
        ...     _monoid = list_m
        >>> LT.tell(["hello"], Either).run()
        Right((None, ['hello']))
        """
        return cls(monad.pure((None, output)))

    @classmethod
    def from_writer(cls, value: _A, output: _W, monad: type) -> WriterT:
        """Lift a value + output pair into WriterT.

        Use when you have the inner writer value but not the outer monad.

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.typeclasses import Monoid
        >>> list_m = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
        >>> class LT(WriterT):
        ...     _monoid = list_m
        >>> LT.from_writer(42, ["init"], Either).run()
        Right((42, ['init']))
        """
        return cls(monad.pure((value, output)))

    @classmethod
    def lift_f(cls, fa: _F) -> WriterT:
        """Lift F[A] into WriterT — output is empty.

        Haskell equivalent: ``lift :: m a -> WriterT w m a``
        """
        return cls(fa.map(lambda a: (a, cls._monoid.empty)))

    @classmethod
    def do(cls, gen_fn) -> Callable[..., WriterT]:
        """Do-notation via generators. Accumulates output across yields. Returns a callable.

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.typeclasses import Monoid
        >>> list_m = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
        >>> class LogT(WriterT):
        ...     _monoid = list_m
        >>> def pipeline():
        ...     x = yield LogT(Right((1, ["init"])))
        ...     y = yield LogT(Right((x + 10, ["step"])))
        ...     return x + y
        >>> LogT.do(pipeline)().run()
        Right((12, ['init', 'step']))
        """

        def _thunk(*args, **kwargs):
            def _unwrap(first_run):
                gen = gen_fn(*args, **kwargs)
                next(gen)

                monoid = cls._monoid

                def step(aw):
                    a, w_acc = aw
                    try:
                        next_wt = gen.send(a)
                        return next_wt.run().bind(
                            lambda bw: step((bw[0], monoid.combine(w_acc, bw[1])))
                        )
                    except StopIteration as e:
                        return first_run.__class__.pure((e.value, w_acc))

                return step

            def _run_do():
                gen = gen_fn(*args, **kwargs)
                first_wt = next(gen)
                first_fa = first_wt.run()
                return first_fa.bind(_unwrap(first_fa))

            return cls(_run_do())

        return _thunk

    def listen(self) -> WriterT:
        """Expose the output alongside the value: A → (A, W).

        Cats: ``WriterT.listen``

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.typeclasses import Monoid
        >>> list_m = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
        >>> class LT(WriterT):
        ...     _monoid = list_m
        >>> LT(Right((42, ["log"]))).listen().run()
        Right(((42, ['log']), ['log']))
        """
        cls = self.__class__
        return cls(self._run.map(lambda aw: ((aw[0], aw[1]), aw[1])))

    def written(self) -> object:
        """Extract just the output, discarding the value. Returns F[W].

        >>> from funstruct.monad.either import Either, Right
        >>> from funstruct.typeclasses import Monoid
        >>> list_m = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
        >>> class LT(WriterT):
        ...     _monoid = list_m
        >>> LT(Right((42, ["log"]))).written()
        Right(['log'])
        """
        return self._run.map(lambda aw: aw[1])

    def and_then(self, other: WriterT) -> WriterT:
        """Kleisli composition: value from self feeds into other."""
        cls = self.__class__
        monoid = cls._monoid

        def _step(aw):
            a, w1 = aw
            return other.run().map(lambda bw: (bw[0], monoid.combine(w1, bw[1])))

        return cls(self._run.bind(_step))

    def __repr__(self) -> str:
        return f"WriterT({self._run})"


__all__ = [
    "WriterT",
]
