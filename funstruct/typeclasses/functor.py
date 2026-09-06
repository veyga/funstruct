"""Functor — map a function over a value in context.

    F[A] → (A → B) → F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from funstruct.typeclasses.mixins.auto_register import AutoRegister


class Functor(AutoRegister):
    """map: F[A] → (A → B) → F[B]"""

    @abstractmethod
    def map(self, fa, f: Callable) -> object: ...


__all__ = ["Functor"]
