"""Foldable — reduce a structure to a single value.

fold_left:  (B, A → B) → F[A] → B
fold_right: (A, B → B) → F[A] → B
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from typing import Any, TypeVar

from funstruct.typeclasses.typeclass import BaseTypeclass

_A = TypeVar("_A")
_B = TypeVar("_B")


class Foldable(BaseTypeclass):
    """fold_left + fold_right."""

    @abstractmethod
    def fold_left(self, fa, acc: _B, f: Callable[[_B, _A], _B]) -> _B: ...

    @abstractmethod
    def fold_right(self, fa, acc: _B, f: Callable[[_A, _B], _B]) -> _B: ...


__all__ = ["Foldable"]
