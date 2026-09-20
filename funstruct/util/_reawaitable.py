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

from __future__ import annotations

import enum
import inspect
from collections.abc import Awaitable, Generator
from typing import Generic, TypeVar

_A = TypeVar("_A")


class _Sentinel(enum.Enum):
    UNSET = "UNSET"


class ReAwaitable(Generic[_A]):
    """Awaitable wrapper that caches the result of the first await.

    Allows a coroutine to be safely shared across multiple consumers
    (e.g., branching a Future into two map calls).
    """

    _coro: Awaitable[_A]
    _cache: _A | _Sentinel

    def __init__(self, coro: Awaitable[_A]) -> None:
        self._coro = coro
        self._cache = _Sentinel.UNSET

    def __del__(self):
        if self._cache is _Sentinel.UNSET and inspect.iscoroutine(self._coro):
            self._coro.close()

    def __await__(self) -> Generator[None, None, _A]:
        return self._awaitable().__await__()

    async def _awaitable(self) -> _A:
        cache = self._cache
        if isinstance(cache, _Sentinel):
            cache = await self._coro
            self._cache = cache
        return cache


__all__ = [
    "ReAwaitable",
]
