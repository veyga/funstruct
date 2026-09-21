"""Representable — the repr() representation of a value.

represent: A → String

Maps to Python's __repr__. Used by repr(), REPL, and debuggers.
For human-friendly __str__, see Stringable.

Examples:

    >>> from funstruct.types.option import Some, Nothing
    >>> repr(Some(42))
    'Some(42)'
    >>> repr(Nothing())
    'Nothing()'
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.typeclass import BaseTypeclass


class Representable(BaseTypeclass):
    """repr() representation for a type."""

    @abstractmethod
    def represent(self, a) -> str:
        # a: A → String
        ...


__all__ = ["Representable"]
