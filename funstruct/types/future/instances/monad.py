from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.monad import Monad
from funstruct.types.future import Future

_A = TypeVar("_A")
_B = TypeVar("_B")


class _FutureMonad(Monad, for_type=Future):
    def pure(self, value: _A) -> Future[_A]:
        async def _inner():
            return value

        return Future(_inner())

    def bind(self, fa: Future[_A], f: Callable[[_A], Future[_B]]) -> Future[_B]:
        async def _inner():
            result = await fa._coro
            return await f(result)

        return Future(_inner())
