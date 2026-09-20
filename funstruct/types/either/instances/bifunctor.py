from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.types.either import Either, Left, Right

_A = TypeVar("_A")
_B = TypeVar("_B")
_E = TypeVar("_E")


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
