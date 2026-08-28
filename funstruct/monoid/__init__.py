"""Monoid typeclass instances"""

from __future__ import annotations

from types import SimpleNamespace as ___

from funstruct.typeclasses import Monoid
from funstruct.collections.cons import CList, Nil

IntAddition = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)
IntMultiplication = Monoid(typ=int, combine=lambda a, b: a * b, empty=1)
StrConcat = Monoid(typ=str, combine=lambda a, b: a + b, empty="")
CListConcat = Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil())


__all__ = [
    "IntAddition",
    "IntMultiplication",
    "StrConcat",
    "CListConcat",
]
