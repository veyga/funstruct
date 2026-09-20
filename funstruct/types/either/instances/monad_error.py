from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.monad_error import MonadError
from funstruct.types.either import Either, Left, Right

_A = TypeVar("_A")
_B = TypeVar("_B")
_E = TypeVar("_E")


class _EitherMonadError(MonadError, for_type=Either):
    def pure(self, value: _A) -> Either[_E, _A]:
        return Right(value)

    def bind(
        self, fa: Either[_E, _A], f: Callable[[_A], Either[_E, _B]]
    ) -> Either[_E, _B]:
        match fa:
            case Right(value):
                return f(value)
            case Left():
                return fa
            case _:
                raise TypeError(f"Expected Either, got {type(fa)}")

    def raise_error(self, error: _E) -> Either[_E, _A]:
        return Left(error)

    def handle_error_with(
        self, fa: Either[_E, _A], f: Callable[[_E], Either[_E, _A]]
    ) -> Either[_E, _A]:
        match fa:
            case Left(error):
                return f(error)
            case _:
                return fa
