"""Semigroup typeclass instances"""

from __future__ import annotations

from types import SimpleNamespace as ___

from funstruct.typeclasses import Semigroup
from funstruct.collections.cons import CList

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
