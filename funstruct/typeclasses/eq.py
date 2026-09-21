"""Eq — structural equality comparison.

eq: A → A → Bool

Examples:

    >>> from funstruct.types.option import Some, Nothing
    >>> Some(1) == Some(1)
    True
    >>> Some(1) == Nothing()
    False
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.typeclass import BaseTypeclass


class Eq(BaseTypeclass):
    """Structural equality for a type."""

    @abstractmethod
    def eq(self, a, b) -> bool:
        # a: A, b: A → Bool
        ...


__all__ = ["Eq"]
