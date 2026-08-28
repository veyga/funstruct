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


__all__ = [
    "Semigroup",
]
