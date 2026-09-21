from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.types.result import AsyncResult, Err, Ok

_A = TypeVar("_A")
_B = TypeVar("_B")


class _AsyncResultBifunctor(Bifunctor, for_type=AsyncResult):
    def bimap(
        self,
        fa: AsyncResult[_A],
        f: Callable[[Exception], Exception],
        g: Callable[[_A], _B],
    ) -> AsyncResult[_B]:
        async def _inner():
            result = await fa._coro
            match result:
                case Ok(value):
                    return Ok(g(value))
                case Err(error):
                    return Err(f(error))
                case _:
                    return result

        return AsyncResult(_inner())

    def left_map(
        self,
        fa: AsyncResult[_A],
        f: Callable[[Exception], Exception],
    ) -> AsyncResult[_A]:
        async def _inner():
            result = await fa._coro
            match result:
                case Err(error):
                    return Err(f(error))
                case _:
                    return result

        return AsyncResult(_inner())
