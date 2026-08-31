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
from typing import TypeVar

from funstruct.typeclasses._applicative import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")


class Monad(Applicative[_A]):
    """Sequence computations that produce new contexts.

    Type parameter:
        _A: The value type inside the monad.
    """

    @abstractmethod
    def bind(self, f: Callable[[_A], Monad[_B]]) -> Monad[_B]: ...

    @classmethod
    @abstractmethod
    def do(cls, gen_fn: Callable) -> Monad[_A]:
        """Do-notation via generators. Flattens nested binds."""
        ...

    def ap(self, other: Monad[_B]) -> Monad[tuple[_A, _B]]:
        """Default ap derived from bind + map.

        Every Monad is an Applicative, and ap can always be derived from
        bind + map. This can't live on Applicative itself because Applicative
        doesn't have bind — only Monad does. Standalone Applicatives
        must implement ap directly.
        """
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    def map2(self, other: Monad[_B], f: Callable) -> Monad:
        """Combine two monadic values with a function.

        map2(fa, fb, f) = fa.bind(a => fb.map(b => f(a, b)))

        Like ap, but you choose the combiner instead of always tupling.
        """
        return self.bind(lambda a: other.map(lambda b: f(a, b)))

    def __rshift__(self, f: Callable[[_A], Monad[_B]]) -> Monad[_B]:
        """Alias for bind."""
        return self.bind(f)


__all__ = [
    "Monad",
]
