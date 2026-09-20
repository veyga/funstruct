"""Bifunctor — map over both type parameters.

bimap:    F[A, B] → (A → C) → (B → D) → F[C, D]
left_map: F[A, B] → (A → C) → F[C, B]  (derived)
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from typing import Any, TypeVar

from funstruct.typeclasses.typeclass import BaseTypeclass

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")


class Bifunctor(BaseTypeclass):
    """bimap + left_map."""

    @abstractmethod
    def bimap(self, fa, f: Callable[[_A], _C], g: Callable[[_B], _D]) -> Any: ...

    def left_map(self, fa, f: Callable[[_A], _B]) -> Any:
        return self.bimap(fa, f, lambda x: x)


__all__ = ["Bifunctor"]
