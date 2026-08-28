"""
Semigroup: an associative binary combine operation over a type.

Law: combine(combine(a, b), c) == combine(a, combine(b, c))

Unlike a Protocol/ABC, this is a value — you can have multiple
Semigroup instances for the same type (e.g. int under + vs int under *).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Semigroup:
    """An associative binary operation over a type."""

    typ: type
    combine: Callable


# Common instances
int_add = Semigroup(typ=int, combine=lambda a, b: a + b)
int_mul = Semigroup(typ=int, combine=lambda a, b: a * b)
str_concat = Semigroup(typ=str, combine=lambda a, b: a + b)
list_concat = Semigroup(typ=list, combine=lambda a, b: a + b)


__all__ = ["Semigroup", "int_add", "int_mul", "str_concat", "list_concat"]
