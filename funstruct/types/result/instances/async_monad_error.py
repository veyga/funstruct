from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.monad_error import MonadError
from funstruct.types.result import AsyncResult, Err, Ok

_A = TypeVar("_A")


class _AsyncResultMonadError(MonadError, for_type=AsyncResult):
    def pure(self, value: _A) -> AsyncResult[_A]:
        async def _inner():
            return Ok(value)

        return AsyncResult(_inner())

    def bind(
        self, fa: AsyncResult[_A], f: Callable[[_A], Any]
    ) -> AsyncResult:
        async def _inner():
            result = await fa._coro
            match result:
                case Ok(value):
                    return await AsyncResult._resolve(f(value))
                case _:
                    return result

        return AsyncResult(_inner())

    def raise_error(self, error: Exception) -> AsyncResult:
        async def _inner():
            return Err(error)

        return AsyncResult(_inner())

    def handle_error_with(
        self, fa: AsyncResult[_A], f: Callable[[Exception], Any]
    ) -> AsyncResult:
        async def _inner():
            result = await fa._coro
            match result:
                case Err(error):
                    return await AsyncResult._resolve(f(error))
                case _:
                    return result

        return AsyncResult(_inner())
