"""
Applicative: combine independent computations.

F[A] ─┐
       ├──> F[(A, B)]
F[B] ─┘
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses import Functor


class Applicative(Functor):
    """Combine independent computations."""

    @abstractmethod
    def pure(cls, value, *args, **kwargs) -> Applicative:
        """Lift a value into the context."""

    @abstractmethod
    def ap(self, other: Applicative) -> Applicative: ...

    def __add__(self, other: Applicative) -> Applicative:
        return self.ap(other)


__all__ = [
    "Applicative",
]
