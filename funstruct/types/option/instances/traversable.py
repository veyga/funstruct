from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.traversable import Traversable
from funstruct.types.option import Nothing, Option, Some

_A = TypeVar("_A")
_B = TypeVar("_B")


class _OptionTraversable(Traversable, for_type=Option):
    def fold_left(self, fa: Option[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        match fa:
            case Some(value):
                return f(acc, value)
            case _:
                return acc

    def fold_right(self, fa: Option[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        match fa:
            case Some(value):
                return f(value, acc)
            case _:
                return acc

    def traverse(self, fa: Option[_A], f: Callable[[_A], Any], G: Applicative) -> Any:
        match fa:
            case Some(value):
                return G.map(f(value), Some)
            case _:
                return G.pure(Nothing())
