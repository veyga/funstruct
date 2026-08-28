"""Reader monad — computations that read from an environment.

Reader[Ctx, A] wraps Ctx -> A.
Unlike ReaderT, this is not a transformer — no inner monad.

Example::

    >>> from funstruct.monad.reader import Reader
    >>> greet = Reader(lambda name: f"hello {name}")
    >>> greet.run("Alice")
    'hello Alice'
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad

_Ctx = TypeVar("_Ctx")
_A = TypeVar("_A")
_B = TypeVar("_B")


class Reader(Monad, Generic[_Ctx, _A]):
    """Reader: Ctx -> A.

    A computation that reads from a shared environment.
    """

    __slots__ = ("_run",)

    def __init__(self, run: Callable) -> None:
        self._run = run

    def run(self, ctx):
        """Execute with the given context."""
        return self._run(ctx)

    def __call__(self, ctx):
        return self.run(ctx)

    def map(self, f: Callable) -> Reader:
        """Transform the produced value."""
        return Reader(lambda ctx: f(self._run(ctx)))

    def bind(self, f: Callable) -> Reader:
        """Chain: f receives the value, returns a new Reader."""
        return Reader(lambda ctx: f(self._run(ctx)).run(ctx))

    @classmethod
    def pure(cls, value, *args, **kwargs) -> Reader:
        """Lift a value — ignores context."""
        return cls(lambda _: value)

    @classmethod
    def ask(cls) -> Reader:
        """Return the context itself as the value."""
        return cls(lambda ctx: ctx)

    def __repr__(self) -> str:
        return f"Reader({self._run})"


__all__ = ["Reader"]
