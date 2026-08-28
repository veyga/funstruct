"""
Semigroup: a type with an associative binary combine operation.

Law: combine(combine(a, b), c) == combine(a, combine(b, c))
"""

from __future__ import annotations

from typing import Protocol


class Semigroup(Protocol):
    """Any type that supports + (associative combine)."""

    def __add__(self, other: Semigroup) -> Semigroup: ...


__all__ = ["Semigroup"]
