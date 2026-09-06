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
    - Parallel fetches: fetch(user_id) * fetch(prefs_id) → (User, Prefs)
    - Schema parsing: parse each column independently, report all failures
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses._functor import Functor

_A = TypeVar("_A")
_B = TypeVar("_B")


# See _functor.py for the fa/ff/fb naming convention.


class Applicative(Functor[_A]):
    """Combine independent computations.

    Type parameter:
        _A: The value type inside the applicative.
    """

    @classmethod
    @abstractmethod
    def pure(cls, value: _A, *args, **kwargs) -> Applicative[_A]:
        """Lift a value into the context.

        Scala: ``def pure[A](a: A): F[A]``
        """
        ...

    def map(fa: Applicative[_A], f: Callable[[_A], _B]) -> Applicative[_B]:
        """Derived from ap + pure: ``pure(f).ap(fa)``.

        Monad overrides this with ``bind + pure`` to break the
        ap ↔ map circularity.
        """
        return fa.__class__.pure(f).ap(fa)

    @abstractmethod
    def ap(
        ff: Applicative[Callable[[_A], _B]], fa: Applicative[_A]
    ) -> Applicative[_B]:
        """Apply a wrapped function to a wrapped value.

        Scala: ``def ap[A, B](ff: F[A => B])(fa: F[A]): F[B]``

        ff: F[A → B], fa: F[A] → F[B]
        """
        ...

    def map2(
        fa: Applicative[_A], fb: Applicative[_B], f: Callable[[_A, _B], object]
    ) -> Applicative:
        """Combine two values with a function. Derived from map + ap."""
        return fa.map(lambda a: lambda b: f(a, b)).ap(fb)

    def product(fa: Applicative[_A], fb: Applicative[_B]) -> Applicative[tuple[_A, _B]]:
        """Combine two independent values into a tuple.

        Derived from map + ap.
        """
        return fa.map(lambda a: lambda b: (a, b)).ap(fb)

    def __mul__(fa: Applicative[_A], fb: Applicative[_B]) -> Applicative[tuple[_A, _B]]:
        """Alias for product."""
        return fa.product(fb)


__all__ = [
    "Applicative",
]
