"""Monoid typeclass instances"""

from __future__ import annotations

from funstruct.collections.cons import CList, Nil
from funstruct.typeclasses import Monoid

IntAddition: Monoid[int] = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)
IntMultiplication: Monoid[int] = Monoid(typ=int, combine=lambda a, b: a * b, empty=1)
StrConcat: Monoid[str] = Monoid(typ=str, combine=lambda a, b: a + b, empty="")
ListConcat: Monoid[list] = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
CListConcat: Monoid[CList] = Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil())
BoolOr: Monoid[bool] = Monoid(typ=bool, combine=lambda a, b: a or b, empty=False)
BoolAnd: Monoid[bool] = Monoid(typ=bool, combine=lambda a, b: a and b, empty=True)


__all__ = [
    "IntAddition",
    "IntMultiplication",
    "StrConcat",
    "CListConcat",
]
