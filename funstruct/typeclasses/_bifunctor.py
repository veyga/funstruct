"""Bifunctor — map over both type parameters.

F[A, B].bimap(f, g) → F[C, D]
F[A, B].left_map(f) → F[C, B]  (derived: bimap(f, id))

Scala/Cats: ``trait Bifunctor[F[_, _]]``

Instances: Either, Result.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")


class Bifunctor:
    """Map over both sides of a two-parameter type."""

    @abstractmethod
    def bimap(
        fa: Bifunctor,
        f: Callable[[_A], _C],
        g: Callable[[_B], _D],
    ) -> Bifunctor: ...

    def left_map(fa: Bifunctor, f: Callable[[_A], _C]) -> Bifunctor:
        """Derived: map over the left/error side only."""
        return fa.bimap(f, lambda x: x)


__all__ = [
    "Bifunctor",
]
