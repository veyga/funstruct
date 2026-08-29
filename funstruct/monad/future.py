"""Future — lazy async computation.

Future[A] wraps Awaitable[A]. A generic async monad — no error semantics built in.
For error handling, use AsyncResult[A] from funstruct.monad.result.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Generator
from typing import Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")


class Future(Generic[A]):
    """Lazy async computation that produces A when awaited.

    Build pipelines with .bind(), .map() — no await needed.
    Execute once at the boundary with await.

    Future[A] is a generic async monad. It does not know about errors.
    For error-aware async, use AsyncResult[A] from funstruct.monad.result.
    """

    __slots__ = ("_coro",)

    def __init__(self, coro: Awaitable[A]) -> None:
        self._coro = coro

    def __del__(self):
        if hasattr(self._coro, "close"):
            self._coro.close()

    def __await__(self) -> Generator[None, None, A]:
        return self._awaitable().__await__()

    async def _awaitable(self) -> A:
        return await self._coro

    def map(self, f: Callable[[A], B]) -> Future[B]:
        """Transform the value without executing."""

        async def _inner():
            result = await self._coro
            return f(result)

        return Future(_inner())

    def bind(self, f: Callable[[A], Future[B]]) -> Future[B]:
        """Chain: f receives the value, returns a new Future."""

        async def _inner():
            result = await self._coro
            return await f(result)

        return Future(_inner())

    def then(self, next_future: Future[B]) -> Future[B]:
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: next_future)

    @classmethod
    def pure(cls, value: A) -> Future[A]:
        """Lift a plain value into a Future."""

        async def _inner():
            return value

        return cls(_inner())

    def __repr__(self) -> str:
        return f"Future({self._coro})"


__all__ = ["Future"]
