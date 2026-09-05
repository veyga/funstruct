"""Applicative: independent computations combined in context.

F[A → B] ─┐
           ├──ap──> F[B]
F[A] ─────┘

F[A] ─┐
       ├──product──> F[(A, B)]
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
    - Parallel fetches: fetch(user_id).product(fetch(prefs_id)) → (User, Prefs)
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
    def ap(self, other: Applicative[_A]) -> Applicative[_B]:
        """Apply a wrapped function to a wrapped value.

        self contains a function A → B, other contains A. Returns F[B].
        """
        ...

    def product(self, other: Applicative[_B]) -> Applicative[tuple[_A, _B]]:
        """Combine two independent values into a tuple.

        Derived from map + ap: lift the tupling function, then apply.
        """
        return self.map(lambda a: lambda b: (a, b)).ap(other)

    def __add__(self, other: Applicative[_B]) -> Applicative[tuple[_A, _B]]:
        """Alias for product."""
        return self.product(other)


__all__ = [
    "Applicative",
]
