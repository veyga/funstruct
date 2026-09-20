"""Applicative — independent computations combined in context.

pure: A → F[A]
ap:   F[A → B] → F[A] → F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.functor import Functor

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")


class Applicative(Functor):
    """pure + ap, with map derived from ap + pure."""

    @abstractmethod
    def pure(self, value: _A) -> Any:
        # A → F[A]
        ...

    @abstractmethod
    def ap(self, ff, fa) -> Any:
        # ff: F[A → B], fa: F[A] → F[B]
        ...

    def map(self, fa, f: Callable[[_A], _B]) -> Any:
        # fa: F[A] → F[B]
        return self.ap(self.pure(f), fa)

    def map2(self, fa, fb, f: Callable[[_A, _B], _C]) -> Any:
        # fa: F[A], fb: F[B] → F[C]
        return self.ap(self.map(fa, lambda a: lambda b: f(a, b)), fb)  # type: ignore[arg-type]

    def product(self, fa, fb) -> Any:
        # fa: F[A], fb: F[B] → F[(A, B)]
        return self.map2(fa, fb, lambda a, b: (a, b))


__all__ = ["Applicative"]
