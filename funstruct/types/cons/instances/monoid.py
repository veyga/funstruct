from __future__ import annotations

from funstruct.typeclasses.monoid import Monoid
from funstruct.types.cons import CList, Nil


class _CListMonoid(Monoid, for_type=CList):
    def combine(self, a, b):
        return a.append(b)

    def empty(self):
        return Nil()


CListConcat = _CListMonoid()
