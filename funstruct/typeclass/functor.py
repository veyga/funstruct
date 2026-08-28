"""
Functor: transform the value inside a context.

F[A] ---( f: A -> B )---> F[B]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable


class Functor(ABC):
    """Transform the value inside a context."""

    @abstractmethod
    def map(self, f: Callable) -> Functor: ...


__all__ = ["Functor"]
