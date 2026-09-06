"""Applicative — independent computations combined in context.

pure: A → F[A]
ap:   F[A → B] → F[A] → F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from funstruct.typeclasses.functor import Functor


class Applicative(Functor):
    """pure + ap, with map derived from ap + pure."""

    @abstractmethod
    def pure(self, value) -> object: ...

    @abstractmethod
    def ap(self, ff, fa) -> object:
        """F[A → B] → F[A] → F[B]"""
        ...

    def map(self, fa, f: Callable) -> object:
        return self.ap(self.pure(f), fa)

    def map2(self, fa, fb, f: Callable) -> object:
        return self.ap(self.map(fa, lambda a: lambda b: f(a, b)), fb)

    def product(self, fa, fb) -> object:
        return self.map2(fa, fb, lambda a, b: (a, b))


__all__ = ["Applicative"]
