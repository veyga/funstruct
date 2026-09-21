"""Eq instance for CList."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.cons import CList, Cons, Nil


class _CListEq(Eq, for_type=CList):
    def eq(self, a, b) -> bool:
        match a, b:
            case Cons(ah, at), Cons(bh, bt):
                return ah == bh and at == bt
            case Nil(), Nil():
                return True
            case _, list():
                return list(a) == b
            case _:
                return False
