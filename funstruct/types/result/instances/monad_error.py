from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.monad_error import MonadError
from funstruct.types.result import Err, Ok, Result

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
