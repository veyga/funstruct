from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.alternative import Alternative
from funstruct.types.cons import CList, Cons, Nil

_A = TypeVar("_A")
_B = TypeVar("_B")


class _CListAlternative(Alternative, for_type=CList):
    def pure(self, value: _A) -> CList[_A]:
        return Cons(value)

    def ap(
        self,
        ff: CList[Callable[[_A], _B]],
        fa: CList[_A],
    ) -> CList[_B]:
        result: CList[_B] = Nil()
        for f in ff:
            for a in fa:
                result = Cons(f(a), result)
        return result.reversed()

    def empty(self) -> CList:
        return Nil()

    def or_else(self, fa: CList[_A], fb: CList[_A]) -> CList[_A]:
        return fa.append(fb)
