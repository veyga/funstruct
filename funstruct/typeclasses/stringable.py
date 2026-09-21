"""Stringable — the str() representation of a value.

string: A → String

Maps to Python's __str__. Used by print(), str(), and f-strings.
Falls back to __repr__ (via Representable) if no Stringable instance exists.

For constructor-syntax repr(), see Representable.
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.typeclass import BaseTypeclass


class Stringable(BaseTypeclass):
    """str() representation for a type — human-friendly display."""

    @abstractmethod
    def string(self, a) -> str:
        # a: A → String
        ...


__all__ = ["Stringable"]
