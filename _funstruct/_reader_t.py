"""Generic ReaderT monad transformer.

``ReaderT[M, Ctx, A]`` wraps ``Ctx -> M[A]`` where M is any monad
with ``.bind()``, ``.map()``, and optionally ``.lash()``.

Delegates all composition to the inner monad M — one implementation
works for any M (Option, StateT, Result, etc.).

Haskell: ``ReaderT r m a``
Scala cats:   ``Kleisli[F, Ctx, A]``

Example with Option::

    >>> from _funstruct._option import Option, Some, Nothing
    >>> from _funstruct._reader_t import ReaderT
    >>> step = ReaderT(lambda ctx: Some(ctx + 1))
    >>> step.run(5)
    Some(6)

"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses._monad_transformer import MonadTransformer


def lift(monad_cls, value):
    """Lift a value into a monad — uses from_value if available, else pure."""
    if hasattr(monad_cls, "from_value"):
        return monad_cls.from_value(value)
    return monad_cls.pure(value)


_Ctx = TypeVar("_Ctx")
_M = TypeVar("_M")
_A = TypeVar("_A")
_B = TypeVar("_B")


class ReaderT(MonadTransformer, Generic[_Ctx, _M, _A]):
    """ReaderT: ``Ctx -> M[A]``.

    M is the inner monad (StateT, Result, etc.). Composition delegates to M's
    bind/map/lash — ReaderT just threads the context to both sides.
    """

    __slots__ = ("_run",)

    def __init__(self, run: Callable) -> None:
        self._run = run

    def run(self, ctx):
        """Apply context, returning the inner M[A]."""
        return self._run(ctx)

    def __call__(self, ctx):
        """Apply context (alias for run)."""
        return self._run(ctx)

    def bind(
        self,
        f: Callable[[_A], ReaderT[_Ctx, _M, _B]],
    ) -> ReaderT[_Ctx, _M, _B]:
        """FlatMap: compose via M's bind, threading ctx."""

        def inner(ctx):
            return self._run(ctx).bind(lambda a: f(a).run(ctx))

        return ReaderT(inner)

    def map(self, f: Callable[[_A], _B]) -> ReaderT[_Ctx, _M, _B]:
        """Transform value via M's map."""

        def inner(ctx):
            return self._run(ctx).map(f)

        return ReaderT(inner)

    def lash(self, f: Callable) -> ReaderT[_Ctx, _M, _A]:
        """Recover from failure via M's lash."""

        def inner(ctx):
            return self._run(ctx).lash(lambda err: f(err).run(ctx))

        return ReaderT(inner)

    # ap inherited from Monad (derived from bind + map)

    def and_then(self, other: ReaderT) -> ReaderT:
        """Kleisli composition: output of self becomes input (ctx) of other.

        Short-circuits on inner monad failure.
        """
        return ReaderT(
            lambda ctx: self._run(ctx).bind(lambda result: other._run(result))
        )

    @classmethod
    def do(cls, gen_fn) -> ReaderT:
        """Do-notation via generators. Flattens nested binds.

        Each `yield` extracts the value from a ReaderT (shared ctx).
        Short-circuits on inner monad failure.
        """

        def _run(ctx):
            gen = gen_fn()
            try:
                monadic_val = next(gen)
            except StopIteration:
                raise ValueError("do block must yield at least once")

            def step(value):
                try:
                    next_val = gen.send(value)
                    return next_val._run(ctx).bind(step)
                except StopIteration as e:
                    return lift(monadic_val._run(ctx).__class__, e.value)

            return monadic_val._run(ctx).bind(step)

        return cls(_run)

    def then(
        self,
        next_step: ReaderT[_Ctx, _M, _B],
    ) -> ReaderT[_Ctx, _M, _B]:
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: next_step)

    @classmethod
    def pure(cls, value, monad) -> ReaderT:
        """Lift a raw value into ReaderT via monad.from_value."""
        return cls(lambda _: lift(monad, value))

    @classmethod
    def lift(cls, m) -> ReaderT:
        """Lift an existing M[A] into ReaderT (ignoring context).

        Haskell: ``lift :: m a -> ReaderT r m a``
        """
        return cls(lambda _: m)

    def __repr__(self) -> str:
        return f"ReaderT({self._run})"


__all__ = [
    "ReaderT",
]
