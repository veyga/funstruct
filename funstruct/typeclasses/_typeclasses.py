"""Typeclass hierarchy — instance classes, not mixins.

In v2, typeclasses are standalone operation dictionaries.
Concrete instances (OptionMonad, ResultMonadError, etc.) inherit
from these and only implement the primitives. Derived operations
(map from bind+pure, ap from bind+map) come from the hierarchy.

    class OptionMonad(Monad):
        def pure(self, value): return Some(value)
        def bind(self, fa, f): ...
        # map, ap, product inherited for free
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable


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

    def then(self, fa, fb) -> object:
        return self.bind(fa, lambda _: fb)

    def map2(self, fa, fb, f: Callable) -> object:
        return self.bind(fa, lambda a: self.map(fb, lambda b: f(a, b)))


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


class Traversable(Foldable):
    """traverse + sequence."""

    @abstractmethod
    def traverse(self, fa, f: Callable, G: Applicative) -> object: ...

    def sequence(self, fga, G: Applicative) -> object:
        return self.traverse(fga, lambda x: x, G)


class Bifunctor(ABC):
    """bimap + left_map."""

    @abstractmethod
    def bimap(self, fa, f: Callable, g: Callable) -> object: ...

    def left_map(self, fa, f: Callable) -> object:
        return self.bimap(fa, f, lambda x: x)


__all__ = [
    "Functor",
    "Applicative",
    "Monad",
    "MonadError",
    "Alternative",
    "Foldable",
    "Traversable",
    "Bifunctor",
]
