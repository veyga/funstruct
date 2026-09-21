"""Traversable — map each element to an effect, then collect results.

traverse: (A → G[B]) → F[A] → G[F[B]]
sequence: F[G[A]] → G[F[A]]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.foldable import Foldable

_A = TypeVar("_A")


class Traversable(Foldable):
    """traverse + sequence."""

    @abstractmethod
    def traverse(self, fa, f: Callable[[_A], Any], G: Applicative) -> Any: ...

    def sequence(self, fga, G: Applicative) -> Any:
        return self.traverse(fga, lambda x: x, G)


__all__ = ["Traversable"]
