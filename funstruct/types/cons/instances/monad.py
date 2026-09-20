from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.monad import Monad
from funstruct.types.cons import CList, Cons, Nil

_A = TypeVar("_A")
_B = TypeVar("_B")


class _CListMonad(Monad, for_type=CList):
    def pure(self, value: _A) -> CList[_A]:
        return Cons(value)

    def bind(self, fa: CList[_A], f: Callable[[_A], CList[_B]]) -> CList[_B]:
        return fa.fold_right(Nil(), lambda a, acc: f(a).append(acc))
