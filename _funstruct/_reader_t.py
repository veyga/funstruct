"""
Generic ReaderT monad transformer.

``ReaderT[M, Ctx, A]`` wraps ``Ctx -> M[A]`` where M is any monad
with ``.bind()``, ``.map()``, and optionally ``.lash()``.

Delegates all composition to the inner monad M — one implementation
works for any M (StateT, Result, FutureResult, etc.).

Haskell: ``ReaderT r m a``
Scala cats:   ``Kleisli[F, Ctx, A]``

Example with Result::

    >>> from returns.result import Result
    >>> from funstruct.monad import ReaderT
    >>> step = ReaderT(lambda ctx: Result.from_value(ctx + 1))
    >>> step.run(5)
    <Success: 6>

Example with StateT::

    >>> from returns.result import Result
    >>> from funstruct.monad import StateT
    >>> from funstruct.monad import ReaderT
    >>> step = ReaderT(lambda ctx: StateT(
    ...     lambda s: Result.from_value((s + ctx, s))
    ... ))
    >>> step.run(10).run(0)
    <Success: (10, 0)>

"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclass.monad import Monad

_Ctx = TypeVar("_Ctx")
_M = TypeVar("_M")
_A = TypeVar("_A")
_B = TypeVar("_B")


class ReaderT(Monad, Generic[_Ctx, _M, _A]):
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

    def ap(self, other) -> ReaderT:
        """Applicative ap: delegates to M's product."""

        def inner(ctx):
            return self._run(ctx).ap(other._run(ctx))

        return ReaderT(inner)

    def then(
        self,
        next_step: ReaderT[_Ctx, _M, _B],
    ) -> ReaderT[_Ctx, _M, _B]:
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: next_step)

    @classmethod
    def pure(cls, value, monad) -> ReaderT:
        """Lift a raw value into ReaderT via monad.from_value."""
        return cls(lambda _: monad.from_value(value))

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
