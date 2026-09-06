"""Typeclass instances for Either.

EitherMonadError: pure + bind + raise_error + handle_error_with.
map, ap, map2, product derived from the Monad hierarchy.
"""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Bifunctor, MonadError
from funstruct.monad.either import Either, Left, Right


class EitherMonadError(MonadError):

    def pure(self, value):
        return Right(value)

    def bind(self, fa: Either, f):
        match fa:
            case Right(value):
                return f(value)
            case Left():
                return fa
            case _:
                raise TypeError(f"Expected Either, got {type(fa)}")

    def raise_error(self, error):
        return Left(error)

    def handle_error_with(self, fa: Either, f):
        match fa:
            case Left(error):
                return f(error)
            case _:
                return fa


class EitherBifunctor(Bifunctor):

    def bimap(self, fa: Either, f, g):
        match fa:
            case Right(value):
                return Right(g(value))
            case Left(error):
                return Left(f(error))


register(MonadError, Either, EitherMonadError())
register(Bifunctor, Either, EitherBifunctor())


__all__ = ["EitherMonadError", "EitherBifunctor"]
