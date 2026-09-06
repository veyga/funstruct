"""Monad — sequential computation where each step depends on the previous.

bind: F[A] → (A → F[B]) → F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from funstruct.typeclasses.applicative import Applicative


class Monad(Applicative):
    """bind (flatMap), with map and ap derived."""

    @abstractmethod
    def bind(self, fa, f: Callable) -> object: ...

    def map(self, fa, f: Callable) -> object:
        return self.bind(fa, lambda a: self.pure(f(a)))

    def ap(self, ff, fa) -> object:
        return self.bind(ff, lambda f: self.map(fa, f))

    def then(self, fa, fb) -> object:
        return self.bind(fa, lambda _: fb)

    def map2(self, fa, fb, f: Callable) -> object:
        return self.bind(fa, lambda a: self.map(fb, lambda b: f(a, b)))


__all__ = ["Monad"]
