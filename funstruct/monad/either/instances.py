"""Typeclass instances for Either."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.utils.registry import register
from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.typeclasses.monad_error import MonadError
from funstruct.monad.either import Either, Left, Right

_A = TypeVar("_A")
_B = TypeVar("_B")
_E = TypeVar("_E")


class _EitherMonadError(MonadError):

    def pure(self, value: _A) -> Either[_E, _A]:
        return Right(value)

    def bind(self, fa: Either[_E, _A], f: Callable[[_A], Either[_E, _B]]) -> Either[_E, _B]:
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


class _EitherBifunctor(Bifunctor):

    def bimap(
        self,
        fa: Either[_E, _A],
        f: Callable[[_E], _B],
        g: Callable[[_A], _B],
    ) -> Either:
        match fa:
            case Right(value):
                return Right(g(value))
            case Left(error):
                return Left(f(error))


register(MonadError, Either, _EitherMonadError())
register(Bifunctor, Either, _EitherBifunctor())
