"""Truthable — whether a value is truthy or falsy.

Python-specific typeclass for the __bool__ protocol.

Examples:

    >>> from funstruct.types.option import Some, Nothing
    >>> bool(Some(42))
    True
    >>> bool(Nothing())
    False
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.typeclass import BaseTypeclass


class Truthable(BaseTypeclass):
    """Whether a value is truthy or falsy."""

    @abstractmethod
    def is_truthy(self, a) -> bool: ...


__all__ = ["Truthable"]
