"""
Semigroup & Monoid: algebraic structures for combining values.

Semigroup: a type with an associative binary combine operation.
    Law: combine(combine(a, b), c) == combine(a, combine(b, c))

Monoid: a Semigroup with an identity element.
    Law: combine(empty, a) == a == combine(a, empty)

In Python, __add__ serves as the combine operation.
list, str, tuple are all Monoids (with [] / "" / () as identity).
"""

from __future__ import annotations

from typing import Protocol, Self


class Semigroup(Protocol):
    """Any type that supports + (associative combine)."""

    def __add__(self, other: Self) -> Self: ...


class Monoid(Semigroup, Protocol):
    """A Semigroup with an identity element (empty)."""

    @staticmethod
    def empty() -> Monoid: ...


__all__ = ["Semigroup", "Monoid"]
