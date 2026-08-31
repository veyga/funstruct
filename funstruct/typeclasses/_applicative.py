"""Applicative: combine independent computations.

F[A] ─┐
       ├──> F[(A, B)]
F[B] ─┘

Key distinction from Monad:
    Applicative: computations are INDEPENDENT — later values can't depend
    on earlier results. This enables parallel execution and error accumulation.

    Monad: computations are SEQUENTIAL — each step can depend on the
    previous result. This forces serial execution.

When to use Applicative (not Monad):
    - Form validation: validate all fields independently, collect ALL errors
    - Parallel API calls: fetch user AND preferences simultaneously
    - Config parsing: parse each field independently, combine results

Business examples:
    - Validated: validate name + email + age independently, accumulate errors
    - Parallel fetches: fetch(user_id).ap(fetch(prefs_id)) → (User, Prefs)
    - Schema parsing: parse each column independently, report all failures
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

from funstruct.typeclasses._functor import Functor

_A = TypeVar("_A")
_B = TypeVar("_B")


class Applicative(Functor[_A]):
    """Combine independent computations.

    Type parameter:
        _A: The value type inside the applicative.
    """

    @classmethod
    @abstractmethod
    def pure(cls, value: _A, *args, **kwargs) -> Applicative[_A]:
        """Lift a value into the context."""
        ...

    @abstractmethod
    def ap(self, other: Applicative[_B]) -> Applicative[tuple[_A, _B]]: ...

    def __add__(self, other: Applicative[_B]) -> Applicative[tuple[_A, _B]]:
        """Alias for ap."""
        return self.ap(other)


__all__ = [
    "Applicative",
]
