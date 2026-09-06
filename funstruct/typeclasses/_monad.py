"""Monad: sequential computation where each step depends on the previous.

F[A] ---( f: A -> F[B] )---> F[B]

Key distinction from Applicative:
    Monad adds `bind` — the next computation can DEPEND on the previous
    result. This is what makes it sequential: you can branch, short-circuit,
    or choose the next step based on what just happened.

When to use:
    - Any pipeline where step N depends on the result of step N-1
    - Short-circuiting on failure (Either, Option)
    - Stateful computation where state evolves (State, StateT)
    - Environment-dependent logic (Reader)

Business examples:
    - Either: parse request → validate → fetch from DB → respond
      (each step can fail, later steps depend on earlier results)
    - Option: lookup user → get their email → send notification
      (short-circuits if user doesn't exist)
    - State: parse tokens one-by-one, building an AST
      (each parse step consumes input and updates parser state)
    - Reader: service that reads config at each step
      (DB url, API keys shared across the pipeline)
    - Writer: audit trail — each step logs what it did
      (output accumulates across the pipeline)
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar, final

from funstruct.typeclasses._applicative import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")


# Convention: we use `fa`, `ff`, `fb` instead of `self` in typeclass
# operation methods to more closely match the function signatures of
# Haskell/Scala/Cats, where typeclasses are standalone functions rather
# than methods. This is intentional — not a Python convention violation.
# Python dunder methods (__init__, __repr__, etc.) keep `self` as usual.


class Monad(Applicative[_A]):
    """Sequence computations that produce new contexts.

    Type parameter:
        _A: The value type inside the monad.
    """

    @abstractmethod
    def bind(fa: Monad[_A], f: Callable[[_A], Monad[_B]]) -> Monad[_B]:
        """Scala: ``def flatMap[A, B](fa: F[A])(f: A => F[B]): F[B]``"""
        ...

    @classmethod
    @abstractmethod
    def do(cls, gen_fn: Callable) -> Callable[..., Monad[_A]]:
        """Do-notation via generators. Returns a callable that produces the monad."""
        ...

    @final
    def map(fa: Monad[_A], f: Callable[[_A], _B]) -> Monad[_B]:
        """Derived from bind + pure. Overrides Applicative.map to avoid
        the ap ↔ map circularity.

        Scala: ``def map[A, B](fa: F[A])(f: A => B): F[B]``
        """
        return fa.bind(lambda a: fa.__class__.pure(f(a)))

    @final
    def ap(ff: Monad[_A], fa: Monad[_A]) -> Monad[_B]:
        """Derived from bind + map.

        Scala: ``def ap[A, B](ff: F[A => B])(fa: F[A]): F[B]``

        ff: F[A → B], fa: F[A] → F[B]
        """
        return ff.bind(lambda f: fa.map(f))

    def map2(fa: Monad[_A], fb: Monad[_B], f: Callable[[_A, _B], object]) -> Monad:
        """Combine two monadic values with a function.

        Scala: ``def map2[A, B, C](fa: F[A], fb: F[B])(f: (A, B) => C): F[C]``
        """
        return fa.bind(lambda a: fb.map(lambda b: f(a, b)))

    def then(fa: Monad[_A], fb: Monad[_B]) -> Monad[_B]:
        """Sequence: run fa, discard value, run fb."""
        return fa.bind(lambda _: fb)

    def __rshift__(fa: Monad[_A], f: Callable[[_A], Monad[_B]]) -> Monad[_B]:
        """Alias for bind."""
        return fa.bind(f)


__all__ = [
    "Monad",
]
