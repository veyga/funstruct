"""Semigroup: an associative binary combine operation over a type.

Law: combine(combine(a, b), c) == combine(a, combine(b, c))

Unlike Monad/Functor (one instance per type constructor), a type can have
multiple Semigroup instances (e.g. int under + vs int under *). Create
instances directly rather than using for_type= registration.

Examples:

    >>> from funstruct.typeclasses.semigroup import Semigroup
    >>> class IntAdd(Semigroup):
    ...     def combine(self, a, b): return a + b
    >>> IntAdd().combine(1, 2)
    3
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.typeclass import BaseTypeclass


class Semigroup(BaseTypeclass):
    """An associative binary operation over a type."""

    @abstractmethod
    def combine(self, a, b):
        # a: A, b: A → A
        ...


__all__ = [
    "Semigroup",
]
