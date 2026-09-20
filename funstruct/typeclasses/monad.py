"""Monad — sequential computation where each step depends on the previous.

bind: F[A] → (A → F[B]) → F[B]
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar, final

from funstruct.typeclasses.applicative import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")


class Monad(Applicative):
    """bind (flatMap), with map and ap derived."""

    @abstractmethod
    def bind(self, fa, f: Callable[[_A], Any]) -> Any: ...

    def map(self, fa, f: Callable[[_A], _B]) -> Any:
        return self.bind(fa, lambda a: self.pure(f(a)))  # type: ignore[arg-type]  # HKT limitation

    def ap(self, ff, fa) -> Any:
        return self.bind(ff, lambda f: self.map(fa, f))  # type: ignore[arg-type]  # HKT limitation

    def then(self, fa, fb) -> Any:
        return self.bind(fa, lambda _: fb)

    def map2(self, fa, fb, f: Callable[[_A, _B], _C]) -> Any:
        return self.bind(fa, lambda a: self.map(fb, lambda b: f(a, b)))  # type: ignore[arg-type]  # HKT limitation

    @final
    def do(self, gen_fn: Callable[..., Any]) -> Callable[..., Any]:
        """Do-notation via generators. Desugars to bind/pure."""

        def _thunk(*args, **kwargs):
            gen = gen_fn(*args, **kwargs)
            try:
                monadic_val = next(gen)
            except StopIteration as e:
                return self.pure(e.value)

            def step(value):
                try:
                    next_val = gen.send(value)
                    return self.bind(next_val, step)
                except StopIteration as e:
                    return self.pure(e.value)

            return self.bind(monadic_val, step)

        return _thunk


__all__ = ["Monad"]
