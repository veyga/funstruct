"""
Monad:
'Run this thing, then use its result to decide what to run next'

F[A] ---( f: A -> F[B] )---> F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses._applicative import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")


class Monad(Applicative[_A]):
    """Sequence computations that produce new contexts.

    Type parameter:
        _A: The value type inside the monad.
    """

    @abstractmethod
    def bind(self, f: Callable[[_A], "Monad[_B]"]) -> "Monad[_B]": ...

    @classmethod
    @abstractmethod
    def do(cls, gen_fn: Callable) -> "Monad[_A]":
        """Do-notation via generators. Flattens nested binds."""
        ...

    def ap(self, other: "Monad[_B]") -> "Monad[tuple[_A, _B]]":
        """Default ap derived from bind + map.

        Every Monad is an Applicative, and ap can always be derived from
        bind + map. This can't live on Applicative itself because Applicative
        doesn't have bind — only Monad does. Standalone Applicatives
        must implement ap directly.
        """
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    def flat_map(self, f: Callable[[_A], "Monad[_B]"]) -> "Monad[_B]":
        """Alias for bind."""
        return self.bind(f)

    def __rshift__(self, f: Callable[[_A], "Monad[_B]"]) -> "Monad[_B]":
        """Alias for bind."""
        return self.bind(f)


__all__ = [
    "Monad",
]
