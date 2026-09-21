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
    def bind(self, fa, f: Callable[[_A], Any]) -> Any:
        # fa: F[A], f: A → F[B] → F[B]
        ...

    def map(self, fa, f: Callable[[_A], _B]) -> Any:
        # fa: F[A] → F[B]
        return self.bind(fa, lambda a: self.pure(f(a)))  # type: ignore[arg-type]

    def ap(self, ff, fa) -> Any:
        # ff: F[A → B], fa: F[A] → F[B]
        return self.bind(ff, lambda f: self.map(fa, f))  # type: ignore[arg-type]

    def then(self, fa, fb) -> Any:
        # fa: F[A], fb: F[B] → F[B]
        return self.bind(fa, lambda _: fb)

    def map2(self, fa, fb, f: Callable[[_A, _B], _C]) -> Any:
        # fa: F[A], fb: F[B] → F[C]
        return self.bind(fa, lambda a: self.map(fb, lambda b: f(a, b)))  # type: ignore[arg-type]

    @final
    def do(self, gen_fn: Callable[..., Any]) -> Callable[..., Any]:
        """Do-notation via generators. Desugars yield to bind/pure.

        ``yield`` suspends the generator and extracts the value from
        the monadic context. Works for monads where bind calls the
        continuation exactly once (Option, Result, Either, State, etc.).

        For CList (list monad), use ``funstruct.experimental.do_ast``
        which compiles yield to bind/map chains via AST transformation.

        Example::

            @Result.do
            def pipeline():
                x = yield Ok(10)
                y = yield Ok(x + 1)
                return x + y

            pipeline()  # Ok(21)
        """

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
