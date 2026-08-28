"""Monoid typeclass instances"""

from __future__ import annotations


from funstruct.typeclasses import Monoid
from funstruct.collections.cons import CList, Nil

IntAddition = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)
IntMultiplication = Monoid(typ=int, combine=lambda a, b: a * b, empty=1)
StrConcat = Monoid(typ=str, combine=lambda a, b: a + b, empty="")
CListConcat = Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil())
BoolOr = Monoid(typ=bool, combine=lambda a, b: a or b, empty=False)
BoolAnd = Monoid(typ=bool, combine=lambda a, b: a and b, empty=True)


__all__ = [
    "IntAddition",
    "IntMultiplication",
    "StrConcat",
    "CListConcat",
]
