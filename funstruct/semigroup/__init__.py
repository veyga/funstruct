"""Semigroup typeclass instances"""

from __future__ import annotations

from funstruct.collections.cons import CList
from funstruct.typeclasses import Semigroup

IntAddition = Semigroup(typ=int, combine=lambda a, b: a + b)
IntMultiplication = Semigroup(typ=int, combine=lambda a, b: a * b)
StrConcat = Semigroup(typ=str, combine=lambda a, b: a + b)
CListConcat = Semigroup(typ=CList, combine=lambda a, b: a + b)


__all__ = [
    "IntAddition",
    "IntMultiplication",
    "StrConcat",
    "CListConcat",
]
