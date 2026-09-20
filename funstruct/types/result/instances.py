"""Typeclass instances for Result and AsyncResult."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.typeclasses.monad_error import MonadError
from funstruct.types.result import AsyncResult, Err, Ok, Result

_A = TypeVar("_A")
_B = TypeVar("_B")


class _ResultMonadError(MonadError, for_type=Result):
    def pure(self, value: _A) -> Result[_A]:
        return Ok(value)

    def bind(self, fa: Result[_A], f: Callable[[_A], Result[_B]]) -> Result[_B]:
        match fa:
            case Ok(value):
                return f(value)
            case Err():
                return fa
            case _:
                raise TypeError(f"Expected Result, got {type(fa)}")

    def raise_error(self, error: Exception) -> Result:
        return Err(error)

    def handle_error_with(
        self, fa: Result[_A], f: Callable[[Exception], Result[_A]]
    ) -> Result[_A]:
        match fa:
            case Err(error):
                return f(error)
            case _:
                return fa


class _ResultBifunctor(Bifunctor, for_type=Result):
    def bimap(
        self,
        fa: Result[_A],
        f: Callable[[Exception], Exception],
        g: Callable[[_A], _B],
    ) -> Result[_B]:
        match fa:
            case Ok(value):
                return Ok(g(value))
            case Err(error):
                return Err(f(error))
            case _:
                raise TypeError(f"Expected Result, got {type(fa)}")

    def left_map(
        self,
        fa: Result[_A],
        f: Callable[[Exception], Exception],
    ) -> Result[_A]:
        match fa:
            case Err(error):
                return Err(f(error))
            case _:
                return fa


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
