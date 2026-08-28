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

    def ap(self, other) -> Monad:
        """Default ap derived from bind + map.

        Every Monad is an Applicative, and ap can always be derived from
        bind + map. This can't live on Applicative itself because Applicative
        doesn't have bind — only Monad does. Standalone Applicatives
        must implement ap directly.
        """
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    def flat_map(self, f: Callable) -> Monad:
        """Alias for bind."""
        return self.bind(f)

    def __rshift__(self, f: Callable) -> Monad:
        """Alias for bind."""
        return self.bind(f)


__all__ = [
    "Monad",
]
