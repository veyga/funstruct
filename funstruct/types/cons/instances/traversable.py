from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.traversable import Traversable
from funstruct.types.cons import CList, Cons, Nil

_A = TypeVar("_A")
_B = TypeVar("_B")


class _CListTraversable(Traversable, for_type=CList):
    def fold_left(self, fa: CList[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        return fa.fold_left(acc, f)

    def fold_right(self, fa: CList[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        return fa.fold_right(acc, f)

    def traverse(
        self,
        fa: CList[_A],
        f: Callable[[_A], Any],
        G: Applicative,
    ) -> Any:
        return fa.fold_right(
            G.pure(Nil()),
            lambda a, acc: G.map2(f(a), acc, lambda b, bs: Cons(b, bs)),  # type: ignore[arg-type]  # HKT limitation
        )
