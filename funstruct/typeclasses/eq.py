"""Eq — structural equality and hashing.

Python requires that if a == b then hash(a) == hash(b).
Eq bundles both operations so this invariant can't be violated.

Examples:

    >>> from funstruct.types.option import Some, Nothing
    >>> Some(1) == Some(1)
    True
    >>> Some(1) == Nothing()
    False
    >>> hash(Some(1)) == hash(Some(1))
    True
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.typeclass import BaseTypeclass


class Eq(BaseTypeclass):
    """Structural equality and hashing for a type."""

    @abstractmethod
    def eq(self, a, b) -> bool:
        # a: A, b: A → Bool
        ...

    @abstractmethod
    def hash(self, a) -> int:
        # a: A → Int
        ...


__all__ = ["Eq"]
