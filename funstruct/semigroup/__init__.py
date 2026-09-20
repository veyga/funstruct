"""Semigroup typeclass instances"""

from __future__ import annotations

from funstruct.collections.cons import CList
from funstruct.typeclasses import Semigroup

IntAddition: Semigroup[int] = Semigroup(typ=int, combine=lambda a, b: a + b)
IntMultiplication: Semigroup[int] = Semigroup(typ=int, combine=lambda a, b: a * b)
StrConcat: Semigroup[str] = Semigroup(typ=str, combine=lambda a, b: a + b)
CListConcat: Semigroup[CList] = Semigroup(typ=CList, combine=lambda a, b: a + b)


__all__ = [
    "IntAddition",
    "IntMultiplication",
    "StrConcat",
    "CListConcat",
]
