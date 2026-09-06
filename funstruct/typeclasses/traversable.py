"""Traversable — map each element to an effect, then collect results.

traverse: (A → G[B]) → F[A] → G[F[B]]
sequence: F[G[A]] → G[F[A]]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.foldable import Foldable


class Traversable(Foldable):
    """traverse + sequence."""

    @abstractmethod
    def traverse(self, fa, f: Callable, G: Applicative) -> object: ...

    def sequence(self, fga, G: Applicative) -> object:
        return self.traverse(fga, lambda x: x, G)


__all__ = ["Traversable"]
