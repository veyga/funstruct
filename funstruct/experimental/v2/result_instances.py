"""Typeclass instances for Result.

ResultMonadError provides: pure, bind, raise_error, handle_error_with
Inherits for free:         map, ap, map2, product
"""

from __future__ import annotations

from funstruct.experimental.v2._registry import register
from funstruct.experimental.v2._typeclasses import MonadError
from funstruct.experimental.v2.result import Err, Ok, Result


class ResultMonadError(MonadError):

    def pure(self, value) -> Ok:
        return Ok(value)

    def bind(self, fa: Result, f):
        match fa:
            case Ok(value):
                return f(value)
            case Err():
                return fa
            case _:
                raise TypeError(f"Expected Result, got {type(fa)}")

    def raise_error(self, error: Exception) -> Err:
        return Err(error)

    def handle_error_with(self, fa: Result, f):
        match fa:
            case Err(error):
                return f(error)
            case _:
                return fa


register(MonadError, Result, ResultMonadError())


__all__ = ["ResultMonadError"]
