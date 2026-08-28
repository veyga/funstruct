"""
Monoid: a Semigroup with an identity element.

Laws:
  combine(empty, a) == a  (left identity)
  combine(a, empty) == a  (right identity)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from types import SimpleNamespace as ___

from funstruct.typeclass.semigroup import Semigroup
from funstruct.collections.cons import CList


from typing import final


@final
@dataclass(frozen=True)
class Monoid(Semigroup):
    """A Semigroup with an identity element (empty)."""

    typ: type
    combine: Callable
    empty: object


COMMON = ___(
    INT_ADD=Monoid(typ=int, combine=lambda a, b: a + b, empty=0),
    INT_MUL=Monoid(typ=int, combine=lambda a, b: a * b, empty=1),
    STR_CONCAT=Monoid(typ=str, combine=lambda a, b: a + b, empty=""),
    CLIST_CONCAT=Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil()),
)


__all__ = [
    "Monoid",
    "COMMON",
]
