"""
Functor: transform the value inside a context.

F[A] ---( f: A -> B )---> F[B]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")


class Functor(ABC, Generic[_A]):
    """Transform the value inside a context.

    Type parameter:
        _A: The value type inside the functor.
    """

    @abstractmethod
    def map(self, f: Callable[[_A], _B]) -> "Functor[_B]": ...


__all__ = [
    "Functor",
]
