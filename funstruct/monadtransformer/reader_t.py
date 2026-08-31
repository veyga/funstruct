"""ReaderT — reader monad transformer over any monad.

**ReaderT** — shared environment + inner monad's effects (failure, state, etc.)

```python
ReaderT[F, Ctx, A]  =  Ctx -> F[A]
```

bind: chain computations that share context, any can fail.
and_then: pipe output forward as the next context (Kleisli composition).

Examples:
    >>> from funstruct.monadtransformer import ReaderT
    >>> from funstruct.monad.either import Either, Right, Left

    bind — shared context, with failure:

    >>> get_db = ReaderT(lambda cfg: (
    ...     Right(cfg["db"]) if "db" in cfg
    ...     else Left("missing db")))
    >>> validate = lambda url: ReaderT(lambda cfg: (
    ...     Right(url) if url.startswith("postgres://")
    ...     else Left(f"bad url: {url}")))
    >>> connect = lambda url: ReaderT(lambda cfg: (
    ...     Right(f"{url} as {cfg['user']}")))
    >>> pipeline = (
    ...     get_db
    ...     .bind(validate)
    ...     .bind(connect)
    ... )
    >>> pipeline.run({"db": "postgres://localhost/app", "user": "admin"})
    Right('postgres://localhost/app as admin')
    >>> pipeline.run({"db": "mysql://bad", "user": "admin"})
    Left('bad url: mysql://bad')

    and_then — output feeds as next input, short-circuits on failure:

    >>> parse_int = ReaderT(lambda s: (
    ...     Right(int(s)) if s.isdigit()
    ...     else Left(f"not a number: {s}")))
    >>> double = ReaderT(lambda n: Right(n * 2))
    >>> to_str = ReaderT(lambda n: Right(str(n)))
    >>> pipeline = (
    ...     parse_int
    ...     .and_then(double)
    ...     .and_then(to_str)
    ... )
    >>> pipeline.run("21")
    Right('42')
    >>> pipeline.run("abc")
    Left('not a number: abc')
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses._monad_transformer import MonadTransformer


def _pure(monad_cls, value):
    """Lift a value into a monad via pure."""
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

    def or_else(self, f: Callable) -> ReaderT[_Ctx, _M, _A]:
        """Recover from failure via inner monad's or_else."""

        def inner(ctx):
            return self._run(ctx).or_else(lambda err: f(err).run(ctx))

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
                    return _pure(monadic_val._run(ctx).__class__, e.value)

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
        """Lift a plain value into ReaderT via monad.pure."""
        return cls(lambda _: _pure(monad, value))

    @classmethod
    def lift_f(cls, m) -> ReaderT:
        """Lift M[A] into ReaderT (ignoring context).

        Haskell equivalent: ``lift :: m a -> ReaderT r m a``
        """
        return cls(lambda _: m)

    def __repr__(self) -> str:
        return f"ReaderT({self._run})"


__all__ = [
    "ReaderT",
]
