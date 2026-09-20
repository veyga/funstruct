from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.traversable import Traversable
from funstruct.types.either import Either, Right

_A = TypeVar("_A")
_B = TypeVar("_B")
_E = TypeVar("_E")


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
        match fa:
            case Right(value):
                return G.map(f(value), Right)
            case _:
                return G.pure(fa)
