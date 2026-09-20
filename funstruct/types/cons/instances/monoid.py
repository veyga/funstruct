from __future__ import annotations

from funstruct.typeclasses.monoid import Monoid
from funstruct.types.cons import Nil


class _CListMonoid(Monoid):
    def combine(self, a, b): return a + b
    def empty(self): return Nil()


CListConcat = _CListMonoid()
