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
        """Do-notation — compiles yield statements to bind/map chains.

        ``yield`` is a syntactic marker for monadic bind, NOT a generator.
        At decoration time, the function's AST is parsed and each
        ``x = yield expr`` is rewritten to ``expr.bind(lambda x: ...)``.
        No generator runs at call time — the result is a plain function
        of nested bind/map calls.

        Falls back to generator replay when source is unavailable (REPL).

        Works for ALL monads including CList (list monad).

        Example::

            @Result.do
            def pipeline():
                x = yield Ok(10)      # x = yield ... → bind
                y = yield Ok(x + 1)   # same
                return x + y           # final value → map

            # Compiles to:
            # Ok(10).bind(lambda x: Ok(x + 1).map(lambda y: x + y))
        """
        try:
            from funstruct.typeclasses.do_ast import do_ast

            return do_ast(gen_fn)
        except (OSError, TypeError, SyntaxError):
            return self._do_generator(gen_fn)

    def _do_generator(self, gen_fn: Callable[..., Any]) -> Callable[..., Any]:
        """Fallback: generator replay for when AST source is unavailable."""
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
