"""ReAwaitable — an awaitable wrapper that caches the result.

Allows a coroutine to be safely shared across multiple consumers.
Without caching, awaiting a coroutine twice raises RuntimeError.

Examples:
    >>> import asyncio
    >>> from funstruct.util._reawaitable import ReAwaitable

    >>> async def main():
    ...     r = ReAwaitable(asyncio.coroutine(lambda: 42)())
    ...     return await r

"""

import inspect
from collections.abc import Awaitable, Generator
from typing import TypeVar

_A = TypeVar("_A")
_SENTINEL = object()


class ReAwaitable:
    """Awaitable wrapper that caches the result of the first await.

    Allows a coroutine to be safely shared across multiple consumers
    (e.g., branching a Future into two map calls).
    """

    def __init__(self, coro: Awaitable[_A]) -> None:
        self._coro = coro
        self._cache = _SENTINEL

    def __del__(self):
        if self._cache is _SENTINEL and inspect.iscoroutine(self._coro):
            self._coro.close()

    def __await__(self) -> Generator[None, None, _A]:
        return self._awaitable().__await__()

    async def _awaitable(self) -> _A:
        if self._cache is _SENTINEL:
            self._cache = await self._coro
        return self._cache


__all__ = [
    "ReAwaitable",
]
