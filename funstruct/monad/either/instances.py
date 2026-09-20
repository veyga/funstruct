"""Typeclass instances for Either."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.monad.either import Either, Left, Right
from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.typeclasses.monad_error import MonadError
from funstruct.typeclasses.traversable import Traversable

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


class _EitherBifunctor(Bifunctor, for_type=Either):
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
            case _:
                raise TypeError(f"Expected Either, got {type(fa)}")


class _EitherTraversable(Traversable, for_type=Either):
    def fold_left(self, fa: Either[_E, _A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        match fa:
            case Right(value):
                return f(acc, value)
            case _:
                return acc

    def fold_right(self, fa: Either[_E, _A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        match fa:
            case Right(value):
                return f(value, acc)
            case _:
                return acc

    def traverse(self, fa: Either[_E, _A], f: Callable[[_A], Any], G: Applicative) -> Any:
        # Right(a) → f(a).map(Right)
        # Left(e) → G.pure(Left(e))
        match fa:
            case Right(value):
                return G.map(f(value), Right)
            case _:
                return G.pure(fa)
