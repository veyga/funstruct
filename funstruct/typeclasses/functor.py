"""Functor — map a function over a value in context.

F[A] → (A → B) → F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.typeclass import BaseTypeclass

_A = TypeVar("_A")
_B = TypeVar("_B")


class Functor(BaseTypeclass):
    """map: F[A] → (A → B) → F[B]"""

    @abstractmethod
    def map(self, fa, f: Callable[[_A], _B]) -> Any: ...


__all__ = ["Functor"]
