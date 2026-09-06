"""Bifunctor — map over both type parameters.

    bimap:    F[A, B] → (A → C) → (B → D) → F[C, D]
    left_map: F[A, B] → (A → C) → F[C, B]  (derived)
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from funstruct.typeclasses.typeclass import BaseTypeclass


class Bifunctor(BaseTypeclass):
    """bimap + left_map."""

    @abstractmethod
    def bimap(self, fa, f: Callable, g: Callable) -> object: ...

    def left_map(self, fa, f: Callable) -> object:
        return self.bimap(fa, f, lambda x: x)


__all__ = ["Bifunctor"]
