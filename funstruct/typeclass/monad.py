"""
Monad: sequence computations that produce new contexts.

F[A] ---( f: A -> F[B] )---> F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from funstruct.typeclass.applicative import Applicative


class Monad(Applicative):
    """Sequence computations that produce new contexts."""

    @abstractmethod
    def bind(self, f: Callable) -> Monad: ...

    def flat_map(self, f: Callable) -> Monad:
        """Alias for bind"""
        return self.bind(f)

    def __rshift__(self, f: Callable) -> Monad:
        """alias for bind"""
        return self.bind(f)


__all__ = ["Monad"]
