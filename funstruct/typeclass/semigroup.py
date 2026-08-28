"""
Semigroup: an associative binary combine operation over a type.

Law: combine(combine(a, b), c) == combine(a, combine(b, c))

Unlike a Protocol/ABC, this is a value — you can have multiple
Semigroup instances for the same type (e.g. int under + vs int under *).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from funstruct.collections.cons import CList
from types import SimpleNamespace as ___


@dataclass(frozen=True)
class Semigroup:
    """An associative binary operation over a type."""

    typ: type
    combine: Callable


COMMON = ___(
    INT_ADD=Semigroup(typ=int, combine=lambda a, b: a + b),
    INT_MUL=Semigroup(typ=int, combine=lambda a, b: a * b),
    STR_CONCAT=Semigroup(typ=str, combine=lambda a, b: a + b),
    CLIST_CONCAT=Semigroup(typ=CList, combine=lambda a, b: a + b),
)


__all__ = [
    "Semigroup",
    "COMMON",
]
