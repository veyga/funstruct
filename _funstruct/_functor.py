"""
Functor / Applicative / Monad hierarchy.

Functor:     map(f: A -> B) -> F[B]
Applicative: product(F[B]) -> F[(A,B)]  +  pure(A) -> F[A]
Monad:       bind(f: A -> F[B]) -> F[B]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")


class Functor(ABC):
    """Transform the value inside a context."""

    @abstractmethod
    def map(self, f: Callable) -> Functor: ...


class Applicative(Functor):
    """Combine independent computations."""

    @abstractmethod
    def product(self, other: Applicative) -> Applicative: ...

    def __add__(self, other: Applicative) -> Applicative:
        return self.product(other)


class Monad(Applicative):
    """Sequence computations that produce new contexts."""

    @abstractmethod
    def bind(self, f: Callable) -> Monad: ...

    def flat_map(self, f: Callable) -> Monad:
        return self.bind(f)


__all__ = ["Functor", "Applicative", "Monad"]
