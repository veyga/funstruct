"""Typeclass hierarchy — instance classes, not mixins.

In v1, Option(Monad) inherits typeclass methods directly.
In v2, typeclasses are standalone operation dictionaries:

    class OptionMonad(Monad):
        def pure(self, value): return Some(value)
        def bind(self, fa, f): ...

    # map, ap, product are inherited from Monad → Applicative → Functor

The typeclass hierarchy provides derived operations via inheritance.
Concrete instances only implement the primitives.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")


class Functor(ABC):
    """map: F[A] → (A → B) → F[B]"""

    @abstractmethod
    def map(self, fa, f: Callable) -> object: ...


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


class Monad(Applicative):
    """bind (flatMap), with map and ap derived."""

    @abstractmethod
    def bind(self, fa, f: Callable) -> object: ...

    def map(self, fa, f: Callable) -> object:
        return self.bind(fa, lambda a: self.pure(f(a)))

    def ap(self, ff, fa) -> object:
        return self.bind(ff, lambda f: self.map(fa, f))


class MonadError(Monad):
    """raise_error + handle_error_with."""

    @abstractmethod
    def raise_error(self, error) -> object: ...

    @abstractmethod
    def handle_error_with(self, fa, f: Callable) -> object: ...


class Alternative(Applicative):
    """empty + or_else."""

    @abstractmethod
    def empty(self) -> object: ...

    @abstractmethod
    def or_else(self, fa, fb) -> object: ...


class Foldable(ABC):
    """fold_left + fold_right."""

    @abstractmethod
    def fold_left(self, fa, acc, f: Callable) -> object: ...

    @abstractmethod
    def fold_right(self, fa, acc, f: Callable) -> object: ...


__all__ = [
    "Functor",
    "Applicative",
    "Monad",
    "MonadError",
    "Alternative",
    "Foldable",
]
