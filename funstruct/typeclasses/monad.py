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
        """Do-notation via generators. Desugars to bind/pure.

        Replays the generator from scratch for each bind path. 
        Each bind creates a fresh generator + replays previous sends 
        to reach the current point.
        """
        monad = self

        def _thunk(*args, **kwargs):
            def go(history):
                gen = gen_fn(*args, **kwargs)
                mv = next(gen)
                for sv in history:
                    mv = gen.send(sv)

                def step(value):
                    try:
                        test = gen_fn(*args, **kwargs)
                        next(test)
                        for sv in history:
                            test.send(sv)
                        test.send(value)
                        return go(history + [value])
                    except StopIteration as e:
                        return monad.pure(e.value)

                return monad.bind(mv, step)

            try:
                return go([])
            except StopIteration as e:
                return monad.pure(e.value)

        return _thunk

    # def do_single(self, gen_fn: Callable[..., Any]) -> Callable[..., Any]:
    #     """Fast do-notation for monads where bind calls the continuation exactly once.
    #
    #     ~3x faster than do() but INCORRECT for CList (list monad) where bind
    #     calls the continuation multiple times. Use when performance matters
    #     and you know the monad is deterministic (Option, Result, Either, State, etc.).
    #     """
    #
    #     def _thunk(*args, **kwargs):
    #         gen = gen_fn(*args, **kwargs)
    #         try:
    #             monadic_val = next(gen)
    #         except StopIteration as e:
    #             return self.pure(e.value)
    #
    #         def step(value):
    #             try:
    #                 next_val = gen.send(value)
    #                 return self.bind(next_val, step)
    #             except StopIteration as e:
    #                 return self.pure(e.value)
    #
    #         return self.bind(monadic_val, step)
    #
    #     return _thunk


__all__ = ["Monad"]
