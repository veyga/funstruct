"""
Applicative:
'Run these independent things and combine their results'

F[A] ─┐
       ├──> F[(A, B)]
F[B] ─┘

A good way to think of applicatives is when you want to
combine independent computations, but you explicitly don't
want later computations to depend on earlier results.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

from funstruct.typeclasses._functor import Functor

_A = TypeVar("_A")
_B = TypeVar("_B")


class Applicative(Functor[_A]):
    """Combine independent computations.

    Type parameter:
        _A: The value type inside the applicative.
    """

    @classmethod
    @abstractmethod
    def pure(cls, value: _A, *args, **kwargs) -> Applicative[_A]:
        """Lift a value into the context."""
        ...

    @abstractmethod
    def ap(self, other: Applicative[_B]) -> Applicative[tuple[_A, _B]]: ...

    def __add__(self, other: Applicative[_B]) -> Applicative[tuple[_A, _B]]:
        """Alias for ap."""
        return self.ap(other)


__all__ = [
    "Applicative",
]
