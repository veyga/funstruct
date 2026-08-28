"""
Monoid: a Semigroup with an identity element.

Law: combine(empty, a) == a == combine(a, empty)

list, str, tuple are all Monoids (with [] / "" / () as identity).
"""

from __future__ import annotations

from typing import Protocol

from funstruct.typeclass.semigroup import Semigroup


class Monoid(Semigroup, Protocol):
    """A Semigroup with an identity element (empty)."""

    @staticmethod
    def empty() -> Monoid: ...


__all__ = ["Monoid"]
