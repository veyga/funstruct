"""
Monoid: a Semigroup with an identity element.

Laws:
  combine(empty, a) == a  (left identity)
  combine(a, empty) == a  (right identity)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from funstruct.typeclass.semigroup import Semigroup


@dataclass(frozen=True)
class Monoid(Semigroup):
    """A Semigroup with an identity element (empty)."""

    typ: type
    combine: Callable
    empty: object


# Common instances
int_add = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)
int_mul = Monoid(typ=int, combine=lambda a, b: a * b, empty=1)
str_concat = Monoid(typ=str, combine=lambda a, b: a + b, empty="")
list_concat = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])


__all__ = ["Monoid", "int_add", "int_mul", "str_concat", "list_concat"]
