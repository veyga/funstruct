"""Monad — sequential computation where each step depends on the previous.

bind: F[A] → (A → F[B]) → F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable

from typing import Any, TypeVar

from funstruct.typeclasses.applicative import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")


class Monad(Applicative):
    """bind (flatMap), with map and ap derived."""

    @abstractmethod
    def bind(self, fa, f: Callable[[_A], Any]) -> Any: ...

    def map(self, fa, f: Callable[[_A], _B]) -> Any:
        return self.bind(fa, lambda a: self.pure(f(a)))

    def ap(self, ff, fa) -> Any:
        return self.bind(ff, lambda f: self.map(fa, f))

    def then(self, fa, fb) -> Any:
        return self.bind(fa, lambda _: fb)

    def map2(self, fa, fb, f: Callable[[_A, _B], _C]) -> Any:
        return self.bind(fa, lambda a: self.map(fb, lambda b: f(a, b)))


__all__ = ["Monad"]
