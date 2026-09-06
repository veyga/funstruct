"""Foldable — reduce a structure to a single value.

    fold_left:  (B, A → B) → F[A] → B
    fold_right: (A, B → B) → F[A] → B
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from funstruct.typeclasses.typeclass import BaseTypeclass


class Foldable(BaseTypeclass):
    """fold_left + fold_right."""

    @abstractmethod
    def fold_left(self, fa, acc, f: Callable) -> object: ...

    @abstractmethod
    def fold_right(self, fa, acc, f: Callable) -> object: ...


__all__ = ["Foldable"]
