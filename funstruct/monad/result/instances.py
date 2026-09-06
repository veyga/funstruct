"""Typeclass instances for Result and AsyncResult."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.registry import register
from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.typeclasses.monad_error import MonadError
from funstruct.monad.result import AsyncResult, Err, Ok, Result

_A = TypeVar("_A")
_B = TypeVar("_B")


class _ResultMonadError(MonadError):

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


class _ResultBifunctor(Bifunctor):

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


class _AsyncResultMonadError(MonadError):

    def pure(self, value: _A) -> AsyncResult[_A]:
        return AsyncResult.pure(value)

    def bind(
        self, fa: AsyncResult[_A], f: Callable[[_A], AsyncResult[_B]]
    ) -> AsyncResult[_B]:
        return fa.bind(f)

    def raise_error(self, error: Exception) -> AsyncResult:
        return AsyncResult.raise_error(error)

    def handle_error_with(
        self, fa: AsyncResult[_A], f: Callable[[Exception], AsyncResult[_A]]
    ) -> AsyncResult[_A]:
        return fa.handle_error_with(f)


register(MonadError, Result, _ResultMonadError())
register(Bifunctor, Result, _ResultBifunctor())
register(MonadError, AsyncResult, _AsyncResultMonadError())
